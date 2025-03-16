import unittest
from unittest.mock import patch, Mock
import os
from src.sec.sec import get_recent_folders, download_filings, SOURCE_SEC_DIRECTORY

class TestSEC(unittest.TestCase):
    def setUp(self):
        self.symbol = "AAPL"
        self.filing_type = "10-K"
        self.test_dir = os.path.join(SOURCE_SEC_DIRECTORY, self.symbol, self.filing_type)

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_get_recent_folders(self, mock_isdir, mock_listdir, mock_exists):
        # Mock the directory exists
        mock_exists.return_value = True
        
        # Mock directory contents
        mock_folders = [
            '0000320193-23-000106',  # 2023
            '0000320193-22-000108',  # 2022
            '0000320193-21-000105',  # 2021
            '0000320193-20-000096'   # 2020
        ]
        mock_listdir.return_value = mock_folders
        
        # Mock isdir to return True for all entries
        mock_isdir.return_value = True

        # Get recent folders (default num_years=3)
        folders = get_recent_folders(self.symbol, self.filing_type)
        
        # Verify results
        self.assertEqual(len(folders), 3)
        self.assertEqual(folders, [
            '0000320193-23-000106',
            '0000320193-22-000108',
            '0000320193-21-000105'
        ])

    @patch('os.path.exists')
    def test_get_recent_folders_error(self, mock_exists):
        # Mock the directory doesn't exist
        mock_exists.return_value = False
        
        # Should raise ValueError when directory doesn't exist
        with self.assertRaises(ValueError):
            get_recent_folders(self.symbol, self.filing_type)

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_get_recent_folders_custom_years(self, mock_isdir, mock_listdir, mock_exists):
        # Mock the directory exists
        mock_exists.return_value = True
        
        # Mock directory contents
        mock_folders = [
            '0000320193-23-000106',  # 2023
            '0000320193-22-000108',  # 2022
            '0000320193-21-000105',  # 2021
            '0000320193-20-000096'   # 2020
        ]
        mock_listdir.return_value = mock_folders
        
        # Mock isdir to return True for all entries
        mock_isdir.return_value = True

        # Get recent folders with custom num_years
        folders = get_recent_folders(self.symbol, self.filing_type, num_years=2)
        
        # Verify results
        self.assertEqual(len(folders), 2)
        self.assertEqual(folders, [
            '0000320193-23-000106',
            '0000320193-22-000108'
        ])

    @patch('sec.sec.dl')
    def test_download_filings(self, mock_dl):
        mock_dl.get.return_value = True
        download_filings(self.symbol, self.filing_type)
        mock_dl.get.assert_called_once_with(
            self.filing_type, 
            self.symbol, 
            download_details=True
        )

    @patch('sec.sec.dl')
    def test_download_filings_error(self, mock_dl):
        mock_dl.get.side_effect = Exception("Test error")
        download_filings(self.symbol, self.filing_type)
        mock_dl.get.assert_called_once_with(
            self.filing_type, 
            self.symbol, 
            download_details=True
        )

    def tearDown(self):
        # Clean up any test files or directories if needed
        pass