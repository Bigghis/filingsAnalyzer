import pytest
from queries.QueryEngine import QueryEngine

class TestQueryEngine:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.engine = QueryEngine(
            symbol="AAPL",
            type="10-K",
            key="risk_factors",
            save_to_txt_files=False,
            num_years=1
        )

    def test_get_query_invalid_key(self):
        # print("queriesss", self.engine.get_query("invalid_key"))
        with pytest.raises(ValueError) as exc_info:
            self.engine.get_query("invalid_key")
        assert str(exc_info.value) == "Invalid query key"

    def test_get_query_valid_key(self):
        query_text = self.engine.get_query("risk_factors")
        assert isinstance(query_text, str)
        assert len(query_text) > 0

    def test_get_all_queries(self):
        queries = self.engine.get_all_queries()
        assert isinstance(queries, list)
        assert "risk_factors" in queries
        assert len(queries) > 0

    def test_query_execution(self):
        result = self.engine.query()
        assert isinstance(result, dict)

    def test_query_invalid_key(self):
        engine = QueryEngine(
            symbol="AAPL",
            type="10-K",
            key="invalid_key",
            save_to_txt_files=False,
            num_years=1
        )
        with pytest.raises(ValueError) as exc_info:
            engine.query()
        assert str(exc_info.value) == "Invalid query key"