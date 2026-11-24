
# AI Data Analyst & Business Intelligence Agent

## 1. Project Overview

The AI Data Analyst & Business Intelligence Agent is a data analytics application that helps users explore retail business data through interactive dashboards and natural-language questions.

The application provides important business insights such as total revenue, order count, average order value, monthly revenue trends, product performance, category-wise revenue, and customer metrics.

Users can also ask questions in simple English, such as "What is the total revenue?" or "Which category generated the most revenue?" The AI agent identifies the user's intention, selects an appropriate analytical tool, and returns results based on the available dataset.

The project uses Streamlit for the frontend, FastAPI for backend REST APIs, Python and Pandas for data processing, and SQLite for database storage.

## 2. Project Setup and Installation

### Prerequisites

- Python 3.10 or above
- pip (Python package manager)
- Visual Studio Code or another Python IDE

### Step 1: Clone or Download the Project

Download the project and open its folder in Visual Studio Code.

### Step 2: Create a Virtual Environment

Open the terminal in the project directory and run:

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

If necessary, install the HTTP requests library:

```bash
pip install requests
```

### Step 5: Configure the Environment Variables (Optional)

The application supports optional OpenAI API integration for LLM-assisted tool selection.

Create a `.env` file or configure the environment variables in your terminal:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

The API key must also be available as an environment variable when running the application. The project reads it using `os.getenv()`.

If an API key is not configured, the application uses rule-based tool selection.

Do not upload your API key or `.env` file to a public GitHub repository.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Streamlit | Interactive frontend and dashboard |
| FastAPI | Backend REST API development |
| Uvicorn | Runs the FastAPI application server |
| Pandas | Data cleaning, processing and analysis |
| SQLite | Database storage |
| Plotly | Interactive charts and visualizations |
| OpenAI API | Optional LLM-assisted tool selection |
| Pydantic | Request data validation |
| Requests | HTTP communication between Streamlit and FastAPI |
| Pytest | Automated testing |

## 4. LLM / Model Used

The project supports an optional OpenAI language model for understanding natural-language business questions and selecting the appropriate analytical tool.

- Model: GPT-4o-mini (configurable through the `OPENAI_MODEL` environment variable).
- Integration: OpenAI API using the Chat Completions interface.
- Purpose: Intent understanding and analytical tool selection.
- Output format: JSON containing the selected tool name.

The LLM is instructed to select only from a predefined list of available tools. It does not independently calculate or invent business metrics.

If the OpenAI API key is unavailable or the LLM request fails, the application falls back to rule-based keyword matching.

## 5. Database

The application uses SQLite as its database.

SQLite provides lightweight, local database storage without requiring a separate database server.

The database is initialized through the `initialize_database()` function when the FastAPI application starts.

The application uses retail data involving:

- Customers
- Products
- Orders

Pandas is used to process the data and calculate business metrics.

The project includes illustrative synthetic data for demonstration purposes rather than actual company or customer information.

## 6. Major Features

### A. Interactive Business Dashboard

The Streamlit dashboard displays key business performance indicators:

- Total Revenue
- Total Orders
- Total Customers
- Average Order Value (AOV)

### B. Revenue Analysis

- Monthly revenue trends
- Category-wise revenue analysis
- Revenue comparison between periods
- Revenue change analysis

### C. Product Analysis

- Top-performing products
- Product-wise revenue analysis

### D. Customer Analysis

- Total purchasing customers
- Repeat customers
- Inactive customers
- Top customers

### E. Natural-Language Question Answering

Users can ask business-related questions in simple English.

Examples:

- What is the total revenue?
- Show monthly revenue.
- Which category generated the most revenue?
- Which products generated the highest revenue?
- Which customers are inactive?
- Why did revenue decline last month?

The system selects the appropriate analytical tool and displays the calculated answer.

### F. Interactive Visualizations

Plotly is used to generate interactive charts, including:

- Monthly revenue line charts
- Category-wise revenue bar charts
- Top-products revenue charts

### G. REST API Integration

FastAPI provides backend endpoints that allow the Streamlit frontend to retrieve analytical results and submit natural-language questions.

## 7. AI / Agent Approach

The project uses an LLM-assisted tool-selection approach combined with rule-based fallback logic.

The agent is implemented in `agent.py`.

The workflow consists of the following steps:

