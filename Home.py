from openai import OpenAI
import streamlit as st 
import pandas as pd
import numpy as np 

# 좌측 화살표(슬라이드 토글)는 남기고 삼선 메뉴와 배포 버튼만 확실히 지우는 CSS
final_style = """
<style>
/* 1. 우측 삼선 메뉴(햄버거 버튼) 완전히 제거 */
[data-testid="stActionButton"] {
    display: none !important;
}

/* 2. 배포(Deploy) 버튼 완전히 제거 (두 가지 버전 클래스 모두 대응) */
.stDeployButton, .stAppDeployButton {
    display: none !important;
}

/* 3. 하단 푸터(Made with Streamlit) 제거 */
footer {
    visibility: hidden;
}

/* 4. (선택) 헤더 영역의 불필요한 배경을 투명화하여 좌측 화살표만 깔끔하게 노출 */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}
</style>
"""

st.markdown(final_style, unsafe_allow_html=True)

# 테스트용 사이드바 및 본문 코드
st.sidebar.title("좌측 슬라이드바")
st.sidebar.write("성공! 화살표가 보이며 정상 작동합니다.")
st.title("메인 화면")
st.write("우측 상단의 삼선 메뉴와 배포 버튼만 깔끔하게 숨겨졌습니다.")






with st.sidebar:
    "[메뉴 1 : 네이버](https://www.naver.com)"
    "[메뉴 2 : 다음](https://www.daum.net)"
    "[메뉴 3 : 구글](https://www.google.com)"

st.title("💬 전북 Chatbot")
st.caption("🚀 A RAG chatbot powered by OpenAI")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "무엇을 도와 드릴까요?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
