import streamlit as st
import time 
import requests

# ----------------- 🔒 1. 환경변수 및 보안 로드 -----------------
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"] 
    gemini_keys = st.secrets["gemini"]["api_keys"] 
except KeyError:
    st.error("🚨 보안 설정(st.secrets)에 필수 키가 누락되었습니다.")
    st.stop()


# ----------------- ⏱️ 2. 1분 제한 계산 함수 -----------------
def get_allowed_time_remaining():
    """1분 제한 중 남은 시간(초)을 계산하는 함수 (세션 상태 기반)"""
    # ⚠️ [해결] 에러를 유발하는 쿠키 대신, 독립된 세션 금고를 활용합니다.
    last_send_time = st.session_state.get("last_help_send_time")
    
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

    # 🚨 하드코딩 주소
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    message = (
        "🚨 **[스트림릿 앱 Help 요청]**\n\n"
        f"👤 **요청자:** {user_name}\n"
        f"📧 **이메일:** {user_email}\n"
        f"📝 **문의 내용:**\n{help_content}"
    )
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            # ⚠️ [해결] 발송 성공 시 세션 상태에 발송 시각 박제
            st.session_state["last_help_send_time"] = time.time()
            return True
        else:
            st.error(f"❌ 텔레그램 서버 거부 원인: {response.text}")
            return False
    except Exception as e:
        st.error(f"알림 전송 중 서버 연결 오류 발생: {e}")
        return False

