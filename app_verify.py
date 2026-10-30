import os
import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="소방 실무행정 AI 대항군 개정기", layout="wide")

# 1. 사이드바에 API Key 입력창 배치
st.sidebar.header("🔑 설정")
api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")

st.title("🔥 소방 점검실무행정 다중 기준 대조 및 대항군 개정기")
st.markdown("구형 실무행정 파일과 **여러 개의 최신 법령/화재안전기준 파일(`.md`, `.txt`)**을 동시에 업로드하여 완벽한 신형 개정안을 도출합니다.")

# 2. 파일 업로드 구역 분리
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 1. 구형 실무 원본")
    old_file = st.file_uploader("구형 점검실무행정 파일 선택", type=["md", "txt"], key="old")

with col2:
    st.subheader("📚 2. 최신 법령 및 기준 파일들 (최대 5개 이상)")
    modern_files = st.file_uploader(
        "최신 화재안전기준, 시설법 등 참고할 파일들을 모두 선택하세요.", 
        type=["md", "txt"], 
        accept_multiple_files=True, 
        key="moderns"
    )
    if modern_files:
        st.info(f"현재 선택된 최신 기준 파일 개수: **{len(modern_files)}개**")

code_number = st.text_input("기준 번호 (예: 101, 102 등)", value="101")

# 3. 실행 버튼 및 로직
if st.button("🚀 다중 기준 대조 개정안 생성 및 대항군 검증 시작"):
    if not api_key:
        st.error("좌측 사이드바에 Gemini API Key를 먼저 입력해주세요!")
    elif not old_file or not modern_files:
        st.warning("구형 원본 파일과 최소 1개 이상의 최신 기준 파일을 업로드해주세요.")
    else:
        # API 키 설정
        genai.configure(api_key=api_key.strip())
        
        # 구형 원본 내용 읽기
        old_text = old_file.read().decode("utf-8")
        
        # 여러 개의 최신 기준 파일 내용을 하나로 합치기
        modern_texts_combined = ""
        for idx, m_file in enumerate(modern_files):
            file_content = m_file.read().decode("utf-8")
            modern_texts_combined += f"\n\n--- [참고 파일 {idx+1}: {m_file.name}] ---\n{file_content}"
        
        with st.spinner("AI가 여러 개의 최신 기준을 분석·반영하고, 대항군이 허점을 검증 중입니다... 잠시만 기다려주세요."):
            try:
                # 표준 모델명 'gemini-1.5-pro-latest' 사용
                gen_model = genai.GenerativeModel("gemini-1.5-pro-latest")
                
                # 1단계: 초안 작성 (Generator)
                prompt_gen = f"""
                너는 최고 권위의 소방기술사이자 실무행정 개정 편찬 위원장이다.
                아래의 [구형 실무행정 원본] 목차와 뼈대를 살리되, 제공된 [여러 개의 최신 법령 및 화재안전기준 참고 자료]를 종합하여 완벽하게 최신화된 실무행정 가이드를 작성하라.
                
                [구형 실무행정 원본]:
                {old_text}
                
                [최신 법령 및 기준 참고 자료]:
                {modern_texts_combined}
                """
                draft_res = gen_model.generate_content(prompt_gen)
                draft = draft_res.text
                
                # 2단계: 대항군 검증 (Critic)
                prompt_critic = f"""
                너는 타협 없는 수석 소방안전 감사관이자 냉철한 대항군이다.
                아래의 [개정 초안]이 제공된 [최신 법령 및 기준 참고 자료]와 완벽히 부합하는지 엄격하게 검증하라.
                구형 수치, 폐지된 조항, 또는 복수의 법령 간 상충되는 부분이 조금이라도 남아있다면 이를 집요하게 까발리고 정확한 수정안을 제시하라. 완벽하다면 최상단에 [승인]을 적어라.
                
                [최신 법령 및 기준 참고 자료]:
                {modern_texts_combined}
                
                [개정 초안]:
                {draft}
                """
                audit_res = gen_model.generate_content(prompt_critic)
                audit_result = audit_res.text
                
                st.success("다중 기준 대조 개정 및 대항군 검증이 완료되었습니다!")
                
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

            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                st.info("💡 API 키가 올바른지, 혹은 계정에 Gemini API 이용 권한이 정상 활성화되어 있는지 확인해 주세요.")
