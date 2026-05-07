import os, requests, re
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

date = datetime.now()
today = date.strftime("%Y%m%d")

if not API_KEY or not BASE_URL:
    raise ValueError(".env 값 없음")

target = ["USD", "JPY(100)", "EUR"]

def get_api(API_KEY, BASE_URL, date = None, target = ["USD", "JPY(100)", "EUR"]):
    
    params = {
        "authkey": API_KEY,
        "data": "AP01" # 환율
    }
    # date 기본값은 today이다. ex) 20260507 형태로 입력해야함.
    if date is not None:
        params["searchdate"] = date
        
    try:
        response = requests.get(f"{BASE_URL}", params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()

        filtered = [{"code": x.get("cur_nm"), "cur_unit": x.get("cur_unit"), "deal_bas_r": x.get("deal_bas_r")}for x in data if x.get("cur_unit") in target]
    except Exception as e:
        print(f"에러 발생: {e}")

    return filtered

def get_news():
    
    url = "https://kita.net/cmmrcInfo/ehgtNews/ehgtNewsList.do"
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(res.text, "html.parser")
    news = soup.select_one(".board-list li") # 최상단 뉴스 하나만 스크래핑
    
    # title
    title = news.select_one(".subject a").get("title")
    
    # date
    date = news.select_one(".info .date").get_text(strip=True)
    
    # link
    onclick = news.select_one(".subject a").get("onclick")
    match = re.search(r"goDetailPage\('(\d+)',\s*'(\d+)'\)", onclick)
    classification, no = match.groups() # match.group()은 1개
    link = f"https://kita.net/cmmrcInfo/ehgtNews/ehgtNewsDetail.do?classification={classification}&no={no}"
    
    news_info = {
        "title" : title,
        "link" : link,
        "date" : date, 
    }
    
    return news_info
if __name__ == "__main__":
    data = get_api(API_KEY, BASE_URL)
    print(data)
    print(get_news())