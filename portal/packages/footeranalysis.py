import fitz
import re


def extract_foter(pdf_path):
    doc = fitz.open(pdf_path)
    titles = {}
    count_ = 0
    for page in doc:
        Final_text_found = False
        count_ += 1
        page_text = page.get_text("dict")
        width_ = page_text["width"]
        height_ = page_text["height"]
        for block in page_text["blocks"]:
            try:
                text_found_ = False
                for line in block["lines"]:
                    for span in line["spans"]:
                        # if count_ == 20:
                        #     print('height_', height_, "width_", width_)
                        #     print("span['bbox']", span['bbox'])
                        #     print("span['text']", span['text'])
                        #     print("(span['bbox'][1] > 740 and span['bbox'][0] > 500",(span['bbox'][1] > 740 and span['bbox'][0] > 500))
                        if str(span['text']).strip() == '':
                            pass
                        elif ((span['bbox'][1] > 740 and span['bbox'][0] > 500) or (span['bbox'][1] > 731 and span['bbox'][0] > 74)) and (height_ > 785 and width_ > 585):
                            titles[count_] = span['text'].replace('\t', '')
                            text_found_ = True
                            Final_text_found = True
                            break
                        elif (span['bbox'][1] > 740 and span['bbox'][0] > 47) and (height_ > 790 and width_ > 610):
                            titles[count_] = span['text'].replace('\t', '')
                            text_found_ = True
                            Final_text_found = True
                            break
                        elif (span['bbox'][1] > 732 and span['bbox'][0] > 52) and (height_ > 790 and width_ > 593):
                            titles[count_] = span['text'].replace('\t', '')
                            text_found_ = True
                            Final_text_found = True
                            break
                        elif (span['bbox'][1] > 579 or (span['bbox'][0] > 740 and span['bbox'][1] > 530)) and (
                                width_ > 785 and height_ > 585):
                            titles[count_] = span['text'].replace('\t', '')
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

    yes_footer_pages = 0
    No_footer_Pages = 0
    for i in titles:
        if str(titles[i]).strip() == 'None' or str(titles[i]).strip() == '':
            No_footer_Pages += 1
        else:
            yes_footer_pages += 1

    percentage_with_footer = (yes_footer_pages / count_) * 100
    percentage_without_footer = (No_footer_Pages / count_) * 100

    count_of_footers_ = [[round(percentage_with_footer), yes_footer_pages],
                         [round(percentage_without_footer), No_footer_Pages]]

    return titles, count_of_footers_


def extract_footer_backup(pdf_path):
    doc = fitz.open(pdf_path)
    titles = {}
    count_ = 0
    for page in doc:
        Final_text_found = False
        count_ += 1
        page_text = page.get_text("dict")
        width_ = page_text["width"]
        height_ = page_text["height"]
        for block in page_text["blocks"]:
            try:
                text_found_ = False
                for line in block["lines"]:
                    for span in line["spans"]:
                        if str(span['text']).strip() == '':
                            pass
                        elif ((span['bbox'][1] > 740 and span['bbox'][0] > 500) or (
                                span['bbox'][1] > 732 and span['bbox'][0] > 74)) and (height_ > 785 and width_ > 585):
                            titles[count_] = span['text'].replace('\t', '')
                            print('~~~~~~~~~~~~~~~~~start 1~~~~~~~~~~~~~~~~')
                            print(span['bbox'])
                            print('count_', count_)
                            print('text', span['text'].replace('\t', ''))
                            print('~~~~~~~~~~~~~~~~~start~~~~~~~~~~~~~~~~')
                            text_found_ = True
                            Final_text_found = True
                            break
                        elif (span['bbox'][1] > 579 or (span['bbox'][0] > 740 and span['bbox'][1] > 530)) and (
                                width_ > 785 and height_ > 585):
                            titles[count_] = span['text'].replace('\t', '')
                            print('~~~~~~~~~~~~~~~~~start 2~~~~~~~~~~~~~~~~')
                            print('count_', count_)
                            print('text', span['text'].replace('\t', ''))
                            print('~~~~~~~~~~~~~~~~~start~~~~~~~~~~~~~~~~')
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
    return titles


def check_page_number(pdf_file_path):
    # Open the PDF document
    doc = fitz.open(pdf_file_path)

    # Get total number of pages
    total_pages = doc.page_count

    # Initialize lists to store pages with and without page numbers
    pages_with_page_number = []
    pages_without_page_number = []

    image_page_number_accessibility = {}

    # Iterate through each page in the document
    for page_number, page in enumerate(doc, start=1):
        text_found = False  # Flag to track if page number text is found

        # Extract text information for the current page
        page_text = page.get_text("dict")
        width_ = page_text["width"]
        height_ = page_text["height"]

        # Iterate through each block of text on the page
        for block in page_text["blocks"]:
            try:
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Check if the text is within specified areas where page numbers might be located
                        # if ((span['bbox'][1] > 740 and span['bbox'][0] > 500) or (span['bbox'][1] > 731 and span['bbox'][0] > 74)) and (height_ > 785 and width_ > 585):
                        if ((span['bbox'][1] > 740 and span['bbox'][0] > 500) or (
                                span['bbox'][1] > 731 and span['bbox'][0] > 74)) and (
                                height_ > 785 and width_ > 585):
                            # Use regex to identify if the text matches the pattern of a page number
                            page_number_pattern = r"\b\d{1,5}\b"
                            match = re.search(page_number_pattern, span['text'].replace('\t', ''))
                            # If a match is found, set text_found flag to True
                            if match:
                                text_found = True
                                break
                        elif (span['bbox'][1] > 740 and span['bbox'][0] > 47) and (height_ > 790 and width_ > 610):
                            page_number_pattern = r"\b\d{1,5}\b"
                            match = re.search(page_number_pattern, span['text'].replace('\t', ''))
                            if match:
                                text_found = True
                                break
                        elif (span['bbox'][1] > 732 and span['bbox'][0] > 52) and (height_ > 790 and width_ > 593):
                            page_number_pattern = r"\b\d{1,5}\b"
                            match = re.search(page_number_pattern, span['text'].replace('\t', ''))
                            if match:
                                text_found = True
                                break
                        elif (span['bbox'][1] > 579 or (span['bbox'][0] > 740 and span['bbox'][1] > 530)) and (
                                width_ > 785 and height_ > 585):
                            page_number_pattern = r"\b\d{1,3}\b"
                            match = re.search(page_number_pattern, span['text'].replace('\t', ''))

                            # If a match is found, set text_found flag to True
                            if match:
                                text_found = True
                                break
                    if text_found:
                        break
                if text_found:
                    break
            except:
                pass
        # Based on whether page number text is found, append page number to respective list
        if text_found:
            pages_with_page_number.append(page_number)
            image_page_number_accessibility[page_number] = 'Accessible'
        else:
            pages_without_page_number.append(page_number)
            image_page_number_accessibility[page_number] = 'Not Accessible'

    # Calculate the percentage of pages with and without page numbers
    percentage_with_page_number = (len(pages_with_page_number) / total_pages) * 100
    percentage_without_page_number = (len(pages_without_page_number) / total_pages) * 100

    return pages_with_page_number, pages_without_page_number, round(percentage_with_page_number, 1), round(
        percentage_without_page_number, 1), image_page_number_accessibility

#
# titles, count_of_footers_ = extract_foter(
#     "/Users/sandeepkumarrudhravaram/WorkSpace/UntProjects/A11yPDF/pdf_docs/1503202413293439887/Team16_Sprint_2.pdf")
# print('titles', titles, "count_of_footers_", count_of_footers_)
