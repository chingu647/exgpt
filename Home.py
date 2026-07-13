# ###########################################################
# streamlit 1. 경로 설정 
# ###########################################################

import streamlit as st

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ###########################################################
# 2. UI 요소 숨기기 (Custom CSS)
# ###########################################################
hide_streamlit_style = """
    <style>
        /* 우측 상단 깃허브 아이콘, Deploy 버튼, 메인 메뉴 점3개 버튼 숨기기 */
        #GithubIcon { visibility: hidden; }
        .stDeployButton { display: none !important; }
        .stAppDeployButton { display: none !important; }
        #MainMenu { visibility: hidden !important; }
        
        /* [중요] header 자체를 없애지 말고, 우측의 툴바 내부 메뉴만 투명하게 숨김 */
        header[data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important; /* 헤더 배경만 투명화 */
        }
        header[data-testid="stHeader"] [data-testid="stToolbar"] {
            visibility: hidden !important; /* 우측 버튼들만 타겟팅 제거 */
        }

        /* 하단 푸터 숨기기 */
        footer { visibility: hidden !important; }
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
TABS = ["휴게소 챗봇", "입점업체 지원"]
current = st.segmented_control("ex 전북본부", TABS, default="휴게소 챗봇", key="tab")

if current == "휴게소 챗봇":
    from views import service_chatbot as sec
    sec.show_chatbot() 

elif current == "입점업체 지원":
    from views import seller_support as ses
    ses.show_support() 
