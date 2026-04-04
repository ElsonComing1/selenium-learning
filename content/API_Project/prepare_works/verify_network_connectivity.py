import requests
url='http://httpbin.org/ip'
response=requests.get(url)
response.raise_for_status()
print(response.status_code)
print(response.url)
print(response.text)
print(response.json())
# 获取期望值200