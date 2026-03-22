from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

def scrape_ft():
    articles = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto('https://www.ft.com/login')
            page.fill('input[type=email]', os.environ['FT_EMAIL'])
            page.click('button[type=submit]')
            page.wait_for_timeout(1500)
            page.fill('input[type=password]', os.environ['FT_PASSWORD'])
            page.click('button[type=submit]')
            page.wait_for_timeout(3000)
            page.goto('https://www.ft.com')
            page.wait_for_timeout(2000)
            items = page.query_selector_all('a[data-trackable="heading-link"]')[:8]
            for item in items:
                articles.append({
                    'source': 'Financial Times',
                    'title': item.inner_text().strip(),
                    'url': 'https://www.ft.com' + item.get_attribute('href')
                })
            browser.close()
    except Exception as e:
        articles.append({'source': 'FT', 'error': str(e)})
    return articles

def scrape_dn():
    articles = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto('https://www.dn.no/auth/login')
            page.fill('input[name=email]', os.environ['DN_EMAIL'])
            page.fill('input[name=password]', os.environ['DN_PASSWORD'])
            page.click('button[type=submit]')
            page.wait_for_timeout(3000)
            page.goto('https://www.dn.no')
            page.wait_for_timeout(2000)
            items = page.query_selector_all('h2 a, h3 a')[:8]
            for item in items:
                articles.append({
                    'source': 'Dagens Næringsliv',
                    'title': item.inner_text().strip(),
                    'url': item.get_attribute('href')
                })
            browser.close()
    except Exception as e:
        articles.append({'source': 'DN', 'error': str(e)})
    return articles

@app.route('/articles')
def get_articles():
    all_articles = []
    all_articles += scrape_ft()
    all_articles += scrape_dn()
    return jsonify(all_articles)

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
