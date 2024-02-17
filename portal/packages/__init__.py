import fitz
import re
import PyPDF2
from collections import OrderedDict
from portal import LOG, APP
import os
import requests
from datetime import datetime, date
import os
from PIL import Image
import json
import io
from skimage import io, filters
import cv2
import numpy as np
import fitz
from collections import Counter
import threading
from concurrent import futures

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
DIMENSION_THRESHOLD = 1000
NORMALIZATION_CONSTANT = 100
NUM_COLORS = 5
MAX_IMAGES_TO_PROCESS = 6
TIMEOUT_SECONDS = 30


def count_images_in_pdf(pdf_path: str) -> int:
    """
    Count the number of images in a PDF.

    Parameters:
        pdf_path (str): The path to the PDF file.

    Returns:
        int: The total number of images in the PDF.
    """
    with fitz.open(pdf_path) as pdf_document:
        image_count = sum(len(page.get_images(full=True)) for page in pdf_document)

    return image_count


def get_random_numbers(string_length=5):
    import random
    import string
    return ''.join(random.choice(string.digits) for x in range(string_length))


def extract_urls_from_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        links_list = [block['uri'] for page in doc for block in page.get_links()]

    return links_list


def check_url_access(url):
    temp = {}
    try:
        response = requests.get(url)
        temp['url_acc'] = "Yes" if response.ok else "No"
        temp['status_code'] = response.status_code
    except requests.RequestException:
        temp['url_acc'] = "No"
        temp['status_code'] = 400

    return temp


def count_custom_urls_in_pdf(pdf_path):
    links_list = extract_urls_from_pdf(pdf_path)

    final_result = {}
    yes_count = 0
    no_count = 0
    url_access_list={}
    for link_index, link in enumerate(links_list):
        temp_result = check_url_access(link)
        temp_result['url'] = link
        final_result[link_index] = temp_result

        if temp_result['url_acc'] == "Yes":
            yes_count += 1
            url_access_list[link_index]=[link,"Accessible"]
        else:
            no_count += 1
            url_access_list[link_index] = [link, "Not Accessible"]

    count_urls = len(links_list)

    return {"count_urls_": count_urls, "final_": final_result, "yes_count_": yes_count, "no_count_": no_count,
            "url_access_list":url_access_list}


def save_image(image_data, image_name, process_id):
    with open(os.path.join(APP.config["PDF_IMAGES_PDF"], process_id, image_name), "wb") as img_file:
        img_file.write(image_data)


def get_font_size(page, counYimg_fr_pdf_, process_id='', page_number_=1):
    temp_dic_ = {}
    tmp_counYimg_fr_pdf_ = counYimg_fr_pdf_
    if not os.path.exists(os.path.join(APP.config["PDF_IMAGES_PDF"], process_id)):
        os.mkdir(os.path.join(APP.config["PDF_IMAGES_PDF"], process_id))
    counting_number_ = 1;
    try:
        temp_data_ = page.get_text("dict")["blocks"]
        for data_1 in range(len(temp_data_)):
            temp_dic_[str(data_1)] = {}
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            # print("data_1",temp_data_[data_1])
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            try:
                text_1 = temp_data_[data_1]["lines"]
            except:
                try:
                    text_1 = []
                    text_12 = temp_data_[data_1]["image"]
                    tmp_counYimg_fr_pdf_ = tmp_counYimg_fr_pdf_ + 1
                    img_index = str(page_number_) + '_' + str(counting_number_) + '_'
                    image_filename = f"{img_index}.png"
                    save_image(text_12, image_filename, process_id)
                    counting_number_ += 1
                except:
                    text_1 = []
            for i in range(len(text_1)):
                line_total_text_ = ''
                line_font_ = []
                line_size = []
                line_diff_text_ = []
                text_2 = text_1[i]["spans"]
                for jk in range(len(text_2)):
                    if str(text_2[jk]["text"]).strip() == "":
                        pass
                    else:
                        if jk == 0:
                            line_total_text_ = str(text_2[jk]["text"]).strip().replace('    ', '')
                        else:
                            line_total_text_ = str(line_total_text_).strip().replace('    ', '') + ' ' + str(
                                text_2[jk]["text"]).strip().replace('    ', '')
                        if str(text_2[jk]["text"]).strip() != '•' or str(text_2[jk]["text"]).strip() != '●':
                            line_diff_text_.append(str(text_2[jk]["text"]).strip().replace('    ', ''))
                            if str(text_2[jk]["font"]) not in line_font_:
                                line_font_.append(str(text_2[jk]["font"]).strip().replace('    ', ''))
                            if str(text_2[jk]["size"]) not in line_size:
                                line_size.append(str(round(text_2[jk]["size"], 2)).strip().replace('    ', ''))
                if line_total_text_ != '':
                    temp_dic_[str(data_1)][str(i)] = {"font_line": line_total_text_, "font_font_type": line_font_,
                                                      "font_sizes": line_size, "font_diff_text": line_diff_text_}
                    line_total_text_ = ''
                    line_font_ = []
                    line_size = []
    except:
        temp_dic_ = {}
    return temp_dic_, tmp_counYimg_fr_pdf_


