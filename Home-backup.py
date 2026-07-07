from openai import OpenAI
import streamlit as st 
import pandas as pd
import numpy as np 

# -----------------------------------------------------------------------------
# st.sidebar.title("좌측 슬라이드바")
# st.sidebar.write("사이드바가 정상적으로 열리고 닫힙니다.")

# st.title("최종 메인 화면")
# st.write("우측 상단의 햄버거 삼선 메뉴와 배포 버튼이 완벽히 사라졌습니다.")
# -----------------------------------------------------------------------------

st.sidebar.title("좌측 슬라이드바")
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