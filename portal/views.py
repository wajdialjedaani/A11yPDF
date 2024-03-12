import io
import json
import os
from concurrent.futures import ThreadPoolExecutor
from fitz import fitz
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, make_response, \
    Response, jsonify
import threading
from . import APP, LOG
from werkzeug.utils import secure_filename
from .packages import get_final_result, extract_headers, extract_foter, get_tables_count, \
    get_image_resolution_aspect_ratio, assess_pdf_quality, get_top_colors, analyze_figure_captions, get_tables_count
import pandas as pd
from .packages.image_caption_analysis import analyze_figure_captions_parallel
from .packages.contast_ratio_ import analyze_pdf, check_page_number
from .packages.extract_and_summarize import *
from .packages.colorblind import *
import time
import random
import string
from datetime import datetime, date
import shutil
import PyPDF2
import re
from .packages.table_caption import *
from .packages.dylexia import *

bp = Blueprint('view', __name__, url_prefix='/PDFAnalyzerX', template_folder="./templates", static_folder="./static")


@bp.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("upload_file.html")


@bp.route('/dashboard/', methods=["GET", "POST"])
def dashboard():
    if request.method == "GET":
        return render_template("index.html")


@bp.route('/get_random_numbers/', methods=["GET", "POST"])
def get_random_numbers(string_length=5):
    random_numbers = ''.join(random.choice(string.digits) for x in range(string_length))
    random_numbers = datetime.now().strftime("%d%m%Y%H%M%S") + random_numbers
    return jsonify({"random_numbers": random_numbers})


def remove_file_after_wait(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


@bp.route("/api_upload_pdf", methods=["GET", 'POST'])
def api_upload_bill():
    if request.method == "POST":
        pdf_docs = APP.config["PDF_DIR"]
        try:
            if 'pdf_file' not in request.files:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "pdf_file is request"})
                resp.status_code = 400
                return resp
            file = request.files['pdf_file']
            if file.filename == '':
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "no pdf selected for uploading"})
                resp.status_code = 400
                return resp
            filename = secure_filename(file.filename)
            if ".pdf" not in filename.lower():
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "please check the file format"})
                resp.status_code = 400
                return resp
            if os.path.exists(os.path.join(pdf_docs)):
                file.save(os.path.join(pdf_docs, filename))
                count_urls_, count_images_, dict_final_, pdf_document_page_count = get_final_result(
                    os.path.join(pdf_docs, filename))
                resp = {"success": True,
                        "data": {"pdf name": str(filename),
                                 "no of images in pdf": str(count_images_),
                                 "no of urls": str(count_urls_),
                                 "no of pages in pdf": str(pdf_document_page_count),
                                 "font": dict_final_},
                        "errors": "None"}
                return resp

            else:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "pdf file directory is not created"})
                resp.status_code = 400
                return resp
        except Exception as e:
            LOG.error(e, exc_info=True)
            resp = jsonify({"success": False,
                            "data": {"pdf name": "None"},
                            "errors": "Something went wrong"})
            resp.status_code = 400
            return resp


