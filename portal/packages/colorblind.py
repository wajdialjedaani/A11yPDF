import cv2
import pandas as pd
import numpy as np
import colorsys
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import fitz
from sklearn.cluster import MiniBatchKMeans
import concurrent.futures
# quantise image from
# https://www.tutorialspoint.com/color-quantization-in-an-image-using-k-means-in-opencv-python
AAL = 1 / 3
AASAAAL = 1 / 4.5
AAAS = 1 / 7


def quantise(img):
    z = img.reshape((-1, 3))

    # convert to np.float32
    z = np.float32(z)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 8
    ret, label, center = cv2.kmeans(z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    img = res.reshape((img.shape))
    return img


# luminance function from WCAG
def luminance(rgb):
    L = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    return L

def relevantTests(hue, sat):
    hue *= 360
    sat *= 100

    if sat < 15:
        return "NA"

    if hue > 320 or hue < 11:
        return "PD"

    elif hue < 170 and hue > 80:
        return "PD"

    elif hue > 40 and hue < 81:
        return "PDT"

    elif hue > 169 and hue < 281:
        return "T"

    else:
        return "NA"

def analyzeFrame(img, ratios):
    img = quantise(img)
    # blank set
    rgb = set()
    # opencv was made when bgr was standard so swap to rgb
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # quantise the colours
    img = quantise(img)

    # height and width
    h = img.shape[0]
    w = img.shape[1]

    # loop over the image, pixel by pixel
    # get every colour as a rgb value
    for y in range(0, h):
        for x in range(0, w):
            b, g, r = img[y, x]
            colours = (r, g, b)
            if colours not in rgb:
                rgb.add(colours)

        # for every rgb value, get the luminance
    for col1 in rgb:
        lum1 = luminance(col1)
        lum2 = 0

        # get the luminance of every other colour
    for col2 in rgb:
        if col2 != col1:
            lum2 = luminance(col2)

            # get the contrast ratio, and which tests the colours count for
            if lum1 > lum2:
                ratio = (lum2 + 0.05) / (lum1 + 0.05)
            else:
                ratio = (lum1 + 0.05) / (lum2 + 0.05)

                temp = (col2, col1, ratio)
                hue1 = colorsys.rgb_to_hsv(col1[0], col1[1], col1[2])
                hue2 = colorsys.rgb_to_hsv(col2[0], col2[1], col2[2])

                letters1 = relevantTests(hue1[0], hue1[1])
                letters2 = relevantTests(hue2[0], hue2[1])

                # add ratio to ratios if it hasn't been added
                temp = (col2, col1, ratio, letters2, letters1)
                if temp not in ratios:
                    temp = (col1, col2, ratio)
                    temp = (col1, col2, ratio, letters1, letters2)
                    ratios.append(temp)

        # sort by ratio
        ratios = sorted(ratios, key=lambda a: a[2], reverse=True)
        data = processResults(ratios)
        print(ratios)

        print(data)
    return data
    # chart(data)


def processResults(ratios):
    contrast = 0
    highestRatioPD = 0
    highestRatioT = 0
    highestRatioM = 0

    for x in ratios:
        print(x[0], x[1], "Relevant Tests: ")
        # Directly print information instead of using Tkinter Text widget
        output_info = f"{x[0]} {x[1]} \nRatio: {round(x[2], 2)}\n"

        if x[3] == "PD" or x[3] == "PDT" and x[4] == "PD" or x[4] == "PDT":
            output_info += "Protonopia, Deuteranopia\n"
            if x[2] > highestRatioPD:
                highestRatioPD = x[2]
            if x[2] > highestRatioM:
                highestRatioM = x[2]

        if x[3] == "T" or x[3] == "PDT" and x[4] == "T" or x[4] == "PDT":
            output_info += "Tritanopia, Monochromacy\n"
            if x[2] > highestRatioT:
                highestRatioT = x[2]
            if x[2] > highestRatioM:
                highestRatioM = x[2]

        # Additional checks and information appending goes here

        print(output_info)  # Print the information

    data = {'Monochromacy': [round(highestRatioM, 2)], 'Protonopia/Deuteranopia': [round(highestRatioPD, 2)],
            'Tritanopia': [round(highestRatioT, 2)]}
    return data


def get_data_from_image(img):
    ratios = []
    # img is already an image array, so no need to read it from a file.

    # The rest of your function as before, but ensure any modifications needed
    # to work directly with the 'img' array are made.
    data = analyzeFrame(img, ratios)
    return data


def pdf_page_to_image(page, zoom=2):
    """Render a PDF page to an image."""
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    return img

def process_page_image(image):
    """Process a single page image."""
    ratios = []
    data = analyzeFrame(image,ratios)
    return data

def categorize_values(data):
    categorized_data = {}
    for key, values in data.items():
        categories = {'0-0.5': 0, '0.5-1': 0}
        for value in values:
            # if value == 0:
            #     categories['0'] += 1
            if 0 <= value <= 0.5:
                categories['0-0.5'] += 1
            elif 0.5 < value <= 1:
                categories['0.5-1'] += 1
            # else:
            #     categories['1+'] += 1
        categorized_data[key] = categories
    return categorized_data

def resize_image(image, max_width=800):
    """Resize the image to a maximum width to reduce processing time."""
    h, w = image.shape[:2]
    if w > max_width:
        ratio = max_width / w
        image = cv2.resize(image, (max_width, int(h * ratio)))
    return image

def quantise(img, K=8):
    """Apply color quantization to reduce the number of colors in the image."""
    img = resize_image(img)  # Resize for faster processing
    z = img.reshape((-1, 3))
    z = np.float32(z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    kmeans = MiniBatchKMeans(n_clusters=K)
    labels = kmeans.fit_predict(z)
    center = np.uint8(kmeans.cluster_centers_)
    res = center[labels.flatten()]
    img = res.reshape((img.shape))
    return img

def analyze_pdf_colorblind(pdf_path, zoom=2):
    doc = fitz.open(pdf_path)
    combined_data = {
        'Monochromacy': [],
        'Protonopia/Deuteranopia': [],
        'Tritanopia': [],
        'page number': []
    }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit PDF page processing tasks
        future_to_page = {executor.submit(process_page_image, pdf_page_to_image(page, zoom)): page.number for page in
                          doc}

        for future in concurrent.futures.as_completed(future_to_page):
            page_number = future_to_page[future]
            try:
                page_data = future.result() # Updated to use the new function
                combined_data['page number'].append(page_number+1)
                for key in combined_data:
                    if key in page_data and key != 'page number':
                        combined_data[key].append(page_data[key][0])  # Assuming page_data[key] is a list with a single element
            except Exception as exc:
                print(f'Page {page_number} generated an exception: {exc}')
    doc.close()
    final_data_=categorize_values(combined_data)

    zipped_data = zip(combined_data["page number"], combined_data["Monochromacy"], combined_data["Protonopia/Deuteranopia"], combined_data["Tritanopia"])

    # Sort the zipped data by the first element of each tuple (the page number)
    sorted_zipped_data = sorted(zipped_data)

    # print(sorted_zipped_data)

    # Unzip the sorted data back into lists
    sorted_page_numbers, sorted_monochromacy, sorted_protonopia_deuteranopia, sorted_tritanopia = zip(
        *sorted_zipped_data)

    # Update the original dictionary with the sorted lists
    combined_data["page number"] = list(sorted_page_numbers)
    combined_data["Monochromacy"] = list(sorted_monochromacy)
    combined_data["Protonopia/Deuteranopia"] = list(sorted_protonopia_deuteranopia)
    combined_data["Tritanopia"] = list(sorted_tritanopia)
    return final_data_,combined_data