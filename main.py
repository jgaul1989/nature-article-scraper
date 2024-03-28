import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def fetch_webpage(url):
    try:
        response = requests.get(url)
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None


def parse_articles(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.find_all("article")


def set_next_url_page(base_url, html_content, page_number: int):
    soup = BeautifulSoup(html_content, 'html.parser')
    li_tag = soup.find("li", {"class": "c-pagination__item", "data-page": str(page_number)})
    return extract_link_from_tag(li_tag, base_url)


def extract_link_from_tag(tag, base_url):
    a_tag = tag.find("a")
    full_url = urljoin(base_url, a_tag['href'])
    return full_url


def extract_news_links(articles, base_url):
    article_links = []
    for article in articles:
        if article.find('span', string='News'):
            full_url = extract_link_from_tag(article, base_url)
            article_links.append(full_url)
    return article_links


def get_news_articles(pages: int):
    url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020"

    curr_page = 1
    article_links = []
    while curr_page <= pages:
        html_content = fetch_webpage(url)
        if html_content:
            articles = parse_articles(html_content)
            article_links.extend(extract_news_links(articles, url))
        curr_page += 1
        url = set_next_url_page(url, html_content, curr_page)

    return article_links


def get_article_information(articles):
    for article in articles:
        html_content = fetch_webpage(article)
        soup = BeautifulSoup(html_content, 'html.parser')
        teaser = soup.find("p", {"class": "article__teaser"}).get_text()
        title = soup.find("h1", class_="c-article-magazine-title").get_text()
        save_article_information(title, teaser)


def save_article_information(title, teaser):
    formatted_title = title.replace(' ', '_').strip()
    translator = str.maketrans('', '', ".?!")
    formatted_title = formatted_title.translate(translator)
    filename = formatted_title + '.txt'

    with open(filename, "wb") as file:
        binary_str = teaser.strip().encode("utf-8")
        file.write(binary_str)


def get_user_params():
    num_pages = int(input(""))
    return num_pages


if __name__ == "__main__":
    pages_to_parse = get_user_params()
    news_articles = get_news_articles(pages_to_parse)
    get_article_information(news_articles)