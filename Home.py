from openai import OpenAI
import streamlit as st 
import pandas as pd
import numpy as np 

# 좌측 사이드바 버튼은 남기고 삼선 메뉴, 배포 버튼, 푸터만 숨기기
hide_elements_style = """
<style>
/* 1. 삼선 메뉴 숨기기 */
#MainMenu {visibility: hidden;}

/* 2. 배포(Deploy) 버튼 숨기기 (버전별 호환) */
.stDeployButton {display: none !important;}
.stAppDeployButton {display: none !important;}

/* 3. 하단 푸터 숨기기 */
footer {visibility: hidden;}

/* 4. 헤더 자체는 남겨두되 투명하게 만들고 높이를 줄여 사이드바 버튼 위치 확보 */
header[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0) !important;
    background: transparent !important;
}
</style>
"""

st.markdown(hide_elements_style, unsafe_allow_html=True)


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
