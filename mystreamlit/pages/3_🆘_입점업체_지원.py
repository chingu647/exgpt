import streamlit as st
from src.telegram import send_telegram_detail_alert, get_allowed_time_remaining


# ==========================================
# # 2. 입점업체 지원 화면
# ==========================================

# ----------------- 💻 4. UI 레이아웃 및 폼 제어 -----------------
def show_users(): 
    c1, c2 = st.columns([3,1], vertical_alignment="center", border=False)
    c1.subheader("✔  입점업체 **SOS**")
    c2.markdown("☎ [063-714-6000](tel:063-714-6000)", width="stretch", text_alignment="right")
    st.markdown("(대금 미지급 등) :red[**현장**]의 :red[**애로 사항**]을 알려 주세요.")

    # 실시간 제한 시간 안내 바
    remaining = get_allowed_time_remaining()
    if remaining > 0: 
        st.warning(f"🔒 도배 방지를 위해 잠시 발송이 제한됩니다. (남은 시간: {remaining}초)")

    # 폼 키에 타임스탬프를 섞어 StreamlitAPIException(중복 폼 에러)을 원천 차단합니다.
    form_id = f"help_form_session_{int(time.time() // 60)}"
    
    with st.form(key=form_id, clear_on_submit=True):
        name = st.text_input("이름 또는 닉네임", placeholder="홍길동")
        email = st.text_input("답변받을 이메일 (선택)", placeholder="example@email.com")
        content = st.text_area("도움이 필요한 내용", placeholder="👉 **담당자에게 메시지 전달 즉시 자료는 삭제**됩니다. \n\n  ※ 다시쓰기는 60초 이후 가능합니다.^^")
        
        submit_button = st.form_submit_button("❓ **Help 요청하기**")

    # ⚠️ 중요: submit_button 체크 로직은 with st.form과 같은 들여쓰기 라인(외부)에 위치해야 정상 작동합니다.
    if submit_button:
        remaining_check = get_allowed_time_remaining()
        
        if remaining_check > 0:
            st.error(f"🚨 요청 실패: {remaining_check}초 후에 다시 보낼 수 있습니다.")
        elif not name or not content:
            st.warning("이름과 문의 내용은 필수 입력 항목입니다.")
        elif len(content) > 1000:
            st.error("문의 내용은 1,000자 이하로 작성해 주세요.")
        else:
            with st.spinner("관리자에게 상세 내용을 안전하게 전달하는 중..."):
                success = send_telegram_detail_alert(name, email, content)
                if success:
                    st.success("요청이 정상적으로 접수되었습니다! 개발자 알림 발송 완료.")
                    time.sleep(8) # 성공 메시지를 잠시 보여주기 위함
                    st.rerun()
