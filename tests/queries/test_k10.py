import unittest
from queries.K10 import K10Query

class TestK10Query(unittest.TestCase):
    def setUp(self):
        self.query = K10Query("AAPL", ["2021", "2022"])

    def test_init(self):
        self.assertEqual(self.query.symbol, "AAPL")
        # self.assertEqual(len(self.query.years), 2)

    def test_get_query(self):
        query = self.query.get_query("SWOT")
        self.assertIsInstance(query, str)
        self.assertIn("risk factors", query.lower())

    def test_invalid_query_key(self):
        with self.assertRaises(AttributeError):
            self.query.get_query("invalid_key")

    def test_get_all_queries(self):
        queries = self.query.get_all_queries()
        self.assertIsInstance(queries, dict)
        self.assertGreater(len(queries), 0) 