# @bp.route("/upload_pdf/<string:process_id>", methods=["GET", 'POST'])
# def upload_bill(process_id):
#     if request.method == "POST":
#         pdf_docs = APP.config["PDF_DIR"]
#         print('PDF_DIR', pdf_docs)
#         pdf_docs_json = APP.config["PDF_RESULT_JSON"]
#         images_path_of_pdf = APP.config["PDF_IMAGES_PDF"]
#         print('pdf_docs_json', pdf_docs_json)
#
#         if not os.path.exists(os.path.join(pdf_docs, process_id)):
#             os.mkdir(os.path.join(pdf_docs, process_id))
#         try:
#             if 'pdf_file' not in request.files:
#                 resp = jsonify({"success": False,
#                                 "data": {"pdf name": "None"},
#                                 "errors": "pdf_file is request"})
#                 resp.status_code = 400
#                 return resp
#             file = request.files['pdf_file']
#             if file.filename == '':
#                 resp = jsonify({"success": False,
#                                 "data": {"pdf name": "None"},
#                                 "errors": "no pdf selected for uploading"})
#                 resp.status_code = 400
#                 return resp
#             filename = secure_filename(file.filename)
#             if ".pdf" not in filename.lower():
#                 resp = jsonify({"success": False,
#                                 "data": {"pdf name": "None"},
#                                 "errors": "please check the file format"})
#                 resp.status_code = 400
#                 return resp
#             if os.path.exists(os.path.join(pdf_docs, process_id)):
#                 file.save(os.path.join(pdf_docs, process_id, filename))
#                 count_urls_, count_images_, dict_final_, pdf_document_page_count = get_final_result(
#                     os.path.join(pdf_docs, process_id, filename), process_id)
#                 percentage_with_caption_table, percentage_without_caption_table, captions_with_tables = analyze_table_caption(
#                     os.path.join(pdf_docs, process_id, filename))
#
#                 titles, No_headers_Pages, yes_headers_pages, percentage_with_headers, percentage_without_headers = extract_headers(
#                     os.path.join(pdf_docs, process_id, filename))
#
#                 titles_for_footers_, count_of_footers_ = extract_foter(os.path.join(pdf_docs, process_id, filename))
#                 table_count_ = get_tables_count(os.path.join(pdf_docs, process_id, filename))
#
#                 image_info_dict, final_list_of_rsa = get_image_resolution_aspect_ratio(
#                     os.path.join(images_path_of_pdf, process_id))
#
#                 overall_sharpness, overall_contrast, overall_visibility = assess_pdf_quality(
#                     os.path.join(pdf_docs, process_id, filename))
#                 # overall_sharpness, overall_contrast, overall_visibility=0,0,0
#                 final_dic_for_access_ = [
#                     [round(overall_sharpness, 2), round(overall_visibility, 2), round(overall_contrast)]]
#
#                 # top_colors_list = get_top_colors(os.path.join(images_path_of_pdf, process_id))
#                 top_colors_list = []
#                 font_size_dict_ = {}
#                 font_type_dict_ = {}
#                 count_ = 0
#
#                 count_urls_final_ = count_urls_['count_urls_']
#                 no_of_work = {'Number Of Urls Accessible': round(count_urls_['yes_count_']),
#                               "Number Of Not Urls Accessible": round(count_urls_['no_count_'])}
#
#                 percentage_with_captions, percentage_without_captions, captions_with_images = analyze_figure_captions(
#                     os.path.join(pdf_docs, process_id, filename))
#                 meets_wcag_count, does_not_meet_wcag_count, meets_wcag_percentage, does_not_meet_wcag_percentage, meets_wcag_pages, does_not_meet_wcag_pages = analyze_pdf(
#                     os.path.join(pdf_docs, process_id, filename))
#                 meets_wcag_count, does_not_meet_wcag_count, meets_wcag_percentage, does_not_meet_wcag_percentage = meets_wcag_count, does_not_meet_wcag_count, round(
#                     meets_wcag_percentage, 2), round(does_not_meet_wcag_percentage, 2)
#
#                 final_json_ = {"count_urls_": count_urls_final_, "dict_final_": dict_final_,
#                                "count_images_": count_images_,
#                                "pdf_document_page_count": pdf_document_page_count, "no_of_work": no_of_work,
#                                "titles": titles, "No_headers_Pages": No_headers_Pages,
#                                "yes_headers_pages": yes_headers_pages,
#                                "percentage_with_headers": percentage_with_headers,
#                                "percentage_without_headers": percentage_without_headers,
#                                "titles_for_footers_": titles_for_footers_, "count_of_footers_": count_of_footers_,
#                                "table_count_": table_count_,
#                                "final_list_of_rsa": final_list_of_rsa,
#                                "image_info_dict": image_info_dict, "final_dic_for_access_": final_dic_for_access_,
#                                "percentage_with_captions": percentage_with_captions,
#                                "percentage_without_captions": percentage_without_captions,
#                                "captions_with_images": captions_with_images, "meets_wcag_count": meets_wcag_count,
#                                "does_not_meet_wcag_count": does_not_meet_wcag_count,
#                                "meets_wcag_percentage": meets_wcag_percentage,
#                                "does_not_meet_wcag_percentage": does_not_meet_wcag_percentage,
#                                "meets_wcag_pages": meets_wcag_pages,
#                                "does_not_meet_wcag_pages": does_not_meet_wcag_pages,
#                                "percentage_with_caption_table": percentage_with_caption_table,
#                                "percentage_without_caption_table": percentage_without_caption_table,
#                                "captions_with_tables": captions_with_tables}
#
#                 fina_header_count_ = [[percentage_with_headers, yes_headers_pages],
#                                       [percentage_without_headers, No_headers_Pages]]
#
#                 if not os.path.exists(os.path.join(pdf_docs_json, process_id)):
#                     os.mkdir(os.path.join(pdf_docs_json, process_id))
#                 with open(os.path.join(pdf_docs_json, process_id, "result.json"), "w") as file:
#                     json.dump(final_json_, file)
#                     file.close()
#                 with open(os.path.join(pdf_docs_json, process_id, "result_imagescolor.json"), "w") as file:
#                     json.dump(top_colors_list, file)
#                     file.close()
#                 for i in dict_final_:
#                     for j in dict_final_[i]:
#                         for k in dict_final_[i][j]:
#                             # print(dict_final_[i][j][k]['font_line'])
#                             if str(dict_final_[i][j][k]['font_line']).strip() == '' or dict_final_[i][j][k][
#                                 'font_line'] == '':
#                                 pass
#                             else:
#                                 count_ = count_ + 1
#                                 for fnt in dict_final_[i][j][k]['font_font_type']:
#                                     font_ = fnt
#                                     font_type_dict_[font_] = font_type_dict_.get(font_, 0) + 1
#
#                                 for fntsz in dict_final_[i][j][k]['font_sizes']:
#                                     font_size = fntsz
#                                     font_size_dict_[font_size] = font_size_dict_.get(font_size, 0) + 1
#
#                 top_4_fonts_types = dict(sorted(font_type_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
#                 total_counts_types = sum(font_type_dict_.values())
#                 # print('total_counts_types', total_counts_types)
#                 # print('count',top_4_fonts_types)
#                 # exit()
#                 percentage_dict_types = {font: round((count / total_counts_types) * 100, 2) for font, count in
#                                          top_4_fonts_types.items()}
#                 length_of_percentage_dict_types = len(percentage_dict_types)
#                 # for font, percentage in percentage_dict_types.items():
#                 #     print("Percentage of {} compared to all fonts: {:.2f}%".format(font, percentage))
#
#                 top_4_font_size_ = dict(sorted(font_size_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
#                 total_counts_size = sum(font_size_dict_.values())
#
#                 sum_greater_than_16 = sum(value for key, value in font_size_dict_.items() if float(key) >= 14)
#                 percentage_greater_than_16 = round((sum_greater_than_16 / total_counts_size) * 100, 2)
#
#                 sum_less_than_16 = sum(value for key, value in font_size_dict_.items() if float(key) < 14)
#                 percentage_less_than_16 = round((sum_less_than_16 / total_counts_size) * 100, 2)
#
#                 print('percentage_greater_than_16', percentage_greater_than_16)
#                 print('percentage_less_than_16', percentage_less_than_16)
#
#                 percentage_dict_size = {font: round((count / total_counts_size) * 100, 2) for font, count in
#                                         top_4_font_size_.items()}
#                 length_of_percentage_dict_size = len(percentage_dict_size)
#
#                 # for size, percentage in percentage_dict_size.items():
#                 #     print("Percentage of {} compared to all sizes: {:.2f}%".format(size, percentage))
#
#                 # resp = {"success": True,
#                 #         "data": {"pdf name": str(filename),
#                 #                  "no of images in pdf": str(count_images_),
#                 #                  "no of urls": str(count_urls_),
#                 #                  "no of pages in pdf": str(pdf_document_page_count),
#                 #                  "font": dict_final_},
#                 #         "errors": "None"}
#                 # return resp
#                 print('top_4_font_size_', top_4_font_size_)
#                 print('percentage_dict_size', percentage_dict_size)
#                 print('fina_header_count_', fina_header_count_)
#                 print('fina_header_count_', fina_header_count_, "count_of_footers_", count_of_footers_)
#
#                 print('final_dic_for_access_', final_dic_for_access_)
#
#                 pass_percentages = [fina_header_count_[0][0], count_of_footers_[0][0]]
#                 fail_percentages = [fina_header_count_[1][0], count_of_footers_[1][0]]
#
#                 overall_pass_average = round(sum(pass_percentages) / len(pass_percentages), 2)
#                 overall_fail_average = round(sum(fail_percentages) / len(fail_percentages), 2)
#
#                 item_path = os.path.join(images_path_of_pdf, process_id)
#                 if os.path.isdir(item_path):
#                     shutil.rmtree(item_path)
#
#                 print('top_colors_list', top_colors_list)
#                 return render_template("index.html", top_4_font_size_=top_4_font_size_,
#                                        top_4_fonts_types=top_4_fonts_types, total_counts_size=total_counts_size,
#                                        total_counts_types=total_counts_types, count_urls_=count_urls_final_,
#                                        count_images_=count_images_, pdf_document_page_count=pdf_document_page_count,
#                                        percentage_dict_types=percentage_dict_types,
#                                        percentage_dict_size=percentage_dict_size,
#                                        length_of_percentage_dict_types=length_of_percentage_dict_types,
#                                        length_of_percentage_dict_size=length_of_percentage_dict_size,
#                                        count_=count_, no_of_work=no_of_work, titles_for_headers=titles,
#                                        fina_header_count_=fina_header_count_, count_of_footers_=count_of_footers_,
#                                        table_count_=table_count_, final_list_of_rsa=final_list_of_rsa,
#                                        final_dic_for_access_=final_dic_for_access_, top_colors_list=top_colors_list,
#                                        percentage_greater_than_16=percentage_greater_than_16
#                                        , percentage_less_than_16=percentage_less_than_16,
#                                        overall_pass_average=overall_pass_average,
#                                        overall_fail_average=overall_fail_average,
#                                        percentage_with_captions=round(percentage_with_captions, 2),
#                                        percentage_without_captions=round(percentage_without_captions, 2),
#                                        captions_with_images=captions_with_images, process_id=process_id,
#                                        meets_wcag_count=meets_wcag_count,
#                                        does_not_meet_wcag_count=does_not_meet_wcag_count,
#                                        meets_wcag_percentage=meets_wcag_percentage,
#                                        does_not_meet_wcag_percentage=does_not_meet_wcag_percentage,
#                                        percentage_with_caption_table=percentage_with_caption_table,
#                                        percentage_without_caption_table=percentage_without_caption_table,
#                                        captions_with_tables=captions_with_tables)
#             else:
#                 resp = jsonify({"success": False,
#                                 "data": {"pdf name": "None"},
#                                 "errors": "pdf file directory is not created"})
#                 resp.status_code = 400
#                 return resp
#         except Exception as e:
#             LOG.error(e, exc_info=True)
#             resp = jsonify({"success": False,
#                             "data": {"pdf name": "None"},
#                             "errors": "Something went wrong"})
#             resp.status_code = 400
#             return resp
#     if request.method == "GET":
#         pdf_docs_json = APP.config["PDF_RESULT_JSON"]
#         if os.path.exists(os.path.join(pdf_docs_json, process_id)):
#             if os.path.exists(os.path.join(pdf_docs_json, process_id, "result.json")):
#                 with open(os.path.join(pdf_docs_json, process_id, "result.json"), "r") as file:
#                     finl_dd = json.load(file)
#                     file.close()
#
#                 with open(os.path.join(pdf_docs_json, process_id, "result_imagescolor.json"), "r") as file:
#                     top_colors_list = json.load(file)
#                     file.close()
#
#                 count_urls_ = finl_dd['count_urls_']
#                 no_of_work = finl_dd['no_of_work']
#                 count_images_ = finl_dd['count_images_']
#                 dict_final_ = finl_dd['dict_final_']
#                 pdf_document_page_count = finl_dd['pdf_document_page_count']
#
#                 final_list_of_rsa = finl_dd['final_list_of_rsa']
#                 image_info_dict = finl_dd['image_info_dict']
#
#                 final_dic_for_access_ = finl_dd["final_dic_for_access_"]
#
#                 percentage_with_headers = finl_dd["percentage_with_headers"]
#                 percentage_without_headers = finl_dd["percentage_without_headers"]
#
#                 titles_for_footers_ = finl_dd["titles_for_footers_"]
#                 count_of_footers_ = finl_dd["count_of_footers_"]
#
#                 meets_wcag_count = finl_dd["meets_wcag_count"]
#                 does_not_meet_wcag_count = finl_dd["does_not_meet_wcag_count"]
#                 meets_wcag_percentage = finl_dd["meets_wcag_percentage"]
#                 does_not_meet_wcag_percentage = finl_dd["does_not_meet_wcag_percentage"]
#
#                 meets_wcag_pages = finl_dd["meets_wcag_pages"]
#                 does_not_meet_wcag_pages = finl_dd["does_not_meet_wcag_pages"]
#
#                 percentage_with_caption_table = finl_dd["percentage_with_caption_table"]
#                 percentage_without_caption_table = finl_dd["percentage_without_caption_table"]
#                 captions_with_tables = finl_dd["captions_with_tables"]
#
#                 titles = finl_dd["titles"]
#                 No_headers_Pages = finl_dd["No_headers_Pages"]
#                 yes_headers_pages = finl_dd["yes_headers_pages"]
#                 table_count_ = finl_dd["table_count_"]
#                 percentage_with_captions, percentage_without_captions, captions_with_images = finl_dd[
#                                                                                                   "percentage_with_captions"], \
#                                                                                               finl_dd[
#                                                                                                   "percentage_without_captions"], \
#                                                                                               finl_dd[
#                                                                                                   "captions_with_images"]
#
#                 fina_header_count_ = [[percentage_with_headers, yes_headers_pages],
#                                       [percentage_without_headers, No_headers_Pages]]
#
#                 font_size_dict_ = {}
#                 font_type_dict_ = {}
#                 count_ = 0
#                 final_json_ = {"count_urls_": count_urls_, "dict_final_": dict_final_, "count_images_": count_images_,
#                                "pdf_document_page_count": pdf_document_page_count, "no_of_work": no_of_work,
#                                "titles": titles, "No_headers_Pages": No_headers_Pages,
#                                "yes_headers_pages": yes_headers_pages,
#                                "percentage_with_headers": percentage_with_headers,
#                                "percentage_without_headers": percentage_without_headers,
#                                "titles_for_footers_": titles_for_footers_, "count_of_footers_": count_of_footers_,
#                                "table_count_": table_count_
#                     , "final_list_of_rsa": final_list_of_rsa,
#                                "image_info_dict": image_info_dict, "final_dic_for_access_": final_dic_for_access_,
#                                "top_colors_list": top_colors_list, "percentage_with_captions": percentage_with_captions,
#                                "percentage_without_captions": percentage_without_captions,
#                                "captions_with_images": captions_with_images
#                     , "meets_wcag_count": meets_wcag_count, "does_not_meet_wcag_count": does_not_meet_wcag_count,
#                                "meets_wcag_percentage": meets_wcag_percentage,
#                                "does_not_meet_wcag_percentage": does_not_meet_wcag_percentage,
#                                "meets_wcag_pages": meets_wcag_pages,
#                                "does_not_meet_wcag_pages": does_not_meet_wcag_pages,
#                                "percentage_with_caption_table": percentage_with_caption_table,
#                                "percentage_without_caption_table": percentage_without_caption_table,
#                                "captions_with_tables": captions_with_tables
#                                }
#                 pdf_docs_json = APP.config["PDF_RESULT_JSON"]
#                 if not os.path.exists(os.path.join(pdf_docs_json, process_id)):
#                     os.mkdir(os.path.join(pdf_docs_json, process_id))
#                 with open(os.path.join(pdf_docs_json, process_id, "result.json"), "w") as file:
#                     json.dump(final_json_, file)
#                     file.close()
#                 for i in dict_final_:
#                     for j in dict_final_[i]:
#                         for k in dict_final_[i][j]:
#                             # print(dict_final_[i][j][k]['font_line'])
#                             if str(dict_final_[i][j][k]['font_line']).strip() == '' or dict_final_[i][j][k][
#                                 'font_line'] == '':
#                                 pass
#                             else:
#                                 count_ = count_ + 1
#                                 for fnt in dict_final_[i][j][k]['font_font_type']:
#                                     font_ = fnt
#                                     font_type_dict_[font_] = font_type_dict_.get(font_, 0) + 1
#
#                                 for fntsz in dict_final_[i][j][k]['font_sizes']:
#                                     font_size = fntsz
#                                     font_size_dict_[font_size] = font_size_dict_.get(font_size, 0) + 1
#                 top_4_fonts_types = dict(sorted(font_type_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
#                 total_counts_types = sum(font_type_dict_.values())
#                 # print('total_counts_types', total_counts_types)
#                 # exit()
#                 percentage_dict_types = {font: round((count / total_counts_types) * 100, 2) for font, count in
#                                          top_4_fonts_types.items()}
#                 length_of_percentage_dict_types = len(percentage_dict_types)
#
#                 top_4_font_size_ = dict(sorted(font_size_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
#                 total_counts_size = sum(font_size_dict_.values())
#
#                 sum_greater_than_16 = sum(value for key, value in font_size_dict_.items() if float(key) >= 14)
#                 percentage_greater_than_16 = round((sum_greater_than_16 / total_counts_size) * 100, 2)
#
#                 sum_less_than_16 = sum(value for key, value in font_size_dict_.items() if float(key) < 14)
#                 percentage_less_than_16 = round((sum_less_than_16 / total_counts_size) * 100, 2)
#
#                 percentage_dict_size = {font: round((count / total_counts_size) * 100, 2) for font, count in
#                                         top_4_font_size_.items()}
#                 length_of_percentage_dict_size = len(percentage_dict_size)
#
#                 print('fina_header_count_', fina_header_count_)
#
#                 pass_percentages = [fina_header_count_[0][0], count_of_footers_[0][0]]
#                 fail_percentages = [fina_header_count_[1][0], count_of_footers_[1][0]]
#
#                 overall_pass_average = round(sum(pass_percentages) / len(pass_percentages), 2)
#                 overall_fail_average = round(sum(fail_percentages) / len(fail_percentages), 2)
#
#                 print('overall_pass_average', overall_pass_average)
#                 print('overall_fail_average', overall_fail_average)
#                 return render_template("index.html", top_4_font_size_=top_4_font_size_,
#                                        top_4_fonts_types=top_4_fonts_types, total_counts_size=total_counts_size,
#                                        total_counts_types=total_counts_types, count_urls_=count_urls_,
#                                        count_images_=count_images_, pdf_document_page_count=pdf_document_page_count,
#                                        percentage_dict_types=percentage_dict_types,
#                                        percentage_dict_size=percentage_dict_size,
#                                        length_of_percentage_dict_types=length_of_percentage_dict_types,
#                                        length_of_percentage_dict_size=length_of_percentage_dict_size,
#                                        count_=count_, no_of_work=no_of_work, titles_for_headers=titles,
#                                        fina_header_count_=fina_header_count_, count_of_footers_=count_of_footers_,
#                                        table_count_=table_count_, final_list_of_rsa=final_list_of_rsa,
#                                        final_dic_for_access_=final_dic_for_access_, top_colors_list=top_colors_list,
#                                        percentage_greater_than_16=percentage_greater_than_16,
#                                        percentage_less_than_16=percentage_less_than_16,
#                                        overall_pass_average=overall_pass_average,
#                                        overall_fail_average=overall_fail_average,
#                                        percentage_with_captions=round(percentage_with_captions, 2),
#                                        percentage_without_captions=round(percentage_without_captions, 2),
#                                        captions_with_images=captions_with_images, process_id=process_id,
#                                        meets_wcag_count=meets_wcag_count,
#                                        does_not_meet_wcag_count=does_not_meet_wcag_count,
#                                        meets_wcag_percentage=meets_wcag_percentage,
#                                        does_not_meet_wcag_percentage=does_not_meet_wcag_percentage
#                                        , percentage_with_caption_table=percentage_with_caption_table,
#                                        percentage_without_caption_table=percentage_without_caption_table,
#                                        captions_with_tables=captions_with_tables)
#             else:
#                 resp = jsonify({"success": False,
#                                 "data": {"pdf name": "None"},
#                                 "errors": "Result Not Found"})
#                 resp.status_code = 400
#                 return resp
#         else:
#             resp = jsonify({"success": False,
#                             "data": {"pdf name": "None"},
#                             "errors": "Data Is Not Available"})
#             resp.status_code = 400
#             return resp


