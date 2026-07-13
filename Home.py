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
    st.session_state["FIXED_PDF_FILENAME"] = FIXED_PDF_FILENAME

# 🔒 [보안 Lifecycle 변수 초기화] 업로드된 파일명을 추적하기 위한 세션 바인딩
if "LAST_UPLOADED_FILE_NAME" not in st.session_state:
    st.session_state["LAST_UPLOADED_FILE_NAME"] = None

# ###########################################################
from src import admin_sidebar as ads
from src.auth import get_current_api_key
from src.gemini import delete_google_file  # 🔒 자산 파기 함수 임포트

# 1. 공통 UI 컴포넌트 로드 (사이드바 메뉴 상시 노출)
ads.render_admin_sidebar()

# 2. 메인 내비게이션 구성
TABS = ["휴게시설 챗봇", "입점업체 지원"]

# 🔒 [보안 조치] 사용자가 다른 메뉴를 클릭하여 탭이 변경되는 순간을 감지합니다.
previous_tab = st.session_state.get("current_tab_tracker", "휴게시설 챗봇")
current = st.segmented_control("ex 전북본부", TABS, default="휴게시설 챗봇", key="tab")
st.session_state["current_tab_tracker"] = current

# 🔒 [자동 Lifecycle 파기] 챗봇을 쓰다가 '입점업체 지원' 등으로 탭을 옮기면 구글 서버 자산을 즉시 삭제합니다.
if previous_tab == "휴게시설 챗봇" and current != "휴게시설 챗봇":
    if st.session_state["LAST_UPLOADED_FILE_NAME"]:
        current_key = get_current_api_key()
        delete_google_file(current_key, st.session_state["LAST_UPLOADED_FILE_NAME"])
        st.session_state["LAST_UPLOADED_FILE_NAME"] = None


# 3. 각 탭 영역 조건부 렌더링
if current == "휴게시설 챗봇":
    from views import service_chatbot as sec
    sec.show_chatbot() 

elif current == "입점업체 지원":
    from views import seller_support as ses
    ses.show_support() 
    
