# import fitz
# from concurrent.futures import ThreadPoolExecutor
#
#
# def is_caption_near_image(caption_box, image_box, max_distance=20):
#     """
#     Determine if a caption is near an image using their bounding boxes.
#
#     Parameters:
#     - caption_box: The bounding box of the caption ([x0, y0, x1, y1]).
#     - image_box: The bounding box of the image ([x0, y0, x1, y1]).
#     - max_distance: Maximum distance allowed between caption and image to consider them related.
#
#     Returns:
#     - True if the caption is near the image; False otherwise.
#     """
#     # Calculate vertical distance and check overlap in the horizontal direction
#     vertical_distance = caption_box[1] - image_box[3]  # caption's y0 - image's y1
#     horizontal_overlap = min(caption_box[2], image_box[2]) - max(caption_box[0], image_box[0])
#
#     if 0 <= vertical_distance <= max_distance and horizontal_overlap > 0:
#         return True
#     return False
#
#
# # def analyze_page(filename, page_num):
# #     doc = fitz.open(filename)
# #     page = doc.load_page(page_num)
# #     images_with_captions = 0
# #     captions_with_images = []
# #
# #     image_blocks = [img for img in page.get_images(full=True)]
# #     text_blocks = [block for block in page.get_text("blocks") if not block[4].startswith(('Figure', 'Fig.', 'Image'))]
# #
# #     for img_block in image_blocks:
# #         img_rect = page.get_image_bbox(img_block)
# #         for text_block in text_blocks:
# #             text_rect = fitz.Rect(text_block[:4])  # Text block bounding box
# #             if is_caption_near_image(text_rect, img_rect):
# #                 images_with_captions += 1
# #                 captions_with_images.append({"page_number": page_num + 1,
# #                                              "caption_text": text_block[4].strip(),
# #                                              "image_info": img_block})
# #                 break  # Assuming one caption per image
# #
# #     return images_with_captions, captions_with_images
#
# def get_imgcaptionslits(page):
#     text_blocks = []
#     try:
#         temp_data_ = page.get_text("dict")["blocks"]
#         for data_1 in temp_data_:
#             try:
#                 text_1 = data_1["lines"]
#             except KeyError:
#                 text_1 = []
#             for line in text_1:
#                 line_total_text_ = ''
#                 text_2 = line["spans"]
#                 for span in text_2:
#                     span_text = span["text"].strip().replace('    ', '')
#                     if span_text:
#                         line_total_text_ += f' {span_text}' if line_total_text_ else span_text
#                 if line_total_text_ and line_total_text_.lower().strip().startswith(
#                         ("figure", "fig", "img", "image", "fig")):
#                     text_blocks.append(data_1)
#     except:
#         text_blocks = []
#     return text_blocks
#
# def analyze_page(filename, page_num):
#     doc = fitz.open(filename)
#     page = doc.load_page(page_num)
#     images_with_captions = 0
#     captions_with_images = []
#
#     image_blocks = [img for img in page.get_images(full=True)]
#     # text_blocks = [block for block in page.get_text("blocks") if block[4].replace("\n", "").lower().strip().startswith(("figure", "fig", "img", "image","Fig"))]
#     text_blocks = get_imgcaptionslits(page)
#     print('text_blocks',text_blocks)
#
#     image_count_=1
#     for img_block in image_blocks:
#         img_rect = page.get_image_bbox(img_block)
#         image_csp=image_count_
#         image_count_+=1
#         caption_found = False
#         for text_block in text_blocks:
#             print("text_block",text_block)
#             text_rect = fitz.Rect(text_block[:4])  # Text block bounding box
#             if is_caption_near_image(text_rect, img_rect):
#                 caption_found = True
#                 images_with_captions += 1
#                 captions_with_images.append({
#                     "page_number": page_num + 1,
#                     "caption_text": text_block[4].strip(),
#                     "image_info": img_block,
#                     "image Index In Pdf": img_block[7],
#                     "image Index In Page":image_csp,
#                     "Accessibility": "Accessible"
#                 })
#                 break  # Assuming one caption per image, stop after finding the first match
#
#         if not caption_found:
#             captions_with_images.append({
#                 "page_number": page_num + 1,
#                 "caption_text": "No Caption",
#                 "image_info": img_block,
#                 "image Index In Pdf": img_block[7],
#                 "image Index In Page": image_csp,
#                 "Accessibility":"Not Accessible"
#             })
#
#     return images_with_captions, captions_with_images
#
#
#
# def analyze_figure_captions_parallel(filename):
#     doc = fitz.open(filename)
#     total_images = sum(len(page.get_images(full=True)) for page in doc)
#     all_captions_with_images = []
#     images_with_captions_final=0
#
#     with ThreadPoolExecutor() as executor:
#         future_to_page = {executor.submit(analyze_page, filename, i): i for i in range(len(doc))}
#         for future in future_to_page:
#             images_with_captions, captions_with_images = future.result()
#             all_captions_with_images.extend(captions_with_images)
#             images_with_captions_final+=images_with_captions
#
#     images_with_captions_count = len(all_captions_with_images)
#     percentage_with_captions = (images_with_captions_final / total_images * 100) if total_images else 0
#     percentage_without_captions = 100 - percentage_with_captions
#
#     return percentage_with_captions, percentage_without_captions, all_captions_with_images
#
#
#
# # Adjust the filepath to your PDF
# pdf_filepath = '/Users/sandeepkumarrudhravaram/WorkSpace/UntProjects/pdf_analyzer_prod_final/Issues/s10209-022-00897-5_5.pdf'
# percentage_with_captions, percentage_without_captions, captions_with_images = analyze_figure_captions_parallel(
#     pdf_filepath)
# print(f'Percentage with captions: {percentage_with_captions}%')
# print(f'Percentage without captions: {percentage_without_captions}%')
# print('Captions with images:', captions_with_images)

