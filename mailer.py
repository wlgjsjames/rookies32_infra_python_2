import os
from dotenv import load_dotenv
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

load_dotenv()

def send_mail(file_path, content="", to_email=None):
    """
    app.py 또는 main.py에서 호출하여 메일을 발송합니다.
    :param content: 메일 본문에 들어갈 텍스트 내용
    :param file_path: 첨부할 엑셀 파일의 경로
    :param to_email: 수신자 주소 (None일 경우 환경변수의 EMAIL_USER에게 발송)
    """
    # smtp 접속정보 load
    user_email = os.getenv("EMAIL_USER")
    user_password = os.getenv("EMAIL_PASS")
    smtp_server = os.getenv("SMTP_SVR")
    smtp_port = int(os.getenv("SMTP_PORT"))
    
    # 수신자가 지정되지 않았다면 자기 자신에게 발송
    target_email = to_email if to_email else user_email

    msg = MIMEMultipart()
    msg["Subject"] = "[환율 분석 리포트] 요청하신 데이터가 도착했습니다."
    msg["From"] = user_email
    msg["To"] = target_email

    # 1. 메일 본문 추가 (app.py에서 넘어온 content 사용)
    msg.attach(MIMEText(content, 'plain'))

    # 2. 엑셀 파일 첨부
    if not os.path.exists(file_path):
        print(f"오류: 첨부할 파일이 존재하지 않습니다. ({file_path})")
        return False

    try:
        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", 
            f"attachment; filename={os.path.basename(file_path)}"
        )
        msg.attach(part)

        # 3. 서버 접속 및 발송
        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(user_email, user_password)
            server.send_message(msg)
            print(f"📧 메일 발송 성공 -> {target_email}")
            return True
            
    except Exception as e:
        print(f"❌ 메일 발송 중 오류 발생: {e}")
        return False

# 테스트 실행 시
if __name__ == "__main__":
    # 테스트용 데이터
    test_content = "테스트 본문 내용입니다."
    test_file = "exchange_report.xlsx" # 실제 존재하는 파일명으로 변경 필요
    # send_mail(test_content, test_file)