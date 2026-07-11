# ###########################################################
# streamlit 1. 경로 설정 
# ###########################################################

import streamlit as st

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# ###########################################################
# streamlit 2. 전역변수 설정 
# ###########################################################

FIXED_PDF_FILENAME = "abcd.txt"
if "FIXED_PDF_FILENAME" not in st.session_state: 
    # ⚠️ [해결] 중괄호 오타(})를 대괄호(])로 수정하여 SyntaxError 차단
    st.session_state["FIXED_PDF_FILENAME"] = FIXED_PDF_FILENAME



# ###########################################################
from src.ui import render_admin_sidebar

# 1. 공통 UI 컴포넌트 로드 (사이드바 메뉴 상시 노출)
render_admin_sidebar()

# 2. 메인 내비게이션 구성
TABS = ["휴게소 챗봇", "휴게소 성과", "입점업체 지원"]
current = st.segmented_control("ex 전북본부", TABS, default="휴게소 챗봇", key="tab")

if current == "휴게소 챗봇":
    from views import service_chatbot
    service_chatbot.show_chatbot() 

elif current == "휴게소 성과":
    from views import service_overview
    service_overview.show_overview() 

elif current == "입점업체 지원":
    from views import seller_support
    seller_support.show_support() 
