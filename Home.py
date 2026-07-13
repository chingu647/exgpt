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
# 스트림릿 자체 푸터 + 클라우드 전용 툴바/호스팅 바 전체 제거 CSS
hide_cloudflare_style = """
    <style>
    /* 1. 기본 스트림릿 메뉴 및 푸터 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. 스트림릿 클라우드(공식 배포) 전용 하단 'Manage app' 및 호스팅 툴바 숨기기 */
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    div.embeddedAppMetaInfoBar_container__DxxL1 {display: none !important;}
    
    /* 혹시 모를 앱 관리용 플로팅 버튼들 강제 제거 */
    [data-testid="stDecoration"] {display: none;}
    </style>
"""
st.markdown(hide_cloudflare_style, unsafe_allow_html=True)
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
