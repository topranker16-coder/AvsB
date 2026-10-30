import os
import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="소방 실무행정 AI 대항군 개정기", layout="wide")

st.title("🔥 소방 점검실무행정 신/구 기준 대조 및 대항군 검증기")

# API 키 입력 (또는 st.secrets 활용)
api_key = st.text_input("Gemini API Key를 입력하세요", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 구형 실무 원본 입력")
        old_text = st.text_area("구형 실무 행정 `.md` 내용 붙여넣기", height=300)
        
    with col2:
        st.subheader("📚 최신 법령 및 NFTC 기준 입력")
        modern_text = st.text_area("최신 화재안전기준 `.md` 내용 붙여넣기", height=300)
        
    code_number = st.text_input("기준 번호 (예: 101, 102 등)", value="101")
    
    if st.button("🚀 신형 개정안 생성 및 대항군 검증 시작"):
        if not old_text or not modern_text:
            st.warning("구형 원본과 최신 기준을 모두 입력해주세요.")
        else:
            with st.spinner("AI가 최신 기준을 반영하고 대항군이 허점을 검증 중입니다..."):
                
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
                
            st.success("개정 및 검증 완료!")
            
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
