import streamlit as st

from src.auth import get_current_api_key
# 🔒 보안 및 수명주기(Lifecycle) 추적을 위해 필요한 함수 온전하게 호출
from src.gemini import get_gemini_client, upload_fixed_file_once, generate_content_with_retry
from google.genai.errors import APIError


# ==========================================
# # 1. 챗봇 화면
# ==========================================

def show_chatbot():
    st.subheader("💬 휴게시설 업무 Chatbot")
#    st.markdown(":rocket: :green[**휴게시설 업무기준**] 및 :sparkles: :green[**자체투자사업 매뉴얼**] 안내")
    st.divider()

    # 🔒 [보안 강화 및 줄간격/여백 교정 완료] 
    # 문장 내부에 <br> 태그를 주입하여 파기코드 들여쓰기는 유지하면서 화면 여백은 축소함
    st.error(
        "⚠️ **[보안 필수 준수 사항]**<br><br>"
        "🔹 **개인정보·실명 입력 절대 금지**: 사람 이름, 주민번호, 특정 업체 실명은 빼고 입력.<br><br>"
        "🔹 **가명 처리 필수**: **'OO휴게소', '업체A'** 등으로 바꾸어 질문하십시오.<br><br>"
        "🔹 **최종 확인 의무**: AI 답변은 참고용입니다. 중요사항은 반드시 원문 확인이 필요."
    )

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "무엇이 궁금하세요? 답변해 드리겠습니다."}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # 🔒 [보안 통제] 입력창 내부에도 직관적인 예시 힌트 제공
    chat_placeholder = "질문을 입력하세요 (예: OO휴게소 업체A 대금 미지급 처분 기준은?)"

    if prompt := st.chat_input(chat_placeholder):
        # ⚠️ API Key 가져오기 및 클라이언트 빌드
        current_key = get_current_api_key()
        client = get_gemini_client(current_key)

        # ⚠️ 고정 파일 탐색 및 업로드
        target_filename = st.session_state["FIXED_PDF_FILENAME"]
        google_file = upload_fixed_file_once(current_key, target_filename)

        # 🔒 [보안 Lifecycle 반영] Home.py에서 메뉴 이탈 시 자동 추적 및 파기할 수 있도록 고유 파일명 세션 기록
        if google_file:
            st.session_state["LAST_UPLOADED_FILE_NAME"] = google_file.name

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
                with st.spinner("답변을 생성 중입니다... (내용 정리 중)"):
                    # 🔒 src/gemini.py에 반영된 시스템 지침 및 안전 온도가 작동합니다.
                    response = generate_content_with_retry(
                        client=client,
                        model='gemini-3.1-flash-lite',
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
