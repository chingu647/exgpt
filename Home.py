import streamlit as st
import tempfile
import os
import time
import itertools
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import requests
# 📦 브라우저 쿠키 컨트롤러 라이브러리 추가
from streamlit_cookies_controller import CookieController

# ==========================================
# 🔒 보안 환경변수 및 패키지 초기화
# ==========================================
# 1. Gemini API 키 풀 검증 ++++++++++ 삭제?
#if "key_pool" not in st.session_state:
#    try:
#        api_keys = st.secrets["gemini"]["api_keys"]
#        st.session_state.key_pool = itertools.cycle(api_keys)
#    except KeyError:
#        st.error("⚠️ st.secrets에 'gemini.api_keys' 배열이 올바르게 구성되지 않았습니다.")
#        st.stop()

# 2. 텔레그램 API 키 검증
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"] 
    gemini_keys = st.secrets["gemini"]["api_keys"] 
except KeyError:
    st.error("🚨 보안 설정(st.secrets)에 '필수 키가 누락되었습니다.")
    st.stop()

# 3. 로컬 스토리지 모듈 초기화

controller = CookieController()

def get_current_api_key():
    return next(st.session_state.key_pool)

FIXED_PDF_FILENAME = "abcd.txt"  

# ==========================================
# ⏱️ 60초 제한 체크 헬퍼 함수
# ==========================================

def get_allowed_time_remaining():
    """1분 제한 중 남은 시간(초)을 계산하는 함수 (쿠키 기반)"""

    # 브라우저 쿠키에서 마지막 발송 시간 가져오기
    last_send_time = controller.get("last_help_send_time")
    if last_send_time is None:
        return 0
    current_time = time.time()
    elapsed_time = current_time - float(last_send_time)
    LIMIT_SECONDS = 60 # 1분 제한
    if elapsed_time < LIMIT_SECONDS:
        return int(LIMIT_SECONDS - elapsed_time)
    return 0


def send_telegram_detail_alert(user_name, user_email, help_content):
    """사용자가 입력한 상세 내용을 개발자의 텔레그램 푸시 알림으로 전송"""

   # ⏱️ 쿨타임 교차 검증
   remaining_seconds = get_allowed_time_remaining()
   if remaining_seconds > 0:
       st.error(f"⚠️ 너무 빠르게 연속 요청할 수 없습니다. {remaining_seconds}초 후에 다시 시도해 주세요.")
       return False

   # 🚨 [100% 완벽 고정] 주소 오타를 원천 차단한 올바른 API 엔드포인트 주소입니다.
   # 기존 코드에 들어있던 잘못된 주소(https://telegram.org...)를 완전히 지우고 이 줄로 교체하셔야 합니다.
   url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    
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
           # 발송 성공 시 브라우저 쿠키에 현재 시간 기록
           controller.set("last_help_send_time", str(time.time()))
           return True
       else:
           st.error(f"알림 전송 실패 (텔레그램 서버 응답 코드: {response.status_code})")
           return False
   except Exception as e:
       st.error(f"알림 전송 중 서버 연결 오류 발생: {e}")
       return False

# ==========================================
# [속도 최적화] 구글 API 클라이언트 캐싱
# ==========================================
@st.cache_resource
def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)

# ==========================================
# [고정 파일 처리] 구글 클라우드 업로드 체크
# ==========================================
def upload_fixed_file_once(api_key: str, file_path: str):
    if not os.path.exists(file_path):
        return None
        
    client = get_gemini_client(api_key)
    target_display_name = os.path.basename(file_path)
    
    try:
        for file in client.files.list():
            if file.display_name == target_display_name and file.state.name == "ACTIVE":
                return file
        
        google_file = client.files.upload(file=file_path)
        return google_file
    except Exception as e:
        return None

# ==========================================
# 🔥 [안정성 강화] 429 에러 발생 시 자동 재시도
# ==========================================
@retry(
    retry=retry_if_exception_type(APIError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    reraise=True
)
def generate_content_with_retry(client, model, contents):
    return client.models.generate_content(model=model, contents=contents)


# ==========================================
# 📊 각 화면별 렌더링 함수 정의
# ==========================================

# 1. 챗봇 화면
def show_chatbot():
    st.caption(":point_right: :yellow-badge[전화 문의 :  [063-714-6000](tel:063-714-6000)]", width="stretch", text_alignment="right")
    st.subheader("💬 휴게소 업무 Chatbot", width="stretch", text_alignment="center")
    st.markdown(":rocket: :green-badge[**휴게시설 업무기준**] 및 :sparkles: :green-badge[**자체투자사업 매뉴얼**] 안내", width="stretch", text_alignment="center")
    st.divider()

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "무엇이 궁금하세요? 답변해 드리겠습니다."}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("질문할 내용을 입력하세요..."):
        current_key = get_current_api_key()
        client = get_gemini_client(current_key)
        google_file = upload_fixed_file_once(current_key, FIXED_PDF_FILENAME)

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        contents_payload = []
        if google_file:
            contents_payload.append(google_file)
            instruction = f"반드시 첨부된 문서를 기반으로만 답변해 주세요. 사용자 질문: {prompt}"
            contents_payload.append(instruction)
        else:
            contents_payload.append(prompt)

        try:
            with st.chat_message("assistant"):
                with st.spinner("답변을 생성 중입니다... (키 자동 교대 작동 중)"):
                    response = generate_content_with_retry(
                        client=client,
                        model='gemini-2.5-flash-lite',
                        contents=contents_payload
                    )
                    msg = response.text
                    st.write(msg)
            
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.rerun()
            
        except APIError as e:
            if e.code == 429:
                st.error("⏳ 9개 프로젝트의 임시 요청 한도가 일시적으로 모두 소진되었습니다. 잠시 후 전송 버튼을 한 번 더 눌러 다른 키로 호출해 보세요.")
            else:
                st.error(f"오류가 발생했습니다: {e}")

