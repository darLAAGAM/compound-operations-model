# Chapter 10i: The Invoice Pipeline — From Inbox to General Ledger

## The boring automation that pays back

Invoice intake is not glamorous. That is why it is a good first back-office automation.

Every consumer SME has some version of the same mess: supplier invoices arrive in multiple inboxes, PDFs get downloaded by hand, filenames are inconsistent, tax fields are copied into spreadsheets, accounting receives late documents, and payment status lives in someone's head.

The invoice pipeline turns that into structured review work.

Not autonomous payment. Not magical accounting. A controlled path from inbox to filed PDF to spreadsheet row to accounting review.

## The pipeline

```text
Gmail inbox
  |
  v
Find PDF attachments
  |
  v
Extract text
  |
  v
Classify invoice vs non-invoice
  |
  v
Extract supplier, tax ID, invoice number, dates, base, tax, total
  |
  v
File original PDF in Drive
  |
  v
Append structured row to Sheet
  |
  v
Human review / accounting import
```

The reference backfill processed 100 emails and registered 117 invoices. That is the right kind of result: enough volume to expose messy cases, not so much autonomy that mistakes become expensive.

## What to extract

Use a schema:

| Field | Required | Notes |
|---|---:|---|
| Supplier name | Yes | Normalize aliases later |
| Supplier tax ID | Yes where available | VAT/NIF/EIN depending country |
| Invoice number | Yes | Detect duplicates |
| Invoice date | Yes | Used for filing and accounting period |
| Due date | If available | Payment planning |
| Currency | Yes | Multi-currency needs explicit handling |
| Tax base | If available | Required for tax review |
| Tax amount | If available | VAT/GST/sales tax |
| Total amount | Yes | Must reconcile with PDF |
| Category | Draft | Logistics, inventory, rent, software, marketing, etc. |
| Confidence | Yes | Controls review priority |
| Drive link | Yes | Original evidence |
| Source email | Yes | Traceability |

For a food brand, categories may include ingredients, co-packing, lab testing, cold-chain logistics, and certifications. For beauty, packaging, formulation, compliance, PR samples, and fulfillment. For home, bulky freight, spare parts, assembly content, and warranties. For pet, subscription packaging, safety testing, and delivery. For outdoor, technical materials, warranty repair, and seasonal logistics.

## Filing convention

Use predictable Drive paths:

```text
Finance/
  Invoices/
    2026/
      05/
        supplier-name_invoice-number_2026-05-12.pdf
```

Do not optimize filenames for beauty. Optimize for retrieval and duplicate detection.

## Classification

The first classifier should be conservative:

- Invoice.
- Credit note.
- Receipt.
- Statement.
- Quote/proforma.
- Shipping/customs document.
- Not finance.
- Unknown.

Only invoice and credit-note classes should enter the accounting review queue. Unknowns should be easy to review, not hidden.

## Anomaly cases

Expect mess:

- Scanned PDFs with no embedded text.
- Multi-page invoices with tables split across pages.
- Emails with several invoices attached.
- One invoice sent twice.
- Proforma invoices later replaced by final invoices.
- Supplier names that differ from legal entity names.
- VAT reverse-charge or import documents.
- Multi-currency invoices.
- Handwritten or image-based receipts.
- Invoices embedded as links instead of attachments.

Your pipeline should not pretend these are rare. It should route them to exceptions.

## From Sheet to general ledger

The first month should stop at the review sheet. The second month can connect to accounting.

The safe path:

1. Finance reviews extracted rows.
2. Approved rows are marked ready for import.
3. The accounting system receives a draft bill, not a posted payment.
4. The original PDF link is attached.
5. A later reconciliation checks whether the accounting bill total matches the extracted total.

This keeps the automation useful without letting it move money. The general ledger remains the source of truth after close. The pipeline is intake, classification, evidence filing, and draft preparation.

For recurring suppliers, you can add rules:

- Expected tax ID.
- Expected category.
- Expected currency.
- Expected payment terms.
- Expected monthly range.

Then the system can flag anomalies: a logistics supplier invoice that is 80% above normal, a packaging supplier using a new legal entity, a software invoice charged in the wrong currency, or a duplicated invoice number.

## Review queue design

The review sheet should not be a data dump. It should prioritize work.

Useful columns:

- Status: new, needs review, approved, imported, duplicate, rejected.
- Confidence: high, medium, low.
- Anomaly reason.
- Reviewer.
- Reviewed at.
- Accounting record link.

Finance should be able to filter by “needs review” and clear the queue. If the sheet requires reading every row every day, the automation has only moved the manual work.

## OCR limits

OCR is useful, not perfect. It struggles with low-quality scans, rotated pages, stamps over totals, and complex tables. LLM extraction can infer too much if the text is poor.

Controls:

- Store raw extracted text.
- Store confidence.
- Require human review below threshold.
- Never pay from extracted data alone.
- Reconcile totals against accounting import later.

## What success looks like

After one month:

- Invoices are no longer trapped in inboxes.
- Finance has one review sheet.
- PDFs are filed consistently.
- Duplicate invoices are visible.
- Exceptions are named.
- The accounting owner trusts the queue enough to use it daily.

That is enough. General-ledger posting can come later.

## How to start this in your business

1. Pick one inbox and one Drive folder. Do not start with every employee's email.
2. Build the extraction sheet with supplier, tax ID, invoice number, dates, amounts, currency, confidence, Drive link, and source email.
3. Backfill 50-100 emails and manually inspect every exception category.
4. Keep payment and accounting posting human-approved until the extraction has a clean audit trail.
5. Fork `skills/invoice-pipeline.md` and `prompts/invoice-extract.md` as the artifacts.
