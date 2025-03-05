import os
from sec_edgar_downloader import Downloader
from ..config import COMPANY_NAME, EMAIL, DATA_DIRECTORY, SOURCE_SEC_DIRECTORY

dl = Downloader(COMPANY_NAME, EMAIL, DATA_DIRECTORY)


def download_filings(ticker, filing_type="10-K", download_details=True):
    """
    Download SEC filings for a given company.
    
    Args:
    ticker (str): The stock ticker symbol of the company.
    filing_type (str): The type of SEC filing to download. Default is "10-K".
    download_details (bool): Whether to download the details of the filings. Default is True.
    
    Returns:
    None
    """
    try:
        dl.get(filing_type, ticker, download_details=True)
        print(f"Successfully downloaded {filing_type} filing(s) for {ticker}.")
    except Exception as e:
        print(f"Error downloading {filing_type} for {ticker}: {str(e)}")


def get_recent_folders(symbol, filing_type="10-K", num_years=3):
    """
    Get the most recent folders for a given company and filing type.
    """
    dir_path = os.path.join(SOURCE_SEC_DIRECTORY, symbol, filing_type)
    if not os.path.exists(dir_path):
        raise ValueError(f"Directory {dir_path} does not exist")
    all_entries = os.listdir(dir_path)

    # Filter out only the folders after the year 2000
    # "0000320193-98-000105" -> not a valid year
    # "0000320193-21-000105" -> valid year
    all_folders = [entry for entry in all_entries if os.path.isdir(os.path.join(dir_path, entry)) and int(entry.split('-')[1]) < 25]

    # Extract years and sort them, assuming the folder format includes the year as shown
    # Folder format example: "0000320193-21-000105"
    # Extracts the '21' part as the year
    sorted_folders = sorted(all_folders, key=lambda x: int('20' + x.split('-')[1]), reverse=True)

    # Get the most recent 'num_years' folders
    recent_folders = sorted_folders[:num_years]
    return recent_folders


