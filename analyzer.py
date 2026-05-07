# 메인 화면에서 호출하여 사용 (import)
# 메인 화면에서 환율 넣어줌   
    # 메인에서 넘겨 주었으면 하는 데이터 형식
    # today_data = {"USD": 1340.5, "JPY": 890.0, "EUR": 1450.2}
    # yesterday_data = {"USD": 1350.0, "JPY": 885.5, "EUR": 1460.0}
    # result = analyzer.check_currency_drop(today_data, yesterday_data)
# 각 통화별 하락 여부 및 퍼센트 반환

# 환율 변동에 따른 비교
def check_currency_drop(today_rates, yesterday_rates):

    analysis_result = {
                        "is_any_dropped": False,   # 하나라도 하락했는가?
                        "details": {}              # 각 통화별 변경 퍼센트
    }
    
    # 비교할 통화 목록
    currencies = ["USD", "JPY", "EUR"]
    
    for curr in currencies:
        today     = float(today_rates.get(curr, 0))
        yesterday = float(yesterday_rates.get(curr, 0))
        
        # 하락 여부 판단
        is_dropped = today < yesterday   

        # 변동 금액 (차이)          
        diff = round(today - yesterday, 2)   
        
        # 변동 퍼센트 계산 ((오늘-어제)/어제 * 100)
            # 마이너스 = 하락, 플러스 = 상승
        try:
            percent = round(((today - yesterday) / yesterday) * 100, 2)
        except ZeroDivisionError:
            # 어제 환율이 0일 경우(에러 발생) 
            percent = 0.0
        except Exception as e:
            print(f"[에러 발생] : {e}")

        # 하나라도 하락했다면 전체 결과 True로 저장
        if is_dropped:
            analysis_result["is_any_dropped"] = True

        # 상세 결과 저장
        analysis_result["details"][curr] = {
            "today"     : today,
            "yesterday" : yesterday,
            "diff"      : diff,
            "percent"   : f"{percent}%",
            "is_dropped": is_dropped
        }
    
    return analysis_result