import streamlit as st
import pandas as pd
import numpy as np 
import tempfile
import os
from google import genai
from google.genai import types  # 상단으로 이동하여 효율성 최적화
from google.genai.errors import APIError

# ==========================================
# [추가] 구글 API 클라이언트 캐싱 함수
# ==========================================
@st.cache_resource
def get_gemini_client(api_key: str):
    """
    한 번 생성된 API 클라이언트를 메모리에 보존하여
    채팅을 입력할 때마다 발생하는 객체 생성 딜레이를 완벽히 제거합니다.
    """
    return genai.Client(api_key=api_key)


# ==========================================
# 1. 사이드바 구성 (설정 및 파일 업로드)
# ==========================================
st.sidebar.title("🛠️ RAG 설정 패널")

# Google API Key 입력창
google_api_key = st.sidebar.text_input("Google API Key", type="password", placeholder="AI Studio에서 발급받은 키 입력")

# RAG용 PDF 파일 업로더
uploaded_file = st.sidebar.file_uploader("학습할 PDF 문서를 올려주세요", type=["pdf"])

# 업로드된 파일의 구글 URI 상태를 저장할 세션 초기화
if "uploaded_file_uri" not in st.session_state:
    st.session_state["uploaded_file_uri"] = None
if "uploaded_file_mime" not in st.session_state:
    st.session_state["uploaded_file_mime"] = None


# ==========================================
# 2. 메인 화면 구성 및 챗 초기화
# ==========================================
st.title("💬 전북 RAG Chatbot")
st.caption("🚀 Google AI Studio (Gemini 2.5) 기반 문서 대화 로봇")

# 챗 메시지 세션 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! 왼쪽 사이드바에 API 키와 PDF 문서를 등록하시면 해당 문서를 기반으로 정밀 답변해 드립니다."}]

# 기존 대화 렌더링
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ==========================================
# 3. 사용자 채팅 입력 및 처리
# ==========================================
if prompt := st.chat_input():
    # 3-1. API 키 검증
    if not google_api_key:
        st.info("시작하기 전에 왼쪽 사이드바에 Google API Key를 입력해 주세요.")
        st.stop()
        
    # [수정] 매번 생성하지 않고 캐싱된 고속 클라이언트를 즉시 불러옴
    client = get_gemini_client(google_api_key)

    # 3-2. 새 문서가 감지되면 구글 File API로 업로드 처리
    if uploaded_file and st.session_state["uploaded_file_uri"] is None:
        with st.spinner("문서를 분석용 서버로 업로드하는 중입니다..."):
            try:
                # 임시 파일로 변환하여 구글 서버에 업로드
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # 구글 File API 업로드 실행
                google_file = client.files.upload(file=tmp_path)
                os.remove(tmp_path) # 로컬 임시파일 삭제
                
                # 세션에 구글 파일 링크 정보 저장
                st.session_state["uploaded_file_uri"] = google_file.uri
                st.session_state["uploaded_file_mime"] = google_file.mime_type
                st.sidebar.success("✅ 문서 분석 완료! 이제 질문을 던져보세요.")
            except Exception as e:
                st.error(f"파일 업로드 오류: {e}")
                st.stop()

    # 3-3. 사용자 입력 화면 출력 및 세션 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 3-4. Gemini 모델 생성 프롬프트 구성 (RAG 핵심)
    contents_payload = []
    
    if st.session_state["uploaded_file_uri"]:
        # 파일이 주어지면 텍스트와 함께 구글 저장소 URI 객체를 조립
        file_part = types.Part.from_uri(
            file_uri=st.session_state["uploaded_file_uri"],
            mime_type=st.session_state["uploaded_file_mime"]
        )
        contents_payload.append(file_part)
        
        # 문서 기반 답변을 강제하는 시스템 유도 질문 추가
        instruction = f"반드시 첨부된 문서를 기반으로만 답변해 주세요. 사용자 질문: {prompt}"
        contents_payload.append(instruction)
    else:
        # 파일이 없을 경우 일반 대화 프롬프트로 작동
        contents_payload.append(prompt)

    # 3-5. [수정] 실시간 스트리밍 호출 및 응답 출력 처리
    try:
        # AI 답변 말풍선 미리 생성
        with st.chat_message("assistant"):
            # 대기시간을 제거하기 위해 스트리밍 API로 전환하여 호출
            response_stream = client.models.generate_content_stream(
                model='gemini-2.5-flash-lite',
                contents=contents_payload,
            )
            # 실시간으로 글자가 한 자씩 타이핑되는 연출을 적용하고 최종 텍스트 수집
            msg = st.write_stream(chunk.text for chunk in response_stream)
        
        # 전체 수집 완료된 AI 답변을 대화 세션에 최종 저장
        st.session_state.messages.append({"role": "assistant", "content": msg})
        
    except APIError as e:
        if e.code == 429:
            st.error("⏳ 무료 RPM(분당 요청 한도)을 초과했습니다. 약 1분 후 다시 시도해 주세요.")
        else:
            st.error(f"오류가 발생했습니다: {e}")
