from PIL import Image
from colorspacious import cspace_converter
import fitz  # PyMuPDF
import io
import re


def get_contrast_ratio(color1, color2):
    # Calculate contrast ratio using colorspacious library
    converter = cspace_converter("sRGB1", "CAM02-UCS")
    color1_lab = converter(color1)
    color2_lab = converter(color2)

    l1, _, _ = color1_lab
    l2, _, _ = color2_lab

    # Calculate contrast ratio using luminance values
    contrast_ratio = (l1 + 0.05) / (l2 + 0.05)
    return contrast_ratio


def check_contrast(image):
    # Get the RGB values of two pixels (e.g., top-left and bottom-right corners)
    pixel1 = image.getpixel((0, 0))
    pixel2 = image.getpixel((image.width - 1, image.height - 1))


    # Calculate contrast ratio
    contrast_ratio = get_contrast_ratio(pixel1, pixel2)

    # print(f"Contrast Ratio: {contrast_ratio:.2f}")

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


def analyze_pdf(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    total_pages = pdf_document.page_count
    meets_wcag_count = 0
    does_not_meet_wcag_count = 0
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
            xref = img_info[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            # Calculate contrast for the image
            status_,ratio_of_image=check_contrast(image)
            if status_:
                meets_wcag_count += 1
                # page_meets_wcag = True
                image_status = "Accessible"
            else:
                does_not_meet_wcag_count += 1
                image_status ="Not Accessible"
                # page_does_not_meet_wcag = True
            key = f"{page_num + 1}_{img_index + 1}"
            image_accessibility[key] = image_status
            image_ratio_of_accessibility[key]=ratio_of_image
        # if page_meets_wcag:
        #     meets_wcag_pages.append(page_num + 1)  # Pages are 0-indexed, adding 1 for human-readable format
        # if page_does_not_meet_wcag:
        #     does_not_meet_wcag_pages.append(page_num + 1)

    # Calculate percentages
    meets_wcag_percentage = (meets_wcag_count / total_pages) * 100
    does_not_meet_wcag_percentage = (does_not_meet_wcag_count / total_pages) * 100

    print(f"Total Pages: {total_pages}")
    print(f"Pages meeting WCAG AA standards: {meets_wcag_count} ({meets_wcag_percentage:.2f}%)")
    print(f"Pages not meeting WCAG AA standards: {does_not_meet_wcag_count} ({does_not_meet_wcag_percentage:.2f}%)")

    pdf_document.close()
    return meets_wcag_count, does_not_meet_wcag_count, meets_wcag_percentage, does_not_meet_wcag_percentage,image_accessibility,image_ratio_of_accessibility

