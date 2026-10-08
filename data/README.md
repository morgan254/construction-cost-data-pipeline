# Source data dictionary

All records are invented for learning. Currency is Kenyan shillings (KES); amounts exclude tax. Dates use ISO `YYYY-MM-DD` format.

| File | Grain | Key fields and meaning |
|---|---|---|
| `source/projects.csv` | One row per project | `project_id`, name, location, area in square metres, start/end date |
| `source/work_packages.csv` | One row per work package | `work_package_id`, `project_id`, package description |
| `source/boq.xlsx` | One row per priced BOQ line (BOQ worksheet) | `boq_line_id`, package, quantity, unit rate, budget amount (`quantity * unit_rate`) |
| `source/purchases.csv` | One row per purchase order | Order amount is commitment; invoiced amount is actual cost to date |
| `source/valuations.csv` | One row per interim valuation | Certified amount and certification date |
| `source/payments.csv` | One row per client payment | Payment against a valuation, with paid amount and date |
| `source/variations.csv` | One row per variation | Only approved variations affect the current variation total |

All supplier and company names are fictional. The sample reconciles: BOQ budgets equal quantity times rate; invoices do not exceed orders; payments do not exceed certification; all references point to included records. Package cost differences from budget are intentional.

`actual_cost` means supplier invoices recorded against the included purchase orders. It is a learning proxy for actual project cost and does not yet include labour, plant, or other cost ledgers. `committed_cost` is the full order value. Payment lag uses the number of calendar days from a valuation's certification date to its last recorded payment; unpaid valuations have no lag value.
