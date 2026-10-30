import os
import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="소방 실무행정 AI 대항군 개정기", layout="wide")

# 1. 사이드바에 API Key 입력창 배치
st.sidebar.header("🔑 설정")
api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")

st.title("🔥 소방 점검실무행정 신/구 기준 대조 및 대항군 검증기")
st.markdown("구형 실무행정 파일(`.md`, `.txt`)과 최신 화재안전기준 파일(`.md`, `.txt`)을 업로드하면, AI가 최신화를 수행하고 대항군(Critic)이 허점을 검증합니다.")

# 2. 파일 업로드 창 (md와 txt 모두 선택 가능하도록 수정)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 구형 실무 원본 (.md / .txt)")
    old_file = st.file_uploader("구형 점검실무행정 파일 선택", type=["md", "txt"], key="old")

with col2:
    st.subheader("📚 최신 법령 및 NFTC 기준 (.md / .txt)")
    modern_file = st.file_uploader("최신 화재안전기준 파일 선택", type=["md", "txt"], key="modern")

code_number = st.text_input("기준 번호 (예: 101, 102 등)", value="101")

# 3. 실행 버튼 및 로직
if st.button("🚀 신형 개정안 생성 및 대항군 검증 시작"):
    if not api_key:
        st.error("좌측 사이드바에 Gemini API Key를 먼저 입력해주세요!")
    elif not old_file or not modern_file:
        st.warning("구형 원본 파일과 최신 기준 파일을 모두 업로드해주세요.")
    else:
        genai.configure(api_key=api_key)
        
        # 업로드된 파일 내용 읽기 (utf-8 인코딩)
        old_text = old_file.read().decode("utf-8")
        modern_text = modern_file.read().decode("utf-8")
        
        with st.spinner("AI가 최신 기준을 반영하고 대항군이 허점을 검증 중입니다... 잠시만 기다려주세요."):
            
            # 1단계: 초안 작성 (Generator)
            gen_model = genai.GenerativeModel("gemini-2.5-pro")
            prompt_gen = f"""
            너는 최고 권위의 소방기술사이자 실무행정 개정 편찬 위원장이다.
            아래의 [구형 실무행정 자료] 목차와 뼈대를 살리되, [최신 기준]에 맞춰 완벽하게 최신화하라.
            
            [구형 실무행정 원본]:
            {old_text}
            
            [최신 기준 참고]:
            {modern_text}
            """
            draft = gen_model.generate_content(prompt_gen).text
            
            # 2단계: 대항군 검증 (Critic)
            critic_model = genai.GenerativeModel("gemini-2.5-pro")
            prompt_critic = f"""
            너는 타협 없는 수석 소방안전 감사관이자 냉철한 대항군이다.
            아래의 [개정 초안]이 [최신 기준]과 완벽히 부합하는지 검증하라.
            구형 수치나 모순이 있다면 허를 찌르고 수정안을 제시하라. 완벽하면 [승인]을 적어라.
            
            [최신 기준]:
            {modern_text}
            
            [개정 초안]:
            {draft}
            """
            audit_result = critic_model.generate_content(prompt_critic).text
            
        st.success("개정 및 대항군 검증이 완료되었습니다!")
        
        # 결과 출력
        st.markdown("---")
        st.subheader("🛡️ 대항군(Critic) 검증 리포트")
        st.markdown(audit_result)
        
        st.markdown("---")
        st.subheader("📝 최종 개정 실무행정 초안")
        st.markdown(draft)
        
        # 다운로드 버튼
        final_output = f"# [대항군 검증 리포트]\n{audit_result}\n\n---\n\n# [최종 개정 본문]\n{draft}"
        st.download_button(
            label="📥 최종 개정 파일(.md) 다운로드",
            data=final_output,
            file_name=f"practical_{code_number}_revised.md",
            mime="text/markdown"
        )
