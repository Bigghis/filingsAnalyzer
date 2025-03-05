import os
import unicodedata
from bs4 import BeautifulSoup, Tag

# https://www.sec.gov/files/reada10k.pdf
# https://www.wallstreetprep.com/knowledge/10-k-filing/ 

RELEVANT_ITEMS = {
            "Item 1" : {"title_description": "Business"},
            "Item 1A" : {"title_description": "Risk Factors"},
            "Item 7" : {"title_description": "Management"},
            "Item 7A" : {"title_description": "Quantitative and Qualitative Disclosures about Market Risk"},
            "Item 8" : {"title_description": "Financial Statements and Supplementary Data"},
            "Item 9" : {"title_description": "Changes in and Disagreements with Accountants on Accounting"},
        }

class K10:
    def __init__(self, symbol, file_path):
        self.symbol = symbol
        self.file_path = file_path
        self.year = None
        self.soup = None
        self.summary_table = None

        self.relevant_items = RELEVANT_ITEMS

        self._load_html()


    # Load HTML content from the specified file path
    def _load_html(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        folder = self.file_path.split('/')[-2]
        self.year = "20" + folder.split('-')[1]
        self.soup = BeautifulSoup(html_content, 'html.parser')


    def _get_summary_table(self):
        tables = self.soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_text = ' '.join(cell.get_text(strip=True) for cell in cells)
                if 'Item 1' in cell_text and 'Business' in cell_text:
                    self.summary_table = table
                    break

    def _get_hrefs(self, item_key, title_description):
        # Check if summary table was found
        hrefs = {}
        if self.summary_table:
            # Scan through all rows in summary table
            rows = self.summary_table.find_all('tr')
            for row in rows:
                # Get all cells in row
                cells = row.find_all(['td', 'th'])
                cell_text = ' '.join(cell.get_text(strip=True).lower() for cell in cells)
                
                # Check each relevant item
                # for item_key in self.relevant_items.keys():
                if item_key.lower() in cell_text and title_description.lower() in cell_text:
                    # Find href in this row
                    link = row.find('a')
                    if link and link.get('href'):
                        hrefs["begin"] = link.get('href')
                        # Get next row
                        next_row = row.find_next_sibling('tr')
                        if next_row:
                            next_link = next_row.find('a')
                            if next_link and next_link.get('href'):
                                hrefs["end"] = next_link.get('href')

                        # Find next row
                        #return link.get('href')
        return hrefs


    def _normalize_text(self, text):
        return unicodedata.normalize('NFKD', text)


    def extract_item_contents(self, save_to_txt_files=True):
        """Extract contents of relevant items from the 10-K document.

        This method performs the following steps:
        1. Gets the summary table containing item references
        2. Extracts begin and end href links for each relevant item
        3. Extracts text content between the href locations for each item
        4. Optionally saves the extracted content to separate text files

        Args:
            save_to_txt_files (bool): If True, saves extracted content to text files

        The extracted content for each item is stored in self.relevant_items dictionary.
        If save_to_txt_files is True, content is saved to: /tmp/{item_key}_{year}.txt
        """
        # Initialize dictionary to store relevant items
        self._get_summary_table()

        # Get begin and end hrefs for each item
        for item_key in self.relevant_items.keys():
            self.relevant_items[item_key]["hrefs"] = self._get_hrefs(item_key, self.relevant_items[item_key]["title_description"])
            # adds year to each item
            self.relevant_items[item_key]["year"] = self.year


        # Extract text content between hrefs for each item
        for item_key, item_data in self.relevant_items.items():
            if "hrefs" in item_data and "begin" in item_data["hrefs"] and "end" in item_data["hrefs"]:
                # Find begin and end elements
                begin_id = item_data["hrefs"]["begin"].replace("#", "")
                end_id = item_data["hrefs"]["end"].replace("#", "")
                
                # Find begin element
                begin_elem = self.soup.find(attrs={"id": begin_id})
                end_elem = self.soup.find(attrs={"id": end_id})
                
                if begin_elem and end_elem:
                    # Get all div elements between begin and end
                    content = []
                    current = begin_elem
                    while current and current != end_elem:
                        if isinstance(current, Tag) and current.name == 'div':
                            text = current.get_text(strip=True)
                            if text and text.lower() != "table of contents" and not text.strip().isdigit():
                                content.append(current.get_text(strip=True))
                        current = current.next_element
                    
                    # Store extracted content
                    self.relevant_items[item_key]["content"] = self._normalize_text(" ".join(content))
                else:
                    self.relevant_items[item_key]["content"] = ""
            else:
                self.relevant_items[item_key]["content"] = ""
        
        # Save content of each item to separate files
        if save_to_txt_files:
            for item_key, item_data in self.relevant_items.items():
                if "content" in item_data and item_data["content"]:
                    # Create filename using item key and year
                    filename = f"/tmp/{self.symbol}_{item_key.replace(' ', '_')}_{self.year}.txt"
                    
                    # Write content to file
                    with open(filename, 'w', encoding='utf-8') as f:
                            f.write(item_data["content"])

        return self.relevant_items
    
