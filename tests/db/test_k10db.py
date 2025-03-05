import unittest
from unittest.mock import Mock, patch
from db.K10 import K10_DB

class TestK10DB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock embeddings and other dependencies
        cls.mock_embeddings = Mock()
        cls.persist_directory = "test_persist_dir"
        cls.symbol = "AAPL"

    def setUp(self):
        # Create fresh instance for each test
        self.db = K10_DB(
            self.persist_directory,
            self.symbol,
            self.mock_embeddings,
            save_to_txt_files=False,
            num_years=1
        )

    def test_init(self):
        self.assertEqual(self.db.symbol, "AAPL")
        self.assertEqual(self.db.persist_directory, "test_persist_dir")

    # @patch('db.K10.load_filings')
    # def test_get_available_documents(self, mock_load_filings):
    #     mock_load_filings.return_value = ["doc1", "doc2"]
    #     docs = self.db.get_available_documents()
    #     self.assertEqual(len(docs), 2)

    # @patch('db.K10.load_filings')
    # def test_get_available_years(self, mock_load_filings):
    #     mock_load_filings.return_value = ["2021", "2022"]
    #     years = self.db.get_available_years()
    #     self.assertEqual(len(years), 2)

    def test_get_retriever_chain(self):
        years = ["2021", "2022"]
        retriever = self.db.get_retriever_chain(years)
        self.assertIsNotNone(retriever)
