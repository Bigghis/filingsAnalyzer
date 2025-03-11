# Filings Analyzer API

The Filings Analyzer API is a financial data platform that provides access to **SEC filings**, and to **Yahoo Finance** stocks data (statements, market data), and provides analytical tools for investment research and analysis.

It uses **yfinance** library to get the stock data from Yahoo finance, and 
provides a system to grab all relevant data from SEC Edgar filings and save them in a ChromaDB vectorial database.  

It also provides a system **RAG** (Retrieval-Augmented Generation) via **langchain** and **openai API** to extract data from the database using a predefined set of queries, or to ask the user to provide a custom query.


## Features

### SEC Edgar Filings Analysis
- Query and analyze SEC filings (10-K, etc.) for public companies
- Extract specific information from filings using predefined queries
- WebSocket support for long-running queries

### Financial Data (via yfinance)
- Company information and metrics
- Financial statements:
  - Balance sheets
  - Income statements
  - Cash flow statements
- Stock price data
- Dividend information
- Insider transactions
- Institutional holders

### Market Analysis (via OpenAI)
- Industry and sector data
- Stock screening with customizable criteria
- News aggregation for companies

### Authentication
- Secure user registration and authentication
- JWT-based access tokens with refresh capability
- Token blacklisting for secure logout

## SEC Edgar Downloader

The API includes functionality to download data from the SEC using the `sec_edgar_downloader` library.
Files will be saved as HTML in the `data/sec-edgar-filings` folder.

## Technical Details
- Built with FastAPI
- Redis caching for improved performance
- WebSocket support for real-time data
- Comprehensive error handling

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/filings-analyzer-api.git
   cd filings-analyzer-api
   ```

2. Create and activate a virtual environment:
   ```bash
   # Using venv
   python -m venv venv
   
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application with Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Start Redis server (optional for caching data):
   ```bash
   # On Linux with Redis installed
   redis-server 
   # or sudo systemctl start redis.service
   
   # On Windows with Docker
   docker run --name redis -p 6379:6379 -d redis
   
   # Verify Redis connection
   redis-cli ping

6. Access the API documentation at http://localhost:8000/docs


## Examples 

### Get Available Queries for a Company

Retrieve available predefined queries for Apple's 10-K filings from the last 3 years:

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/queries/available/?symbol=AAPL&filing_type=10-K&num_years=3' \
  -H 'accept: application/json'
```

Example response:

```json
{
  "available_queries": {
    "Overview": "Based on the comprehensive review of all items of the latest year 2024 of 10-K filing of AAPL, identify and analyze three positive and three negative aspects regarding the company's prospects...",
    
    "Business and Risk": "Using the combined information from Item 1 (Business Overview), Item 1A (Risk Factors), Item 7 (Management's Discussion and Analysis), Item 7A (Quantitative and Qualitative Disclosures About Market Risk), and Item 8 (Financial Statements) from the latest 10-K filing of AAPL, perform a detailed analysis...",
    
    "Strategic Outlook and Future Projections": "With reference to the information available in Item 1 (Business Overview), Item 1A (Risk Factors), Item 7 (Management's Discussion and Analysis), Item 7A (Quantitative and Qualitative Disclosures About Market Risk), and Item 8 (Financial Statements) of {self.symbol}'s recent 10-K filing, synthesize a strategic report...",
    
    "Risk Factors Years": "Based on the information available in Item 1A (Risk Factors) and Item 7A (Quantitative and Qualitative Disclosures About Market Risk) of 10-K filings of AAPL for last year (2024), Provide a structured analysis how risks have changed and what impacts they have had over the years...",
    
    "SWOT": "Create a SWOT analysis with reference to the information available in Item 1 (Business Overview) and Item 1A (Risk Factors) and Item 7 (Management's Discussion and Analysis) and Item 7A (Quantitative and Qualitative Disclosures About Market Risk) and Item 8 (Financial Statements) of 2024 for AAPL's 10-K filing"
  }
}
```

This endpoint returns a list of available predefined queries that can be run against the specified company's filings.


### Execute a query

Execute a predefined query for Apple's 10-K filings from the last 3 years:

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/queries/execute/?symbol=AAPL&key=SWOT&filing_type=10-K&save_to_txt=true&num_years=3' \
  -H 'accept: application/json'
```

response: 

```json
{
  "query": "Create a SWOT analysis with reference to the information available in Item 1 (Business Overview) and Item 1A (Risk Factors) and Item 7 (Management's Discussion and Analysis) and Item 7A (Quantitative and Qualitative Disclosures About Market Risk) and Item 8 (Financial Statements) of 2024 for AAPL's 10-K filing",
  "response": {
    "SWOT Analysis for Apple Inc. (AAPL) - 2024": {
      "Strengths": [
        "Strong Brand and Market Position: Apple is a leading player in the technology sector, known for its innovative products such as the iPhone, Mac, iPad, and wearables. The brand loyalty and premium pricing strategy contribute to its strong market position.",
        "Diverse Product Portfolio: The company offers a wide range of products and services, including hardware, wearables, and services.",
        "Robust Financial Performance: Total net sales of $391 billion in 2024, with 46.2% gross margin and $140.8 billion cash reserve.",
        "Strong R&D Investment: $31.4 billion in R&D expenses in 2024.",
        "Global Reach: Significant international presence across Americas, Europe, Greater China, Japan, and Rest of Asia Pacific."
      ],
      "Weaknesses": [
        "High Dependency on iPhone Sales: 51.5% of revenue in 2024 from iPhone sales.",
        "Supply Chain Vulnerabilities: Reliance on single or limited suppliers.",
        "High Price Point: Premium pricing may limit market share in price-sensitive segments.",
        "Legal and Regulatory Challenges: Ongoing antitrust and tax-related issues."
      ],
      "Opportunities": [
        "Expansion of Services: 13% revenue increase in services segment in 2024.",
        "Emerging Markets: Growth potential in markets with increasing smartphone penetration.",
        "Technological Advancements: AI, AR, and health technology developments.",
        "Sustainability Initiatives: Leverage environmental responsibility for brand enhancement."
      ],
      "Threats": [
        "Intense Competition: From Samsung, Google, and emerging Chinese brands.",
        "Macroeconomic Conditions: Economic downturns, inflation, and currency fluctuations.",
        "Supply Chain Disruptions: Geopolitical tensions and trade restrictions.",
        "Cybersecurity Risks: Data security and privacy regulatory challenges."
      ]
    }
  }
}
```
