import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, Reference
from datetime import datetime
import os

class ExcelReportManager:
    def __init__(self):
        # [디자인 가이드] 파스텔톤 & 가시성 높은 어두운 텍스트
        self.color_header = PatternFill(start_color="F2F4F7", end_color="F2F4F7", fill_type="solid")
        self.color_drop_bg = PatternFill(start_color="E6F4EA", end_color="E6F4EA", fill_type="solid") # 연한 녹색 (매수적기)
        self.color_rise_bg = PatternFill(start_color="FCE8E6", end_color="FCE8E6", fill_type="solid") # 연한 빨간색 (보류)
        
        self.font_main = Font(name='Malgun Gothic', size=10, color="202124")
        self.font_header = Font(name='Malgun Gothic', size=10, color="202124", bold=True)
        self.font_link = Font(name='Malgun Gothic', size=10, color="0563C1", underline="single")
        
        self.border = Border(
            left=Side(style="thin", color="DADCE0"),
            right=Side(style="thin", color="DADCE0"),
            top=Side(style="thin", color="DADCE0"),
            bottom=Side(style="thin", color="DADCE0")
        )

    def create_report(self, analysis_details, news_info, history_data=None):
        """
        1. analysis_details: 3번(analyzer)의 결과 details 딕셔너리
        2. news_info: 1번(scraper)의 결과 딕셔너리
        3. history_data: 2번(DB)에서 가져온 최근 7일치 환율 리스트 (차트용)
        """
        file_name = "exchange_report.xlsx"
        
        # --- [기능 2] 직구 시뮬레이션 가공 ---
        rate_data = []
        for curr, data in analysis_details.items():
            today_rate = data['today']
            rate_data.append({
                '통화명': curr,
                '현재 환율': today_rate,
                '전일 환율': data['yesterday'],
                '변동 수치': data['diff'],
                '변동률(%)': data['percent'],
                '등락 여부': '하락' if data['is_dropped'] else ('상승' if data['diff'] > 0 else '보합'),
                'iPhone 15 Pro ($999)': f"{int(today_rate * 999):,}원",
                'AirPods Pro ($249)': f"{int(today_rate * 249):,}원"
            })

        # --- [기능 4] 관련 뉴스 기사 가공 (mailer.py 연동용) ---
        news_data = [{
            'n_title': news_info.get('title', '제목 없음'), # mailer.py 핵심 키
            'news_link': news_info.get('link', '#'),
            'created_at': news_info.get('date', datetime.now().strftime("%Y.%m.%d"))
        }]

        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            # 시트 생성 (mailer.py가 읽기 쉽도록 뉴스를 첫 번째 시트로)
            pd.DataFrame(news_data).to_excel(writer, index=False, sheet_name='관련 뉴스 기사')
            pd.DataFrame(rate_data).to_excel(writer, index=False, sheet_name='오늘의 환율 현황')
            
            # 히스토리 데이터가 있다면 차트용 시트 추가
            if history_data:
                pd.DataFrame(history_data).to_excel(writer, index=False, sheet_name='데이터 트렌드')

            # 스타일 및 기능 적용
            self._apply_news_style(writer.sheets['관련 뉴스 기사'])
            self._apply_rate_style(writer.sheets['오늘의 환율 현황'])
            
            # --- [기능 3] 미니 변동 차트 삽입 ---
            if history_data:
                self._add_trend_chart(writer.sheets['오늘의 환율 현황'], writer.sheets['데이터 트렌드'], len(history_data))

        return file_name

    def _apply_news_style(self, sheet):
        """뉴스 시트 스타일링 (5번 mailer.py 최적화)"""
        for col in range(1, sheet.max_column + 1):
            column_letter = get_column_letter(col)
            sheet.column_dimensions[column_letter].width = 60 if col == 1 else 30
            
            cell = sheet.cell(row=1, column=col)
            cell.fill = self.color_header
            cell.font = self.font_header
            cell.alignment = Alignment(horizontal='center')
            cell.border = self.border

        for row in range(2, sheet.max_row + 1):
            for col in range(1, sheet.max_column + 1):
                cell = sheet.cell(row=row, column=col)
                cell.font = self.font_main if col != 2 else self.font_link
                cell.border = self.border
                cell.alignment = Alignment(horizontal='left', indent=1)

    def _apply_rate_style(self, sheet):
        """환율 시트 스타일링 ([기능 1] 신호등 포함)"""
        for col in range(1, sheet.max_column + 1):
            column_letter = get_column_letter(col)
            sheet.column_dimensions[column_letter].width = 18
            
            cell = sheet.cell(row=1, column=col)
            cell.fill = self.color_header
            cell.font = self.font_header
            cell.alignment = Alignment(horizontal='center')
            cell.border = self.border

        # 데이터 행 스타일 및 [신호등] 적용
        for row in range(2, sheet.max_row + 1):
            status_val = sheet.cell(row=row, column=6).value # '등락 여부' 컬럼
            
            for col in range(1, sheet.max_column + 1):
                cell = sheet.cell(row=row, column=col)
                cell.font = self.font_main
                cell.border = self.border
                cell.alignment = Alignment(horizontal='center')

                # [신호등 로직] 배경색 자동 지정
                if status_val == '하락':
                    cell.fill = self.color_drop_bg
                elif status_val == '상승':
                    cell.fill = self.color_rise_bg

    def _add_trend_chart(self, target_sheet, data_sheet, data_count):
        """[기능 3] 데이터 트렌드 차트 생성"""
        chart = LineChart()
        chart.title = "최근 7일 환율 추이"
        chart.style = 13
        chart.y_axis.title = "환율 (KRW)"
        chart.x_axis.title = "수집일"
        
        # 데이터 영역 (데이터 트렌드 시트의 2열(환율값) 참조)
        data_ref = Reference(data_sheet, min_col=2, min_row=1, max_row=data_count + 1)
        # 카테고리 영역 (1열 날짜 참조)
        cats_ref = Reference(data_sheet, min_col=1, min_row=2, max_row=data_count + 1)
        
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats_ref)
        
        # 차트 위치 (환율 현황 시트의 우측 상단)
        target_sheet.add_chart(chart, "J2")

# --- 통합 테스트용 코드 ---
if __name__ == "__main__":
    # 3번 analyzer 데이터
    mock_analysis = {
        "USD": {"today": 1340.5, "yesterday": 1350.0, "diff": -9.5, "percent": "-0.7%", "is_dropped": True},
        "JPY(100)": {"today": 890.0, "yesterday": 885.5, "diff": 4.5, "percent": "0.51%", "is_dropped": False},
        "EUR": {"today": 1455.0, "yesterday": 1455.0, "diff": 0, "percent": "0.0%", "is_dropped": False}
    }
    # 1번 scraper 뉴스 데이터
    mock_news = {
        "title": "금일 환율 하락세, 해외 직구족 늘어날까",
        "link": "https://kita.net/news/123",
        "date": "2026.05.07 10:00"
    }
    # 2번 database 히스토리 데이터 (최근 7일)
    mock_history = [
        {"date": "05.01", "USD": 1360}, {"date": "05.02", "USD": 1358},
        {"date": "05.03", "USD": 1362}, {"date": "05.04", "USD": 1355},
        {"date": "05.05", "USD": 1352}, {"date": "05.06", "USD": 1350},
        {"date": "05.07", "USD": 1340}
    ]

    report = ExcelReportManager()
    path = report.create_report(mock_analysis, mock_news, mock_history)
    print(f"통합 리포트 생성 완료: {os.path.abspath(path)}")