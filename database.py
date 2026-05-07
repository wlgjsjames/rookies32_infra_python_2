import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from datetime import datetime, time
from scraper import get_api, get_news
from pymongo import MongoClient

load_dotenv()
# DB 연결
client = MongoClient('mongodb://localhost:27017')

# DB 및 컬렉션 선택
db = client['exchrate_db']
rate_col = db['ExchangeRates']
article_col = db['article']

# Create: 데이터 넣기
def Create_db():

    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    
    today_str = datetime.now().strftime("%Y%m%d")

    rate_data = get_api(API_KEY, BASE_URL, today_str)
    news_data = get_news()

    # 환율 데이터 불러오기 및 rate_col에 저장
    if rate_data:
        str_date = datetime.now().strftime("%Y.%m.%d")

        for item in rate_data:
            # 각 리스트 요소(dict)에 'collected_at' 필드 추가
            item['date'] = str_date
        
        rate_col.insert_many(rate_data)
        print(f"환율 데이터 {len(rate_data)}건에 수집시간 포함하여 저장 완료!")

    # 뉴스 데이터 불러오기 및 article_col에 저장
    if news_data:
        article_col.insert_many([news_data])
        print(f"뉴스 데이터 {len(news_data)}건 저장 완료!")

# Read: 데이터 찾아오기
def get_data_by_date(target_date):
    
    rate_cursor = rate_col.find({"date": target_date})
    rate_data = list(rate_cursor)

    article_cursor = article_col.find({"date": target_date})
    article_data = list(article_cursor)
    
    return rate_data, article_data

if __name__ == "__main__":
    # Create_db()  # 저장 실행
    
    today_date = datetime.now().strftime("%Y.%m.%d")
    
    # [수정 포인트] 리스트 두 개를 따로따로 받습니다.
    rates, articles = get_data_by_date(today_date)
    
    # 1. 환율 정보 출력
    if not rates:
        print("오늘 수집된 환율 데이터가 없습니다.")
    else:
        print(f"오늘 수집된 환율 {len(rates)}건을 찾았습니다!")
        for item in rates:  # 이제 item은 리스트 안의 '딕셔너리'입니다.
            print(f"[{item.get('cur_unit')}] 환율: {item.get('deal_bas_r')}")

    # 2. 뉴스 정보 출력 (선택 사항)
    if articles:
        print(f"\n오늘 수집된 뉴스 {len(articles)}건:")
        for news in articles:
            print(f"- {news.get('title')}")