from agent import answer_question

def test_known_question_routes_to_metrics():
    r=answer_question("What is total revenue?")
    assert r["ok"] and r["tool"]=="sales_metrics"

def test_product_question_routes_to_products():
    r=answer_question("Show top 5 products by revenue")
    assert r["ok"] and r["tool"]=="top_products"

def test_multistep_question_routes_correctly():
    r=answer_question("Why did revenue decline last month?")
    assert r["ok"] and r["tool"]=="revenue_decline_analysis"

def test_unsupported_question_is_handled():
    r=answer_question("What is the weather tomorrow?")
    assert not r["ok"] and r["tool"] is None

def test_empty_question_is_rejected():
    assert not answer_question(" ")["ok"]
