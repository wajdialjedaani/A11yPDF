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


def count_images_in_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    image_count = 0
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        image_list = page.get_images(full=True)
        image_count += len(image_list)

    pdf_document.close()
    return image_count


def get_random_numbers(string_length=5):
    import random
    import string
    return ''.join(random.choice(string.digits) for x in range(string_length))


def count_custom_urls_in_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    links_l = []
    final_ = {}
    yes_count_ = 0
    no_count_ = 0
    for page in doc:
        page_text = page.get_links()
        for block in page_text:
            links_l.append(block['uri'])
    count_urls_ = len(links_l)
    for link in range(len(links_l)):
        temp_ = {}
        try:
            response_ = requests.get(links_l[link])
            if response_.status_code == 200:
                temp_['url_acc'] = "Yes"
                yes_count_ += 1
            else:
                temp_['url_acc'] = "No"
                no_count_ += 1
            temp_['status_code'] = response_.status_code
        except:
            temp_['url_acc'] = "No"
            no_count_ += 1
            temp_['status_code'] = 400
        temp_['url'] = links_l[link]
        final_[link] = temp_
    final_out_ = {"count_urls_": count_urls_, "final_": final_, "yes_count_": yes_count_, "no_count_": no_count_}
    return final_out_

    # for page in pdf_file.pages:
    #     text = page.extractText()
    #     urls = re.findall(r'h?%?ps?://\S+', text)
    #     url_count += len(urls)
    # return url_count


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

    count_of_footers_ = [[round(percentage_with_footer, 2), yes_footer_pages],
                         [round(percentage_without_footer, 2), No_footer_Pages]]

    return titles, count_of_footers_


def get_tables_count_(pdf_path):
    import pdfplumber
    table_count_ = 0
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            l_ = page.extract_tables()
            if len(l_) > 0:
                for i in l_:
                    if len(i) > 1:
                        table_count_ += 1
    return table_count_


def get_image_info(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            aspect_ratio = width / height
            return width, height, aspect_ratio
    except IOError:
        print(f"Unable to open {image_path}")
        return None, None, None


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
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):  # Checking for image file extensions
            image_path = os.path.join(folder_path, filename)
            width, height, aspect_ratio = get_image_info(image_path)
            sharpness, file_size_mb = get_image_contarct(image_path)
            # print('file_size_mb', file_size_mb)
            if width is not None:
                image_info_dict[filename] = {
                    "width": width,
                    "height": height,
                    "aspect_ratio": round(aspect_ratio, 3)
                }
                # print('filename',filename)
                list_of_filename.append(str(tmp_file_name).replace('.png', ''))
                list_of_width.append(width)
                list_of_height.append(height)
                list_of_aspect_ratio.append(round(aspect_ratio, 2))
                list_of_sharpness.append(round(sharpness, 2))
                list_of_file_size_mb.append(round(file_size_mb, 3))
    final_list_of_rsa = [list_of_filename, list_of_width, list_of_height, list_of_aspect_ratio, list_of_sharpness,
                         list_of_file_size_mb]
    final_list_of_rsa = json.dumps(final_list_of_rsa)
    return image_info_dict, final_list_of_rsa


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
    # Get image dimensions
    height, width, _ = image.shape

    # Assess based on dimensions
    min_threshold = 1000  # Define your threshold for minimum resolution here
    quality_percentage = ((min(height, width) + max(height, width)) / 2) / min_threshold * 100
    return min(quality_percentage, 100)  # Cap at 100%


def assess_sharpness(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate image sharpness using Laplacian method
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Normalize sharpness to a scale of 0-100 (higher is sharper)
    sharpness_percentage = min(sharpness, 100) / 100 * 100
    return sharpness_percentage


def assess_contrast(image):
    # Calculate image contrast
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    contrast = cv2.compareHist(hist, hist, cv2.HISTCMP_BHATTACHARYYA)

    # Normalize contrast to a scale of 0-100 (higher is better)
    contrast_percentage = (1 - min(contrast, 1)) * 100
    return contrast_percentage


def assess_image_quality(image_path):
    try:
        # Open the image using OpenCV
        img = cv2.imread(image_path)

        # Assess image quality based on different factors
        dimensions_score = assess_dimensions(img)
        sharpness_score = assess_sharpness(img)
        contrast_score = assess_contrast(img)
        visibility_score = assess_visibility(img)

        # Combine the scores to get an overall quality score (simple average here)
        overall_score = (dimensions_score + sharpness_score + contrast_score + visibility_score) / 4

        print(f"The overall image quality score is approximately {overall_score:.2f}%")

    except Exception as e:
        print(f"Error: {e}")


def assess_visibility(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate average luminance/brightness of the image
    visibility_score = cv2.mean(gray)[0]  # Average pixel value

    # Normalize visibility to a scale of 0-100 (higher is better)
    visibility_percentage = (visibility_score / 255) * 100
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


def get_top_colors_call_(image_paths, num_colors=5):
    top_colors_list = []
    threads = []

    def run_function(image_path):
        top_colors = get_data_for_colors_(image_path, num_colors)
        top_colors_list.append(top_colors)

    for image_path in image_paths:
        thread = threading.Thread(target=run_function, args=(image_path,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join(timeout=10)  # Set the timeout to 30 seconds
        if thread.is_alive():
            print("Function for an image took too long, skipping...")
            continue

    return top_colors_list


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
    percentage_with_captions=0
    percentage_without_captions=0
    doc = fitz.open(filename)
    captions_with_images = []

    for page_num,page in enumerate(doc,start=1):
        images = page.get_images()
        if images:
            total_images += len(images)
            blocks = page.get_text("blocks")
            for block in blocks:
                if block[4].replace("\n", "").lower().strip().startswith("figure") or block[4].replace("\n", "").lower().strip().startswith("fig") or block[4].replace("\n", "").lower().strip().startswith("img") or block[4].replace("\n", "").lower().strip().startswith("image"):
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

    return percentage_with_captions,percentage_without_captions,captions_with_images
