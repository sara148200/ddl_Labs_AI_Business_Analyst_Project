
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from analytics import (
    get_dataset,
    get_sales_metrics,
    monthly_revenue,
    revenue_by_category,
    top_products,
    customer_metrics,
    revenue_decline_analysis,
    initialize_database
)

from agent import answer_question

app = FastAPI(
    title="AI Data Analyst & BI Agent",
    version="1.0.0",
    description="Grounded retail analytics API with controlled tool routing."
)


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return get_sales_metrics()


@app.get("/monthly-revenue")
def monthly():
    return monthly_revenue().to_dict("records")


@app.get("/category-revenue")
def categories():
    return revenue_by_category().to_dict("records")


@app.get("/top-products")
def products():
    return top_products().to_dict("records")


@app.get("/customer-metrics")
def customers():
    data = customer_metrics()

    # Convert a nested DataFrame into JSON-compatible records
    if isinstance(data, dict) and hasattr(data.get("top_customers"), "to_dict"):
        data["top_customers"] = data["top_customers"].to_dict("records")

    return data


@app.get("/dataset-preview")
def dataset_preview():
    return get_dataset().head(30).to_dict("records")


@app.post("/ask")
def ask(payload: Question):
    result = answer_question(payload.question)

    if not result["ok"]:
        raise HTTPException(
            status_code=400,
            detail=result["answer"]
        )

    return result
