import camelot
import pdfminer.high_level
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_pages

def find_table_captions(pdf_path):
    tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
    print('Number of tables found:', len(tables))
    captions_with_tables = []
    tables_with_captions = set()  # To track tables that have captions

    for page_num, page_layout in enumerate(extract_pages(pdf_path, laparams=LAParams()), start=1):
        for element in page_layout:
            if isinstance(element, pdfminer.layout.LTTextBoxHorizontal):
                text = element.get_text().replace("\n", "").lower().strip()
                if text.startswith(("table", "tbl", "tab")):  # Add more prefixes as needed
                    caption = element.get_text().strip().replace("\n", " ")
                    for table in tables:
                        if table.page == page_num:
                            # print("table._bbox",table._bbox,"element.y0",element.y0,"caption",caption)
                            if abs(element.y0 - table._bbox[2]) < 70:  # Adjust threshold as needed
                                captions_with_tables.append({
                                    "page_number": page_num,
                                    "table": table,
                                    "caption_text": caption
                                })
                                tables_with_captions.add(table)
                                break

    # Add tables without captions
    for table in tables:
        if table not in tables_with_captions:
            captions_with_tables.append({
                "page_number": table.page,
                "table": table,
                "caption_text": None  # Indicate that no caption was found
            })

    return captions_with_tables

def calculate_percentage(captions_with_tables):
    total_tables = len(captions_with_tables)
    tables_with_caption = sum(1 for item in captions_with_tables if item['caption_text'] is not None)
    tables_without_caption = total_tables - tables_with_caption
    percentage_with_caption=0
    percentage_without_caption=0
    if total_tables > 0:
        percentage_with_caption = round((tables_with_caption / total_tables) * 100)
        percentage_without_caption = round((tables_without_caption / total_tables) * 100)
    return percentage_with_caption,percentage_without_caption

# Example usage
def analyze_table_caption(pdf_file):
    captions_with_tables=find_table_captions(pdf_file)
    percentage_with_caption,percentage_without_caption=calculate_percentage(captions_with_tables)
    return percentage_with_caption,percentage_without_caption,captions_with_tables
