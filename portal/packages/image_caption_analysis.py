import fitz
from concurrent.futures import ThreadPoolExecutor


def is_caption_near_image(caption_box, image_box, max_distance=400):
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

    if 0 <= vertical_distance <= max_distance and horizontal_overlap > 0:
        return True
    return False


# def analyze_page(filename, page_num):
#     doc = fitz.open(filename)
#     page = doc.load_page(page_num)
#     images_with_captions = 0
#     captions_with_images = []
#
#     image_blocks = [img for img in page.get_images(full=True)]
#     text_blocks = [block for block in page.get_text("blocks") if not block[4].startswith(('Figure', 'Fig.', 'Image'))]
#
#     for img_block in image_blocks:
#         img_rect = page.get_image_bbox(img_block)
#         for text_block in text_blocks:
#             text_rect = fitz.Rect(text_block[:4])  # Text block bounding box
#             if is_caption_near_image(text_rect, img_rect):
#                 images_with_captions += 1
#                 captions_with_images.append({"page_number": page_num + 1,
#                                              "caption_text": text_block[4].strip(),
#                                              "image_info": img_block})
#                 break  # Assuming one caption per image
#
#     return images_with_captions, captions_with_images

def analyze_page(filename, page_num):
    doc = fitz.open(filename)
    page = doc.load_page(page_num)
    images_with_captions = 0
    captions_with_images = []

    image_blocks = [img for img in page.get_images(full=True)]
    # Update here to filter text blocks based on the specific starting words
    text_blocks = [block for block in page.get_text("blocks") if block[4].replace("\n", "").lower().strip().startswith(("figure", "fig", "img", "image"))]

    image_count_=1
    for img_block in image_blocks:
        img_rect = page.get_image_bbox(img_block)
        image_csp=image_count_
        image_count_+=1
        caption_found = False
        for text_block in text_blocks:
            text_rect = fitz.Rect(text_block[:4])  # Text block bounding box
            if is_caption_near_image(text_rect, img_rect):
                caption_found = True
                images_with_captions += 1
                captions_with_images.append({
                    "page_number": page_num + 1,
                    "caption_text": text_block[4].strip(),
                    "image_info": img_block,
                    "image Index In Pdf": img_block[7],
                    "image Index In Page":image_csp,
                    "Accessibility": "Accessible"
                })
                break  # Assuming one caption per image, stop after finding the first match

        if not caption_found:
            captions_with_images.append({
                "page_number": page_num + 1,
                "caption_text": "No Caption",
                "image_info": img_block,
                "image Index In Pdf": img_block[7],
                "image Index In Page": image_csp,
                "Accessibility":"Not Accessible"
            })

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



# # Adjust the filepath to your PDF
# pdf_filepath = 'ImageCaptionTest4.pdf'
# percentage_with_captions, percentage_without_captions, captions_with_images = analyze_figure_captions_parallel(
#     pdf_filepath)
# print(f'Percentage with captions: {percentage_with_captions}%')
# print(f'Percentage without captions: {percentage_without_captions}%')
# print('Captions with images:', captions_with_images)
