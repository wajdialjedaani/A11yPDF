import camelot
import pdfminer.high_level
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_pages


def find_table_captions(pdf_path):
    tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
    print('Number of tables found:', len(tables))
    # print("tables",tables[1].df)
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
                            # Check both the top and bottom of the table for proximity to the caption
                            is_near_top = abs(element.y1 - table._bbox[3]) < 90  # Caption above the table
                            is_near_bottom = abs(element.y0 - table._bbox[2]) < 70  # Caption below the table
                            if is_near_top or is_near_bottom:
                                captions_with_tables.append({
                                    "page_number": page_num,
                                    # "table": table,
                                    "caption_text": caption,
                                    "Accessible": "Yes"
                                })
                                tables_with_captions.add(table)
                                break

    # Add tables without captions
    for table in tables:
        if table not in tables_with_captions:
            captions_with_tables.append({
                "page_number": table.page,
                # "table": table,
                "caption_text": "None",  # Indicate that no caption was found
                "Accessible": "No"
            })

    return captions_with_tables


def calculate_percentage(captions_with_tables):
    total_tables = len(captions_with_tables)
    tables_with_caption = sum(
        1 for item in captions_with_tables if item['caption_text'] is not None and item['caption_text'] != "None")
    tables_without_caption = total_tables - tables_with_caption

    if total_tables > 0:
        percentage_with_caption = round((tables_with_caption / total_tables) * 100)
        percentage_without_caption = round((tables_without_caption / total_tables) * 100)
        # print(f"Percentage of tables with captions: {percentage_with_caption:.2f}%")
        # print(f"Percentage of tables without captions: {percentage_without_caption:.2f}%")
    else:
        percentage_with_caption = 0
        percentage_without_caption = 0
    return percentage_with_caption, percentage_without_caption


# Example usage
def analyze_table_caption(pdf_file):
    captions_with_tables = find_table_captions(pdf_file)
    percentage_with_caption, percentage_without_caption = calculate_percentage(captions_with_tables)
    return percentage_with_caption, percentage_without_caption, captions_with_tables

# analyze_table_caption("/Users/sandeepkumarrudhravaram/WorkSpace/UntProjects/A11yPDF/pdf_docs/1403202408551189600/bioinformatics_35_21_4381.pdf")
