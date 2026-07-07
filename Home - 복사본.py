import streamlit as st
import tempfile
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError

# ==========================================
# [보안 및 설정] st.secrets를 통해 안전하게 키 가져오기
# ==========================================
FIXED_GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
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
# 메인 화면 구성 및 챗 초기화
# ==========================================
st.title("💬 전북 Chatbot")
st.caption("🚀 고정 지침 문서를 기반으로 답변하는 안내 챗봇입니다.")

# ------------------------------------------
# 🔥 [임시 추가] 스트림릿 웹에서 구글 서버 파일 일괄 청소하는 버튼
# ------------------------------------------
with st.sidebar: # 관리 편의를 위해 사이드바에 배치합니다.
    st.header("⚙️ 관리자 전용 메뉴")
    if st.button("🗑️ 구글 API 저장소 중복 파일 일괄 삭제"):
        with st.spinner("구글 서버 청소 중... 잠시만 기다려주세요."):
            try:
                client = genai.Client(api_key=FIXED_GOOGLE_API_KEY)
                deleted_count = 0
                for file in client.files.list():
                    client.files.delete(name=file.name)
                    deleted_count += 1
                
                # 중복 업로드 방지 캐시 초기화
                st.cache_resource.clear() 
                st.success(f"✨ 청소 완료! 총 {deleted_count}개의 파일이 구글 서버에서 영구 삭제되었습니다.")
                st.rerun() # 화면 새로고침
            except Exception as e:
                st.error(f"삭제 실패: {e}")
# ------------------------------------------

google_file = upload_fixed_file_once(FIXED_GOOGLE_API_KEY, FIXED_PDF_FILENAME)

if not google_file:
    st.warning(f"⚠️ 관리자 알림: 고정할 '{FIXED_PDF_FILENAME}' 파일이 서버 환경에 없거나 업로드에 실패했습니다.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요? 준비된 문서를 바탕으로 친절히 답변해 드리겠습니다."}]

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
            response_stream = client.models.generate_content_stream(
                model='gemini-2.5-flash-lite',
                contents=contents_payload,
            )
            msg = st.write_stream(chunk.text for chunk in response_stream)
        
        st.session_state.messages.append({"role": "assistant", "content": msg})
        
    except APIError as e:
        if e.code == 429:
            st.error("⏳ 현재 사용량이 많아 요청 한도를 초과했습니다. 잠시 후 다시 입력해 주세요.")
        else:
            st.error(f"오류가 발생했습니다: {e}")
