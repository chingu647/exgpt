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
# 2. UI 요소 숨기기 (업그레이드된 완벽 차단 CSS)
hide_streamlit_style = """
    <style>
        /* 1) 우측 상단 깃허브 아이콘 및 Deploy 버튼 숨기기 */
        #GithubIcon {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* 2) 화면 가운데 아래 'Made with Streamlit' 및 헤더 메뉴 숨기기 */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 3) ⚠️ [추가] 우측 하단 'Manage App' 관리자 도구 박스 숨기기 */
        [data-testid="stStatusWidget"] {visibility: hidden !important;}
        
        /* 4) ⚠️ [추가] 우측 하단 스트림릿 호스트/연결 배지 레이어 통째로 숨기기 */
        .stAppDeployWithStreamlit {display: none !important;}
        div[class^="stAppDeployWithStreamlit"] {display: none !important;}
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
TABS = ["휴게소 챗봇", "휴게소 성과", "입점업체 지원"]
current = st.segmented_control("ex 전북본부", TABS, default="휴게소 챗봇", key="tab")

if current == "휴게소 챗봇":
    from views import service_chatbot as sec
    sec.show_chatbot() 

elif current == "휴게소 성과":
    from views import service_overview as seo
    seo.show_overview() 

elif current == "입점업체 지원":
    from views import seller_support as ses
    ses.show_support() 
