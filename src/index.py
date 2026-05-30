#!/usr/bin/env python3
"""
tax-doc-parser — W-2, 1099, P60, tax documents → structured fields
Ready for tax software import. Multi-country. Validates totals.
"""
import anthropic, base64, json, re, sys
from pathlib import Path

SYSTEM = """You are a tax professional and document processing specialist.
Extract all tax data from this document into structured, importable JSON.

Rules:
- Validate math: totals should equal sum of components
- Flag any discrepancies between expected and actual totals
- Note the tax year clearly
- Do NOT store SSN/NIN/TIN in full — last 4 digits only for identification
- Map to standard field names across countries

Return ONLY valid JSON — no markdown, no explanation.

{
  "document_type": "W-2|1099-NEC|1099-INT|1099-DIV|1099-B|1099-MISC|1099-G|K-1|P60|P45|P11D|SA302|T4|other",
  "tax_year": "YYYY",
  "issuer": {
    "name": "string or null",
    "ein_or_payer_id": "last 4 digits only",
    "address": "string or null"
  },
  "recipient": {
    "name": "string or null",
    "ssn_last4": "last 4 digits only",
    "address": "string or null"
  },
  "income": {
    "total_income": number_or_null,
    "wages_salaries": number_or_null,
    "tips": number_or_null,
    "self_employment_income": number_or_null,
    "interest_income": number_or_null,
    "dividend_income": number_or_null,
    "qualified_dividends": number_or_null,
    "capital_gains_net": number_or_null,
    "rental_income": number_or_null,
    "other_income": number_or_null
  },
  "taxes_withheld": {
    "federal_income_tax": number_or_null,
    "state_income_tax": number_or_null,
    "social_security_tax": number_or_null,
    "medicare_tax": number_or_null,
    "local_tax": number_or_null,
    "total_taxes_withheld": number_or_null
  },
  "deductions_and_benefits": {
    "retirement_401k": number_or_null,
    "health_insurance": number_or_null,
    "hsa_contributions": number_or_null,
    "dependent_care_fsa": number_or_null,
    "other_pretax_deductions": number_or_null
  },
  "employer_contributions": {
    "retirement_match": number_or_null,
    "health_premiums_employer": number_or_null
  },
  "all_boxes": [
    {"box":"1","label":"Wages, tips, other compensation","value":number_or_null}
  ],
  "currency": "USD|GBP|CAD|EUR|...",
  "state_or_province": "string or null",
  "validation": {
    "totals_check": true_or_false,
    "discrepancies": ["list of math errors or inconsistencies found"],
    "missing_fields": ["fields present on the form type but not found"]
  },
  "tax_software_import": {
    "turbotax_compatible": true_or_false,
    "hrblock_compatible": true_or_false,
    "notes": "import instructions"
  },
  "disclaimer": "Always verify with original documents before filing. Consult a tax professional.",
  "confidence": 0.0
}"""

def parse(source: str) -> dict:
    client = anthropic.Anthropic()
    path = Path(source)
    if path.exists() and source.endswith(".pdf"):
        data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        content = [
            {"type":"document","source":{"type":"base64","media_type":"application/pdf","data":data}},
            {"type":"text","text":"Extract all tax data from this document."}
        ]
    elif path.exists():
        suffix = path.suffix.lower()
        if suffix in (".jpg",".jpeg",".png",".webp"):
            mt = {"jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png","webp":"image/webp"}[suffix.lstrip(".")]
            data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
            content = [
                {"type":"image","source":{"type":"base64","media_type":mt,"data":data}},
                {"type":"text","text":"Extract all tax data from this tax document."}
            ]
        else:
            text = path.read_text(encoding="utf-8",errors="replace")[:20000]
            content = [{"type":"text","text":f"Extract tax data:\n\n{text}"}]
    else:
        content = [{"type":"text","text":f"Extract tax data:\n\n{source[:20000]}"}]

    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=2000, system=SYSTEM,
        messages=[{"role":"user","content":content}]
    )
    raw = re.sub(r'^```(?:json)?\s*','',resp.content[0].text.strip(),flags=re.MULTILINE)
    raw = re.sub(r'\s*```$','',raw,flags=re.MULTILINE)
    return json.loads(raw)

def fmt(v, curr=""): return f"{curr}{v:,.2f}" if v is not None else "N/A"

def print_report(r: dict):
    inc = r.get("income",{})
    taxes = r.get("taxes_withheld",{})
    ded = r.get("deductions_and_benefits",{})
    val = r.get("validation",{})
    curr = r.get("currency","USD")
    print(f"\n{'═'*60}")
    print(f"  TAX DOC PARSER — {r.get('document_type','?')} ({r.get('tax_year','?')})")
    print(f"  Issuer: {r.get('issuer',{}).get('name','?')}")
    print(f"  {'✅ Totals verified' if val.get('totals_check') else '⚠ Math discrepancy found'}")
    print(f"{'═'*60}")
    print(f"\n  INCOME")
    if inc.get("wages_salaries"): print(f"  Wages/Salary:    {fmt(inc['wages_salaries'],curr)}")
    if inc.get("self_employment_income"): print(f"  Self-employment: {fmt(inc['self_employment_income'],curr)}")
    if inc.get("interest_income"): print(f"  Interest:        {fmt(inc['interest_income'],curr)}")
    if inc.get("dividend_income"): print(f"  Dividends:       {fmt(inc['dividend_income'],curr)}")
    if inc.get("capital_gains_net"): print(f"  Capital gains:   {fmt(inc['capital_gains_net'],curr)}")
    if inc.get("total_income"): print(f"  TOTAL:           {fmt(inc['total_income'],curr)}")
    print(f"\n  TAXES WITHHELD")
    if taxes.get("federal_income_tax"): print(f"  Federal:         {fmt(taxes['federal_income_tax'],curr)}")
    if taxes.get("state_income_tax"): print(f"  State:           {fmt(taxes['state_income_tax'],curr)}")
    if taxes.get("social_security_tax"): print(f"  Social Security: {fmt(taxes['social_security_tax'],curr)}")
    if taxes.get("medicare_tax"): print(f"  Medicare:        {fmt(taxes['medicare_tax'],curr)}")
    if taxes.get("total_taxes_withheld"): print(f"  TOTAL:           {fmt(taxes['total_taxes_withheld'],curr)}")
    if ded.get("retirement_401k") or ded.get("health_insurance"):
        print(f"\n  PRE-TAX DEDUCTIONS")
        if ded.get("retirement_401k"): print(f"  401(k):          {fmt(ded['retirement_401k'],curr)}")
        if ded.get("health_insurance"): print(f"  Health ins:      {fmt(ded['health_insurance'],curr)}")
    discrep = val.get("discrepancies",[])
    if discrep:
        print(f"\n  ⚠ DISCREPANCIES")
        for d in discrep: print(f"  ! {d}")
    missing = val.get("missing_fields",[])
    if missing: print(f"\n  Missing fields: {', '.join(missing[:3])}")
    print(f"\n  ⚠ {r.get('disclaimer','')}")
    print(f"  Confidence: {int(r.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    if len(sys.argv)<2: print("Usage: python -m tax_doc_parser <w2.pdf|1099.jpg|.txt> [--json]"); sys.exit(0)
    r = parse(sys.argv[1])
    if "--json" in sys.argv: print(json.dumps(r,indent=2,ensure_ascii=False))
    else: print_report(r)
