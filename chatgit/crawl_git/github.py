import urllib.request
import json
import os
import time
from urllib.parse import urlencode

import requests
from chatgit.crawl_git.crawl_git_base import CrawlGitBase, HttpMethod


class CrawlGithub(CrawlGitBase):
    def __init__(self):
        super().__init__("https://api.github.com/search/repositories")

    def get_data(self, page_size=100):
        total_count = self.get_total_repo()
        total_page = int(total_count / page_size) + 1
        for page in range(total_page):
            query_param_str = f"per_page={page_size}&stars>={self.stars_gte}&sort=stars&page={page}"
            url = self.base_url + "?" + query_param_str
            repo_resp = self.request(HttpMethod.GET, url)
            if repo_resp.status_code == 200:
                repo_json = repo_resp.json()
                id = repo_json["id"]
                name = repo_json["name"]
                index_url = repo_json["html_url"]
                description = repo_json["description"]
                language = repo_json["language"]
                has_wiki = repo_json["has_wiki"]
                forks_count = repo_json["forks_count"]
                license = repo_json["license"]  # json
                topics = repo_json["topics"]  # list
                repo_info = {
                    "id": id,
                    "name": name,
                    "index_url": index_url,
                    "description": description,
                    "language": language,
                    "has_wiki": has_wiki,
                    "forks_count": forks_count,
                    "license": license,
                    "topics": topics,
                }
                print(repo_info)
            else:
                pass

    def get_total_repo(self):
        url = self.base_url + "?" + f"stars>={self.stars_gte}"
        resp = self.request(HttpMethod.GET, url)
        if resp.status_code == 200:
            data_json = resp.json()
            return data_json["total_count"]
        else:
            raise Exception("Get total_repo faild.")

#
# n = 5  # number of fetched READMEs
# url = 'https://api.github.com/search/repositories?q=stars:%3E100&sort=stars'
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
# }
# request = urllib.request.Request(url, headers=headers)
# response = urllib.request.urlopen(request)
# page = response.read().decode()
# api_json = json.loads(page)
#
# repos = api_json['items'][:n]
#
#
# for repo in repos:
#     full_name = repo['full_name']
#     contents_url = repo['url'] + '/contents'
#     request = urllib.request.Request(contents_url, headers=headers)
#     response = urllib.request.urlopen(request)
#     page = response.read().decode()
#     contents_json = json.loads(page)
#     readme_url = [file['download_url'] for file in contents_json if file['name'].lower() == 'readme.md'][0]
#     # download readme contents
#     try:
#         resp = requests.get(readme_url)
#         res = resp.content
#     except urllib.error.HTTPError as error:
#         print(error)
#         continue
#
#     # create folder named after repo's name and save readme.md there
#     try:
#         os.mkdir(repo['name'])
#     except OSError as error:
#         print(error)
#     with open(repo['name'] + '/README.md', 'wb') as f:
#         f.write(resp.content)
#         print('ok')
#
#     # only 10 requests per min for unauthenticated requests
#     if n >= 9:  # n + 1 initial request
#         time.sleep(6)
