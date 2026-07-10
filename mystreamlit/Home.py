import streamlit as st
from src.ui import render_admin_sidebar

# 1. 공통 UI 컴포넌트 로드 (사이드바 메뉴 상시 노출)
render_admin_sidebar()

# 2. 메인 내비게이션 구성
TABS = ["휴게소 챗봇", "휴게소 성과", "입점업체 지원"]
current = st.segmented_control("ex 전북본부", TABS, default="휴게소 챗봇", key="tab")

if current == "휴게소 챗봇":
    from pages import 1_💬_휴게소_챗봇 as chatbot
    chatbot.show_chatbot() # 내부에서 src.auth 및 src.data를 필요에 따라 import 사용

elif current == "휴게소 성과":
    from pages import 2_📊_휴게소_성과 as overview
    overview.show_overview() # 내부에서 src.auth 및 src.data를 필요에 따라 import 사용

elif current == "휴게소 챗봇":
    from pages import 3_🆘_입점업체_지원 as users
    users.show_users() # 내부에서 src.auth 및 src.data를 필요에 따라 import 사용