@bp.route('/pdf_viewer', methods=["GET", "POST"])
def pdf_viewer():
    if request.method == "GET":
        return render_template('pdfViewer.html')


@bp.route('/highlight_pdf', methods=['POST'])
def highlight_pdf():
    print('asdafdad')

    file_name = request.json['fileName']
    # Get size data from the request
    size = request.json['size']
    data = request.get_json()

    # Provide the path to your PDF file
    root_ = APP.config["ROOT_DIR"]
    pdf_file_path = os.path.join(root_, "portal", "static", "tmp", file_name)
    # os.path.join(pdf_docs, process_id)
    # pdf_file_path = "../static/tmp/{file_name}"
    print('pdf_file_path', pdf_file_path)

    result = extract_text_by_font_size(pdf_file_path, size)

    print('result', result)
    return jsonify({'status': 'success'})


def extract_text_by_font_size(pdf_path, target_font_size):
    doc = fitz.open(pdf_path)
    text_with_target_size = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        blocks = page.get_text("blocks")

        for block in blocks:
            for line in block:
                font_size = line[0]['size']
                text = line[4]

                if font_size == target_font_size:
                    text_with_target_size.append(text)

    doc.close()
    return text_with_target_size


@bp.route('/preview', methods=['GET'])
def preview():
    print('abcdefgh')
    chart_type = request.args.get('chartType', 'bar')  # Default to 'bar' if not provided
    chart_data = request.args.get('chartData', '{}')
    print('chart_data', chart_data)
    return render_template('pdfViewer.html', chart_type=chart_type, chart_data=chart_data)


def split_filename(filename):
    parts = filename.split('_')
    return parts[0], parts[1]


@bp.route('/generate_report/<string:process_id>', methods=["GET", "POST"])
def generate_report(process_id):
    pdf_docs_json = APP.config["PDF_RESULT_JSON"]
    finl_dd = {}
    filepath = os.path.join(pdf_docs_json, process_id, "Report_" + str(process_id) + ".xlsx")
    try:
        if os.path.exists(os.path.join(pdf_docs_json, process_id)):
            if os.path.exists(filepath):
                file_name1 = "Report_" + str(process_id) + ".xlsx"
                try:
                    return send_file(filepath, download_name=file_name1, as_attachment=True)
                except:
                    return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        excel_file = filepath
        if os.path.exists(os.path.join(pdf_docs_json, process_id)):
            if os.path.exists(os.path.join(pdf_docs_json, process_id, "result.json")):
                with open(os.path.join(pdf_docs_json, process_id, "result.json"), "r") as file:
                    finl_dd = json.load(file)
                    file.close()
                print('finl_dd', finl_dd)
                rows = []
                data = finl_dd['dict_final_']
                for page, contents in data.items():
                    for section, content in contents.items():
                        for _, text_data in content.items():
                            if text_data:
                                try:
                                    row = {
                                        "Page": page,
                                        "Section": section,
                                        "Font Line": text_data.get("font_line", ""),
                                        "Font Type": ", ".join(text_data.get("font_font_type", [])),
                                        "Font Sizes": ", ".join(text_data.get("font_sizes", []))
                                    }
                                except:
                                    row = {}
                                    pass
                                rows.append(row)

                # Create DataFrame
                df = pd.DataFrame(rows)

                # Write to Excel file

                df.to_excel(excel_file, sheet_name="Fonts Analysis", index=False)

                image_data = finl_dd['captions_with_images']

                # Create a DataFrame from the new JSON data
                image_rows = []
                for item in image_data:
                    try:
                        row = {
                            "Caption Text": item.get("caption_text", ""),
                            "Image Index": item.get("image_info", {}).get("image_index", ""),
                            "Page Number": item.get("page_number", "")
                        }
                    except:
                        row = {}
                        pass
                    image_rows.append(row)

                image_df = pd.DataFrame(image_rows)
                with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
                    image_df.to_excel(writer, sheet_name='Caption Analysis', index=False)

                # image_details_data = finl_dd['image_info_dict']
                #
                # # Create a DataFrame from the new JSON data
                # image_details_rows = []
                # for filename, details in image_details_data.items():
                #     page_number, image_number = split_filename(filename)
                #     try:
                #         image_details_rows.append({
                #             'Page Number': page_number,
                #             'Image Number': image_number,
                #             'Image Name': filename,
                #             'Aspect Ratio': details['aspect_ratio'],
                #             'Height': details['height'],
                #             'Width': details['width']
                #         })
                #     except:
                #         pass
                #
                # image_details_df = pd.DataFrame(image_details_rows)
                #
                # # Write to a new sheet in the existing Excel file
                # with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
                #     image_details_df.to_excel(writer, sheet_name='Image Analysis', index=False)
                pdf_titles_data = finl_dd['titles']
                pdf_footer_data = finl_dd['titles_for_footers_']
                additional_data = {
                    "Page with Headers Count": finl_dd["yes_headers_pages"],
                    "Page without Headers Count": finl_dd["No_headers_Pages"],
                    "No of Images in PDF": finl_dd["count_images_"],
                    "No of Urls in PDF": finl_dd["count_urls_"],
                    "No of Pages in PDF": finl_dd["pdf_document_page_count"],
                    "Images With Captions": finl_dd["percentage_with_captions"],
                    "Images Without Captions": finl_dd["percentage_without_captions"]
                }
                pdf_titles_rows = []
                for item in pdf_titles_data:
                    try:
                        row = {
                            "Page Number": item,
                            "Page Header": pdf_titles_data[item]
                        }
                    except:
                        row = {}
                        pass
                    pdf_titles_rows.append(row)

                image_df = pd.DataFrame(pdf_titles_rows)
                with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
                    image_df.to_excel(writer, sheet_name='Headers In Pdf', index=False)

                pdf_titles_rows = []
                for item in pdf_footer_data:
                    row = {
                        "Page Number": item,
                        "Page Footer": pdf_footer_data[item]
                    }
                    pdf_titles_rows.append(row)

                image_df = pd.DataFrame(pdf_titles_rows)
                df_additional_data = pd.DataFrame([additional_data])
                with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
                    image_df.to_excel(writer, sheet_name='Footers In Pdf', index=False)
                    df_additional_data.to_excel(writer, sheet_name='Additional Info', index=False)

                file_name1 = "Report_" + str(process_id) + ".xlsx"

                try:
                    return send_file(filepath, download_name=file_name1, as_attachment=True)
                except:
                    return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
    except Exception as e:
        resp = jsonify({"success": False,
                        "errors": "Something went wrong",
                        "e": str(e)})
        resp.status_code = 400
        return resp
    else:
        resp = jsonify({"success": False,
                        "errors": "Result Not Found"})
        resp.status_code = 400
        return resp


