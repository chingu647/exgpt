import streamlit as st
import tempfile
import os
import time
import itertools
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ==========================================
# 🔄 API 키 풀(Pool) 초기화 및 헬퍼 함수
# ==========================================
if "key_pool" not in st.session_state:
    try:
        api_keys = st.secrets["gemini"]["api_keys"]
        st.session_state.key_pool = itertools.cycle(api_keys)
    except KeyError:
        st.error("⚠️ st.secrets에 'gemini.api_keys' 배열이 올바르게 구성되지 않았습니다.")
        st.stop()

def get_current_api_key():
    return next(st.session_state.key_pool)

FIXED_PDF_FILENAME = "abcd.txt"  

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

# 1. 챗봇 화면 (기존 챗봇 메인 화면이었던 부분)
def show_chatbot():
    st.subheader("💬 휴게소 업무 Chatbot", width="stretch", text_alignment="center")
    st.markdown(":rocket: :green-badge[휴게시설 업무기준] 및 :sparkles: :green-badge[**자체투자사업 매뉴얼 안내**]", width="stretch", text_alignment="center")

    st.divider()

    # 💬 채팅 내역 출력 파트
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "무엇이 궁금하세요? 답변해 드리겠습니다."}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # 💬 사용자 채팅 입력 및 처리
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
                with st.spinner("답변을 생성 중입니다... (9개 키 자동 교대 작동 중)"):
                    response = generate_content_with_retry(
                        client=client,
                        model='gemini-2.5-flash-lite',
                        contents=contents_payload
                    )
                    msg = response.text
                    st.write(msg)
            
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.rerun() # 채팅 상태 즉시 반영을 위한 리런
            
        except APIError as e:
            if e.code == 429:
                st.error("⏳ 9개 프로젝트의 임시 요청 한도가 일시적으로 모두 소진되었습니다. 잠시 후 전송 버튼을 한 번 더 눌러 다른 키로 호출해 보세요.")
            else:
                st.error(f"오류가 발생했습니다: {e}")

# 2. 개요 화면 (플레이스홀더)
def show_overview():
    st.header("💰 개요 현황")
    st.write("개요 화면입니다.")

# 3. 사용자 화면 (플레이스홀더)
def show_users():
    st.header("👥 사용자 목록")
    st.write("사용자 데이터 및 현황을 관리하는 화면입니다.")


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
TABS = ["챗봇", "개요", "사용자"]
current = st.segmented_control("ex 전북본부 :point_right: [063-714-6000](tel:063-714-6000)", TABS, default="챗봇", key="tab")

if current == "챗봇":
    show_chatbot()
elif current == "개요":
    show_overview()
elif current == "사용자":
    show_users()
