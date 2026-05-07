import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from datetime import datetime, time
from scraper import get_api, get_news

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
    if news_data and len(news_data) > 0:
        article_col.insert_many([news_data])
        print(f"뉴스 데이터 {len(news_data)}건 저장 완료!")
    else:
        print("저장할 뉴스 데이터가 없습니다. (수집 결과 0건)")

# Read: 데이터 찾아오기
def get_data_by_date():
    # 1. 오늘의 시작 시간 (00:00:00)과 끝 시간 (23:59:59) 객체 만들기
    today = datetime.now()
    start_of_day = datetime.combine(today, time.min) # 2026-05-07 00:00:00
    end_of_day = datetime.combine(today, time.max)   # 2026-05-07 23:59:59

    # 2. 범위 쿼리 날리기 ($gte: 크거나 같다, $lte: 작거나 같다)
    query = {
        "collected_at": {
            "$gte": start_of_day,
            "$lte": end_of_day
        }
    }
    
    # 3. 결과 반환
    return list(rate_col.find(query))

if __name__ == "__main__":
    # data = Create_db()
        
    data = get_data_by_date()
    
    if not data:
        print("조회된 데이터가 없습니다. DB의 필드명을 확인해보세요.")
    else:
        print(f"오늘 수집된 데이터 {len(data)}건을 찾았습니다!")
        for item in data:  
            print(f"[{item.get('cur_unit')}] 환율: {item.get('deal_bas_r')}")