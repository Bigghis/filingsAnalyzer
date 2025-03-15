# Filings Analyzer API

The Filings Analyzer API is a financial data platform that provides access to **SEC filings** (https://www.sec.gov/edgar/search/), and to **Yahoo Finance** stocks data (statements, market data), and provides analytical tools for investment research and analysis.

It uses **yfinance** library to get the stock data from Yahoo finance, and 
provides a system to grab all relevant data from SEC Edgar filings and save them in a ChromaDB vectorial database.  

It also provides a system **RAG** (Retrieval-Augmented Generation) via **langchain** and **openai API** to extract data from the database using a predefined set of queries, or to ask the user to provide a custom query.


## Features

### SEC Edgar Filings Analysis
- Query and analyze SEC filings (10-K, etc.) for public companies
- Extract specific information from filings using predefined queries


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


## Technical Details
- Built with FastAPI
- Redis caching for improved performance (Yahoo Finance data only)
- BeautifulSoup for parsing SEC filings
- ChromaDB vectorial database for storing and retrieving SEC filings
- WebSocket support for real-time data (TO be implemented..)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/filings-analyzer-api.gitS
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

4. Start Redis server (optional for caching Yahoo Finance data like income statements, balance sheets, etc.):
   ```bash
   # On Linux with Redis installed
   redis-server 
   # or sudo systemctl start redis.service
   
   # On Windows with Docker
   docker run --name redis -p 6379:6379 -d redis
   
   # Verify Redis connection
   redis-cli ping
  ```


## Configuration

The application uses a configuration file `config.py` to manage the parameters.
So you need to set some parameters in the file:

for SEC you need to provide
* COMPANY_NAME: the name of your company, or personal use
* EMAIL: your email

```python
COMPANY_NAME = "Personal Use"
EMAIL = "user@example.com"
``` 


  
## Run the application

5. Run the application with Uvicorn:
   ```bash
   uvicorn src.api.main:app --reload
   ```

6. Access the API documentation at http://localhost:8000/docs

## Details 

### SEC Edgar Downloader

The API includes functionality to download data from the SEC using the `sec_edgar_downloader` library.
Files will be saved as HTML in the `data/sec-edgar-filings` folder. 

#### Document Processing and Storage (example Form 10-K or Form 10-Q filings)

After downloading Form 10-K documents, the system:

1. **Parses HTML Content**: Uses BeautifulSoup to scan and extract text from relevant sections of the 10-K filing, including:
   - Item 1: Business Overview
   - Item 1A: Risk Factors
   - Item 7: Management's Discussion and Analysis
   - Item 7A: Quantitative and Qualitative Disclosures About Market Risk
   - Item 8: Financial Statements

2. **Text Processing**: Cleans and processes the extracted text to remove irrelevant HTML elements, normalize whitespace, and prepare it for vectorization.

3. **ChromaDB Storage**: Stores the processed text in a ChromaDB vectorial database:
   - Each section is stored as a separate document with appropriate metadata (categorized by year and filing type)
   - The database enables semantic search and retrieval for the RAG system


### RAG System

The RAG system uses the ChromaDB vectorial database to store and retrieve SEC filings.
And uses **langchain** manipulations to create queries with relevant long context,
 and **openai API** to create the responses.
So we can query the LLM with a question, and it will use the context from the database to answer the question.
We use OpenAI  `gpt-4o-mini` to generate the responses.



### Data stocks (Yahoo Finance)

The API provides a system to grab all relevant data from Yahoo Finance via yfinance library, providing:

 * Company information
 * Financial statements:
   - Balance sheets
   - Income statements
   - Cash flow statements
 * Historical prices
 * Holders compnay information
 * generic industries and sectors information
 * A screener to filter stocks based on custom criteria 


## Examples 

#### Get Available Queries for a Company

Retrieve available predefined queries for Apple's 10-K filings:

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/queries/available/?symbol=AAPL&filing_type=10-K' \
  -H 'accept: application/json'
```

response:

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


#### Execute a query

Execute a predefined query for Apple's 10-K filings:

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/queries/execute/?symbol=AAPL&key=SWOT&filing_type=10-K&save_to_txt=true' \
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

