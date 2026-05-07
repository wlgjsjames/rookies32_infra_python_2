import schedule
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 각 파일들
import scraper
import database
import analyzer
import csv_gen
import mailer

load_dotenv()

# 데이터 규격 맞추기
def list_to_dict(rate_list):
  result = {}
  for item in rate_list:
    # api에서 받은 'JPY(100)' -> 'JPY'로 통합
    unit = item.get('cur_unit').split('(')[0] 
    
    # 쉼표 제거 후 실수형 변환
    val = float(item.get('deal_bas_r').replace(',', ''))
    result[unit] = val
  return result

def job():
  print(f"[{datetime.now()}] 금일 환율 비교 시작")
  
  try:
    # DB Create
    database.Create_db()
    
    # 날짜 설정
    today = datetime.now()
    today_str = today.strftime("%Y.%m.%d")
    yesterday_str = (today - timedelta(days=1)).strftime("%Y.%m.%d")
    
    # 데이터 가져오기
    today_rates, _ = database.get_data_by_date(today_str)
    yesterday_rates, _ = database.get_data_by_date(yesterday_str)
    
    if not today_rates:
        print("오늘자 환율 데이터 수집에 실패했습니다.")
        return
    else:
        today_dict = list_to_dict(today_rates)

    if not yesterday_rates:
      print("전날 환율 데이터 없음. 0%로 취급.")
      yesterday_dict = today_dict
    else:
      yesterday_dict = list_to_dict(yesterday_rates)
    
    # 분석 요청 및 결과 저장
    analysis_result = analyzer.check_currency_drop(today_dict, yesterday_dict)
    
    # 하락 감지 시
    if analysis_result["is_any_dropped"]:
      print("환율 하락 통화 감지. 리포트 생성을 시작합니다.")
      
      # 뉴스 정보 가져오기
      news = scraper.get_news()
      # 리포트 만들기
      report = csv_gen.ExcelReportManager()
      
      # cvs_gen에서 'exchange_report.xlsx' 생성
      file_path = report.create_report(
        analysis_result['details'], 
        news, 
        history_data=None 
      )
      
      # 메일발송 - xls 파일경로 불일치로 임의 수정했습니다.
      # mailer에서 파일이름을 수정 or 매개변수로 추가인데 후자로 했습니다.
      mailer.send_mail(file_path) 
      
      print(f"보고서 발송 성공: {file_path}")
    else:
      print("하락한 통화가 없거나 첫 실행일입니다. 분석을 종료합니다.")

  except Exception as e:
    print(f"프로세스 실행 중 오류 발생: {e}")

# 매일 정각 스케쥴링
schedule.every().day.at("00:00").do(job)

if __name__ == "__main__":
  # 테스트 시 주석 풀기
  #job()
  #time.sleep(5)
  #job()
  
  while True:
    schedule.run_pending()
    time.sleep(1)