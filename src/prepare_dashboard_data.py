from pathlib import Path
import pandas as pd


# --- Paths (relative to this file) ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # project-02-olist-dashboard/
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "olist"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = DATA_PROCESSED_DIR / "dashboard_orders.csv"


def main() -> None:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # --- Load raw data ---
    orders = pd.read_csv(DATA_RAW_DIR / "olist_orders_dataset.csv")
    items = pd.read_csv(DATA_RAW_DIR / "olist_order_items_dataset.csv")
    products = pd.read_csv(DATA_RAW_DIR / "olist_products_dataset.csv")
    cat_tr = pd.read_csv(DATA_RAW_DIR / "product_category_name_translation.csv")

    print("orders:", orders.shape)
    print("items:", items.shape)
    print("products:", products.shape)
    print("category_translation:", cat_tr.shape)

    # quick sanity check
    print("orders columns:", list(orders.columns)[:8])
    print("items columns:", list(items.columns)[:8])

    # --- Basic cleaning / typing ---
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"]
    )

    # Keep only delivered orders for revenue analysis
    orders_delivered = orders.loc[
        orders["order_status"] == "delivered"
    ].copy()

    # Date columns for filtering and time series
    orders_delivered["order_date"] = (
        orders_delivered["order_purchase_timestamp"].dt.date
    )
    orders_delivered["order_month"] = (
        orders_delivered["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    print("delivered orders:", orders_delivered.shape)
    print(
        "date range:",
        orders_delivered["order_purchase_timestamp"].min(),
        "->",
        orders_delivered["order_purchase_timestamp"].max(),
    )

    # --- Item-level GMV ---
    items = items.copy()
    items["item_gmv"] = items["price"] + items["freight_value"]

    # --- Aggregate to order level ---
    order_metrics = (
        items.groupby("order_id", as_index=False)
        .agg(
            order_gmv=("item_gmv", "sum"),
            order_items=("order_item_id", "count"),
        )
    )

    print("order_metrics:", order_metrics.shape)
    print(order_metrics.head())

    # --- Join back to delivered orders ---
    dash_base = orders_delivered.merge(order_metrics, on="order_id", how="inner")

    print("dash_base:", dash_base.shape)
    print("GMV total:", dash_base["order_gmv"].sum())
    # --- Add category to items ---
    items_cat = (
        items.merge(
            products[["product_id", "product_category_name"]],
            on="product_id",
            how="left"
        )
        .merge(
            cat_tr,
            on="product_category_name",
            how="left"
        )
    )

    # Use English category name
    items_cat["category"] = items_cat["product_category_name_english"].fillna("unknown")

    # --- Dominant category per order (by GMV) ---
    dominant_category = (
        items_cat
        .sort_values("item_gmv", ascending=False)
        .groupby("order_id", as_index=False)
        .first()[["order_id", "category"]]
    )

    print("dominant_category:", dominant_category.shape)
    print(dominant_category["category"].value_counts().head())

    dash_base = dash_base.merge(dominant_category, on="order_id", how="left")
    print("dash_base with category:", dash_base.shape)

    dashboard_orders = dash_base[
        ["order_id", "customer_id", "order_date", "order_month", "order_gmv", "order_items", "category"]
    ].copy()

    dashboard_orders.to_csv(OUTPUT_FILE, index=False)

    print("Final dataset saved:", OUTPUT_FILE)
    print("final shape:", dashboard_orders.shape)
    print(dashboard_orders.head())




if __name__ == "__main__":
    main()