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


def extract_news_links(articles, base_url):
    article_links = []
    for article in articles:
        if article.find('span', string='News'):
            a_tag = article.find('a')
            if a_tag and a_tag.has_attr('href'):
                full_url = urljoin(base_url, a_tag['href'])
                article_links.append(full_url)
    return article_links


def get_news_articles():
    url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020&page=3"
    html_content = fetch_webpage(url)
    if html_content:
        articles = parse_articles(html_content)
        return extract_news_links(articles, url)
    else:
        return []


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


if __name__ == "__main__":
    news_articles = get_news_articles()
    get_article_information(news_articles)