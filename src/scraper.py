import requests
from requests import Response
from typing import List
from bs4 import BeautifulSoup
from bs4.element import ResultSet
import os
from dotenv import load_dotenv
load_dotenv()


NAME_IDENTIFIER = "reports that "
CAPTION_IDENTIFIER = 'class="wp-caption-text"'
END_OF_ARTICLE_MARKER = '<a href="https://www.fishermanspost.com/author/fish-post/">'
FISHING_REPORTS_URL = "https://www.fishermanspost.com/category/fishing-reports/page/"
MAX_PAGES = 770
MIN_PARAGRAPH_LENGTH = 25


def make_fishing_blog_request(url: str) -> Response:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.google.com/",
    }
    return requests.get(url, headers=headers)


def extract_location_and_date(url):
    parts = url.split("/")
    location_and_date = parts[-2].split("-")
    location = " ".join(location_and_date[:-2]).title()
    date = " ".join(location_and_date[-2:]).title()
    return location, date


def get_article_links_from_fishing_reports(page: str = 1) -> List[str]:
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
              'november', 'december']
    response = make_fishing_blog_request(FISHING_REPORTS_URL + str(page))
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a")

    article_links = []
    for link in links:
        href = str(link.get("href"))
        parts = href.split("-")
        month, year = None, ""
        if len(parts) > 2:
            year = parts[-1][:-1]
            month = parts[-2]
        if month in months and year.isdigit() and href not in article_links:
            article_links.append(href)
    return article_links


def remove_names(paragraph: str) -> str:
    if NAME_IDENTIFIER in paragraph:
        paragraph = paragraph.split(NAME_IDENTIFIER)[1].capitalize()
    return paragraph


def clean_paragraphs(paragraphs: ResultSet) -> List[str]:
    cleaned_paragraphs = []
    for p in paragraphs:
        if CAPTION_IDENTIFIER not in str(p):
            p = remove_names(p.get_text())
            if len(p) > MIN_PARAGRAPH_LENGTH:
                cleaned_paragraphs.append(p)
    return cleaned_paragraphs


def get_paragraphs_from_article_link(article_url: str) -> List[str]:
    response = make_fishing_blog_request(article_url)
    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.find_all("p")
    paragraphs = clean_paragraphs(paragraphs)
    return paragraphs

