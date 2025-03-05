from langchain_core.structured_query import Comparator
from langchain.chains.query_constructor.base import StructuredQueryOutputParser, get_query_constructor_prompt
# from sec.K10 import RELEVANT_ITEMS
document_content_description = "Yearly financial reports of the company"

# Define allowed comparators list
allowed_comparators = [
        Comparator.EQ,
        Comparator.NE,
        Comparator.GT,
        Comparator.GTE,
        Comparator.LT,
        Comparator.LTE,
        Comparator.IN,
        Comparator.NIN
    ]

# Examples for few-shot learning
examples = [
    (
        "The Item1 in 2023 financial report",
        {
            "query": "get the Item1 for 2023",
            "filter": 'and(in("year", ["2023"]),in("type", ["Item 1"]))',
        },
    ),
    (
        "The Item8 in 2022 financial report",
        {
            "query": "get the Item8 for 2022",
            "filter": 'and(in("year", ["2022"]),in("type", ["Item 8"]))',
        },
    ),
    (
        "All items in 2022 financial report",
        {
            "query": "get all items for 2022",
            "filter": 'and(in("year", ["2022"]))',
        },
    ),
]

def get_query_constructor(metadata_field_info):
    # Create constructor prompt
    constructor_prompt = get_query_constructor_prompt(
        document_content_description,
        metadata_field_info,
        allowed_comparators=allowed_comparators,
        examples=examples,
    )
    return constructor_prompt


class K10Query:
    def __init__(self, symbol, available_years=None):
        self.symbol = symbol
        self.available_years = available_years if available_years else []
        self.latest_year = available_years[-1] if available_years else ""
        self.queries = {}
        self._init_queries()


    def _init_queries(self):
        self.queries = {
            "Overview": self._get_overview_query(),
            "Business and Risk": self._get_business_and_risk_query(),
            "Strategic Outlook and Future Projections": self._get_strategic_outlook_and_future_projections_query(),
            "Risk Factors Years": self._get_risk_factors_years_query(),
            "SWOT": self._get_swot_query(),
        }


    def _get_overview_query(self):
        return f"""
Based on the comprehensive review of all items of the latest year {self.latest_year} of 10-K filing of {self.symbol}, identify and analyze three positive and three negative aspects regarding the company's prospects.
Organize your analysis in the following format:

1. **Positive Insights**:
- **Strengths and Opportunities**: Detail three major strengths or opportunities that {self.symbol} is poised to capitalize on.
- **Potential Positive Outcomes**: Discuss the possible beneficial outcomes if these strengths and opportunities are effectively leveraged.

2. **Negative Insights**:
- **Challenges and Threats**: Enumerate three significant challenges or threats facing {self.symbol}.
- **Potential Negative Consequences**: Explore the potential adverse impacts these challenges could have on {self.symbol}'s future performance.
"""


    def _get_business_and_risk_query(self):
        return f"""
Using the combined information from Item 1 (Business Overview), Item 1A (Risk Factors), Item 7 (Management’s Discussion and Analysis), 
Item 7A (Quantitative and Qualitative Disclosures About Market Risk), and Item 8 (Financial Statements) from the latest 10-K filing 
of {self.symbol}, perform a detailed analysis to provide:

1. **Business and Financial Overview**:
- **Core Business Operations**: Summarize the main activities and market positions outlined in Item 1.
- **Financial Health**: From Item 8, highlight key financial metrics and year-over-year changes.
- **Management Analysis**: Extract key insights from Item 7 about financial trends, operational challenges, and management's strategic focus.

2. **Integrated Risk Profile**:
- **Risk Landscape**: Using information from Item 1A and Item 7A of the latest 10-K filing of {self.symbol}, identify and describe the major operational and market risks.
- **Impact and Mitigation**: Discuss the potential impacts of these risks on the business and financial performance, and outline the risk mitigation strategies provided by management across these sections.

Provide this analysis in a structured format, aiming to offer stakeholders a clear and concise overview of both opportunities and threats,
as well as the company’s preparedness to handle its market and operational challenges.
"""


    def _get_strategic_outlook_and_future_projections_query(self):
        return f"""
With reference to the information available in Item 1 (Business Overview), Item 1A (Risk Factors), Item 7 (Management’s Discussion and Analysis),
Item 7A (Quantitative and Qualitative Disclosures About Market Risk), and Item 8 (Financial Statements) 
of {{self.symbol}}'s recent 10-K filing, synthesize a strategic report that addresses:

1. **Strategic Positioning and Opportunities**:
- **Market Dynamics**: Analyze the business landscape as described in Item 1 and Item 7, focusing on competitive positioning and market opportunities.
- **Operational Strengths**: Highlight operational strengths and efficiencies that bolster the company's market position.

2. **Future Financial Prospects**:
- **Financial Projections**: Discuss future financial prospects based on trends and data from Item 7 and Item 8.
- **Risk and Opportunities Balance**: Weigh the financial risks (Item 1A and 7A) against potential opportunities, and discuss how the company plans to leverage its strengths to mitigate these risks and capitalize on market trends.

This analysis should offer a forward-looking perspective, aiming to provide potential investors and company stakeholders with a deep understanding of the company’s strategic initiatives, market risks, and financial outlook.
"""


    def _get_swot_query(self):
        return f"""
Create a SWOT analysis with reference to the information available in Item 1 (Business Overview) and Item 1A (Risk Factors) and 
Item 7 (Management's Discussion and Analysis) and Item 7A (Quantitative and Qualitative Disclosures About Market Risk) and Item 8 (Financial Statements) 
of {self.latest_year} for {self.symbol}'s 10-K filing
"""


    def _get_risk_factors_years_query(self):
        if self.available_years:
            available_years_str = ", ".join(self.available_years)
        else:
            available_years_str = ""
        return f"""
Based on the information available in Item 1A (Risk Factors) and Item 7A (Quantitative and Qualitative Disclosures About Market Risk) of 10-K filings of {self.symbol} for last {self._get_num_years_str()} ({available_years_str}),
Provide a structured analysis how risks have changed and what impacts they have had over the years, starting from the least recent to the present, to gain insights into how the company has identified and categorized its risks over time.
- **Identify key themes**: Look for recurring themes or new risks that have emerged.
- **Assess Changes in Language and Tone**: identify and evaluate any shifts in the company's risk perception or management's approach to risk management.
- **Quantify Impact**: For each risk factor, assess the potential impact on the company's operations, financial performance, and reputation.
- **Consider External Factors**: Evaluate how external factors such as regulatory changes, economic conditions, or technological advancements may have influenced the risk factors over the years.
- **Summarize Findings**: Provide a concise summary of the key findings changes in risk factors, highlighting any new risks that have emerged, risks that have been downplayed, and any significant shifts in the company’s risk profile.
"""


    def _get_num_years_str(self):
        """
        Returns the number (in string) of years in a string.
        """
        len_years = len(self.available_years)
        if len_years <= 1:
            return "year"
        elif len_years == 2:
            return "two years"
        elif len_years == 3:
            return "three years"
        elif len_years > 3:
            return "last " + str(len_years) + " years"


    def get_query(self, key):
        if key not in self.queries:
            raise AttributeError(f"Key {key} not found")
        return self.queries[key]


    def get_all_queries(self):
        return self.queries
