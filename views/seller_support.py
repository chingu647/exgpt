import streamlit as st 
import time 
from src.telegram import send_telegram_detail_alert, get_allowed_time_remaining 

# ========================================== # 
# 2. 입점업체 지원 화면 
# ========================================== # 
# ----------------- 💻 4. UI 레이아웃 및 폼 제어 ----------------- 
def show_support():
    c1, c2 = st.columns([3, 1], vertical_alignment="center", border=False)
    c1.subheader("✔ 입점업체 **sms**") 
    
    # text_alignment 속성은 st.markdown에 없으므로 안전한 HTML 스타일로 대체 적용 
    c2.markdown("<div style='text-align: right;'><a href='tel:063-714-6000'>☎ 063-714-6076</a></div>", unsafe_allow_html=True) 
    st.markdown("(대금 미지급 등) :red[**현장**]의 :red[**애로 사항**]을 알려 주세요.") 

    # 실시간 제한 시간 안내 바 
    remaining = get_allowed_time_remaining() 
    if remaining > 0: 
        # 현재 시간에 남은 초를 더해 재발송 가능 시각 계산
        available_time = datetime.now() + timedelta(seconds=remaining)
        available_time_str = available_time.strftime("%H시 %M분 %S초")
        st.warning(f"🔒 다시 쓰기는 ({available_time_str}) 이후 가능합니다.") 

    # [개선] clear_on_submit을 False로 설정하여, 검증 실패 시 입력 내용이 지워지지 않도록 차단합니다.
    # [개선] 폼 ID가 분(Minute)마다 바뀌면 값이 유실될 수 있으므로 고정된 고유 키를 사용합니다.
    form_id = "help_form_session_fixed" 
    
    with st.form(key=form_id, clear_on_submit=False): 
        name = st.text_input("이름 또는 닉네임", placeholder="홍길동") 
        email = st.text_input("답변받을 이메일 (선택)", placeholder="example@email.com") 
        content = st.text_area("도움이 필요한 내용", placeholder="예) 대금 미지급 등. \n\n ※ 다시쓰기는 60초 이후 가능합니다.^^") 
        submit_button = st.form_submit_button("❓ **Help 요청하기**") 

    # submit_button 체크 로직 
    if submit_button: 
        remaining_check = get_allowed_time_remaining() 
        
        if remaining_check > 0: 
            # 제한 시간에 걸린 경우 (기존 입력 내용 유지됨)
            st.error(f"🚨 요청 실패: {remaining_check}초 후에 다시 보낼 수 있습니다.") 
            
        elif not name or not content: 
            # 필수 값을 입력하지 않은 경우 (기존 입력 내용 유지됨)
            st.warning("이름과 문의 내용은 필수 입력 항목입니다.") 
            
        elif len(content) > 1000: 
            # 글자 수 제한을 초과한 경우 (기존 입력 내용 유지됨)
            st.error("문의 내용은 1,000자 이하로 작성해 주세요.") 
            
        else: 
            # 모든 조건 만족 시 전송 시작
            with st.spinner("관리자에게 상세 내용을 안전하게 전달하는 중..."): 
                success = send_telegram_detail_alert(name, email, content) 
                
                if success: 
                    st.success("요청이 정상적으로 접수되었습니다! 개발자 알림 발송 완료.") 
                    time.sleep(3) 
                    # [개선] 전송이 완벽히 성공한 시점에만 rerun()을 호출하여 입력 폼을 깨끗하게 초기화합니다.
                    st.rerun() 
                else:
                    # 텔레그램 전송 자체가 실패한 경우 (기존 입력 내용 유지됨)
                    st.error("서버 오류로 전송에 실패했습니다. 잠시 후 다시 시도해 주세요.")
                    
