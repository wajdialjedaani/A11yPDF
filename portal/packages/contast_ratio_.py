from PIL import Image
from colorspacious import cspace_converter
import fitz  # PyMuPDF
import io
import re


def get_contrast_ratio(color1, color2):
    color1_rgb = color1[:3]
    color2_rgb = color2[:3]
    converter = cspace_converter("sRGB1", "CAM02-UCS")
    color1_lab = converter(color1_rgb)
    color2_lab = converter(color2_rgb)

    l1, _, _ = color1_lab
    l2, _, _ = color2_lab
    contrast_ratio = (l1 + 0.05) / (l2 + 0.05)
    return contrast_ratio


def check_contrast(image):
    # Get the RGB values of two pixels (e.g., top-left and bottom-right corners)
    pixel1 = image.getpixel((0, 0))
    pixel2 = image.getpixel((image.width - 1, image.height - 1))


    # Calculate contrast ratio
    try:
        contrast_ratio = get_contrast_ratio(pixel1, pixel2)
    except:
        contrast_ratio=1.0

    # Determine if the contrast meets accessibility standards (WCAG)
    if contrast_ratio >= 4.5:
        # print("Contrast meets WCAG AA standards for normal text.")
        return True,contrast_ratio
    elif contrast_ratio >= 3:
        # print("Contrast meets WCAG AA standards for large text.")
        return True,contrast_ratio
    else:
        # print("Contrast does not meet WCAG AA standards.")
        return False,contrast_ratio

#
# def convert_image_to_standard_format(image_bytes):
#     # Open the image using Wand
#     with WandImage(blob=image_bytes) as img:
#         # Convert the image to PNG format
#         img.format = 'png'
#         # Convert Wand image to bytes
#         return img.make_blob()


def analyze_pdf(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    total_pages = pdf_document.page_count
    meets_wcag_count = 0
    does_not_meet_wcag_count = 0
    images_cont_=0
    meets_wcag_pages = []  # To store page numbers of images meeting WCAG standards
    image_accessibility = {}
    image_ratio_of_accessibility = {}
    # Loop through each page in the PDF
    for page_num in range(total_pages):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        page_meets_wcag = False
        page_does_not_meet_wcag = False
        # Loop through each image in the page
        if not image_list:  # If there are no images on the page, consider it as "Access"
            key2 = f"{page_num+1}_{0}"
            image_accessibility[key2] = "No Images"
            image_ratio_of_accessibility[key2]="none"
            continue
        for img_index, img_info in enumerate(image_list):
            images_cont_+=1
            xref = img_info[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_extension = base_image["ext"]

            if image_extension.lower() != 'jb2':
                image = Image.open(io.BytesIO(image_bytes))
                status_,ratio_of_image=check_contrast(image)
                if status_:
                    meets_wcag_count += 1
                    # page_meets_wcag = True
                    image_status = "Accessible"
                else:
                    does_not_meet_wcag_count += 1
                    image_status = "Not Accessible"
                key = f"{page_num + 1}_{img_index + 1}"
                image_accessibility[key] = image_status
                image_ratio_of_accessibility[key] = ratio_of_image
            else:
                does_not_meet_wcag_count += 1
                key = f"{page_num + 1}_{img_index + 1}"
                image_accessibility[key] = "Image is not in correct format"
                image_ratio_of_accessibility[key] = "none"
            # else:
            #     does_not_meet_wcag_count += 1
            #     image_status = "Not Accessible"
            #     key = f"{page_num + 1}_{img_index + 1}"
            #     image_accessibility[key] = image_status
            #     image_ratio_of_accessibility[key] = "Image is jp2 format"

        # if page_meets_wcag:
        #     meets_wcag_pages.append(page_num + 1)  # Pages are 0-indexed, adding 1 for human-readable format
        # if page_does_not_meet_wcag:
        #     does_not_meet_wcag_pages.append(page_num + 1)

    # Calculate percentages
    if images_cont_==0:
        meets_wcag_percentage=0
        does_not_meet_wcag_percentage=0
    else:
        meets_wcag_percentage = (meets_wcag_count / images_cont_) * 100
        does_not_meet_wcag_percentage = (does_not_meet_wcag_count / images_cont_) * 100

    # print(f"Total Pages: {total_pages}")
    # print(f"Pages meeting WCAG AA standards: {meets_wcag_count} ({meets_wcag_percentage:.2f}%)")
    # print(f"Pages not meeting WCAG AA standards: {does_not_meet_wcag_count} ({does_not_meet_wcag_percentage:.2f}%)")

    pdf_document.close()
    return meets_wcag_count, does_not_meet_wcag_count, meets_wcag_percentage, does_not_meet_wcag_percentage,image_accessibility,image_ratio_of_accessibility

# meets_wcag_count, does_not_meet_wcag_count, meets_wcag_percentage, does_not_meet_wcag_percentage,image_accessibility,image_ratio_of_accessibility=analyze_pdf("/Users/sandeepkumarrudhravaram/WorkSpace/UntProjects/pdf_analyzer_prod_final/Issues/Team16_Sprint_2.pdf")
#
# print(meets_wcag_count, does_not_meet_wcag_count, meets_wcag_percentage, does_not_meet_wcag_percentage,image_accessibility,image_ratio_of_accessibility)