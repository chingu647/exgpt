import streamlit as st
import itertools

def init_key_pool():
    """세션 상태에 API 키 풀 초기화"""
    if "key_pool" not in st.session_state:
        try:
            api_keys = st.secrets["gemini"]["api_keys"]
            st.session_state.key_pool = itertools.cycle(api_keys)
        except KeyError:
            st.error("⚠️ st.secrets에 'gemini.api_keys' 배열이 올바르게 구성되지 않았습니다.")
            st.stop()

def get_current_api_key():
    """회전 중인 다음 API 키 반환"""
    init_key_pool()
    return next(st.session_state.key_pool)
