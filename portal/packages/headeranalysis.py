import fitz

def extract_entire_block_text(block_lines):
    """
    Concatenates text from all spans within each line of a given block.

    Args:
    - block_lines: A list of lines, where each line contains spans with text.

    Returns:
    - A string representing the concatenated text of the entire block.
    """
    block_text = ""
    try:
        for line in block_lines:
            # Join text from all spans in the line, then add to the block text
            line_text = ''.join(span['text'] for span in line['spans'])
            block_text += line_text + " "  # Add a space for readability/separation
    except:
        pass

    return block_text.strip()  # Remove trailing space for a cleaner output

def extract_headers(pdf_path):
    doc = fitz.open(pdf_path)
    titles = {}
    count_ = 0
    for page in doc:
        Final_text_found = False
        count_ += 1
        page_text = page.get_text("dict")
        # with open('output_file.txt', 'a') as file:
        #     new_text = f"\n{page_text}"
        #     file.write(new_text)
        for block in page_text["blocks"]:
            try:
                text_found_ = False
                for line in block["lines"]:
                    for span in line["spans"]:
                        if str(span['text']).strip() == '':
                            pass
                        elif span['bbox'][1] < 50:
                            block_txt = extract_entire_block_text(block["lines"])
                            titles[count_] = block_txt
                            text_found_ = True
                            Final_text_found = True
                            break
                    if text_found_:
                        break
                if text_found_:
                    break
            except:
                pass
        if not Final_text_found:
            titles[count_] = 'None'
    doc.close()
    yes_headers_pages = 0
    No_headers_Pages = 0
    for i in titles:
        if str(titles[i]).strip() == 'None' or str(titles[i]).strip() == '':
            No_headers_Pages += 1
        else:
            yes_headers_pages += 1

    percentage_with_headers = (yes_headers_pages / count_) * 100
    percentage_without_headers = (No_headers_Pages / count_) * 100

    return titles, No_headers_Pages, yes_headers_pages, round(percentage_with_headers, 2), round(
        percentage_without_headers)

def extract_header_backup(pdf_path):
    doc = fitz.open(pdf_path)
    titles = {}
    count_ = 0
    for page in doc:
        Final_text_found = False
        count_ += 1
        page_text = page.get_text("dict")
        for block in page_text["blocks"]:
            try:
                text_found_ = False
                for line in block["lines"]:
                    for span in line["spans"]:
                        if str(span['text']).strip() == '':
                            pass
                        elif span['bbox'][1] < 50:
                            block_txt = extract_entire_block_text(block["lines"])
                            titles[count_] = block_txt
                            text_found_ = True
                            Final_text_found = True
                            break
                    if text_found_:
                        break
                if text_found_:
                    break
            except:
                pass
        if not Final_text_found:
            titles[count_] = ''
    doc.close()
    print(len(titles))
    return titles