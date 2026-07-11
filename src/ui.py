import streamlit as st
from src.data import clean_all_projects_data

def render_admin_sidebar():
    """상시 유지되는 관리자 전용 사이드바 UI 렌더링"""
    with st.sidebar:
        st.header("⚙️ 관리자 전용 메뉴")
        if st.button("🗑️ 파일 인식 및 정리"):
            with st.spinner("9개 프로젝트 전체 청소 중..."):
                try:
                    count = clean_all_projects_data()
                    st.cache_resource.clear() 
                    st.success(f"✨ 청소 완료! 모든 프로젝트에서 총 {count}개의 파일이 삭제되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"삭제 실패: {e}")