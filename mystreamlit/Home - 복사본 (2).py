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
# 🔄 [핵심 수정] st.secrets를 통해 9개 API 키 가져오기 및 풀(Pool) 생성
# ==========================================
if "key_pool" not in st.session_state:
    try:
        # secrets에서 키 리스트를 가져와서 순환 이터레이터로 만듭니다.
        api_keys = st.secrets["gemini"]["api_keys"]
        st.session_state.key_pool = itertools.cycle(api_keys)
    except KeyError:
        st.error("⚠️ st.secrets에 'gemini.api_keys' 배열이 올바르게 구성되지 않았습니다.")
        st.stop()

# 현재 실행에 사용할 API 키 하나를 꺼내는 헬퍼 함수
def get_current_api_key():
    return next(st.session_state.key_pool)

FIXED_PDF_FILENAME = "abcd.txt"  


# ==========================================
# [속도 최적화] 구글 API 클라이언트 캐싱 (각 키별로 캐싱)
# ==========================================
@st.cache_resource
def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)


# ==========================================
# [고정 파일 처리] 중복 업로드 방지 및 기존 파일 재사용
# ==========================================
# 키마다 독립된 클라우드 프로젝트이므로, 호출한 키 프로젝트 내에 파일이 있는지 확인합니다.
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
        # 특정 프로젝트 키의 권한 이슈나 업로드 에러 방지
        return None


# ==========================================
# 🔥 [안정성 강화] 429 에러 발생 시 자동 재시도 함수 (지수 백오프)
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
# 메인 화면 구성 및 챗 초기화
# ==========================================
st.subheader("💬 휴게소 업무 Chatbot", width="stretch", text_alignment="center")
st.markdown(":rocket: :green-badge[**휴게시설 업무기준**] 및 :sparkles: :green-badge[**자체투자사업 매뉴얼 안내**]", width="stretch", text_alignment="center")
st.caption(":point_right: :yellow-badge[전화 문의 :  [063-714-6000](tel:063-714-6000)]", width="stretch", text_alignment="right")

st.divider()

# [임시 관리 메뉴] 저장소 비우기 사이드바
with st.sidebar:
    st.header("⚙️ 관리자 전용 메뉴")
    if st.button("🗑️ 구글 API 저장소 중복 파일 일괄 삭제"):
        with st.spinner("9개 프로젝트 전체 청소 중..."):
            try:
                deleted_count = 0
                # secrets에 등록된 모든 키의 저장소를 돌면서 청소합니다.
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

# 💬 채팅 출력 파트
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "무엇이 궁금하세요? 답변해 드리겠습니다."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ==========================================
# 사용자 채팅 입력 및 처리
# ==========================================
if prompt := st.chat_input("질문할 내용을 입력하세요..."):
    
    # 🔄 [핵심 수정] 사용자가 질문할 때마다 새로운 API 키를 꺼내어 할당합니다.
    current_key = get_current_api_key()
    client = get_gemini_client(current_key)
    
    # 선택된 키(프로젝트) 서버에 abcd.txt 고정 파일이 올라가 있는지 체크 후 연동
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
                # 자동으로 지수 백오프 재시도가 일어납니다.
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
            st.error("⏳ 9개 프로젝트의 임시 요청 한도가 일시적으로 모두 소진되었습니다. 잠시 후 전송 버튼을 한 번 더 눌러 다른 키로 호출해 보세요.")
        else:
            st.error(f"오류가 발생했습니다: {e}")