def extract_font_sizes(page, count_images, process_id='', page_number=1):
    temp_dict = {}
    tmp_count_images = count_images

    if not os.path.exists(os.path.join(APP.config["PDF_IMAGES_PDF"], process_id)):
        os.mkdir(os.path.join(APP.config["PDF_IMAGES_PDF"], process_id))

    counting_number = 1

    try:
        temp_data = page.get_text("dict")["blocks"]

        for block_index, block_data in enumerate(temp_data):
            temp_dict[str(block_index)] = {}

            try:
                lines = block_data["lines"]
            except KeyError:
                try:
                    lines = []
                    image_data = block_data["image"]
                    tmp_count_images += 1
                    img_index = f"{page_number}_{counting_number}_"
                    image_filename = f"{img_index}.png"
                    save_image(image_data, image_filename, process_id)
                    counting_number += 1
                except KeyError:
                    lines = []

            for line_index, line_data in enumerate(lines):
                temp_dict[str(block_index)][str(line_index)] = process_line_data(line_data)

    except Exception:
        temp_dict = {}

    return temp_dict, tmp_count_images


def process_line_data(line_data):
    line_total_text = ''
    line_font = []
    line_size = []
    line_diff_text = []

    for span_data in line_data["spans"]:
        text = span_data["text"].strip()

        if text != "":
            line_total_text = line_total_text.strip().replace('    ', '') + ' ' + text
            if text not in ['•', '●']:
                line_diff_text.append(text)
                if span_data["font"] not in line_font:
                    line_font.append(span_data["font"])
                if round(span_data["size"], 2) not in line_size:
                    line_size.append(round(span_data["size"], 2))

    return {
        "font_line": line_total_text,
        "font_font_type": line_font,
        "font_sizes": line_size,
        "font_diff_text": line_diff_text
    }


def text_font(pdf_path, process_id):
    pdf_document = fitz.open(pdf_path)
    dict_final_ = {}
    counYimg_fr_pdf_ = 0
    page_number_ = 1
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        font_sizes, counYimg_fr_pdf_ = get_font_size(page, counYimg_fr_pdf_, process_id, page_number_)
        font_sizes = font_sizes
        dict_final_[str(page_number)] = font_sizes
        page_number_ += 1

    return dict_final_, pdf_document.page_count, counYimg_fr_pdf_


def extract_header(pdf_path):
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
                            titles[count_] = span['text']
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


def extract_footer(pdf_path):
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
                                span['bbox'][1] > 730 and span['bbox'][0] > 74)) and (height_ > 785 and width_ > 585):
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
            titles[count_] = ''
    doc.close()
    return titles


