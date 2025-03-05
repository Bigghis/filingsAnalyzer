class MockQueryEngine:
    def __init__(self, symbol, type, key, save_to_txt_files=True, num_years=3):
        self.symbol = symbol
        self.type = type
        self.key = key
        self.save_to_txt_files = save_to_txt_files
        self.num_years = num_years

    def query(self):
        if self.key in self.get_all_queries():
            return {
            "sample": "query result"
        } 
        else:
            raise ValueError("Invalid query key")
        

    def get_all_queries(self):
        return ["risk_factors", "business_description"]

    def get_query(self, key):
        if key in self.get_all_queries():
            return "Sample query text" 
        else:
            raise ValueError("Invalid query key")