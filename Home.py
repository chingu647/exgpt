from openai import OpenAI
import streamlit as st 
import pandas as pd
import numpy as np 

# 작동하는 기존 코드 구조를 유지하면서 좌측 버튼만 강제로 살리는 CSS
additional_style = """
<style>
/* [기존 코드 그대로 유지] 상단 헤더 전체 숨기기 */
header {
    visibility: hidden;
}

/* [추가] 헤더 내부의 좌측 슬라이드 버튼 영역만 강제로 보이게(visible) 설정 */
header > div:first-child {
    visibility: visible !important;
}

/* [기존 코드 그대로 유지] 배포 버튼 완전히 제거 */
.stDeployButton {
    display: none !important;
}
.stAppDeployButton {
    display: none !important;
}
</style>
"""

st.markdown(additional_style, unsafe_allow_html=True)



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