# def get_final_result(pdf_file, process_id=''):
#     count_urls = count_custom_urls_in_pdf(pdf_file)
#     dict_final, pdf_document_page_count, count_images = text_font(pdf_file, process_id)
#     return count_urls, count_images, dict_final, pdf_document_page_count

def get_final_result(pdf_file, process_id=''):
    count_urls_ = count_custom_urls_in_pdf(pdf_file)
    # count_images_ = count_images_in_pdf(pdf_file)
    dict_final_, pdf_document_page_count, counYimg_fr_pdf_ = text_font(pdf_file, process_id)
    return count_urls_, counYimg_fr_pdf_, dict_final_, pdf_document_page_count


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
                            titles[count_] = span['text']
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
                        if str(span['text']).strip() == '':
                            pass
                        elif ((span['bbox'][1] > 740 and span['bbox'][0] > 500) or (
                                span['bbox'][1] > 730 and span['bbox'][0] > 74)) and (height_ > 785 and width_ > 585):
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


def get_tables_count(pdf_path):
    table_count = 0
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables_list = page.extract_tables()
            table_count += len(tables_list)

    return table_count


def get_image_info(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            aspect_ratio = width / height
            return width, height, aspect_ratio
    except IOError as e:
        print(f"Error opening {image_path}: {e}")
        return None, None, None


def get_image_contract(image_path):
    sharpness, file_size_mb = 0, 0
    try:
        if os.path.exists(image_path):
            file_size_bytes = os.path.getsize(image_path)
            file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
        else:
            print(f"File {image_path} does not exist.")
    except Exception as e:
        print(f"Error getting file size for {image_path}: {e}")

    try:
        image = io.imread(image_path, as_gray=True)
        sharpness = filters.laplace(image).var()
        return sharpness, file_size_mb
    except FileNotFoundError as e:
        print(f"Error reading image {image_path}: {e}")
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")

    return sharpness, file_size_mb


def get_image_resolution_aspect_ratio(folder_path):
    image_info_dict = {}
    list_of_filename = []
    list_of_width = []
    list_of_height = []
    list_of_sharpness = []
    list_of_file_size_mb = []
    list_of_aspect_ratio = []

    for filename in os.listdir(folder_path):
        tmp_file_name = str(filename)
        if filename.endswith(tuple(ALLOWED_IMAGE_EXTENSIONS)):
            image_path = os.path.join(folder_path, filename)
            width, height, aspect_ratio = get_image_info(image_path)
            sharpness, file_size_mb = get_image_contract(image_path)

            if width is not None:
                image_info_dict[filename] = {
                    "width": width,
                    "height": height,
                    "aspect_ratio": round(aspect_ratio, 3)
                }

                list_of_filename.append(str(tmp_file_name).replace('.png', ''))
                list_of_width.append(width)
                list_of_height.append(height)
                list_of_aspect_ratio.append(round(aspect_ratio, 2))
                list_of_sharpness.append(round(sharpness, 2))
                list_of_file_size_mb.append(round(file_size_mb, 3))

    final_list_of_rsa = [list_of_filename, list_of_width, list_of_height, list_of_aspect_ratio, list_of_sharpness,
                         list_of_file_size_mb]

    return image_info_dict, json.dumps(final_list_of_rsa)


def get_image_contarct(image_path):
    sharpness, file_size_mb = 0, 0
    try:
        if os.path.exists(image_path):
            file_size_bytes = os.path.getsize(image_path)
            file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
        else:
            print(f"File {image_path} does not exist.")
    except:
        pass
    try:
        image = io.imread(image_path, as_gray=True)
        # Compute image sharpness using Laplacian operator
        sharpness = filters.laplace(image).var()
        # print(f"Sharpness of the image: {sharpness}")
        return sharpness, file_size_mb
    except FileNotFoundError:
        print(f"File {image_path} not found.")
    return sharpness, file_size_mb


def assess_dimensions(image):
    """
    Assess image quality based on dimensions.

    Args:
        image: Image in the form of a NumPy array.

    Returns:
        Quality percentage based on dimensions.
    """
    height, width, _ = image.shape
    quality_percentage = ((min(height, width) + max(height, width)) / 2) / DIMENSION_THRESHOLD * NORMALIZATION_CONSTANT
    return min(quality_percentage, NORMALIZATION_CONSTANT)


def assess_sharpness(image):
    """
    Assess image quality based on sharpness.

    Args:
        image: Image in the form of a NumPy array.

    Returns:
        Sharpness percentage.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_percentage = min(sharpness, NORMALIZATION_CONSTANT) / NORMALIZATION_CONSTANT * NORMALIZATION_CONSTANT
    return sharpness_percentage


def assess_contrast(image):
    """
    Assess image quality based on contrast.

    Args:
        image: Image in the form of a NumPy array.

    Returns:
        Contrast percentage.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    contrast = cv2.compareHist(hist, hist, cv2.HISTCMP_BHATTACHARYYA)
    contrast_percentage = (1 - min(contrast, 1)) * NORMALIZATION_CONSTANT
    return contrast_percentage


def assess_image_quality(image_path):
    """
    Assess overall image quality based on different factors.

    Args:
        image_path: Path to the image file.

    Returns:
        None (prints the overall image quality score).
    """
    try:
        img = cv2.imread(image_path)

        dimensions_score = assess_dimensions(img)
        sharpness_score = assess_sharpness(img)
        contrast_score = assess_contrast(img)
        visibility_score = assess_visibility(img)

        overall_score = (dimensions_score + sharpness_score + contrast_score + visibility_score) / 4

        print(f"The overall image quality score is approximately {overall_score:.2f}%")

    except cv2.error as e:
        print(f"Error reading image: {e}")
    except Exception as e:
        print(f"Error: {e}")


def assess_visibility(image):
    """
    Assess image quality based on visibility.

    Args:
        image: Image in the form of a NumPy array.

    Returns:
        Visibility percentage.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    visibility_score = cv2.mean(gray)[0]
    visibility_percentage = (visibility_score / 255) * NORMALIZATION_CONSTANT
    return visibility_percentage


def assess_pdf_quality(pdf_path):
    overall_sharpness = 0
    overall_contrast = 0
    overall_visibility = 0
    try:
        pdf_document = fitz.open(pdf_path)

        sharpness_scores = []
        contrast_scores = []
        visibility_scores = []
        total_pages = pdf_document.page_count

        for page_num in range(total_pages):
            # Extract each page as an image
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)

            # Assess image quality for each page
            sharpness_scores.append(assess_sharpness(img))
            contrast_scores.append(assess_contrast(img))
            visibility_scores.append(assess_visibility(img))

        # Calculate overall scores as averages across all pages
        overall_sharpness = sum(sharpness_scores) / total_pages
        overall_contrast = sum(contrast_scores) / total_pages
        overall_visibility = sum(visibility_scores) / total_pages

        print(f"Overall Sharpness Score: {overall_sharpness:.2f}")
        print(f"Overall Contrast Score: {overall_contrast:.2f}")
        print(f"Overall Visibility Score: {overall_visibility:.2f}")
        return overall_sharpness, overall_contrast, overall_visibility
    except Exception as e:
        print(f"Error: {e}")
        return overall_sharpness, overall_contrast, overall_visibility


def get_data_for_colors_(image_path, num_colors):
    image = cv2.imread(image_path)
    # Convert the image from BGR to RGB (OpenCV reads in BGR format)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Flatten the image to a 2D array of pixels
    pixels = image.reshape((-1, 3))

    # Convert to float32 for k-means clustering
    pixels = np.float32(pixels)

    # Define criteria for k-means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.2)

    # Perform k-means clustering
    _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert centers to uint8
    centers = np.uint8(centers)

    # Get the counts of labels to find the most common colors
    label_counts = Counter(labels.flatten())

    # Sort the colors by frequency and get the top colors
    top_colors = [centers[i] for i, _ in label_counts.most_common(num_colors)]

    return top_colors


# def get_top_colors_call_(image_paths, num_colors=5):
#     top_colors_list = []
#     threads = []
#
#     def run_function(image_path):
#         top_colors = get_data_for_colors_(image_path, num_colors)
#         top_colors_list.append(top_colors)
#
#     for image_path in image_paths:
#         thread = threading.Thread(target=run_function, args=(image_path,))
#         threads.append(thread)
#         thread.start()
#
#     for thread in threads:
#         thread.join(timeout=10)  # Set the timeout to 30 seconds
#         if thread.is_alive():
#             print("Function for an image took too long, skipping...")
#             continue
#
#     return top_colors_list


def get_top_colors_call_(file_path):
    image_paths = [os.path.join(file_path, filename) for filename in os.listdir(file_path)
                   if filename.endswith(('.jpg', '.jpeg', '.png', '.gif'))][:MAX_IMAGES_TO_PROCESS]

    top_colors_list = []

    def run_function(image_path):
        try:
            top_colors = get_data_for_colors_(image_path, NUM_COLORS)
            top_colors_list.append(top_colors)
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")

    with futures.ThreadPoolExecutor() as executor:
        future_to_path = {executor.submit(run_function, path): path for path in image_paths}

        for future in futures.as_completed(future_to_path):
            try:
                future.result(timeout=TIMEOUT_SECONDS)
            except futures.TimeoutError:
                print(f"Function for an image took too long, skipping...")

    return [[color.tolist() for color in colors] for colors in top_colors_list]


def get_top_colors(file_path_):
    import os
    image_paths = []
    len_to_process_ = 1
    for filename in os.listdir(file_path_):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            if len_to_process_ == 6:
                break
            image_path = os.path.join(file_path_, filename)
            image_paths.append(image_path)
            len_to_process_ += 1
    if image_paths:
        top_colors_list = get_top_colors_call_(image_paths, 5)
        top_colors_list = [[color.tolist() for color in colors] for colors in top_colors_list]
    else:
        top_colors_list = []
    return top_colors_list


# # Provide the path to your image
# image_path = '/Users/sandeepkumarrudhravaram/UNTMastersProjects/pdf_analyzer_prodv1/pdf_docs/Team16_Sprint3.pdf'  # Change this to your image's path
# assess_pdf_quality(image_path)

def analyze_figure_captions(filename):
    total_images = 0
    images_with_captions = 0
    percentage_with_captions = 0
    percentage_without_captions = 0
    doc = fitz.open(filename)
    captions_with_images = []

    for page_num, page in enumerate(doc, start=1):
        images = page.get_images()
        if images:
            total_images += len(images)
            blocks = page.get_text("blocks")
            for block in blocks:
                if block[4].replace("\n", "").lower().strip().startswith("figure") or block[4].replace("\n",
                                                                                                       "").lower().strip().startswith(
                    "fig") or block[4].replace("\n", "").lower().strip().startswith("img") or block[4].replace("\n",
                                                                                                               "").lower().strip().startswith(
                    "image"):
                    caption = block[4].strip().replace("\n", "")
                    if images:
                        for img in images:
                            if abs(block[2] - img[0]) < 70 and block[5] - img[1] < 50:
                                images_with_captions += 1
                                captions_with_images.append({
                                    "page_number": page_num,
                                    "image_info": {
                                        "image_index": img[7],
                                        "image_position": (img[0], img[1]),
                                    },
                                    "caption_text": caption
                                })
                                break
    if total_images > 0:
        percentage_with_captions = (images_with_captions / total_images) * 100
        percentage_without_captions = 100 - percentage_with_captions
        print(f"Percentage of images with captions: {percentage_with_captions:.2f}%")
        print(f"Percentage of images without captions: {percentage_without_captions:.2f}%")
    else:
        print("No images found in the PDF.")
        captions_with_images.append("No images found in the PDF.")

    return percentage_with_captions, percentage_without_captions, captions_with_images