1. User Input: The user enters a business-related question through the Streamlit dashboard.

2. Question Processing: The question is passed to the FastAPI `/ask` endpoint.

3. Intent Understanding: The agent attempts to use the OpenAI language model to identify the user's intent and select the appropriate analytical tool.

4. Tool Selection: The agent selects from six predefined tools:
   - `sales_metrics`
   - `monthly_revenue`
   - `revenue_by_category`
   - `top_products`
   - `customer_metrics`
   - `revenue_decline_analysis`

5. Rule-Based Fallback: If the LLM is unavailable or does not return a valid tool, the agent uses keyword-based rule matching.

6. Tool Execution: The selected Python function is executed using the analytics module.

7. Data Analysis: Pandas and the underlying database are used to calculate the actual business results.

8. Response Generation: The agent formats the calculated results into a readable response and returns the answer and supporting data through FastAPI.

The application follows a controlled tool-execution approach. The LLM selects an available tool, while predefined Python functions perform the actual calculations. This helps keep analytical results grounded in the available dataset.

## 8. API Endpoints

The FastAPI backend provides the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks backend availability |
| GET | `/metrics` | Returns overall sales metrics |
| GET | `/monthly-revenue` | Returns monthly revenue data |
| GET | `/category-revenue` | Returns category-wise revenue |
| GET | `/top-products` | Returns top product information |
| GET | `/customer-metrics` | Returns customer analytics |
| GET | `/dataset-preview` | Returns a preview of the dataset |
| POST | `/ask` | Processes natural-language analytical questions |

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 9. How to Run the Application

The project uses two separate applications: a FastAPI backend and a Streamlit frontend.

### Terminal 1: Start the FastAPI Backend

Activate the virtual environment and run:

```bash
uvicorn api:app --reload 
```

The backend will run at:

```text
http://127.0.0.1:8000
```

### Terminal 2: Start the Streamlit Frontend

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run app.py
```

The dashboard will open at:

```text
http://localhost:8501
```

Keep both applications running while using the dashboard.

Streamlit communicates with FastAPI through HTTP GET and POST requests using the Requests library.

## 10. Project Structure

```text
ddl_labs_ai_business_analyst/
│
├── app.py
│   └── Streamlit frontend and dashboard
│
├── api.py
│   └── FastAPI backend and REST endpoints
│
├── agent.py
│   └── LLM-assisted tool selection and agent logic
│
├── analytics.py
│   └── Data processing and business calculations
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
│
├── tests/
│   ├── test_analytics.py
│   └── test_agent.py
│
├── requirements.txt
│   └── Project dependencies
│
├── .env.example
│   └── Example environment configuration
│
├── README.md
│   └── Project documentation
│
└── EXECUTIVE_SUMMARY.md
    └── Project findings and business summary
```

## 11. Testing

The project includes automated tests using Pytest.

The tests cover the analytics functions and agent functionality.

To run the test suite, execute:

```bash
pytest -q
```

The tests help verify:

- Business metric calculations
- Revenue analysis functions
- Analytical tool selection
- Agent responses
- Input validation and unsupported questions

API endpoints can also be tested through the FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## 12. Known Limitations

- Synthetic Dataset: The application uses illustrative retail data. Results do not represent actual company performance.
- Limited Analytical Scope: The agent can answer questions only within the six predefined analytical tools and available dataset.
- Rule-Based Fallback: Without a working OpenAI API connection, tool selection relies on keyword matching, which may not understand every variation of a question.
- LLM Dependency: LLM-assisted tool selection requires a valid OpenAI API key, an available model and an internet connection.
- Limited Context: The agent does not maintain a multi-turn conversational memory or understand complex follow-up questions.
- Revenue Decline Analysis: The analysis identifies changes in revenue, orders and average order value. It does not establish the actual cause of a revenue decline.
- Local Deployment: The application is configured for local development and does not include production authentication, authorization, or deployment hardening.

## 13. Conclusion

The AI Data Analyst & Business Intelligence Agent demonstrates how data analytics, REST API development, and Generative AI can be combined to build an interactive business intelligence application.

It provides a simple interface for exploring retail data, understanding business performance, and obtaining analytical insights through natural-language questions.

The project demonstrates the integration of Python-based analytics, an LLM-assisted tool-selection workflow, FastAPI backend services, SQLite storage, and Streamlit visualizations.
