from analytics import get_sales_metrics, monthly_revenue, revenue_by_category, top_products, customer_metrics, revenue_decline_analysis, load_data

def test_dataset_loads_and_revenue_is_nonnegative():
    df=get_data()
    assert not df.empty
    assert (df.revenue >= 0).all()

def get_data():
    return load_data()[3]

def test_sales_metrics_are_consistent():
    m=get_sales_metrics()
    assert m["orders"] > 0
    assert m["revenue"] >= 0
    assert m["average_order_value"] >= 0

def test_monthly_revenue_has_months():
    m=monthly_revenue()
    assert not m.empty
    assert {"month","revenue","orders"}.issubset(m.columns)

def test_category_and_product_rankings():
    assert len(revenue_by_category()) > 0
    p=top_products()
    assert len(p) > 0
    assert p.iloc[0]["value"] >= p.iloc[-1]["value"]

def test_customer_metrics():
    c=customer_metrics()
    assert c["total_customers"] > 0
    assert c["repeat_customers"] >= 0

def test_multistep_analysis_returns_result():
    result=revenue_decline_analysis()
    assert isinstance(result,dict)
    assert "message" in result or "revenue_change" in result
