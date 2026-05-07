import pandas as pd
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import os

class ExcelReportManager:
    def __init__(self):
        # [디자인 가이드]
        self.color_header = PatternFill(start_color="F2F4F7", end_color="F2F4F7", fill_type="solid")
        self.color_drop_bg = PatternFill(start_color="E6F4EA", end_color="E6F4EA", fill_type="solid") # 하락 (파스텔 그린)
        self.color_rise_bg = PatternFill(start_color="FCE8E6", end_color="FCE8E6", fill_type="solid") # 상승 (파스텔 레드)
        
        # 텍스트 스타일
        self.font_main = Font(name='Malgun Gothic', size=10, color="202124")
        self.font_header = Font(name='Malgun Gothic', size=10, color="202124", bold=True)
        self.font_link = Font(name='Malgun Gothic', size=10, color="0563C1", underline="single")
        
        self.border = Border(
            left=Side(style="thin", color="DADCE0"),
            right=Side(style="thin", color="DADCE0"),
            top=Side(style="thin", color="DADCE0"),
            bottom=Side(style="thin", color="DADCE0")
        )

    def create_report(self, analysis_details, news_info):
        """
        analysis_details: 3번(analyzer)의 결과 details 딕셔너리
        news_info: 1번(scraper)의 결과 또는 2번(DB)에서 꺼낸 뉴스 딕셔너리
        """
        # 5번 담당자(mailer.py)가 참조할 고정 파일명
        file_name = "exchange_report.xlsx"
        
        # 1. [오늘의 환율 현황] 데이터 구성
        rate_data = []
        for curr, data in analysis_details.items():
            rate_data.append({
                '통화명': curr,
                '현재 환율': data['today'],
                '전일 환율': data['yesterday'],
                '변동 수치': data['diff'],
                '변동률(%)': data['percent'],
                '등락 여부': '하락' if data['is_dropped'] else ('상승' if data['diff'] > 0 else '보합')
            })

        # 2. [관련 뉴스 기사] 데이터 구성 
        # mailer.py가 headers.index("n_title")로 찾으므로 컬럼명 엄수
        news_data = [{
            'n_title': news_info.get('title', '제목 없음'),
            'news_link': news_info.get('link', '#'),
            'created_at': news_info.get('date', datetime.now().strftime("%Y.%m.%d"))
        }]

        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            # 5번 mailer가 'active' 시트에서 뉴스를 읽기 쉽게 뉴스를 첫 번째 시트로 배치
            pd.DataFrame(news_data).to_excel(writer, index=False, sheet_name='관련 뉴스 기사')
            pd.DataFrame(rate_data).to_excel(writer, index=False, sheet_name='오늘의 환율 현황')
            
            # 스타일 및 서식 적용
            self._apply_style(writer.sheets['관련 뉴스 기사'], is_rate_sheet=False)
            self._apply_style(writer.sheets['오늘의 환율 현황'], is_rate_sheet=True, status_col=6)

        return file_name

    def _apply_style(self, sheet, is_rate_sheet, status_col=None):
        for col in range(1, sheet.max_column + 1):
            column_letter = get_column_letter(col)
            sheet.column_dimensions[column_letter].width = 18 if is_rate_sheet else 50
            
            header_cell = sheet.cell(row=1, column=col)
            header_cell.fill = self.color_header
            header_cell.font = self.font_header
            header_cell.alignment = Alignment(horizontal='center', vertical='center')
            header_cell.border = self.border

        for row in range(2, sheet.max_row + 1):
            status_val = sheet.cell(row=row, column=status_col).value if status_col else None
            
            for col in range(1, sheet.max_column + 1):
                cell = sheet.cell(row=row, column=col)
                cell.font = self.font_main
                cell.border = self.border
                cell.alignment = Alignment(horizontal='center' if is_rate_sheet else 'left', vertical='center', indent=1)

                # 조건부 서식: 환율 하락/상승 배경색
                if is_rate_sheet and status_val:
                    if status_val == '하락':
                        cell.fill = self.color_drop_bg
                    elif status_val == '상승':
                        cell.fill = self.color_rise_bg
                
                # 뉴스 링크 파란색 처리
                if not is_rate_sheet and col == 2:
                    cell.font = self.font_link

        return sheet

# --- 6번 메인 담당자 사용 예시 ---
if __name__ == "__main__":
    # 각 담당자들이 넘겨줄 최종 데이터 형태 시뮬레이션
    mock_analysis = {
        "USD": {"today": 1340.5, "yesterday": 1350.0, "diff": -9.5, "percent": "-0.7%", "is_dropped": True},
        "JPY(100)": {"today": 890.0, "yesterday": 885.5, "diff": 4.5, "percent": "0.51%", "is_dropped": False}
    }
    mock_news = {
        "title": "원/달러 환율, 미 고용지표 영향으로 하락 마감",
        "link": "https://kita.net/news/123",
        "date": "2026.05.07"
    }

    report = ExcelReportManager()
    saved_path = report.create_report(mock_analysis, mock_news)
    print(f"엑셀 리포트가 성공적으로 생성되었습니다: {saved_path}")