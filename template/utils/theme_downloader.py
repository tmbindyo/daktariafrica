# import os
# import requests
# from urllib.parse import urljoin, urlparse
# from bs4 import BeautifulSoup

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TEMPLATE_DIR = os.path.join(BASE_DIR, "templates", "medicate")
# STATIC_DIR = os.path.join(BASE_DIR, "static", "medicate")


# def ensure_dir(path):
#     os.makedirs(path, exist_ok=True)


# def download_file(url, save_path):
#     r = requests.get(url, timeout=20)
#     r.raise_for_status()
#     with open(save_path, "wb") as f:
#         f.write(r.content)


# def download_theme(url):
#     ensure_dir(TEMPLATE_DIR)
#     ensure_dir(STATIC_DIR)

#     response = requests.get(url)
#     response.raise_for_status()

#     soup = BeautifulSoup(response.text, "lxml")

#     tags = {
#         "link": "href",
#         "script": "src",
#         "img": "src"
#     }

#     for tag, attr in tags.items():
#         for el in soup.find_all(tag):
#             if not el.get(attr):
#                 continue

#             resource_url = urljoin(url, el[attr])
#             parsed = urlparse(resource_url)

#             filename = os.path.basename(parsed.path)
#             if not filename:
#                 continue

#             subdir = "misc"
#             if tag == "link":
#                 subdir = "css"
#             elif tag == "script":
#                 subdir = "js"
#             elif tag == "img":
#                 subdir = "images"

#             local_dir = os.path.join(STATIC_DIR, subdir)
#             ensure_dir(local_dir)

#             local_path = os.path.join(local_dir, filename)

#             try:
#                 download_file(resource_url, local_path)
#             except Exception as e:
#                 print(f"Failed: {resource_url} -> {e}")
#                 continue

#             # Update HTML to Django static path
#             el[attr] = f"{{% static 'medicate/{subdir}/{filename}' %}}"

#     # Add Django static loader
#     soup.html.insert(0, soup.new_string("{% load static %}\n"))

#     with open(os.path.join(TEMPLATE_DIR, "index.html"), "w", encoding="utf-8") as f:
#         f.write(str(soup))

#     print("Theme downloaded successfully.")



import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates", "medicate")
STATIC_DIR = os.path.join(BASE_DIR, "static", "medicate")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def download_file(url, save_path):
    if os.path.exists(save_path):
        return  # already downloaded

    r = requests.get(url, timeout=20)
    r.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(r.content)


def process_html_page(page_url):
    response = requests.get(page_url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    tags = {
        "link": "href",
        "script": "src",
        "img": "src"
    }

    for tag, attr in tags.items():
        for el in soup.find_all(tag):
            src = el.get(attr)
            if not src:
                continue

            resource_url = urljoin(page_url, src)
            parsed = urlparse(resource_url)
            filename = os.path.basename(parsed.path)

            if not filename:
                continue

            if tag == "link":
                subdir = "css"
            elif tag == "script":
                subdir = "js"
            elif tag == "img":
                subdir = "images"
            else:
                subdir = "misc"

            local_dir = os.path.join(STATIC_DIR, subdir)
            ensure_dir(local_dir)

            local_path = os.path.join(local_dir, filename)

            try:
                download_file(resource_url, local_path)
            except Exception as e:
                print(f"Failed: {resource_url} -> {e}")
                continue

            el[attr] = f"{{% static 'medicate/{subdir}/{filename}' %}}"

    # Ensure {% load static %}
    if soup.html:
        soup.html.insert(0, soup.new_string("{% load static %}\n"))

    page_name = os.path.basename(urlparse(page_url).path) or "index.html"
    output_path = os.path.join(TEMPLATE_DIR, page_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"Saved template: {page_name}")


def download_theme(pages):
    ensure_dir(TEMPLATE_DIR)
    ensure_dir(STATIC_DIR)

    for page_url in pages:
        process_html_page(page_url)

    print("All pages downloaded successfully.")
