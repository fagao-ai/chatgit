import requests

# 替换为你的访问令牌
# https://docs.github.com/

proxies = {
    "http": "http://127.0.0.1:1080",
}

# GitHub API 搜索的 URL
search_url = "https://api.github.com/search/repositories?q=stars:>100"

# 设置请求头，包括用户代理和认证

# 发送 API 请求
response = requests.get(
    search_url,
    # headers=headers,
    proxies=proxies,
)

# 解析 JSON 响应
data = response.json()

# 打印搜索结果
for item in data["items"]:
    print(f"Repository: {item['name']}")
    print(f"Stars: {item['stargazers_count']}")
    print(f"Description: {item['description']}\n")
aa = "aaaa" * 100
print(aa)
