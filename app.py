from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from datetime import datetime, timedelta
import database
import analyzer
import csv_gen
import mailer

app = Flask(__name__)
app.secret_key = "secret_key_for_session" # 알림 메시지(flash)용

# 데이터 규격 맞추기 함수 (기존 main.py에서 가져옴)
def list_to_dict(rate_list):
    result = {}
    for item in rate_list:
        unit = item.get('cur_unit').split('(')[0]
        val = float(item.get('deal_bas_r').replace(',', ''))
        result[unit] = val
    return result

@app.route('/')
def index():
    """1. 메인 화면: 등락 요약"""
    today_str = datetime.now().strftime("%Y.%m.%d")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y.%m.%d")
    
    today_rates, _ = database.get_data_by_date(today_str)
    yesterday_rates, _ = database.get_data_by_date(yesterday_str)
    
    summary = None
    if today_rates and yesterday_rates:
        t_dict = list_to_dict(today_rates)
        y_dict = list_to_dict(yesterday_rates)
        analysis = analyzer.check_currency_drop(t_dict, y_dict)
        summary = analysis['details']
        
    return render_template('index.html', summary=summary, now=datetime.now())

@app.route('/details')
def details():
    """2. 상세 분석 화면: 초기 전체 출력 및 조건부 날짜 검색"""
    # HTML의 <input name="search_date">에서 값을 가져옵니다.
    search_date = request.args.get('search_date')
    
    if search_date:
        # [A] 검색어가 있는 경우: 해당 날짜만 필터링
        formatted_date = search_date.replace('-', '.')
        # database.py의 함수를 사용하여 특정 날짜 데이터만 가져옴
        rates, _ = database.get_data_by_date(formatted_date)
    else:
        # [B] 검색어가 없는 경우 (맨 처음 접속 시): DB 전체 정보 조회
        # .sort("date", -1)을 붙여주면 최신 날짜가 맨 위로 옵니다.
        rates = list(database.rate_col.find().sort("date", -1))
        
    return render_template('details.html', rates=rates)

@app.route('/download')
def download():
    """엑셀 다운로드 처리"""
    # 현재 화면의 데이터를 기반으로 엑셀 생성로직 연결
    # 테스트용으로 오늘자 데이터 기준 생성
    today_str = datetime.now().strftime("%Y.%m.%d")
    today_rates, _ = database.get_data_by_date(today_str)
    
    # analyzer와 csv_gen을 거쳐 파일 생성
    # ... (기본 main.py의 리포트 생성 로직 적용)
    file_path = "exchange_report.xlsx" # 생성된 경로
    return send_file(file_path, as_attachment=True)

@app.route('/email', methods=['GET', 'POST'])
def send_email():
    """3. 이메일 전송 화면"""
    if request.method == 'POST':
        email_addr = request.form.get('email')
        content = request.form.get('content')
        file_path = "exchange_report.xlsx" # 미리 생성된 파일 혹은 즉시 생성
        
        try:
            mailer.send_mail_custom(email_addr, content, file_path) # mailer 함수 수정 필요
            flash("이메일 전송에 성공했습니다!")
        except Exception as e:
            flash(f"전송 실패: {e}")
        return redirect(url_for('index'))
        
    return render_template('email.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)