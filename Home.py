import streamlit as st
import requests
import time
from streamlit_cookies_controller import CookieController

# ----------------- 🔒 1. 환경변수 및 보안 로드 -----------------
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"]
except KeyError as e:
    st.error(f"🚨 보안 설정(st.secrets)에 필수 키가 누락되었습니다: {e}")
    st.stop()

# 쿠키 컨트롤러 객체 초기화
controller = CookieController()

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
    url = "https://telegram.org"
    
    message = (
        "🚨 **[스트림릿 앱 Help 요청]**\n\n"
        f"👤 **요청자:** {user_name}\n"
        f"📧 **이메일:** {user_email}\n"
        f"📝 **문의 내용:**\n{help_content}"
    )
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
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

# ----------------- 💻 4. UI 레이아웃 및 폼 제어 -----------------
def show_users():
    st.subheader("👨‍💻 고객 지원 및 Help 센터")
    st.write("문제가 발생했거나 도움이 필요하시면 아래 내용을 적어 제출해 주세요.")

    # 실시간 제한 시간 안내 바
    remaining = get_allowed_time_remaining()
    if remaining > 0:
        st.warning(f"🔒 도배 방지를 위해 잠시 발송이 제한됩니다. (남은 시간: {remaining}초)")

    # 폼 키에 타임스탬프를 섞어 StreamlitAPIException(중복 폼 에러)을 원천 차단합니다.
    form_id = f"help_form_session_{int(time.time() // 60)}"
    
    with st.form(key=form_id, clear_on_submit=True):
        name = st.text_input("이름 또는 닉네임", placeholder="홍길동")
        email = st.text_input("답변받을 이메일 주소", placeholder="example@email.com")
        content = st.text_area("도움이 필요한 내용을 상세히 적어주세요", placeholder="예: 화면이 멈췄어요.")
        
        submit_button = st.form_submit_button("❓ Help 요청하기")

    # ⚠️ 중요: submit_button 체크 로직은 with st.form과 같은 들여쓰기 라인(외부)에 위치해야 정상 작동합니다.
    if submit_button:
        remaining_check = get_allowed_time_remaining()
        
        if remaining_check > 0:
            st.error(f"🚨 요청 실패: {remaining_check}초 후에 다시 보낼 수 있습니다.")
        elif not name or not content:
            st.warning("이름과 문의 내용은 필수 입력 항목입니다.")
        elif len(content) > 1000:
            st.error("문의 내용은 1,000자 이하로 작성해 주세요.")
        else:
            with st.spinner("관리자에게 상세 내용을 안전하게 전달하는 중..."):
                success = send_telegram_detail_alert(name, email, content)
                if success:
                    st.success("요청이 정상적으로 접수되었습니다! 개발자 알림 발송 완료.")
                    time.sleep(10) # 성공 메시지를 잠시 보여주기 위함
                    st.rerun()

# ----------------- 🚀 5. 메인 실행부 -----------------
if __name__ == "__main__":
    show_users()
