import streamlit as st
import tempfile
import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ==========================================
# [보안 및 설정] st.secrets를 통해 안전하게 키 가져오기
# ==========================================
FIXED_GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
FIXED_PDF_FILENAME = "abcd.txt"  


# ==========================================
# [CSS] 우측 햄버거 메뉴 및 배포 버튼 완벽 삭제
# ==========================================
# hide_elements_style = """
# <style>
# [data-testid="stToolbar"] { display: none !important; }
# header[data-testid="stHeader"] { background-color: transparent !important; background: transparent !important; }
# footer { visibility: hidden; }
# </style>
# """
# st.markdown(hide_elements_style, unsafe_allow_html=True)


# ==========================================
# [속도 최적화] 구글 API 클라이언트 캐싱
# ==========================================
@st.cache_resource
def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)


# ==========================================
# [고정 파일 처리] 중복 업로드 방지 및 기존 파일 재사용
# ==========================================
@st.cache_resource
def upload_fixed_file_once(api_key: str, file_path: str):
    if not os.path.exists(file_path):
        return None
        
    client = genai.Client(api_key=api_key)
    target_display_name = os.path.basename(file_path)
    
    try:
        for file in client.files.list():
            if file.display_name == target_display_name and file.state.name == "ACTIVE":
                return file
        
        google_file = client.files.upload(file=file_path)
        return google_file
    except Exception as e:
        st.error(f"⚠️ 파일 업로드 확인 중 오류 발생: {e}")
        return None


# ==========================================
# 🔥 [안정성 강화] 429 에러 발생 시 자동 재시도 함수 (지수 백오프)
# ==========================================
# 429 APIError가 발생하면 2초, 4초, 8초 간격을 두고 최대 3번 자동으로 재시도합니다.
@retry(
    retry=retry_if_exception_type(APIError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    reraise=True
)
def generate_content_with_retry(client, model, contents):
    # 스트리밍 방식은 중간 실패 시 백오프 처리가 까다로우므로 
    # 무료 티어 안정성을 위해 일반 생성(generate_content) 방식으로 처리합니다.
    return client.models.generate_content(model=model, contents=contents)


# ==========================================
# 메인 화면 구성 및 챗 초기화
# ==========================================
st.subheader("💬 휴게소 업무 Chatbot")
st.metric("한국도로공사 전북본부",":rocket: :green[**휴게시설 업무기준**] 및 :sunglasses: :green[**자체투자사업 매뉴얼**] 안내", "작성일자 : 2026.07.08.")

st.divider()

# [임시 관리 메뉴] 저장소 비우기 사이드바
with st.sidebar:
    st.header("⚙️ 관리자 전용 메뉴")
    if st.button("🗑️ 구글 API 저장소 중복 파일 일괄 삭제"):
        with st.spinner("구글 서버 청소 중..."):
            try:
                client = genai.Client(api_key=FIXED_GOOGLE_API_KEY)
                deleted_count = 0
                for file in client.files.list():
                    client.files.delete(name=file.name)
                    deleted_count += 1
                st.cache_resource.clear() 
                st.success(f"✨ 청소 완료! 총 {deleted_count}개의 파일이 삭제되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"삭제 실패: {e}")

google_file = upload_fixed_file_once(FIXED_GOOGLE_API_KEY, FIXED_PDF_FILENAME)

if not google_file:
    st.warning(f"⚠️ 관리자 알림: 고정할 '{FIXED_PDF_FILENAME}' 파일이 서버 환경에 없거나 업로드에 실패했습니다.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "무엇이 궁금하세요? 답변해 드리겠습니다."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ==========================================
# 사용자 채팅 입력 및 처리
# ==========================================
if prompt := st.chat_input("질문할 내용을 입력하세요..."):
    
    client = get_gemini_client(FIXED_GOOGLE_API_KEY)
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
            with st.spinner("답변을 생성 중입니다... (무료 한도 초과 시 자동 재시도 중)"):
                # 안전하게 재시도 로직이 적용된 함수 호출
                response = generate_content_with_retry(
                    client=client,
                    model='gemini-2.5-flash-lite',
                    contents=contents_payload
                )
                msg = response.text
                st.write(msg)
        
        st.session_state.messages.append({"role": "assistant", "content": msg})
        
    except APIError as e:
        if e.code == 429:
            st.error("⏳ 구글 API 무료 제한을 완전히 초과했습니다. 약 1분 뒤에 다시 시도해 주세요. 해결을 원하시면 Google AI Studio에서 결제 연동(유료 티어 전환)을 추천합니다.")
        else:
            st.error(f"오류가 발생했습니다: {e}")
