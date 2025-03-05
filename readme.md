# SEC Edgar Downloader

## Data Collection
Download the data from the SEC using the `sec_edgar_downloader` library.
Files will be saved as HTML in the `data/sec-edgar-filings` folder.

## Development

### Installation
```bash
pip install -e .
```
### Testing
Run unit tests with coverage:
```bash
pytest --cov=src tests/
``` 