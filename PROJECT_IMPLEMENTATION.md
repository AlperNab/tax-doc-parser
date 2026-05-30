# Tax Doc Parser — Standalone Real GUI Implementation

This folder is now its own runnable project app. It does not depend on the root all-project dashboard at runtime.

## Run

```bash
./run_gui.sh
```

Windows:

```powershell
.\run_gui_windows.ps1
```

Default URL: `http://127.0.0.1:9158`

## What is inside this project folder

- `app/` — FastAPI backend for this project.
- `static/` — elegant browser GUI.
- `plugins/tax-doc-parser.json` — this project’s own feature/customization/input schema.
- `project_config.json` — readable copy of the same project-specific configuration.
- `data/` — local SQLite jobs, uploads, exports.
- `tests/` — verifies this project has a registered real local engine.

## Project-specific scope

- Domain: `Finance / Tax`
- Target user: `Domain operator, business owner, analyst, or team member who needs this workflow executed reliably.`
- Core job: Tax documents → classified and extracted fields
- Suite: `Finance Document Suite`

## Deep features applied

- form classification
- field extraction
- missing-data checklist
- year/country profiles
- entity-type logic
- accountant review queue
- redaction

## Customization controls

- `execution_mode` — Execution mode (select)
- `country` — country (select)
- `tax_year` — tax year (text)
- `entity_type` — entity type (text)
- `form_types` — form types (text)
- `redaction` — redaction (text)
- `export_schema` — export schema (select)
- `confidence_threshold` — confidence threshold (slider)
- `output_format` — output format (select)
- `language` — language (select)
- `privacy_mode` — privacy mode (select)

## Input fields

- `tax_documents` — Tax documents (text) required
- `work_brief` — Work brief / source text / URL / instructions (textarea) required

## External data policy

The local deterministic core is real and executable. Live external systems are not simulated. If Shopify, ATS, ERP, OCR/STT, maps, SERP, market data, medical databases, tax/customs databases, or other live systems are required, this project reports the missing connector/API requirement instead of inventing data.

---

## Final UX/UI Layer

This project now uses the **Finance Ops Console** pattern.

**UX workflow:** Document intake → extraction → validation → approval/export

**Domain components:**
- Document intake panel
- Extraction table
- Validation ledger
- Approval checklist
- Export connector cards

**Quick actions:**
- Validate totals
- Check duplicates
- Prepare accounting export
- Flag human review

**No fake-data policy:** external/live actions require real connectors or API keys. Missing connectors are reported instead of simulated.
