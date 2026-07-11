import streamlit as st
import os

from google import genai
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type



# ==========================================
# [1. 속도 최적화] 구글 API 클라이언트 캐싱
# ==========================================
@st.cache_resource
def get_gemini_client(api_key: str):
    """구글 API 클라이언트 캐싱"""
    return genai.Client(api_key=api_key)


# ==========================================
# [2. 고정 파일 처리] 구글 클라우드 업로드 체크
# ==========================================
def upload_fixed_file_once(api_key: str, file_path: str):
    """고정 파일 구글 클라우드 업로드 체크"""
    if not os.path.exists(file_path):
        return None
        
    client = get_gemini_client(api_key)
    target_display_name = os.path.basename(file_path)
    
    try:
        for file in client.files.list():
            if file.display_name == target_display_name and file.state.name == "ACTIVE":
                return file
        
        return client.files.upload(file=file_path)
    except Exception as e:
        return None


# ==========================================
# 🔥 [3. 안정성 강화] 429 에러 발생 시 자동 재시도
# ==========================================
@retry(
    retry=retry_if_exception_type(APIError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    reraise=True
)

def generate_content_with_retry(client, model, contents):
    """429 에러 발생 시 자동 재시도 로직"""
    return client.models.generate_content(model=model, contents=contents)



def clean_all_projects():
    """모든 프로젝트의 구글 클라우드 파일 삭제 (관리자용)"""
    deleted_count = 0
    for key in st.secrets["gemini"]["api_keys"]:
        temp_client = genai.Client(api_key=key)
        for file in temp_client.files.list():
            temp_client.files.delete(name=file.name)
            deleted_count += 1
    st.cache_resource.clear()
    return deleted_count 
