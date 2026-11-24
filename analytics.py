from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "retail.db"

def load_data(data_dir=DATA_DIR):
    """Load, validate, clean and join the three source CSV files."""
    data_dir = Path(data_dir)
    customers = pd.read_csv(data_dir / "customers.csv")
    products = pd.read_csv(data_dir / "products.csv")
    orders = pd.read_csv(data_dir / "orders.csv")
    for df, key in [(customers, "customer_id"), (products, "product_id"), (orders, "order_id")]:
        df.drop_duplicates(subset=[key], inplace=True)
    customers["signup_date"] = pd.to_datetime(customers["signup_date"], errors="coerce")
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    for col in ["quantity", "unit_price", "discount"]:
        orders[col] = pd.to_numeric(orders[col], errors="coerce")
    orders["quantity"] = orders["quantity"].fillna(1).clip(lower=1)
    orders["discount"] = orders["discount"].fillna(0).clip(lower=0, upper=1)
    orders["unit_price"] = orders["unit_price"].fillna(0).clip(lower=0)
    orders = orders.dropna(subset=["order_date", "customer_id", "product_id"])
    orders = orders[orders["customer_id"].isin(customers["customer_id"])]
    orders = orders[orders["product_id"].isin(products["product_id"])]
    df = orders.merge(customers, on="customer_id", how="left").merge(products, on="product_id", how="left", suffixes=("_order", "_catalog"))
    df["unit_price"] = df["unit_price_order"].fillna(df["unit_price_catalog"])
    df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return customers, products, orders, df

def initialize_database():
    customers, products, orders, _ = load_data()
    with sqlite3.connect(DB_PATH) as conn:
        customers.to_sql("customers", conn, if_exists="replace", index=False)
        products.to_sql("products", conn, if_exists="replace", index=False)
        orders.to_sql("orders", conn, if_exists="replace", index=False)
    return DB_PATH

def get_dataset():
    return load_data()[3]

def get_sales_metrics():
    df = get_dataset()
    revenue = float(df.revenue.sum())
    order_count = int(df.order_id.nunique())
    return {"revenue": round(revenue,2), "orders": order_count,
            "customers": int(df.customer_id.nunique()),
            "average_order_value": round(revenue/order_count,2) if order_count else 0}

def monthly_revenue():
    df = get_dataset()
    return df.groupby("month", as_index=False).agg(revenue=("revenue","sum"), orders=("order_id","nunique")).sort_values("month")

def revenue_by_category():
    df = get_dataset()
    return df.groupby("category", as_index=False).agg(revenue=("revenue","sum")).sort_values("revenue",ascending=False)

def top_products(limit=5, by="revenue"):
    df = get_dataset()
    metric = "revenue" if by == "revenue" else "quantity"
    return (df.groupby(["product_id","product_name"],as_index=False)
            .agg(value=(metric,"sum")).sort_values("value",ascending=False).head(limit))

def customer_metrics(inactive_days=90):
    df = get_dataset()
    today = df.order_date.max()
    counts = df.groupby("customer_id").order_id.nunique()
    last = df.groupby("customer_id").order_date.max()
    return {"total_customers": int(df.customer_id.nunique()),
            "new_customers": int((df.groupby("customer_id").signup_date.min() >= today-pd.Timedelta(days=30)).sum()),
            "repeat_customers": int((counts > 1).sum()),
            "inactive_customers": int((last < today-pd.Timedelta(days=inactive_days)).sum()),
            "top_customers": (df.groupby("customer_name",as_index=False).revenue.sum()
                              .sort_values("revenue",ascending=False).head(5).to_dict("records"))}

def revenue_decline_analysis():
    """Compare latest available month with its immediately preceding calendar month."""
    monthly = monthly_revenue().copy()
    if len(monthly) < 2:
        return {"message":"Not enough monthly history to compare two months."}
    latest = pd.Period(monthly.iloc[-1]["month"],freq="M")
    previous = str(latest - 1)
    current = monthly[monthly.month == str(latest)]
    prior = monthly[monthly.month == previous]
    if current.empty or prior.empty:
        return {"message":f"Cannot compare {latest} with {previous}: one month has no recorded orders."}
    cur_rev, prev_rev = float(current.iloc[0].revenue), float(prior.iloc[0].revenue)
    cur_orders, prev_orders = int(current.iloc[0].orders), int(prior.iloc[0].orders)
    cur_aov = cur_rev/cur_orders if cur_orders else 0
    prev_aov = prev_rev/prev_orders if prev_orders else 0
    cur = get_dataset()
    cur_month = cur[cur.month == str(latest)]
    prev_month = cur[cur.month == previous]
    def group_change(frame_a, frame_b, col):
        a=frame_a.groupby(col).revenue.sum()
        b=frame_b.groupby(col).revenue.sum()
        joined=pd.concat([a.rename("current"),b.rename("previous")],axis=1).fillna(0)
        joined["change"]=joined.current-joined.previous
        return joined.sort_values("change").head(3).reset_index().to_dict("records")
    return {"current_month":str(latest),"previous_month":previous,
            "current_revenue":round(cur_rev,2),"previous_revenue":round(prev_rev,2),
            "revenue_change":round(cur_rev-prev_rev,2),
            "revenue_change_pct":round((cur_rev-prev_rev)/prev_rev*100,2) if prev_rev else None,
            "current_orders":cur_orders,"previous_orders":prev_orders,
            "order_change":cur_orders-prev_orders,
            "current_aov":round(cur_aov,2),"previous_aov":round(prev_aov,2),
            "aov_change":round(cur_aov-prev_aov,2),
            "weakest_categories":group_change(cur_month,prev_month,"category"),
            "weakest_products":group_change(cur_month,prev_month,"product_name")}
