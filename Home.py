# ###########################################################
# streamlit 1. 경로 설정 
# ###########################################################

import streamlit as st

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ###########################################################
# 2. UI 요소 숨기기 (Custom CSS) - 접힘메뉴 복원 버전
# ###########################################################
hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# ###########################################################
# streamlit 2. 전역변수 설정 
# ###########################################################

FIXED_PDF_FILENAME = "abcd.txt"
if "FIXED_PDF_FILENAME" not in st.session_state: 
    # ⚠️ [해결] 중괄호 오타(})를 대괄호(])로 수정하여 SyntaxError 차단
    st.session_state["FIXED_PDF_FILENAME"] = FIXED_PDF_FILENAME



# ###########################################################
from src import admin_sidebar as ads

# 1. 공통 UI 컴포넌트 로드 (사이드바 메뉴 상시 노출)
ads.render_admin_sidebar()

# 2. 메인 내비게이션 구성
TABS = ["휴게시설 챗봇", "입점업체 지원"]
current = st.segmented_control("ex 전북본부", TABS, default="휴게시설 챗봇", key="tab")

if current == "휴게시설 챗봇":
    from views import service_chatbot as sec
    sec.show_chatbot() 

elif current == "입점업체 지원":
    from views import seller_support as ses
    ses.show_support() 
