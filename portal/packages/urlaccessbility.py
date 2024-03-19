import requests
import fitz


def check_url_access(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    temp = {}
    try:
        response1 = requests.get(url)
        response2 = requests.get(url,headers=headers)
        if response1.status_code == 403:
            temp['url_acc'] = "Yes"
            temp['status_code'] = response1.status_code
        elif response1.status_code == 200:
            temp['url_acc'] = "Yes"
            temp['status_code'] = response1.status_code  # Or perform other actions with the response
        else:
            if response2.status_code == 403:
                temp['url_acc'] = "Yes"
                temp['status_code'] = response2.status_code
            elif response2.status_code == 200:
                temp['url_acc'] = "Yes"
                temp['status_code'] = response2.status_code
            else:
                temp['url_acc'] = "No"
                temp['status_code'] = 400
    except requests.RequestException:
        temp['url_acc'] = "No"
        temp['status_code'] = 400

    return temp


def extract_urls_from_pdf_to_dict(pdf_path):
    links_dict = {}
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):  # Start page numbering at 1
                try:
                    links = page.get_links()
                    for link in links:
                        if 'uri' in link:  # Ensure the block has a URI
                            if page_num not in links_dict:
                                links_dict[page_num] = []
                            links_dict[page_num].append(link['uri'])
                except:
                    pass
    except Exception as e:
        print(f"An error occurred: {e}")
    return links_dict


def count_custom_urls_in_pdf(pdf_path):
    links_dict = extract_urls_from_pdf_to_dict(pdf_path)

    final_result = {}
    yes_count = 0
    no_count = 0
    url_access_list = {}

    link_index = 0  # Initialize link index to enumerate all links across pages
    for page, links in links_dict.items():
        for link in links:
            temp_result = check_url_access(link)
            temp_result['url'] = link
            final_result[link_index] = temp_result

            if temp_result['url_acc'] == "Yes":
                yes_count += 1
                url_access_list[link_index] = [link, "Accessible", page]
            else:
                no_count += 1
                url_access_list[link_index] = [link, "Not Accessible", page]

            link_index += 1  # Increment link index for a flat enumeration

    count_urls = sum(len(links) for links in links_dict.values())

    return {
        "count_urls_": count_urls,
        "final_": final_result,
        "yes_count_": yes_count,
        "no_count_": no_count,
        "url_access_list": url_access_list
    }