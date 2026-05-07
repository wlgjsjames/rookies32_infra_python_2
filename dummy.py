import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

try:
    client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
    db = client['exchrate_db']
    rate_col = db['ExchangeRates']

    # 어제
    # yesterday_date = (datetime.now() + timedelta(days=1)).strftime("%Y.%m.%d")
    # 오늘
    yesterday_date = (datetime.now()).strftime("%Y.%m.%d")


    dummy_data = [
        {
            "code": "미국 달러", 
            "cur_unit": "USD", 
            "deal_bas_r": "1,480.5",
            "date": yesterday_date
        },
        {
            "code": "일본 옌", 
            "cur_unit": "JPY", 
            "deal_bas_r": "980.0", 
            "date": yesterday_date
        },
        {
            "code": "유로", 
            "cur_unit": "EUR", 
            "deal_bas_r": "1,580.0", 
            "date": yesterday_date
        }
    ]

    rate_col.delete_many({"date": yesterday_date})
    result = rate_col.insert_many(dummy_data)

    print(f"데이터 주입 성공 (날짜: {yesterday_date})")
    print(f"입력된 ID들: {result.inserted_ids}")

except Exception as e:
    print(f"오류 발생: {e}")