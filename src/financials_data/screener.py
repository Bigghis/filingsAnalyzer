import yfinance as yf
from ..utils.utils import map_sort_field

class Screener:
    def __init__(self):
        self.screener = yf.Screener()
    
    def get_predefined_bodies(self):
        """Convert predefined_bodies list to a clean JSON-compatible format."""
        self.get_equity_query()
        return {
            "data": sorted(list(self.screener.predefined_bodies))
        }
    
    def get_valid_equity_maps(self):
        valid_eq_map = yf.EquityQuery('lt', ['pegratio_5y', 1]).valid_eq_operand_map
        # print(dir(valid_eq_map))
        valid_eq_map = {key: sorted(value) for key, value in valid_eq_map.items()}
        return {
            "data": valid_eq_map
        }

    def get_valid_equity_fields(self):
        valid_fields =  yf.EquityQuery('lt', ['pegratio_5y', 1]).valid_operand_fields
        return {
            "data": sorted(valid_fields)
        }

    def get_equity_query(self):
        #  https://ranaroussi.github.io/yfinance/reference/api/yfinance.EquityQuery.html
        equity_query = yf.EquityQuery('lt', ['pegratio_5y', 1])
        # s = self.screener.set_default_body(equity_query)
        # s = self.screener.set_predefined_body('day_gainers')


        # The queries support operators:
        # GT (greater than), LT (less than), BTWN (between), EQ (equals), 
        # and logical operators AND and OR for combining multiple conditions.

        s = self.screener.set_body({
            "offset": 0,
            "size": 100,
            "sortField": "ticker",
            "sortType": "desc",
            "quoteType": "equity",
            "query": equity_query.to_dict(),
            "userId": "",
            "userIdType": "guid"
        })

        # ['operands', 'operator', 'to_dict', 'valid_eq_map', 'valid_fields']

        # print(equity_query.valid_eq_map)
        #print(self.screener.response)


    def run(self, criteria):
        """
        Convert input criteria to a screener query and execute it.
        """
        filters = criteria.get('filters', {})
        if not filters:
            return {"data": [], "total": 0, "count": 0, "start": 0}
        
        offset = criteria.get('start', 0)
        size = criteria.get('size', 25)
        sort = criteria.get('sort', [{ "id": "ticker", "desc": True }])

        sortField = "ticker"
        sortType = "DESC"

        if sort:
            sortField = sort[0]["id"]
            sortType = "desc" if sort[0]["desc"] else "asc"

        if sortField == "symbol":
            sortField = "ticker"

        print("sortField", sortField)
        print("sortType", sortType)

        # Default query structure
        query = {
            "offset": offset,
            "size": size,
            "sortField": map_sort_field(sortField),
            "sortType": sortType,
            "quoteType": "EQUITY",
            "query": {  # Always include query object
                "operator": "AND",
                "operands": []
            },
            "userId": "",
            "userIdType": "guid"
        }

    
        # print("filters = ", filters)
        # Build operands list for the main query
        operands = []
        
        # Define categorical fields that use simple equality comparison
        categorical_fields = ["exchanges", "sector", "region", "peer_group"]
        
        # Handle categorical fields
        for field in categorical_fields:
            if field in filters and filters[field].get("value"):
                operands.append({
                    "operator": "eq",
                    "operands": [
                        field.rstrip('s'),  # remove 's' from plural fields
                        filters[field]["value"]  # Just use the value string
                    ]
                })
        
        # Handle numeric criteria
        for field, condition in filters.items():
            # Skip categorical fields
            if field in categorical_fields:
                continue
            
            operator = condition.get("operator", "").upper()
            value1 = condition.get("value1", "")
            value2 = condition.get("value2", "")
            
            if not operator or not value1:
                continue
            
            if operator == "BTWN" and value2:
                operands.append({
                    "operator": "BTWN",
                    "operands": [field, float(value1), float(value2)]
                })
            elif operator in ["GT", "LT", "EQ"]:
                operands.append({
                    "operator": operator,
                    "operands": [field, float(value1)]
                })
        
        # Update query with operands
        if operands:
            query["query"]["operands"] = operands
        
        # print("query", query)
        # Execute the screener
        self.screener.set_body(query)
        response = self.screener.response

        print("response", response.keys())
        # print("response useRecords", response["useRecords"])
        print("response total", response["total"])
        print("response count", response["count"])
        print("response start", response["start"])

        
        # print("response", response)
        # Format the response
        if response and "quotes" in response:
            filtered_quotes = []
            # print("response quotes", response["quotes"][0].keys())
            for quote in response["quotes"]:
                filtered_quote = {
                    "symbol": quote.get("symbol", ""),
                    "shortName": quote.get("shortName", ""),
                    "region": quote.get("region", ""),
                    "exchange": quote.get("exchange", ""),
                    "marketCap": quote.get("marketCap", ""),
                    "trailingPE": quote.get("trailingPE", ""),
                    "forwardPE": quote.get("forwardPE", ""),
                    "regularMarketPrice": quote.get("regularMarketPrice", ""),
                    "dividendYield": quote.get("dividendYield", ""),
                    "currency": quote.get("currency", ""),
                    "fiftyTwoWeekChangePercent": quote.get("fiftyTwoWeekChangePercent", ""),
                    "twoHundredDayAverageChangePercent": quote.get("twoHundredDayAverageChangePercent", ""),
                    "fiftyTwoWeekLow": quote.get("fiftyTwoWeekLow", ""),
                    "fiftyTwoWeekHigh": quote.get("fiftyTwoWeekHigh", "")
                }
                filtered_quotes.append(filtered_quote)

            return {
                "data": filtered_quotes, # response["quotes"],
                "total": response["total"] if response["total"] else 0,
                "count": response["count"] if response["count"] else 0,
                "start": response["start"] if response["start"] else 0
            }
        
        return {"data": [], "total": 0, "count": 0, "start": 0}
        