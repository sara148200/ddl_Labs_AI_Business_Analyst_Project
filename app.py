
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# FastAPI backend address
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide"
)


# Helper function for GET API calls
def get_api_data(endpoint):
    response = requests.get(
        f"{API_URL}/{endpoint}",
        timeout=30
    )
    response.raise_for_status()
    return response.json()


# Check backend connection
try:
    health = get_api_data("health")

    if health.get("status") != "ok":
        st.error("Backend is not healthy.")
        st.stop()

except requests.exceptions.RequestException:
    st.error(
        "Cannot connect to FastAPI. "
        "Please start the backend using: uvicorn api:app --reload"
    )
    st.stop()


st.title("📊 AI Data Analyst & Business Intelligence Agent")

st.caption(
    "Explore illustrative retail data using business metrics, "
    "charts and natural-language questions."
)


# 1. Sales metrics
metrics = get_api_data("metrics")

cols = st.columns(4)

for col, label, value in zip(
    cols,
    ["Revenue", "Orders", "Customers", "Average Order Value"],
    [
        f"{metrics['revenue']:,.2f}",
        metrics["orders"],
        metrics["customers"],
        f"{metrics['average_order_value']:,.2f}"
    ]
):
    col.metric(label, value)


# 2. Monthly revenue and category revenue
left, right = st.columns(2)

with left:
    st.subheader("Monthly revenue")

    monthly_data = get_api_data("monthly-revenue")
    monthly_df = pd.DataFrame(monthly_data)

    st.plotly_chart(
        px.line(
            monthly_df,
            x="month",
            y="revenue",
            markers=True,
            title="Revenue by month"
        ),
        use_container_width=True
    )


with right:
    st.subheader("Revenue by category")

    category_data = get_api_data("category-revenue")
    category_df = pd.DataFrame(category_data)

    st.plotly_chart(
        px.bar(
            category_df,
            x="category",
            y="revenue",
            title="Revenue by category"
        ),
        use_container_width=True
    )


# 3. Top products and customer metrics
left, right = st.columns(2)

with left:
    st.subheader("Top products")

    product_data = get_api_data("top-products")
    product_df = pd.DataFrame(product_data)

    st.plotly_chart(
        px.bar(
            product_df,
            x="product_name",
            y="value",
            title="Top products by revenue"
        ),
        use_container_width=True
    )


with right:
    st.subheader("Customer metrics")

    customer_data = get_api_data("customer-metrics")

    st.json({
        key: value
        for key, value in customer_data.items()
        if key != "top_customers"
    })

    top_customers = pd.DataFrame(
        customer_data["top_customers"]
    )

    st.dataframe(
        top_customers,
        use_container_width=True
    )


# 4. AI Business Analyst
st.divider()

st.subheader("Ask your AI Business Analyst")

st.write(
    "Examples: What is total revenue? | Show monthly revenue as a chart "
    "| Which category generated the most revenue? "
    "| Why did revenue decline last month? "
    "| Which customers are inactive?"
)

question = st.text_input(
    "Ask a question about the retail data",
    placeholder="e.g. Why did revenue decline last month?"
)


if st.button("Analyse", type="primary") and question.strip():

    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question},
            timeout=60
        )

        if response.status_code == 400:
            error_data = response.json()
            st.warning(
                error_data.get("detail", "Unable to analyse the question.")
            )

        else:
            response.raise_for_status()
            result = response.json()

            st.markdown(result["answer"])

            if result["ok"]:
                st.caption(
                    f"Selected data tool: `{result['tool']}`"
                )

                if result["tool"] == "monthly_revenue":
                    df = pd.DataFrame(result["data"])

                    st.plotly_chart(
                        px.line(
                            df,
                            x="month",
                            y="revenue",
                            markers=True
                        ),
                        use_container_width=True
                    )

                elif result["tool"] == "revenue_by_category":
                    df = pd.DataFrame(result["data"])

                    st.plotly_chart(
                        px.bar(
                            df,
                            x="category",
                            y="revenue"
                        ),
                        use_container_width=True
                    )

                elif result["tool"] == "top_products":
                    df = pd.DataFrame(result["data"])

                    st.plotly_chart(
                        px.bar(
                            df,
                            x="product_name",
                            y="value"
                        ),
                        use_container_width=True
                    )

                else:
                    st.json(result["data"])

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")


# 5. Dataset preview through FastAPI
with st.expander("Dataset preview"):

    dataset_data = get_api_data("dataset-preview")
    dataset_df = pd.DataFrame(dataset_data)

    st.dataframe(
        dataset_df,
        use_container_width=True
    )


st.caption(
    "Sample data is synthetic and intended only to demonstrate "
    "the assignment workflow."
)
