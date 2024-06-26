import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import logging

logging.basicConfig(level=logging.INFO)


def fetch_webpage(url: str):
    logging.info(f"Fetching webpage: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the webpage: {e}")
        return ""


def parse_articles(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.find_all("article")


def get_next_page_url(base_url: str, html_content: str, page_number: int) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    li_tag = soup.find("li", {"class": "c-pagination__item", "data-page": str(page_number)})
    if li_tag:
        return extract_link_from_tag(li_tag, base_url)
    return ""


def extract_link_from_tag(tag, base_url):
    a_tag = tag.find("a")
    full_url = urljoin(base_url, a_tag['href'])
    return full_url


def fetch_article_links(articles, base_url: str, article_type: str):
    article_links = []
    for article in articles:
        if article.find('span', string=article_type):
            full_url = extract_link_from_tag(article, base_url)
            if full_url:
                article_links.append(full_url)
    return article_links


def scrape_nature_website(pages: int, article_type: str):
    url = "https://www.nature.com/nature/articles?sort=PubDate&year=2023"

    curr_page = 1
    article_links = []
    while curr_page <= pages:
        html_content = fetch_webpage(url)
        if html_content:
            articles = parse_articles(html_content)
            article_links.extend(fetch_article_links(articles, url, article_type))
            article_links.append(curr_page)
        curr_page += 1
        url = get_next_page_url(url, html_content, curr_page)

    return article_links


def get_article_information(articles, article_type):
    page_num = 1
    for article in articles:
        if article != page_num:
            html_content = fetch_webpage(article)
            soup = BeautifulSoup(html_content, 'html.parser')
            body = get_article_body(soup, article_type)
            title = soup.find("h1", class_="c-article-magazine-title").get_text()
            save_article_information(title, body, page_num)
        else:
            page_num += 1


def get_article_body(soup_content, article_type):
    article_teasers = ["News", "Research Highlight", "News & Views"]
    if article_type in article_teasers:
        try:
            return soup_content.find("p", {"class": "article__teaser"}).get_text()
        except AttributeError:
            return soup_content.find("div", {"class": "c-article-body main-content"}).get_text()


def save_article_information(title, body, page_number):
    formatted_title = title.replace(' ', '_').strip()
    translator = str.maketrans('', '', ".?!")
    formatted_title = formatted_title.translate(translator)
    filename = formatted_title + '.txt'

    path = os.getcwd() + f"/Page_{page_number}"
    if not os.path.exists(path):
        os.mkdir(path)
    file_path = path + '/' + filename

    with open(file_path, "wb") as file:
        binary_str = body.strip().encode("utf-8")
        file.write(binary_str)


def get_user_input():
    valid_article_types = ["News", "Research Highlight", "News & Views"]
    num_pages = None

    while num_pages is None:
        try:
            num_pages_input = input("Enter the number of pages to parse: ")
            num_pages = int(num_pages_input)
            if num_pages <= 0:
                print("Please enter a positive integer for the number of pages.")
                num_pages = None
        except ValueError:
            print("Invalid input. Please enter a valid integer for the number of pages.")

    article_type = None
    while article_type not in valid_article_types:
        article_type = input(f"Enter the article type to filter ({', '.join(valid_article_types)}): ")
        if article_type not in valid_article_types:
            print(f"Invalid article type. Please choose from {', '.join(valid_article_types)}.")

    return num_pages, article_type


if __name__ == "__main__":
    pages_to_parse, article_category = get_user_input()
    news_articles = scrape_nature_website(pages_to_parse, article_category)
    get_article_information(news_articles, article_category)

