import requests
import os
from bs4 import BeautifulSoup

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"

url = r"https://cmsworkshops.com:443/ICASSP2026/papers/accepted_papers.php"

# 获取 id为acceptedPapers的table，并解析tbody
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', id='acceptedPapers')
rows = table.find_all('tr')[1:]  # 跳过表头
# tr中有2个TD，分别为paper_id和paper_title
total = 0
for row in rows:
    cols = row.find_all('td')
    paper_id = cols[0].text.strip()
    paper_title = cols[1].text.strip()
    print(f"{paper_id}\t{paper_title}")
    total += 1

print(f"当前总录取量：\t{total}")
