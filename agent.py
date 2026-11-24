import json, os, re
from analytics import get_sales_metrics, monthly_revenue, revenue_by_category, top_products, customer_metrics, revenue_decline_analysis

ALLOWED_TOOLS = {"sales_metrics","monthly_revenue","revenue_by_category","top_products","customer_metrics","revenue_decline_analysis"}

def _rule_based_tool(question):
    q=question.lower()
    if any(x in q for x in ["why","decline","drop","decrease","fall"]): return "revenue_decline_analysis"
    if any(x in q for x in ["inactive","repeat","new customer","customer"]): return "customer_metrics"
    if "category" in q: return "revenue_by_category"
    if any(x in q for x in ["top","best","product","selling"]): return "top_products"
    if any(x in q for x in ["month","monthly","trend","chart"]): return "monthly_revenue"
    if any(x in q for x in ["revenue","sales","order","average","aov"]): return "sales_metrics"
    return None

def _llm_select_tool(question):
    """Optional LLM-assisted intent selection. Only an allow-listed tool name is accepted."""
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key: return None
    try:
        from openai import OpenAI
        client=OpenAI(api_key=api_key)
        response=client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
            temperature=0,
            response_format={"type":"json_object"},
            messages=[
                {"role":"system","content":"Select one tool for a retail analytics question. Return JSON only: {\"tool\":\"...\"}. Allowed tools: "+", ".join(sorted(ALLOWED_TOOLS))+". If unsupported, return {\"tool\":\"unsupported\"}. Never calculate or invent data."},
                {"role":"user","content":question}
            ])
        tool=json.loads(response.choices[0].message.content).get("tool")
        return tool if tool in ALLOWED_TOOLS else None
    except Exception:
        return None

def run_tool(tool):
    if tool=="sales_metrics": return get_sales_metrics()
    if tool=="monthly_revenue": return monthly_revenue().to_dict("records")
    if tool=="revenue_by_category": return revenue_by_category().to_dict("records")
    if tool=="top_products": return top_products().to_dict("records")
    if tool=="customer_metrics": return customer_metrics()
    if tool=="revenue_decline_analysis": return revenue_decline_analysis()
    raise ValueError("Unsupported tool")

def answer_question(question):
    if not isinstance(question,str) or not question.strip():
        return {"ok":False,"answer":"Please enter a non-empty question.","tool":None,"data":None}
    if len(question)>500:
        return {"ok":False,"answer":"Question is too long. Please keep it under 500 characters.","tool":None,"data":None}
    tool=_llm_select_tool(question) or _rule_based_tool(question)
    if not tool:
        return {"ok":False,"answer":"I cannot answer that question with the available retail dataset. Try asking about sales, revenue, orders, products, categories or customers.","tool":None,"data":None}
    try:
        data=run_tool(tool)
        return {"ok":True,"answer":_summarize(tool,data),"tool":tool,"data":data}
    except Exception as exc:
        return {"ok":False,"answer":f"Analysis could not be completed: {type(exc).__name__}. Please check the dataset and try again.","tool":tool,"data":None}

def _summarize(tool,data):
    if tool=="sales_metrics":
        return (f"Recorded revenue is {data['revenue']:,.2f} across {data['orders']} orders "
                f"from {data['customers']} customers. Average order value is {data['average_order_value']:,.2f}.")
    if tool=="top_products":
        if not data: return "No product sales were found."
        first=data[0]
        return f"Top product by revenue is {first['product_name']} with {first['value']:,.2f} in recorded revenue."
    if tool=="revenue_by_category":
        if not data: return "No category sales were found."
        return f"{data[0]['category']} is the highest-revenue category with {data[0]['revenue']:,.2f}."
    if tool=="monthly_revenue":
        return f"Retrieved monthly revenue for {len(data)} month(s). The chart/table uses calculated order revenue."
    if tool=="customer_metrics":
        return (f"There are {data['total_customers']} purchasing customers, {data['repeat_customers']} repeat customers "
                f"and {data['inactive_customers']} inactive customers using a {90}-day threshold.")
    if tool=="revenue_decline_analysis":
        if "message" in data: return data["message"]
        direction="increased" if data["revenue_change"]>=0 else "declined"
        pct=data["revenue_change_pct"]
        return (f"Revenue {direction} by {abs(data['revenue_change']):,.2f} ({abs(pct):.2f}%) "
                f"from {data['previous_month']} to {data['current_month']}. "
                f"Orders changed by {data['order_change']}; average order value changed by {data['aov_change']:,.2f}. "
                "The weakest category/product comparisons are included in the analysis data.")
    return "Analysis completed using the selected data tool."
