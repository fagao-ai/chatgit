import urllib.request
import json
import os
import time
from playwright.sync_api import sync_playwright
import random


n = 5  # number of fetched READMEs
url = 'https://api.github.com/search/repositories?q=stars:%3E500&sort=stars'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
request = urllib.request.Request(url, headers=headers)
response = urllib.request.urlopen(request)
page = response.read().decode()
api_json = json.loads(page)

repos = api_json['items'][:n]

p = sync_playwright().start()


browsers = [browser_type.launch() for browser_type in [p.chromium]]
for repo in repos:
    full_name = repo['full_name']
    contents_url = repo['url'] + '/contents'
    request = urllib.request.Request(contents_url, headers=headers)
    response = urllib.request.urlopen(request)
    page = response.read().decode()
    contents_json = json.loads(page)
    readme_url = [file['download_url'] for file in contents_json if file['name'].lower() == 'readme.md'][0]
    # download readme contents
    try:
        browser = random.choice(browsers)
        page = browser.new_page()
        page.goto(readme_url)
        print(page.content())
        browser.close()
    except urllib.error.HTTPError as error:
        print(error)
        continue

    # create folder named after repo's name and save readme.md there
    try:
        os.mkdir(repo['name'])
    except OSError as error:
        print(error)
    with open(repo['name'] + '/README.md', 'wb') as f:
        # f.write(resp.content)
        print('ok')

    # only 10 requests per min for unauthenticated requests
    if n >= 9:  # n + 1 initial request
        time.sleep(6)
