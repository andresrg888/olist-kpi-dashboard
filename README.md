# Olist KPI Dashboard (Streamlit)

Interactive KPI dashboard to explore Olist e-commerce sales performance.

## What you can answer with this dashboard
- How is GMV evolving over time?
- How many orders are happening in a selected time window?
- Is growth driven by more orders or higher AOV?
- Which categories drive most GMV?

## KPIs
- **GMV** (price + freight)
- **Orders**
- **AOV** (GMV / Orders)

## Filters
- Date range (order purchase date)
- Product category (dominant category per order)

## Data pipeline
This project separates data preparation from visualization:
- `src/prepare_dashboard_data.py` builds a clean dataset at **order level**
- Output is saved to `data/processed/dashboard_orders.csv`
- `app.py` loads the processed dataset and renders the dashboard

## How to run locally

### 1) Prepare data
```bash
python src/prepare_dashboard_data.py