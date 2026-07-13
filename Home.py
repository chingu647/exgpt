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
        /* 1) 우측 상단 깃허브 아이콘, Deploy 버튼, 헤더 전체 숨기기 */
        #GithubIcon {visibility: hidden;}
        .stDeployButton {display: none !important;}
        .stAppDeployButton {display: none !important;}
        header {visibility: hidden !important; height: 0px !important;}
        
        /* 2) 화면 가운데 아래 'Made with Streamlit' 및 기본 메뉴 숨기기 */
        footer {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        
        /* 3) 🔥 [최신 패치] 우측 하단 'Manage App' 관리자 도구 박스 완벽 차단 */
        [data-testid="stStatusWidget"] {display: none !important; visibility: hidden !important; height: 0px !important;}
        div[class*="stStatusWidget"] {display: none !important;}
        
        /* 4) 🔥 [최신 패치] 우측 하단 스트림릿 호스트/연결/배지 레이어 접두사 전체 차단 */
        div[class^="viewerBadge"] {display: none !important;}
        div[class*="viewerBadge"] {display: none !important;}
        div[class^="stAppDeployWithStreamlit"] {display: none !important;}
        div[class*="stAppDeployWithStreamlit"] {display: none !important;}
        .viewerBadge_container__1QSob {display: none !important;}
        
        /* 임베드 형태의 메타 정보 바까지 추가 차단 */
        div[class*="embeddedAppMetaInfoBar"] {display: none !important;}
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