def calculate_overall_percentage(data):
    results = {}
    for key, values in data.items():
        # Summing all the values for the current key
        sum_values = sum(values)
        # Calculating the actual percentage and rounding it
        actual_percentage = round((sum_values / len(values)) * 100)
        # Calculating the remaining percentage and rounding it
        remaining_percentage = 100 - actual_percentage
        # Storing the result in the dictionary
        results[key] = {"Actual": actual_percentage, "Remaining": remaining_percentage}
    return results


def prepare_data_for_excel(combined_data):
    # Create a list of dictionaries, each representing a page and its analysis
    pages_data = []
    for i, page_number in enumerate(combined_data['page number']):
        page_data = {'page number': page_number}
        for analysis_type in combined_data:
            if analysis_type != 'page number':  # Exclude the 'page number' list
                # Ensure there is data for the current page; if not, append None or an appropriate placeholder
                page_data[analysis_type] = combined_data[analysis_type][i] if i < len(
                    combined_data[analysis_type]) else None
        pages_data.append(page_data)

    # Sort the list of dictionaries by 'page number'
    sorted_pages_data = sorted(pages_data, key=lambda x: x['page number'])

    return sorted_pages_data


def clean_string(s):
    # Remove non-printable characters
    printable = set(string.printable)
    clean = "".join(filter(lambda x: x in printable, s))
    # Replace any other known problematic characters here
    # For example, to replace '¼' with '1/4', uncomment the next line
    # clean = clean.replace('¼', '1/4')
    return clean