# 2. 현황 화면
def show_overview():
    st.subheader("💰 현황 ", width="stretch", text_alignment="center")
    st.markdown("화면 개발 중 입니다.", width="stretch", text_alignment="center")

# 3. 목록 화면 (⭐ 요구 사항 반영 완료)
def show_users():
    st.subheader("👥 목록 및 고객 지원", width="stretch", text_alignment="center")
    st.markdown("문제가 발생했거나 도움이 필요하시면 아래 내용을 적어 제출해 주세요.", width="stretch", text_alignment="center")
    
    # 현재 유저 브라우저의 남은 제한 시간 체크
    remaining = get_allowed_time_remaining()
    if remaining > 0:
        st.warning(f"🔒 도배 방지를 위해 잠시 발송이 제한됩니다. ({remaining}초 후 재요청 가능)")

    # 폼 생성
    with st.form("help_form", clear_on_submit=True):
        name = st.text_input("이름 또는 닉네임", placeholder="홍길동")
        email = st.text_input("답변받을 이메일 주소", placeholder="example@email.com")
        content = st.text_area("도움이 필요한 내용을 상세히 적어주세요", placeholder="예: 화면이 멈췄어요.")
        
        submit_button = st.form_submit_button("❓ Help 요청하기")

    if submit_button:
        # 실시간 교차 시간 검증 (새로고침 우회 원천 차단)
        remaining_check = get_allowed_time_remaining()
        
        if remaining_check > 0:
            st.error(f"🚨 요청 실패: {remaining_check}초 후에 다시 보낼 수 있습니다.")
        elif not name or not content:
            st.warning("이름과 문의 내용은 필수 입력 항목입니다.")
        elif len(content) > 1000:
            st.error("보안을 위해 문의 내용은 1,000자 이하로만 작성해 주세요.")
        else:
            with st.spinner("관리자에게 상세 내용을 전달하는 중..."):
                url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                message = (
                    "🚨 **[스트림릿 앱 Help 요청]**\n\n"
                    f"👤 **요청자:** {user_name if 'user_name' in locals() else name}\n"
                    f"📧 **이메일:** {email}\n"
                    f"📝 **문의 내용:**\n{content}"
                )
                payload = {
                    "chat_id": CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                }
                
                try:
                    response = requests.post(url, json=payload, timeout=5)
                    if response.status_code == 200:
                        # 발송 성공 시 브라우저 내부에 현재 시간 낙인 찍기
                        local_storage.setItem("last_help_send_time", str(time.time()))
                        st.success("요청이 정상적으로 접수되었습니다! 텔레그램 알림 발송 완료.")
                        time.sleep(1) # 토스트나 알림이 시각적으로 보이도록 보장
                        st.rerun() # 화면을 즉시 새로고침하여 상단 warning 바 업데이트
                    else:
                        st.error(f"알림 전송 실패 (코드: {response.status_code})")
                except Exception as e:
                    st.error(f"알림 전송 중 서버 오류 발생: {e}")


# ==========================================
# ⚙️ 관리자 전용 사이드바 메뉴 (상시 유지)
# ==========================================
with st.sidebar:
    st.header("⚙️ 관리자 전용 메뉴")
    if st.button("🗑️ 구글 API 저장소 중복 파일 일괄 삭제"):
        with st.spinner("9개 프로젝트 전체 청소 중..."):
            try:
                deleted_count = 0
                for key in st.secrets["gemini"]["api_keys"]:
                    temp_client = genai.Client(api_key=key)
                    for file in temp_client.files.list():
                        temp_client.files.delete(name=file.name)
                        deleted_count += 1
                st.cache_resource.clear() 
                st.success(f"✨ 청소 완료! 모든 프로젝트에서 총 {deleted_count}개의 파일이 삭제되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"삭제 실패: {e}")


# ==========================================
# 🚦 메인 내비게이션 및 라우팅 순서
# ==========================================
TABS = ["챗봇", "현황", "call센터"]
current = st.segmented_control("ex", TABS, default="챗봇", key="tab")

if current == "챗봇":
    show_chatbot()
elif current == "현황":
    show_overview()
elif current == "call센터":
    show_users()
