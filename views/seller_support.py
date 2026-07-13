import streamlit as st
import time 
from src.telegram import send_telegram_detail_alert, get_allowed_time_remaining

# ==========================================
# # 2. 입점업체 지원 화면
# ==========================================

# ----------------- 💻 4. UI 레이아웃 및 폼 제어 -----------------
def show_support(): 
    c1, c2 = st.columns([3, 1], vertical_alignment="center", border=False)
    c1.subheader("✔  입점업체 **sms**")

    # text_alignment 속성은 st.markdown에 없으므로 안전한 HTML 스타일로 대체 적용
    c2.markdown("<div style='text-align: right;'><a href='tel:063-714-6000'>☎ 063-714-6000</a></div>", unsafe_allow_html=True)
    st.markdown("(대금 미지급 등) :red[**현장**]의 :red[**애로 사항**]을 알려 주세요.")

    # 실시간 제한 시간 안내 바
    remaining = get_allowed_time_remaining()
    if remaining > 0: 
        st.warning(f"🔒 도배 방지를 위해 잠시 발송이 제한됩니다. (남은 시간: {remaining}초)")

    # 폼 키에 타임스탬프를 섞어 중복 폼 에러를 차단합니다.
    form_id = f"help_form_session_{int(time.time() // 60)}"
    
    with st.form(key=form_id, clear_on_submit=True):
        name = st.text_input("이름 또는 닉네임", placeholder="홍길동")
        email = st.text_input("답변받을 이메일 (선택)", placeholder="example@email.com")
        content = st.text_area("도움이 필요한 내용", placeholder="예) 대금 미지급 등. \n\n  ※ 다시쓰기는 60초 이후 가능합니다.^^")
        
        submit_button = st.form_submit_button("❓ **Help 요청하기**")

    # submit_button 체크 로직
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
                    # ⚠️ [개선] 사용자가 성공 메시지를 인지하고 곧바로 폼을 초기화 및 안내바 갱신을 하도록 처리
                    st.success("요청이 정상적으로 접수되었습니다! 개발자 알림 발송 완료.")
                    time.sleep(2)  # 8초 대기는 유저가 멈춘 것으로 오해할 수 있으므로 2초가 적당합니다.
                    st.rerun()