import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor

def is_caption_near_image(caption_box, image_box, max_distance=50):
    """
    Determine if a caption is near an image using their bounding boxes.

    Parameters:
    - caption_box: The bounding box of the caption ([x0, y0, x1, y1]).
    - image_box: The bounding box of the image ([x0, y0, x1, y1]).
    - max_distance: Maximum distance allowed between caption and image to consider them related.

    Returns:
    - True if the caption is near the image; False otherwise.
    """
    # Calculate vertical distance and check overlap in the horizontal direction
    vertical_distance = caption_box[1] - image_box[3]  # caption's y0 - image's y1
    horizontal_overlap = min(caption_box[2], image_box[2]) - max(caption_box[0], image_box[0])
    print('vertical_distance',vertical_distance)

    if 0 <= vertical_distance <= max_distance and horizontal_overlap > 0:
        return True
    return False

def get_imgcaptionslits(page):
    text_blocks = []
    try:
        temp_data_ = page.get_text("dict")["blocks"]
        for data_1 in temp_data_:
            try:
                text_1 = data_1["lines"]
            except KeyError:
                text_1 = []
            for line in text_1:
                line_total_text_ = ''
                text_2 = line["spans"]
                for span in text_2:
                    span_text = span["text"].strip().replace('    ', '')
                    if span_text:
                        line_total_text_ += f' {span_text}' if line_total_text_ else span_text
                if line_total_text_ and line_total_text_.lower().strip().startswith(
                        ("figure", "fig", "img", "image", "fig")):
                    text_blocks.append(data_1)
    except:
        text_blocks = []
    return text_blocks

def analyze_page(filename, page_num):
    doc = fitz.open(filename)
    page = doc.load_page(page_num)
    images_with_captions = 0
    captions_with_images = []

    image_blocks = [img for img in page.get_images(full=True)]
    text_blocks = get_imgcaptionslits(page)  # Assume this function returns the necessary data correctly
    # print('text_blocks',text_blocks)

    image_count_ = 1
    for img_block in image_blocks:
        image_csp = image_count_
        image_count_ += 1
        img_rect = page.get_image_bbox(img_block)
        # Convert to a list for is_caption_near_image function
        img_box = [img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1]
        caption_found = False
        for text_block in text_blocks:
            # Extracting bounding box for the text block
            text_box = text_block['bbox']  # Assuming 'bbox' is directly accessible and correct
            # Convert to a list for is_caption_near_image function
            caption_box = [text_box[0], text_box[1], text_box[2], text_box[3]]

            if is_caption_near_image(caption_box, img_box):
                caption_found = True
                images_with_captions += 1
                # Constructing caption text by joining all lines and spans
                caption_text = " ".join([" ".join([span['text'] for span in line['spans']]) for line in text_block['lines']])
                captions_with_images.append({
                                    "page_number": page_num + 1,
                                    "caption_text": caption_text,
                                    "image_info": img_block,
                                    "image Index In Pdf": img_block[7],
                                    "image Index In Page":image_csp,
                                    "Accessibility": "Accessible"
                                })
                break
        if not caption_found:
            captions_with_images.append({
                "page_number": page_num + 1,
                "caption_text": "No Caption",
                "image_info": img_block,
                "image Index In Pdf": img_block[7],
                "image Index In Page": image_csp,
                "Accessibility": "Not Accessible"
            })
              # Assuming one caption per image

    # Process images_with_captions and captions_with_images as needed
    # print(f"Images with Captions: {images_with_captions}")
    # print(f"Captions with Images: {captions_with_images}")
    return images_with_captions, captions_with_images



def analyze_figure_captions_parallel(filename):
    doc = fitz.open(filename)
    total_images = sum(len(page.get_images(full=True)) for page in doc)
    all_captions_with_images = []
    images_with_captions_final=0

    with ThreadPoolExecutor() as executor:
        future_to_page = {executor.submit(analyze_page, filename, i): i for i in range(len(doc))}
        for future in future_to_page:
            images_with_captions, captions_with_images = future.result()
            all_captions_with_images.extend(captions_with_images)
            images_with_captions_final+=images_with_captions

    images_with_captions_count = len(all_captions_with_images)
    percentage_with_captions = (images_with_captions_final / total_images * 100) if total_images else 0
    percentage_without_captions = 100 - percentage_with_captions

    return percentage_with_captions, percentage_without_captions, all_captions_with_images

#
# # Example usage
# filename = "/Users/sandeepkumarrudhravaram/WorkSpace/UntProjects/pdf_analyzer_prod_final/Issues/s10209-022-00897-5_5.pdf"
# percentage_with_captions, percentage_without_captions, all_captions_with_images=analyze_figure_captions_parallel(filename)
# print(percentage_with_captions, percentage_without_captions, all_captions_with_images)


# Example usage
filename = "/Users/sandeepkumarrudhravaram/WorkSpace/UntProjects/pdf_analyzer_prod_final/Issues/s10209-022-00897-5_5.pdf"
percentage_with_captions, percentage_without_captions, all_captions_with_images=analyze_figure_captions_parallel(filename)
print(percentage_with_captions, percentage_without_captions, all_captions_with_images)
