import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.chart import LineChart, Reference
from datetime import datetime

class ExcelReportManager:
    def __init__(self):
        # 디자인
        self.color_header = PatternFill(start_color="EBF1F6", end_color="EBF1F6", fill_type="solid") # 연한 블루그레이
        self.color_drop = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")   # 연한 파스텔 그린 (하락/매수적기)
        self.color_rise = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")   # 연한 파스텔 오렌지 (상승)
        self.text_main = Font(name='Pretendard', size=11, color="2C3E50", bold=False) # 가시성 좋은 어두운 색
        self.text_header = Font(name='Pretendard', size=11, color="2C3E50", bold=True)
        
        # 테두리 설정
        thin_border = Side(border_style="thin", color="D5D8DC")
        self.border = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)

    def create_report(self, raw_data):
        """
        raw_data: 2번 담당자(DB)로부터 받은 전체 데이터 리스트
        형식 예시: [{'date': '2024-05-01', 'rate': 1350.5}, ...]
        """
        # 1. 데이터 가공 (Pandas 활용)
        df = pd.DataFrame(raw_data)
        df = df.sort_values(by='date', ascending=True) # 날짜순 정렬

        # [가상 장바구니 컬럼 추가]
        df['iPhone_15_Pro($999)'] = (df['rate'] * 999).round(0)
        df['AirPods_Pro($249)'] = (df['rate'] * 249).round(0)
        
        # 변동폭 계산
        df['diff'] = df['rate'].diff().fillna(0)

        file_path = f"Exchange_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        # 2. 엑셀 파일 생성 및 스타일링
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='환율 리포트')
            workbook = writer.book
            sheet = writer.sheets['환율 리포트']

            # 헤더 스타일 적용
            for col_num, value in enumerate(df.columns):
                cell = sheet.cell(row=1, column=col_num + 1)
                cell.fill = self.color_header
                cell.font = self.text_header
                cell.alignment = Alignment(horizontal='center')
                cell.border = self.border

            # 데이터 행 스타일 및 [신호등 적용]
            for row_num in range(2, len(df) + 2):
                diff_value = sheet.cell(row=row_num, column=4).value # diff 컬럼 위치
                
                # 행 전체 기본 스타일
                for col_num in range(1, len(df.columns) + 1):
                    cell = sheet.cell(row=row_num, column=col_num)
                    cell.font = self.text_main
                    cell.border = self.border
                    cell.alignment = Alignment(horizontal='right')
                    
                    # [신호등 로직] 환율이 하락했으면 해당 행을 파스텔 그린으로
                    if diff_value < 0:
                        cell.fill = self.color_drop
                    elif diff_value > 0:
                        cell.fill = self.color_rise

            # 열 너비 조정
            for column_cells in sheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                sheet.column_dimensions[column_cells[0].column_letter].width = length + 5

            # [변동 차트 추가]
            chart = LineChart()
            chart.title = "최근 환율 변동 추이"
            chart.style = 13
            chart.y_axis.title = "원화(KRW)"
            chart.x_axis.title = "날짜"
            
            data_ref = Reference(sheet, min_col=2, min_row=1, max_row=len(df)+1) # rate 컬럼
            chart.add_data(data_ref, titles_from_data=True)
            sheet.add_chart(chart, "H2") # 엑셀 우측에 차트 배치

        return file_path

# --- 테스트용 (실제 구동 시 2번 담당자의 데이터를 받게 됨) ---
if __name__ == "__main__":
    dummy_data = [
        {'date': '2024-05-01', 'rate': 1360.5},
        {'date': '2024-05-02', 'rate': 1365.2},
        {'date': '2024-05-03', 'rate': 1358.0},
        {'date': '2024-05-04', 'rate': 1355.5},
        {'date': '2024-05-05', 'rate': 1352.1},
        {'date': '2024-05-06', 'rate': 1362.4},
        {'date': '2024-05-07', 'rate': 1350.0},
    ]
    
    gen = ExcelReportManager()
    path = gen.create_report(dummy_data)
    print(f"리포트 생성 완료: {path}")