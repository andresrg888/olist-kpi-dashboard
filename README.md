# Olist KPI Dashboard (Streamlit)

Interactive KPI dashboard to explore Olist e-commerce sales performance, focusing on revenue trends and category-level insights.

## 🚀 Live Demo

You can view the deployed dashboard here:

**[Olist Dashboard Live Demo](https://olist-kpi-dashboard-xgaf4r8t47axffxwx2zmxp.streamlit.app/)**

---

## 📊 Business Questions Answered
This dashboard helps business stakeholders understand:
- **Revenue Growth:** How is GMV (Gross Merchandise Value) evolving month-over-month?
- **Order Volume:** How many delivered orders are being processed in specific timeframes?
- **Operational Efficiency:** Is revenue growth driven by increased organic demand (Order Count) or higher ticket sizes (AOV)?
- **Category Performance:** Which product categories are currently the primary drivers of revenue?

## 💡 Key Metrics (KPIs)
- **GMV:** Total revenue (Price + Freight) from delivered orders.
- **Orders:** Count of unique successfully delivered orders.
- **AOV (Average Order Value):** GMV divided by the number of orders, indicating customer spending behavior.

---

## 🛠 Project Structure
```text
.
├── app.py                # Streamlit application (Frontend)
├── src/
│   └── prepare_dashboard_data.py  # Data processing pipeline
├── data/
│   ├── raw/              # Original dataset (Olist Kaggle)
│   └── processed/
│       └── dashboard_orders.csv   # Cleaned dataset for the dashboard
├── notebooks/            # Exploratory research and drafting
├── requirements.txt      # Python dependencies
└── README.md
```

---

## ⚙️ How to Use This Dashboard

### 1. Filters & Navigation
- **Date Range:** Use the sidebar to select specific windows (e.g., peak seasons like Black Friday).
- **Category Filter:** Filter by specific niches or compare all categories simultaneously.
- **Dynamic Metrics:** KPIs automatically recalculate based on your active filters.

### 2. Local Setup
If you wish to run this project locally:

**Step 1: Clone and install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: (Optional) Refresh data pipeline**
```bash
python src/prepare_dashboard_data.py
```

**Step 3: Launch the app**
```bash
streamlit run app.py
```

---

## 📋 Notes & Data Source
- **Data Source:** [Olist E-Commerce Dataset (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Status:** The processed dataset `data/processed/dashboard_orders.csv` is tracked in the repository to ensure immediate functionality upon deployment.