@bp.route('/generate_report/<string:type_>/<string:process_id>', methods=["GET", "POST"])
def generate_report_pdf(type_, process_id):
    pdf_docs_json = APP.config["PDF_RESULT_JSON"]
    finl_dd = {}
    filepath = os.path.join(pdf_docs_json, process_id, "Report_" + str(process_id) + "_" + str(type_) + ".xlsx")
    if os.path.exists(os.path.join(pdf_docs_json, process_id)):
        if os.path.exists(filepath):
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
    excel_file = filepath
    if os.path.exists(os.path.join(pdf_docs_json, process_id)):
        if os.path.exists(os.path.join(pdf_docs_json, process_id, "result.json")):
            with open(os.path.join(pdf_docs_json, process_id, "result.json"), "r") as file:
                finl_dd = json.load(file)
                file.close()
    if type_ == "fsa":
        try:
            rows = []
            data = finl_dd['dict_final_']
            for page, contents in data.items():
                for section, content in contents.items():
                    for _, text_data in content.items():
                        if text_data:
                            try:
                                row = {
                                    "Page": page,
                                    # "Section": section,
                                    "Font Line": clean_string(text_data.get("font_line", "")),
                                    "Font Type": ", ".join(text_data.get("font_font_type", [])),
                                    "Font Sizes": ", ".join(text_data.get("font_sizes", [])),
                                    "Accessible/Not Accessible":", ".join(text_data.get("font_size_Accessible_status", []))
                                }
                            except:
                                row = {
                                    "Page": page,
                                    # "Section": section,
                                    "Font Line": "",
                                    "Font Type": "",
                                    "Font Sizes": "",
                                    "Accessible/Not Accessible": "Not Accessible"
                                }
                                pass
                            rows.append(row)

            # Create DataFrame
            df = pd.DataFrame(rows)

            # Write to Excel file

            df.to_excel(excel_file, sheet_name="Fonts Analysis", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp
    elif type_ == "cwi":
        try:
            image_data = finl_dd['captions_with_images']
            # Create a DataFrame from the new JSON data
            image_rows = []
            for item in image_data:
                try:
                    row = {
                        "Caption Text": clean_string(item.get("caption_text", "")),
                        # "Image Index": item.get("image_info", {}).get("image_index", ""),
                        "Page Number": item.get("page_number", ""),
                        "image Index In Pdf":item.get("image Index In Pdf", ""),
                        "image Index In Page": item.get("image Index In Page", ""),
                        "Accessibility": item.get("Accessibility", "")
                    }
                except:
                    row = {}
                    pass
                image_rows.append(row)
            if not image_rows:
                image_rows.append({
                    "Caption Text":"No Data" ,
                        # "Image Index": item.get("image_info", {}).get("image_index", ""),
                        "Page Number": "No Data",
                        "image Index In Pdf":"No Data",
                        "image Index In Page": "No Data",
                        "Accessibility": "Not Accessible"
                })

            image_df = pd.DataFrame(image_rows)
            image_df.to_excel(excel_file, sheet_name="Fonts Analysis", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp
    elif type_ == "iid":
        try:
            image_details_data = finl_dd['image_info_dict']
            # Create a DataFrame from the new JSON data
            image_details_rows = []
            for filename, details in image_details_data.items():
                page_number, image_number = split_filename(filename)
                try:
                    image_details_rows.append({
                        'Page Number': page_number,
                        'Image Number': image_number,
                        'Image Name': filename,
                        'Aspect Ratio': details['aspect_ratio'],
                        'Height': details['height'],
                        'Width': details['width']
                    })
                except:
                    pass

            image_details_df = pd.DataFrame(image_details_rows)

            # Write to a new sheet in the existing Excel file
            with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
                image_details_df.to_excel(writer, sheet_name='Image Analysis', index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp
    elif type_ == "headers_analysis":
        try:
            #             image_details_data = finl_dd['image_info_dict":
            pdf_titles_data = finl_dd['titles']
            pdf_titles_rows = []
            for item in pdf_titles_data:
                try:
                    row = {
                        "Page Number": item,
                        "Page Header": clean_string(pdf_titles_data[item])
                    }
                except:
                    row = {}
                    pass
                pdf_titles_rows.append(row)

            image_df = pd.DataFrame(pdf_titles_rows)

            # with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            #     image_df.to_excel(writer, sheet_name='Headers In Pdf', index=False)
            # file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            # return send_file(filepath, download_name=file_name1, as_attachment=True)

            image_df.to_excel(excel_file, sheet_name="Headers In Pdf", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp
    elif type_ == "footers_analysis":
        try:
            pdf_footer_data = finl_dd['titles_for_footers_']
            pdf_titles_rows = []
            for item in pdf_footer_data:
                row = {
                    "Page Number": item,
                    "Page Footer": clean_string(pdf_footer_data[item])
                }
                pdf_titles_rows.append(row)

            image_df = pd.DataFrame(pdf_titles_rows)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"

            # with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            #     image_df.to_excel(writer, sheet_name='Footers In Pdf', index=False)
            # return send_file(filepath, download_name=file_name1, as_attachment=True)
            image_df.to_excel(excel_file, sheet_name="Footers In Pdf", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp
    elif type_ == "Additional_Info":
        try:
            additional_data = {
                "Page with Headers Count": finl_dd["yes_headers_pages"],
                "Page without Headers Count": finl_dd["No_headers_Pages"],
                "No of Images in PDF": finl_dd["count_images_"],
                "No of Urls in PDF": finl_dd["count_urls_"],
                "No of Pages in PDF": finl_dd["pdf_document_page_count"],
                "Images With Captions": finl_dd["percentage_with_captions"],
                "Images Without Captions": finl_dd["percentage_without_captions"]
            }
            df_additional_data = pd.DataFrame([additional_data])
            df_additional_data.to_excel(excel_file, sheet_name="Additional Info", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)

            # with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            #     df_additional_data.to_excel(writer, sheet_name='Additional Info', index=False)
            # return send_file(filepath, download_name=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp
        # except Exception as e:
        #     resp = jsonify({"success": False,
        #                     "errors": "Something went wrong",
        #                     "e": str(e)})
        #     resp.status_code = 400
        #     return resp

    elif type_ == "Page_Contrast":
        try:
            image_accessibility = finl_dd['image_accessibility']
            image_ratio_of_accessibility=finl_dd["image_ratio_of_accessibility"]
            # Create a DataFrame from the new JSON data
            image_rows = []
            for key, accessibility in image_accessibility.items():
                page_number, index = key.split('_')
                try:
                    row = {
                        "Page Number": page_number,
                        "Index": index,
                        "Ratio":image_ratio_of_accessibility[key],
                        "Accessible/Not": accessibility
                    }
                except:
                    row = {
                        "Page Number": page_number,
                        "Index": index,
                        "Ratio": "none",
                        "Accessible/Not": accessibility
                    }
                image_rows.append(row)
            if not image_rows:
                image_rows.append({
                    "Page Numbe": "No Data",
                    "Image Index": "No Data",
                    "Ratio":"none",
                    "Accessible/Not": "No Data"
                })
            image_df = pd.DataFrame(image_rows)
            image_df.to_excel(excel_file, sheet_name="Page Contrast", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp
    elif type_ == "Page_Numbers":
        try:
            image_page_number_accessibility = finl_dd['image_page_number_accessibility']
            # Create a DataFrame from the new JSON data
            image_rows = []
            for key, accessibility in image_page_number_accessibility.items():
                row = {
                    "Page Number": clean_string(key),
                    "Accessible/Not": accessibility
                }
                image_rows.append(row)
            if not image_rows:
                image_rows.append({
                    "Page Number": "No Data",
                    "Accessible/Not": "No Data"
                })
            image_df = pd.DataFrame(image_rows)
            image_df.to_excel(excel_file, sheet_name="Page Numbers", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp

    elif type_ == "color_blindness":
        try:
            combined_data_analyze_pdf_colorblind = finl_dd['combined_data_analyze_pdf_colorblind']
            combined_data_analyze_pdf_colorblind = prepare_data_for_excel(combined_data_analyze_pdf_colorblind)
            image_df = pd.DataFrame(combined_data_analyze_pdf_colorblind)
            image_df.to_excel(excel_file, sheet_name="Color Blindness", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp

    elif type_ == "urls":
        try:
            combined_data_analyze_pdf_colorblind = finl_dd['url_access_list']
            url_rows = []
            for index, (url, accessibility, page) in combined_data_analyze_pdf_colorblind.items():
                row = {
                    "Page Number": page,
                    "URL": url,
                    "Accessible/Not Accessible": accessibility
                }
                url_rows.append(row)

            # Creating a DataFrame from the list of dictionaries
            df_urls = pd.DataFrame(url_rows)
            df_urls.to_excel(excel_file, sheet_name="urls", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp

    elif type_ == "analyze_dylexia":
        try:
            #             image_details_data = finl_dd['image_info_dict":
            non_matching_fonts_analyze_dylexia = finl_dd['non_matching_fonts_analyze_dylexia']
            matching_fonts_analyze_dylexia = finl_dd['matching_fonts_analyze_dylexia']
            pdf_titles_rows = []
            for item in non_matching_fonts_analyze_dylexia:
                try:
                    row = {
                        "Font": item,
                        "Count": non_matching_fonts_analyze_dylexia[item],
                        "Accessible/Not": "Not Accessible"
                    }
                except:
                    row = {}
                    pass
                pdf_titles_rows.append(row)
            for item in matching_fonts_analyze_dylexia:
                try:
                    row = {
                        "Font": item,
                        "Count": matching_fonts_analyze_dylexia[item],
                        "Accessible/Not": "Accessible"
                    }
                except:
                    row = {}
                    pass
                pdf_titles_rows.append(row)

            image_df = pd.DataFrame(pdf_titles_rows)

            # with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            #     image_df.to_excel(writer, sheet_name='Headers In Pdf', index=False)
            # file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            # return send_file(filepath, download_name=file_name1, as_attachment=True)

            image_df.to_excel(excel_file, sheet_name="analyze dylexia", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp
    elif type_ == "table_dylexia":
        try:
            #             image_details_data = finl_dd['image_info_dict":
            non_matching_fonts_analyze_dylexia = finl_dd['captions_with_tables']

            image_df = pd.DataFrame(non_matching_fonts_analyze_dylexia)

            # with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            #     image_df.to_excel(writer, sheet_name='Headers In Pdf', index=False)
            # file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            # return send_file(filepath, download_name=file_name1, as_attachment=True)

            image_df.to_excel(excel_file, sheet_name="Table Caption", index=False)
            file_name1 = "Report_" + str(process_id) + "_" + str(type_) + ".xlsx"
            try:
                return send_file(filepath, download_name=file_name1, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=file_name1, as_attachment=True)
        except Exception as e:
            resp = jsonify({"success": False,
                            "errors": "Something went wrong",
                            "e": str(e)})
            resp.status_code = 400
            return resp

    else:
        resp = jsonify({"success": False,
                        "errors": "Result Not Found"})
        resp.status_code = 400
        return resp


@bp.route('/download/<string:filename>/<string:process_id>', methods=["GET", "POST"])
def generate_download(filename, process_id):
    pdf_docs = APP.config["PDF_DIR"]
    filepath = os.path.join(pdf_docs, process_id, filename)
    if os.path.exists(os.path.join(pdf_docs, process_id, filename)):
        if os.path.exists(filepath):
            try:
                return send_file(filepath, download_name=filename, as_attachment=True)
            except:
                return send_file(filepath, attachment_filename=filename, as_attachment=True)


@bp.route('/result/<string:process_id>/', methods=['GET', "POST"])
def final_result(process_id):
    if request.method == "POST":
        pdf_docs = APP.config["PDF_DIR"]
        print('PDF_DIR', pdf_docs)
        pdf_docs_json = APP.config["PDF_RESULT_JSON"]
        images_path_of_pdf = APP.config["PDF_IMAGES_PDF"]
        print('pdf_docs_json', pdf_docs_json)

        if not os.path.exists(os.path.join(pdf_docs, process_id)):
            os.mkdir(os.path.join(pdf_docs, process_id))
        try:
            if 'pdf_file' not in request.files:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "pdf_file is request"})
                resp.status_code = 400
                return resp
            file = request.files['pdf_file']
            if file.filename == '':
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "no pdf selected for uploading"})
                resp.status_code = 400
                return resp
            filename = secure_filename(file.filename)
            if ".pdf" not in filename.lower():
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "please check the file format"})
                resp.status_code = 400
                return resp
            if os.path.exists(os.path.join(pdf_docs, process_id)):
                file.save(os.path.join(pdf_docs, process_id, filename))
                start_time = time.time()
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(analyze_pdf_colorblind, os.path.join(pdf_docs, process_id, filename))
                    count_urls_, count_images_, dict_final_, pdf_document_page_count = get_final_result(
                        os.path.join(pdf_docs, process_id, filename), process_id)

                    percentage_with_caption_table, percentage_without_caption_table, captions_with_tables = analyze_table_caption(
                        os.path.join(pdf_docs, process_id, filename))

                    titles, No_headers_Pages, yes_headers_pages, percentage_with_headers, percentage_without_headers = extract_headers(
                        os.path.join(pdf_docs, process_id, filename))

                    titles_for_footers_, count_of_footers_ = extract_foter(os.path.join(pdf_docs, process_id, filename))
                    table_count_ = get_tables_count(os.path.join(pdf_docs, process_id, filename))

                    image_info_dict, final_list_of_rsa = {}, []
                    # image_info_dict, final_list_of_rsa = get_image_resolution_aspect_ratio(
                    #     os.path.join(images_path_of_pdf, process_id))

                    # overall_sharpness, overall_contrast, overall_visibility = assess_pdf_quality(
                    #     os.path.join(pdf_docs, process_id, filename))
                    # # overall_sharpness, overall_contrast, overall_visibility=0,0,0
                    # final_dic_for_access_ = [
                    #     [round(overall_sharpness, 2), round(overall_visibility, 2), round(overall_contrast)]]
                    final_dic_for_access_ = []

                    # top_colors_list = get_top_colors(os.path.join(images_path_of_pdf, process_id))
                    top_colors_list = []
                    font_size_dict_ = {}
                    font_type_dict_ = {}
                    count_ = 0

                    count_urls_final_ = count_urls_['count_urls_']
                    no_of_work = {'Number Of Urls Accessible': round(count_urls_['yes_count_']),
                                  "Number Of Not Urls Accessible": round(count_urls_['no_count_'])}
                    url_access_list = count_urls_['url_access_list']

                    percentage_with_captions, percentage_without_captions, captions_with_images = analyze_figure_captions_parallel(
                        os.path.join(pdf_docs, process_id, filename))
                    meets_wcag_count, does_not_meet_wcag_count, meets_wcag_percentage, does_not_meet_wcag_percentage, image_accessibility,image_ratio_of_accessibility = analyze_pdf(
                        os.path.join(pdf_docs, process_id, filename))
                    meets_wcag_count, does_not_meet_wcag_count, meets_wcag_percentage, does_not_meet_wcag_percentage = meets_wcag_count, does_not_meet_wcag_count, round(
                        meets_wcag_percentage), round(does_not_meet_wcag_percentage)
                    pages_with_page_number, pages_without_page_number, percentage_with_page_number, percentage_without_page_number, image_page_number_accessibility = check_page_number(
                        os.path.join(pdf_docs, process_id, filename))

                    full_text, summarized_text = extract_and_summarize_text(
                        os.path.join(pdf_docs, process_id, filename))

                    final_json_ = {"summarized_text": summarized_text, "pages_with_page_number": pages_with_page_number,
                                   "pages_without_page_number": pages_without_page_number,
                                   "percentage_without_page_number": percentage_without_page_number,
                                   "percentage_with_page_number": percentage_with_page_number,
                                   "count_urls_": count_urls_final_, "dict_final_": dict_final_,
                                   "count_images_": count_images_,
                                   "pdf_document_page_count": pdf_document_page_count, "no_of_work": no_of_work,
                                   "titles": titles, "No_headers_Pages": No_headers_Pages,
                                   "yes_headers_pages": yes_headers_pages,
                                   "percentage_with_headers": percentage_with_headers,
                                   "percentage_without_headers": percentage_without_headers,
                                   "titles_for_footers_": titles_for_footers_, "count_of_footers_": count_of_footers_,
                                   "table_count_": table_count_,
                                   "final_list_of_rsa": final_list_of_rsa,
                                   "image_info_dict": image_info_dict, "final_dic_for_access_": final_dic_for_access_,
                                   "percentage_with_captions": percentage_with_captions,
                                   "percentage_without_captions": percentage_without_captions,
                                   "captions_with_images": captions_with_images, "meets_wcag_count": meets_wcag_count,
                                   "does_not_meet_wcag_count": does_not_meet_wcag_count,
                                   "meets_wcag_percentage": meets_wcag_percentage,
                                   "does_not_meet_wcag_percentage": does_not_meet_wcag_percentage,
                                   "filename": filename,
                                   "image_accessibility": image_accessibility,
                                   "image_page_number_accessibility": image_page_number_accessibility,
                                   "url_access_list": url_access_list,
                                   "percentage_with_caption_table": percentage_with_caption_table,
                                   "percentage_without_caption_table": percentage_without_caption_table,
                                   "captions_with_tables": captions_with_tables,
                                   "image_ratio_of_accessibility":image_ratio_of_accessibility}

                    fina_header_count_ = [[round(percentage_with_headers), yes_headers_pages],
                                          [round(percentage_without_headers), No_headers_Pages]]

                    if not os.path.exists(os.path.join(pdf_docs_json, process_id)):
                        os.mkdir(os.path.join(pdf_docs_json, process_id))
                    with open(os.path.join(pdf_docs_json, process_id, "result_imagescolor.json"), "w") as file:
                        json.dump(top_colors_list, file)
                        file.close()
                    for i in dict_final_:
                        for j in dict_final_[i]:
                            for k in dict_final_[i][j]:
                                # print(dict_final_[i][j][k]['font_line'])
                                if str(dict_final_[i][j][k]['font_line']).strip() == '' or dict_final_[i][j][k]['font_line'] == '':
                                    pass
                                else:
                                    count_ = count_ + 1
                                    for fnt in dict_final_[i][j][k]['font_font_type']:
                                        font_ = fnt
                                        font_type_dict_[font_] = font_type_dict_.get(font_, 0) + 1

                                    for fntsz in dict_final_[i][j][k]['font_sizes']:
                                        font_size = fntsz
                                        font_size_dict_[font_size] = font_size_dict_.get(font_size, 0) + 1

                    top_4_fonts_types = dict(sorted(font_type_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
                    total_counts_types = sum(font_type_dict_.values())
                    # print('total_counts_types', total_counts_types)
                    # print('count',top_4_fonts_types)
                    # exit()
                    print('font_size_dict_',font_size_dict_)
                    percentage_dict_types = {font: round((count / total_counts_types) * 100) for font, count in
                                             top_4_fonts_types.items()}
                    length_of_percentage_dict_types = len(percentage_dict_types)
                    # for font, percentage in percentage_dict_types.items():
                    #     print("Percentage of {} compared to all fonts: {:.2f}%".format(font, percentage))

                    top_4_font_size_ = dict(sorted(font_size_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
                    total_counts_size = sum(font_size_dict_.values())

                    sum_greater_than_16 = sum(value for key, value in font_size_dict_.items() if float(key) >= 14)
                    percentage_greater_than_16 = round((sum_greater_than_16 / total_counts_size) * 100)

                    sum_less_than_16 = sum(value for key, value in font_size_dict_.items() if float(key) < 14)
                    percentage_less_than_16 = round((sum_less_than_16 / total_counts_size) * 100)

                    print('percentage_greater_than_16', percentage_greater_than_16)
                    print('percentage_less_than_16', percentage_less_than_16)

                    percentage_dict_size = {font: round((count / total_counts_size) * 100) for font, count in
                                            top_4_font_size_.items()}
                    length_of_percentage_dict_size = len(percentage_dict_size)

                    # for size, percentage in percentage_dict_size.items():
                    #     print("Percentage of {} compared to all sizes: {:.2f}%".format(size, percentage))

                    # resp = {"success": True,
                    #         "data": {"pdf name": str(filename),
                    #                  "no of images in pdf": str(count_images_),
                    #                  "no of urls": str(count_urls_),
                    #                  "no of pages in pdf": str(pdf_document_page_count),
                    #                  "font": dict_final_},
                    #         "errors": "None"}
                    # return resp
                    print('top_4_font_size_', top_4_font_size_)
                    print('percentage_dict_size', percentage_dict_size)
                    print('fina_header_count_', fina_header_count_)
                    print('fina_header_count_', fina_header_count_, "count_of_footers_", count_of_footers_)

                    print('final_dic_for_access_', final_dic_for_access_)

                    pass_percentages = [fina_header_count_[0][0], count_of_footers_[0][0]]
                    fail_percentages = [fina_header_count_[1][0], count_of_footers_[1][0]]

                    overall_pass_average = round(sum(pass_percentages) / len(pass_percentages))
                    overall_fail_average = round(sum(fail_percentages) / len(fail_percentages))

                    item_path = os.path.join(images_path_of_pdf, process_id)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)

                    print('top_colors_list', top_colors_list)
                    # return render_template("index.html", top_4_font_size_=top_4_font_size_,
                    #                        top_4_fonts_types=top_4_fonts_types, total_counts_size=total_counts_size,
                    #                        total_counts_types=total_counts_types, count_urls_=count_urls_final_,
                    #                        count_images_=count_images_, pdf_document_page_count=pdf_document_page_count,
                    #                        percentage_dict_types=percentage_dict_types,
                    #                        percentage_dict_size=percentage_dict_size,
                    #                        length_of_percentage_dict_types=length_of_percentage_dict_types,
                    #                        length_of_percentage_dict_size=length_of_percentage_dict_size,
                    #                        count_=count_, no_of_work=no_of_work, titles_for_headers=titles,
                    #                        fina_header_count_=fina_header_count_, count_of_footers_=count_of_footers_,
                    #                        table_count_=table_count_, final_list_of_rsa=final_list_of_rsa,
                    #                        final_dic_for_access_=final_dic_for_access_, top_colors_list=top_colors_list,
                    #                        percentage_greater_than_16=percentage_greater_than_16
                    #                        , percentage_less_than_16=percentage_less_than_16,
                    #                        overall_pass_average=overall_pass_average,
                    #                        overall_fail_average=overall_fail_average,
                    #                        percentage_with_captions=round(percentage_with_captions, 2),
                    #                        percentage_without_captions=round(percentage_without_captions, 2),
                    #                        captions_with_images=captions_with_images, process_id=process_id,
                    #                        meets_wcag_count=meets_wcag_count,
                    #                        does_not_meet_wcag_count=does_not_meet_wcag_count,
                    #                        meets_wcag_percentage=meets_wcag_percentage,
                    #                        does_not_meet_wcag_percentage=does_not_meet_wcag_percentage)
                    if count_urls_final_ == 0:
                        percentages = [round(percentage_with_captions, 1), round(percentage_with_captions, 1),
                                       round(fina_header_count_[0][0], 1), round(count_of_footers_[0][0], 1),
                                       round(meets_wcag_percentage, 1), round(percentage_with_page_number, 1)]
                    else:
                        try:
                            percentages = [round(percentage_with_captions, 1), round(percentage_with_captions, 1),
                                           round(fina_header_count_[0][0], 1), round(count_of_footers_[0][0], 1),
                                           round(meets_wcag_percentage, 1), round(percentage_with_page_number, 1),
                                           round(no_of_work['Number Of Urls Accessible'], 1)]
                        except:
                            percentages = [round(percentage_with_captions, 1), round(percentage_with_captions, 1),
                                           round(fina_header_count_[0][0], 1), round(count_of_footers_[0][0], 1),
                                           round(meets_wcag_percentage, 1), round(percentage_with_page_number, 1)]
                    overall_percentage = round(sum(percentages) / len(percentages), 1)
                    remaining_percentage = round(100 - overall_percentage, 1)

                    percentage_analyze_dylexia, matching_fonts_analyze_dylexia, non_matching_fonts_analyze_dylexia = analyze_dylexia(
                        font_type_dict_)
                    final_json_['matching_fonts_analyze_dylexia'] = matching_fonts_analyze_dylexia
                    final_json_['non_matching_fonts_analyze_dylexia'] = non_matching_fonts_analyze_dylexia
                    remaining_percentage_dylexia = round(100 - percentage_analyze_dylexia)

                    final_data_analyze_pdf_colorblind, combined_data_analyze_pdf_colorblind = future.result()
                    overall_percentages_colorblind = calculate_overall_percentage(combined_data_analyze_pdf_colorblind)

                    with open(os.path.join(pdf_docs_json, process_id, "result_colorblind.json"), "w") as file:
                        json.dump(final_data_analyze_pdf_colorblind, file)
                        file.close()
                    final_json_['overall_percentages_colorblind'] = overall_percentages_colorblind
                    final_json_["combined_data_analyze_pdf_colorblind"] = combined_data_analyze_pdf_colorblind
                    with open(os.path.join(pdf_docs_json, process_id, "result.json"), "w") as file:
                        json.dump(final_json_, file)
                        file.close()
                    # print('final_data_analyze_pdf_colorblind, combined_data_analyze_pdf_colorblind',final_data_analyze_pdf_colorblind, combined_data_analyze_pdf_colorblind)
                    # exit()
                    elapsed_time = time.time() - start_time
                    print(f"analyze_pdf_colorblind took {elapsed_time:.2f} seconds.")
                # print('font_type_dict_', font_type_dict_)
                # exit()

                return render_template("pdf_analysis_latest.html", top_4_font_size_=top_4_font_size_,
                                       top_4_fonts_types=top_4_fonts_types, total_counts_size=total_counts_size,
                                       total_counts_types=total_counts_types, count_urls_=count_urls_final_,
                                       count_images_=count_images_, pdf_document_page_count=pdf_document_page_count,
                                       percentage_dict_types=percentage_dict_types,
                                       percentage_dict_size=percentage_dict_size,
                                       length_of_percentage_dict_types=length_of_percentage_dict_types,
                                       length_of_percentage_dict_size=length_of_percentage_dict_size,
                                       count_=count_, no_of_work=no_of_work, titles_for_headers=titles,
                                       fina_header_count_=fina_header_count_, count_of_footers_=count_of_footers_,
                                       table_count_=table_count_, final_list_of_rsa=final_list_of_rsa,
                                       final_dic_for_access_=final_dic_for_access_, top_colors_list=top_colors_list,
                                       percentage_greater_than_16=percentage_greater_than_16
                                       , percentage_less_than_16=percentage_less_than_16,
                                       overall_pass_average=overall_pass_average,
                                       overall_fail_average=overall_fail_average,
                                       percentage_with_captions=round(percentage_with_captions),
                                       percentage_without_captions=round(percentage_without_captions),
                                       captions_with_images=captions_with_images, process_id=process_id,
                                       meets_wcag_count=meets_wcag_count,
                                       does_not_meet_wcag_count=does_not_meet_wcag_count,
                                       meets_wcag_percentage=meets_wcag_percentage,
                                       does_not_meet_wcag_percentage=does_not_meet_wcag_percentage,
                                       pages_with_page_number=pages_with_page_number
                                       , pages_without_page_number=pages_without_page_number
                                       , percentage_without_page_number=round(percentage_without_page_number)
                                       , percentage_with_page_number=round(percentage_with_page_number),
                                       summarized_text=summarized_text,
                                       filename=filename, overall_percentage=round(overall_percentage),
                                       remaining_percentage=round(remaining_percentage), elapsed_time=elapsed_time,
                                       final_data_analyze_pdf_colorblind=final_data_analyze_pdf_colorblind,
                                       overall_percentages_colorblind=overall_percentages_colorblind,
                                       percentage_with_caption_table=percentage_with_caption_table,
                                       percentage_without_caption_table=percentage_without_caption_table,
                                       captions_with_tables=captions_with_tables,
                                       percentage_analyze_dylexia=round(percentage_analyze_dylexia),
                                       matching_fonts_analyze_dylexia=matching_fonts_analyze_dylexia,
                                       non_matching_fonts_analyze_dylexia=non_matching_fonts_analyze_dylexia,
                                       remaining_percentage_dylexia=round(remaining_percentage_dylexia))
            else:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "pdf file directory is not created"})
                resp.status_code = 400
                return resp
        except Exception as e:
            LOG.error(e, exc_info=True)
            resp = jsonify({"success": False,
                            "data": {"pdf name": "None"},
                            "errors": "Something went wrong"})
            resp.status_code = 400
            return resp
    if request.method == "GET":
        pdf_docs_json = APP.config["PDF_RESULT_JSON"]
        if os.path.exists(os.path.join(pdf_docs_json, process_id)):
            if os.path.exists(os.path.join(pdf_docs_json, process_id, "result.json")):
                with open(os.path.join(pdf_docs_json, process_id, "result.json"), "r") as file:
                    finl_dd = json.load(file)
                    file.close()

                with open(os.path.join(pdf_docs_json, process_id, "result_imagescolor.json"), "r") as file:
                    top_colors_list = json.load(file)
                    file.close()

                with open(os.path.join(pdf_docs_json, process_id, "result_colorblind.json"), "r") as file:
                    final_data_analyze_pdf_colorblind = json.load(file)
                    file.close()
                # with open(os.path.join(pdf_docs_json, process_id, "result_colorblind.json"), "w") as file:
                #     json.dump(final_data_analyze_pdf_colorblind, file)
                #     file.close()

                count_urls_ = finl_dd['count_urls_']
                no_of_work = finl_dd['no_of_work']
                count_images_ = finl_dd['count_images_']
                dict_final_ = finl_dd['dict_final_']
                pdf_document_page_count = finl_dd['pdf_document_page_count']

                final_list_of_rsa = finl_dd['final_list_of_rsa']
                image_info_dict = finl_dd['image_info_dict']

                final_dic_for_access_ = finl_dd["final_dic_for_access_"]

                percentage_with_headers = finl_dd["percentage_with_headers"]
                percentage_without_headers = finl_dd["percentage_without_headers"]

                titles_for_footers_ = finl_dd["titles_for_footers_"]
                count_of_footers_ = finl_dd["count_of_footers_"]

                meets_wcag_count = finl_dd["meets_wcag_count"]
                does_not_meet_wcag_count = finl_dd["does_not_meet_wcag_count"]
                meets_wcag_percentage = finl_dd["meets_wcag_percentage"]
                does_not_meet_wcag_percentage = finl_dd["does_not_meet_wcag_percentage"]

                pages_with_page_number = finl_dd['pages_with_page_number']
                pages_without_page_number = finl_dd['pages_without_page_number']
                percentage_without_page_number = finl_dd['percentage_without_page_number']
                percentage_with_page_number = finl_dd['percentage_with_page_number']
                overall_percentages_colorblind = finl_dd['overall_percentages_colorblind']
                url_access_list = finl_dd["url_access_list"]

                percentage_with_caption_table = finl_dd["percentage_with_caption_table"]
                percentage_without_caption_table = finl_dd["percentage_without_caption_table"]
                captions_with_tables = finl_dd["captions_with_tables"]

                titles = finl_dd["titles"]
                No_headers_Pages = finl_dd["No_headers_Pages"]
                yes_headers_pages = finl_dd["yes_headers_pages"]
                table_count_ = finl_dd["table_count_"]
                summarized_text = finl_dd['summarized_text']
                filename = finl_dd['filename']
                image_accessibility = finl_dd["image_accessibility"]
                image_ratio_of_accessibility = finl_dd["image_ratio_of_accessibility"]
                image_page_number_accessibility = finl_dd["image_page_number_accessibility"]
                combined_data_analyze_pdf_colorblind = finl_dd["combined_data_analyze_pdf_colorblind"]

                percentage_with_captions, percentage_without_captions, captions_with_images = finl_dd[
                                                                                                  "percentage_with_captions"], \
                                                                                              finl_dd[
                                                                                                  "percentage_without_captions"], \
                                                                                              finl_dd[
                                                                                                  "captions_with_images"]

                fina_header_count_ = [[round(percentage_with_headers), yes_headers_pages],
                                      [round(percentage_without_headers), No_headers_Pages]]

                font_size_dict_ = {}
                font_type_dict_ = {}
                count_ = 0
                matching_fonts_analyze_dylexia = finl_dd['matching_fonts_analyze_dylexia']
                non_matching_fonts_analyze_dylexia = finl_dd['non_matching_fonts_analyze_dylexia']

                final_json_ = {"pages_with_page_number": pages_with_page_number,
                               "pages_without_page_number": pages_without_page_number,
                               "percentage_without_page_number": percentage_without_page_number,
                               "percentage_with_page_number": percentage_with_page_number, "count_urls_": count_urls_,
                               "dict_final_": dict_final_, "count_images_": count_images_,
                               "pdf_document_page_count": pdf_document_page_count, "no_of_work": no_of_work,
                               "titles": titles, "No_headers_Pages": No_headers_Pages,
                               "yes_headers_pages": yes_headers_pages,
                               "percentage_with_headers": percentage_with_headers,
                               "percentage_without_headers": percentage_without_headers,
                               "titles_for_footers_": titles_for_footers_, "count_of_footers_": count_of_footers_,
                               "table_count_": table_count_
                    , "final_list_of_rsa": final_list_of_rsa,
                               "image_info_dict": image_info_dict, "final_dic_for_access_": final_dic_for_access_,
                               "top_colors_list": top_colors_list, "percentage_with_captions": percentage_with_captions,
                               "percentage_without_captions": percentage_without_captions,
                               "captions_with_images": captions_with_images
                    , "meets_wcag_count": meets_wcag_count, "does_not_meet_wcag_count": does_not_meet_wcag_count,
                               "meets_wcag_percentage": meets_wcag_percentage,
                               "does_not_meet_wcag_percentage": does_not_meet_wcag_percentage,
                               "summarized_text": summarized_text,
                               "filename": filename,
                               "overall_percentages_colorblind": overall_percentages_colorblind,
                               "image_accessibility": image_accessibility,
                               "image_page_number_accessibility": image_page_number_accessibility,
                               "combined_data_analyze_pdf_colorblind": combined_data_analyze_pdf_colorblind,
                               "url_access_list": url_access_list,
                               "percentage_with_caption_table": percentage_with_caption_table,
                               "percentage_without_caption_table": percentage_without_caption_table,
                               "captions_with_tables": captions_with_tables,
                               "matching_fonts_analyze_dylexia": matching_fonts_analyze_dylexia,
                               "non_matching_fonts_analyze_dylexia": non_matching_fonts_analyze_dylexia,
                               "image_ratio_of_accessibility":image_ratio_of_accessibility}
                pdf_docs_json = APP.config["PDF_RESULT_JSON"]
                if not os.path.exists(os.path.join(pdf_docs_json, process_id)):
                    os.mkdir(os.path.join(pdf_docs_json, process_id))
                with open(os.path.join(pdf_docs_json, process_id, "result.json"), "w") as file:
                    json.dump(final_json_, file)
                    file.close()
                with open(os.path.join(pdf_docs_json, process_id, "result_colorblind.json"), "w") as file:
                    json.dump(final_data_analyze_pdf_colorblind, file)
                    file.close()

                for i in dict_final_:
                    for j in dict_final_[i]:
                        for k in dict_final_[i][j]:
                            # print(dict_final_[i][j][k]['font_line'])
                            if str(dict_final_[i][j][k]['font_line']).strip() == '' or dict_final_[i][j][k][
                                'font_line'] == '':
                                pass
                            else:
                                count_ = count_ + 1
                                for fnt in dict_final_[i][j][k]['font_font_type']:
                                    font_ = fnt
                                    font_type_dict_[font_] = font_type_dict_.get(font_, 0) + 1

                                for fntsz in dict_final_[i][j][k]['font_sizes']:
                                    font_size = fntsz
                                    font_size_dict_[font_size] = font_size_dict_.get(font_size, 0) + 1
                top_4_fonts_types = dict(sorted(font_type_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
                total_counts_types = sum(font_type_dict_.values())
                # print('total_counts_types', total_counts_types)
                # exit()
                percentage_dict_types = {font: round((count / total_counts_types) * 100) for font, count in
                                         top_4_fonts_types.items()}
                length_of_percentage_dict_types = len(percentage_dict_types)

                top_4_font_size_ = dict(sorted(font_size_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
                total_counts_size = sum(font_size_dict_.values())

                sum_greater_than_16 = sum(value for key, value in font_size_dict_.items() if float(key) >= 14)
                percentage_greater_than_16 = round((sum_greater_than_16 / total_counts_size) * 100)

                sum_less_than_16 = sum(value for key, value in font_size_dict_.items() if float(key) < 14)
                percentage_less_than_16 = round((sum_less_than_16 / total_counts_size) * 100)

                percentage_dict_size = {font: round((count / total_counts_size) * 100) for font, count in
                                        top_4_font_size_.items()}
                length_of_percentage_dict_size = len(percentage_dict_size)

                print('fina_header_count_', fina_header_count_)

                pass_percentages = [fina_header_count_[0][0], count_of_footers_[0][0]]
                fail_percentages = [fina_header_count_[1][0], count_of_footers_[1][0]]

                overall_pass_average = round(sum(pass_percentages) / len(pass_percentages))
                overall_fail_average = round(sum(fail_percentages) / len(fail_percentages))

                print('overall_pass_average', overall_pass_average)
                print('overall_fail_average', overall_fail_average)
                # return render_template("index.html", top_4_font_size_=top_4_font_size_,
                #                        top_4_fonts_types=top_4_fonts_types, total_counts_size=total_counts_size,
                #                        total_counts_types=total_counts_types, count_urls_=count_urls_,
                #                        count_images_=count_images_, pdf_document_page_count=pdf_document_page_count,
                #                        percentage_dict_types=percentage_dict_types,
                #                        percentage_dict_size=percentage_dict_size,
                #                        length_of_percentage_dict_types=length_of_percentage_dict_types,
                #                        length_of_percentage_dict_size=length_of_percentage_dict_size,
                #                        count_=count_, no_of_work=no_of_work, titles_for_headers=titles,
                #                        fina_header_count_=fina_header_count_, count_of_footers_=count_of_footers_,
                #                        table_count_=table_count_, final_list_of_rsa=final_list_of_rsa,
                #                        final_dic_for_access_=final_dic_for_access_, top_colors_list=top_colors_list,
                #                        percentage_greater_than_16=percentage_greater_than_16,
                #                        percentage_less_than_16=percentage_less_than_16,
                #                        overall_pass_average=overall_pass_average,
                #                        overall_fail_average=overall_fail_average,
                #                        percentage_with_captions=round(percentage_with_captions, 2),
                #                        percentage_without_captions=round(percentage_without_captions, 2),
                #                        captions_with_images=captions_with_images, process_id=process_id,
                #                        meets_wcag_count=meets_wcag_count,
                #                        does_not_meet_wcag_count=does_not_meet_wcag_count,
                #                        meets_wcag_percentage=meets_wcag_percentage,
                #                        does_not_meet_wcag_percentage=does_not_meet_wcag_percentage
                #                        )
                # print('no_of_work', no_of_work)
                # print('fina_header_count_', fina_header_count_)
                # print("overal",round(percentage_with_captions, 1), round(percentage_with_captions, 1), round(fina_header_count_[0][0],1),
                #       round(count_of_footers_[0][0],1), round(meets_wcag_percentage,1), round(percentage_with_page_number,1), count_urls_)
                if count_urls_ == 0:
                    percentages = [round(percentage_with_captions, 1), round(percentage_with_captions, 1),
                                   round(fina_header_count_[0][0], 1), round(count_of_footers_[0][0], 1),
                                   round(meets_wcag_percentage, 1), round(percentage_with_page_number, 1)]
                else:
                    try:
                        percentages = [round(percentage_with_captions, 1), round(percentage_with_captions, 1),
                                       round(fina_header_count_[0][0], 1), round(count_of_footers_[0][0], 1),
                                       round(meets_wcag_percentage, 1), round(percentage_with_page_number, 1),
                                       round(no_of_work['Number Of Urls Accessible'], 1)]
                    except:
                        percentages = [round(percentage_with_captions, 1), round(percentage_with_captions, 1),
                                       round(fina_header_count_[0][0], 1), round(count_of_footers_[0][0], 1),
                                       round(meets_wcag_percentage, 1), round(percentage_with_page_number, 1)]
                overall_percentage = round(sum(percentages) / len(percentages))
                remaining_percentage = round(100 - overall_percentage)
                # percentage, matching_fonts, non_matching_fonts = analyze_dylexia(font_type_dict_)
                percentage_analyze_dylexia, matching_fonts_analyze_dylexia, non_matching_fonts_analyze_dylexia = analyze_dylexia(
                    font_type_dict_)
                # print('percentage_analyze_dylexia, matching_fonts_analyze_dylexia, non_matching_fonts_analyze_dylexia',percentage_analyze_dylexia, matching_fonts_analyze_dylexia)
                remaining_percentage_dylexia = round(100 - percentage_analyze_dylexia)
                # print('non_matching_fonts_analyze_dylexia',non_matching_fonts_analyze_dylexia)
                # print('remaining_percentage_dylexia',remaining_percentage_dylexia)
                return render_template("pdf_analysis_latest.html", top_4_font_size_=top_4_font_size_,
                                       top_4_fonts_types=top_4_fonts_types, total_counts_size=total_counts_size,
                                       total_counts_types=total_counts_types, count_urls_=count_urls_,
                                       count_images_=count_images_, pdf_document_page_count=pdf_document_page_count,
                                       percentage_dict_types=percentage_dict_types,
                                       percentage_dict_size=percentage_dict_size,
                                       length_of_percentage_dict_types=length_of_percentage_dict_types,
                                       length_of_percentage_dict_size=length_of_percentage_dict_size,
                                       count_=count_, no_of_work=no_of_work, titles_for_headers=titles,
                                       fina_header_count_=fina_header_count_, count_of_footers_=count_of_footers_,
                                       table_count_=table_count_, final_list_of_rsa=final_list_of_rsa,
                                       final_dic_for_access_=final_dic_for_access_, top_colors_list=top_colors_list,
                                       percentage_greater_than_16=percentage_greater_than_16,
                                       percentage_less_than_16=percentage_less_than_16,
                                       overall_pass_average=overall_pass_average,
                                       overall_fail_average=overall_fail_average,
                                       percentage_with_captions=round(percentage_with_captions),
                                       percentage_without_captions=round(percentage_without_captions),
                                       captions_with_images=captions_with_images, process_id=process_id,
                                       meets_wcag_count=meets_wcag_count,
                                       does_not_meet_wcag_count=does_not_meet_wcag_count,
                                       meets_wcag_percentage=meets_wcag_percentage,
                                       does_not_meet_wcag_percentage=does_not_meet_wcag_percentage,
                                       pages_with_page_number=pages_with_page_number
                                       , pages_without_page_number=pages_without_page_number
                                       , percentage_without_page_number=round(percentage_without_page_number)
                                       , percentage_with_page_number=round(percentage_with_page_number),
                                       summarized_text=summarized_text,
                                       filename=filename, overall_percentage=round(overall_percentage),
                                       remaining_percentage=round(remaining_percentage),
                                       final_data_analyze_pdf_colorblind=final_data_analyze_pdf_colorblind,
                                       overall_percentages_colorblind=overall_percentages_colorblind,
                                       percentage_with_caption_table=percentage_with_caption_table,
                                       percentage_without_caption_table=percentage_without_caption_table,
                                       captions_with_tables=captions_with_tables,
                                       percentage_analyze_dylexia=round(percentage_analyze_dylexia),
                                       matching_fonts_analyze_dylexia=matching_fonts_analyze_dylexia,
                                       non_matching_fonts_analyze_dylexia=non_matching_fonts_analyze_dylexia,
                                       remaining_percentage_dylexia=round(remaining_percentage_dylexia))
            else:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "Result Not Found"})
                resp.status_code = 400
                return resp
        else:
            resp = jsonify({"success": False,
                            "data": {"pdf name": "None"},
                            "errors": "Data Is Not Available"})
            resp.status_code = 400
            return resp
