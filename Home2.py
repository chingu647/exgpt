import streamlit as st
import tempfile
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError

# ==========================================
# [보안 및 설정] st.secrets를 통해 안전하게 키 가져오기
# ==========================================
# 소스 코드에는 키가 노출되지 않으며, 환경 설정에 등록한 값을 동적으로 가져옵니다.
FIXED_GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]

# RAG용 고정 PDF 파일 이름 (코드와 같은 폴더에 위치해야 함)
FIXED_PDF_FILENAME = "abc.pdf"  


# ==========================================
# [CSS] 우측 햄버거 메뉴 및 배포 버튼 완벽 삭제
# ==========================================
hide_elements_style = """
<style>
[data-testid="stToolbar"] { display: none !important; }
header[data-testid="stHeader"] { background-color: transparent !important; background: transparent !important; }
footer { visibility: hidden; }
</style>
"""
st.markdown(hide_elements_style, unsafe_allow_html=True)


# ==========================================
# [속도 최적화] 구글 API 클라이언트 캐싱
# ==========================================
@st.cache_resource
def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)


# ==========================================
# [고정 파일 처리] 서버 시작 시 딱 1번만 구글 서버에 등록
# ==========================================
@st.cache_resource
def upload_fixed_file_once(api_key: str, file_path: str):
    if not os.path.exists(file_path):
        return None, None
        
    client = genai.Client(api_key=api_key)
    try:
        google_file = client.files.upload(file=file_path)
        return google_file.uri, google_file.mime_type
    except Exception:
        return None, None


# ==========================================
# 메인 화면 구성 및 챗 초기화
# ==========================================
st.title("💬 전북 RAG Chatbot")
st.caption("🚀 고정 지침 문서를 기반으로 답변하는 안내 챗봇입니다.")

# 비밀키 기반으로 구글 파일 자동 등록
file_uri, file_mime = upload_fixed_file_once(FIXED_GOOGLE_API_KEY, FIXED_PDF_FILENAME)

if not file_uri:
    st.warning(f"⚠️ 관리자 알림: 고정할 '{FIXED_PDF_FILENAME}' 파일이 소스 코드 폴더에 존재하지 않습니다.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요? 준비된 문서를 바탕으로 친절히 답변해 드리겠습니다."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ==========================================
# 사용자 채팅 입력 및 처리
# ==========================================
if prompt := st.chat_input("질문할 내용을 입력하세요..."):
    
    # 캐싱된 클라이언트 호출
    client = get_gemini_client(FIXED_GOOGLE_API_KEY)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    contents_payload = []
    
    if file_uri:
        file_part = types.Part.from_uri(file_uri=file_uri, mime_type=file_mime)
        contents_payload.append(file_part)
        instruction = f"반드시 첨부된 문서를 기반으로만 답변해 주세요. 사용자 질문: {prompt}"
        contents_payload.append(instruction)
    else:
        contents_payload.append(prompt)

    try:
        with st.chat_message("assistant"):
            response_stream = client.models.generate_content_stream(
                model='gemini-2.5-flash-lite',
                contents=contents_payload,
            )
            msg = st.write_stream(chunk.text for chunk in response_stream)
        
        st.session_state.messages.append({"role": "assistant", "content": msg})
        
    except APIError as e:
        if e.code == 429:
            st.error("⏳ 현재 사용자가 많아 요청 한도를 초과했습니다. 잠시 후 다시 입력해 주세요.")
        else:
            st.error(f"오류가 발생했습니다: {e}")