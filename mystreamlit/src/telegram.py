import streamlit as st

import time 

import requests
# 📦 브라우저 쿠키 컨트롤러 라이브러리 추가
from streamlit_cookies_controller import CookieController

# 전역 쿠키 컨트롤러 인스턴스
controller = CookieController()



# ----------------- 🔒 1. 환경변수 및 보안 로드 -----------------
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"] 
except KeyError:
    st.error("🚨 보안 설정(st.secrets)에 텔레그램 필수 키가 누락되었습니다.")
    st.stop()

def get_allowed_time_remaining():
    """1분 제한 중 남은 시간(초)을 계산 (쿠키 기반)"""
    # 원본 파일 내 내부 구현 필요 부분
    last_send_time = controller.get("last_help_send_time")
    # ... (시간 계산 로직 구현) ...
    return 0 



def send_telegram_detail_alert(user_name, user_email, help_content):
    """사용자가 입력한 상세 내용을 텔레그램 API로 전송"""
    # ... (requests를 이용한 텔레그램 발송 로직 구현) ...
    pass


# ----------------- 🔒 1. 환경변수 및 보안 로드 -----------------
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"] 
    gemini_keys = st.secrets["gemini"]["api_keys"] 
except KeyError:
    st.error("🚨 보안 설정(st.secrets)에 '필수 키가 누락되었습니다.")
    st.stop()

# 쿠키 컨트롤러 객체 초기화
controller = CookieController()

def get_current_api_key():
    return next(st.session_state.key_pool)


# ----------------- ⏱️ 2. 1분 제한 계산 함수 -----------------
def get_allowed_time_remaining():
    """1분 제한 중 남은 시간(초)을 계산하는 함수 (쿠키 기반)"""
    last_send_time = controller.get("last_help_send_time")
    
    if last_send_time is None:
        return 0
    
    current_time = time.time()
    elapsed_time = current_time - float(last_send_time)
    
    LIMIT_SECONDS = 60  # 1분 제한
    
    if elapsed_time < LIMIT_SECONDS:
        return int(LIMIT_SECONDS - elapsed_time)
    return 0


# ----------------- 🚀 3. 텔레그램 발송 함수 -----------------
def send_telegram_detail_alert(user_name, user_email, help_content):
    """사용자가 입력한 상세 내용을 텔레그램 API로 전송"""
    remaining_seconds = get_allowed_time_remaining()
    if remaining_seconds > 0:
        st.error(f"⚠️ 도배 방지를 위해 {remaining_seconds}초 후에 다시 요청해 주세요.")
        return False

    # 🚨 하드코딩 주소 (중간에 오타가 섞이는 것을 방지하기 위해 완전한 실제 주소를 사용합니다)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    message = (
        "🚨 **[스트림릿 앱 Help 요청]**\n\n"
        f"👤 **요청자:** {user_name}\n"
        f"📧 **이메일:** {user_email}\n"
        f"📝 **문의 내용:**\n{help_content}"
    )
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
#        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            # 텔레그램 서버가 수신에 성공(200)했을 때만 락 쿠키를 굽습니다.
            controller.set("last_help_send_time", str(time.time()))
            return True
        else:
            # 실패 시 서버가 뱉은 날것의 에러 원인을 화면에 강제 출력합니다.
            st.error(f"❌ 텔레그램 서버 거부 원인: {response.text}")
            return False
    except Exception as e:
        st.error(f"알림 전송 중 서버 연결 오류 발생: {e}")
        return False 