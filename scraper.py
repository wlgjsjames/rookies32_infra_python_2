import os, requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

date = datetime.now()
today = date.strftime("%Y%m%d")

if not API_KEY or not BASE_URL:
    raise ValueError(".env 값 없음")

params = {
    "authkey": API_KEY,
    "searchdate": today, # default (현재일)
    "data": "AP01" # 환율
}

target = ["USD", "JPY(100)", "EUR"]

try:
    response = requests.get(f"{BASE_URL}", params=params, timeout=5)
    response.raise_for_status()
    
    data = response.json()

    filtered = [{"code": x.get("cur_nm"), "cur_unit": x.get("cur_unit"), "deal_bas_r": x.get("deal_bas_r")}for x in data if x.get("cur_unit") in target]
    print(filtered)
except Exception as e:
    print(f"에러 발생: {e}")




