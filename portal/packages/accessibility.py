# # import cv2
# # import numpy as np
# # import fitz
# # from collections import Counter
# #
# #
# # def assess_dimensions(image):
# #     # Get image dimensions
# #     height, width, _ = image.shape
# #
# #     # Assess based on dimensions
# #     min_threshold = 1000  # Define your threshold for minimum resolution here
# #     quality_percentage = ((min(height, width) + max(height, width)) / 2) / min_threshold * 100
# #     return min(quality_percentage, 100)  # Cap at 100%
# #
# #
# # def assess_sharpness(image):
# #     # Convert the image to grayscale
# #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# #
# #     # Calculate image sharpness using Laplacian method
# #     sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
# #
# #     # Normalize sharpness to a scale of 0-100 (higher is sharper)
# #     sharpness_percentage = min(sharpness, 100) / 100 * 100
# #     return sharpness_percentage
# #
# #
# # def assess_contrast(image):
# #     # Calculate image contrast
# #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# #     hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
# #     contrast = cv2.compareHist(hist, hist, cv2.HISTCMP_BHATTACHARYYA)
# #
# #     # Normalize contrast to a scale of 0-100 (higher is better)
# #     contrast_percentage = (1 - min(contrast, 1)) * 100
# #     return contrast_percentage
# #
# #
# # def assess_image_quality(image_path):
# #     try:
# #         # Open the image using OpenCV
# #         img = cv2.imread(image_path)
# #
# #         # Assess image quality based on different factors
# #         dimensions_score = assess_dimensions(img)
# #         sharpness_score = assess_sharpness(img)
# #         contrast_score = assess_contrast(img)
# #         visibility_score = assess_visibility(img)
# #
# #         # Combine the scores to get an overall quality score (simple average here)
# #         overall_score = (dimensions_score + sharpness_score + contrast_score + visibility_score) / 4
# #
# #         print(f"The overall image quality score is approximately {overall_score:.2f}%")
# #
# #     except Exception as e:
# #         print(f"Error: {e}")
# #
# #
# # def assess_visibility(image):
# #     # Convert the image to grayscale
# #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# #
# #     # Calculate average luminance/brightness of the image
# #     visibility_score = cv2.mean(gray)[0]  # Average pixel value
# #
# #     # Normalize visibility to a scale of 0-100 (higher is better)
# #     visibility_percentage = (visibility_score / 255) * 100
# #     return visibility_percentage
# #
# #
# # def assess_pdf_quality(pdf_path):
# #     overall_sharpness = 0
# #     overall_contrast = 0
# #     overall_visibility = 0
# #     try:
# #         pdf_document = fitz.open(pdf_path)
# #
# #         sharpness_scores = []
# #         contrast_scores = []
# #         visibility_scores = []
# #         total_pages = pdf_document.page_count
# #
# #         for page_num in range(total_pages):
# #             # Extract each page as an image
# #             page = pdf_document.load_page(page_num)
# #             pix = page.get_pixmap()
# #             img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
# #
# #             # Assess image quality for each page
# #             sharpness_scores.append(assess_sharpness(img))
# #             contrast_scores.append(assess_contrast(img))
# #             visibility_scores.append(assess_visibility(img))
# #
# #         # Calculate overall scores as averages across all pages
# #         overall_sharpness = sum(sharpness_scores) / total_pages
# #         overall_contrast = sum(contrast_scores) / total_pages
# #         overall_visibility = sum(visibility_scores) / total_pages
# #
# #         print(f"Overall Sharpness Score: {overall_sharpness:.2f}")
# #         print(f"Overall Contrast Score: {overall_contrast:.2f}")
# #         print(f"Overall Visibility Score: {overall_visibility:.2f}")
# #         return overall_sharpness, overall_contrast, overall_visibility
# #     except Exception as e:
# #         print(f"Error: {e}")
# #         return overall_sharpness, overall_contrast, overall_visibility
# #
# #
# # def get_top_colors_call_(image_paths, num_colors=5):
# #     top_colors_list = []
# #
# #     for image_path in image_paths:
# #         # Read the image using OpenCV
# #         image = cv2.imread(image_path)
# #
# #         # Convert the image from BGR to RGB (OpenCV reads in BGR format)
# #         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# #
# #         # Flatten the image to a 2D array of pixels
# #         pixels = image.reshape((-1, 3))
# #
# #         # Convert to float32 for k-means clustering
# #         pixels = np.float32(pixels)
# #
# #         # Define criteria for k-means
# #         criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.2)
# #
# #         # Perform k-means clustering
# #         _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
# #
# #         # Convert centers to uint8
# #         centers = np.uint8(centers)
# #
# #         # Get the counts of labels to find the most common colors
# #         label_counts = Counter(labels.flatten())
# #
# #         # Sort the colors by frequency and get the top colors
# #         top_colors = [centers[i] for i, _ in label_counts.most_common(num_colors)]
# #
# #         top_colors_list.append(top_colors)
# #
# #     return top_colors_list
# #
# #
# # def get_top_colors(file_path_):
# #     import os
# #     image_paths = []
# #     len_to_process_ = 1
# #     for filename in os.listdir(file_path_):
# #         if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
# #             image_path = os.path.join(file_path_, filename)
# #             image_paths.append(image_path)
# #             if len_to_process_ == 5:
# #                 break
# #             len_to_process_ += 1
# #     top_colors_list = get_top_colors_call_(image_paths, 5)
# #     top_colors_list = [[color.tolist() for color in colors] for colors in top_colors_list]
# #     return top_colors_list
# #
# # # # Provide the path to your image
# # # image_path = '/Users/sandeepkumarrudhravaram/UNTMastersProjects/pdf_analyzer_prodv1/pdf_docs/Team16_Sprint3.pdf'  # Change this to your image's path
# # # assess_pdf_quality(image_path)
#
# # import os
# #
# # def get_image_file_size_mb(image_path):
# #     try:
# #         if os.path.exists(image_path):
# #             file_size_bytes = os.path.getsize(image_path)
# #             file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
# #             return file_size_mb
# #         else:
# #             print("File not found")
# #             return None
# #     except Exception as e:
# #         print(f"Error: {e}")
# #         return None
# #
# # # Usage
# # image_path = "/Users/sandeepkumarrudhravaram/UNTMastersProjects/pdf_analyzer_prodv1/pdfimages/0212202300521495212/3_1_.png"  # Replace with the path to your image
# # size_mb = get_image_file_size_mb(image_path)
# # if size_mb is not None:
# #     print(f"Image file size: {size_mb:.2f} MB")
#
# import threading
#
# def your_function():
#     # Your code here
#     # Replace this sleep with the code you want to measure
#     import time
#     time.sleep(40)  # Simulating a function that takes more than 30 seconds
#     # Replace this sleep with the code you want to measure
#
# def function_with_timeout():
#     def run_function():
#         your_function()
#
#     thread = threading.Thread(target=run_function)
#     thread.start()
#     thread.join(timeout=30)  # Set the timeout to 30 seconds
#
#     if thread.is_alive():
#         # Function took longer than 30 seconds, so skip
#         print("Function took too long, skipping...")
#         return None
#     else:
#         # Function completed within the time limit
#         return "Function executed successfully"
#
# # Usage
# result = function_with_timeout()
# if result is not None:
#     print(result)
#


#
