import streamlit as st
from src.auth import get_current_api_key
from src.gemini import get_gemini_client, upload_fixed_file_once, generate_content_with_retry
from google.genai.errors import APIError

# 모듈 로드 시점에 세션 상태에 안전하게 기록
FIXED_PDF_FILENAME = "abcd.txt"
if "FIXED_PDF_FILENAME" not in st.session_state: 
    # ⚠️ [해결] 중괄호 오타(})를 대괄호(])로 수정하여 SyntaxError 차단
    st.session_state["FIXED_PDF_FILENAME"] = FIXED_PDF_FILENAME

# ==========================================
# # 1. 챗봇 화면
# ==========================================

def show_chatbot():
    st.subheader("💬 휴게소 Chatbot")
    st.markdown(":rocket: :green-badge[**휴게시설 업무기준**] 및 :sparkles: :green-badge[**자체투자사업 매뉴얼**] 안내")
    st.divider()

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "무엇이 궁금하세요? 답변해 드리겠습니다."}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("질문할 내용을 입력하세요..."):
        # ⚠️ [해결] 누락되었던 API Key 가져오기 코드 복구 (NameError 방지)
        current_key = get_current_api_key()
        client = get_gemini_client(current_key)

        # ⚠️ [해결] 들여쓰기 공백 정렬 및 세션 안전 변수 바인딩
        target_filename = st.session_state["FIXED_PDF_FILENAME"]
        google_file = upload_fixed_file_once(current_key, target_filename)

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

