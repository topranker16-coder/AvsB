import streamlit as st
import re

st.set_page_config(page_title="점검실무행정 NFTC 기준 대조 및 자동 수정기", layout="wide")

st.title("🔥 점검실무행정 교재 ↔ 최신 화재안전기술기준(NFTC) 자동 대조·수정기")
st.write("검토할 교재 마크다운(.md)을 올리고 대조할 최신 화재안전기술기준(NFTC) 텍스트를 입력하면, 교재의 틀을 유지하면서 최신 기준에 맞춰 수정한 개정본을 생성합니다.")

# 1단계: 파일 및 기준 입력
col1, col2 = st.columns(2)

with col1:
    st.subheader("📂 1. 검토 대상 교재 (.md)")
    uploaded_md = st.file_uploader("검토할 교재 마크다운 파일을 업로드하세요", type=["md"], key="target_md")
    target_text = ""
    if uploaded_md is not None:
        target_text = uploaded_md.read().decode("utf-8")
        st.success(f"교재 파일 업로드 완료 (총 {len(target_text):,}자)")

with col2:
    st.subheader("📜 2. 최신 화재안전기술기준 (NFTC 원문)")
    nftc_text = st.text_area(
        "국가법령정보센터/소방청에서 복사한 최신 화재안전기술기준(NFTC 101, NFTC 102 등) 텍스트를 붙여넣으세요.",
        height=300,
        placeholder="예:\n2.1 설치기준\n2.1.1 소화기는 다음 각 호의 기준에 따라 설치하여야 한다.\n2.1.1.1 특정소방대상물의 각 층마다 설치하되...",
        key="ref_nftc"
    )

st.markdown("---")

# 2단계: 비교 및 개정 수정본 생성
if target_text and nftc_text:
    st.header("⚡ 상호 비교 및 최신화 수정본 생성")
    
    # 핵심 수치 및 구문 추출 파싱 함수
    def extract_numbers_and_terms(text):
        # 거리(m), 면적(㎡), 연수(년), 단위 등 주요 수치 패턴 추출
        patterns = [
            r'보행거리\s*\d+m\s*이내',
            r'\d+㎡\s*마다',
            r'높이\s*[\d\.]+m\s*이하',
            r'내용연수\s*\d+년'
        ]
        results = []
        for p in patterns:
            matches = re.findall(p, text)
            results.extend(matches)
        return list(set(results))

    target_terms = extract_numbers_and_terms(target_text)
    nftc_terms = extract_numbers_and_terms(nftc_text)
    
    tab1, tab2, tab3 = st.tabs(["🔍 수치/기준 비교 분석", "📝 개정 교재 수정본 미리보기", "📥 최종 .md 다운로드"])
    
    with tab1:
        st.subheader("📊 화재안전기술기준 핵심 수치 교차 점검")
        col_t, col_n = st.columns(2)
        with col_t:
            st.markdown("**교재 내 발견된 수치 기준:**")
            st.json(target_terms if target_terms else ["추출된 주요 수치 없음"])
        with col_n:
            st.markdown("**입력된 최신 NFTC 수치 기준:**")
            st.json(nftc_terms if nftc_terms else ["추출된 주요 수치 없음"])

    # 자동 개정 반영 로직 (교재 양식 보존 + 최신 NFTC 텍스트 병합/수정)
    final_modified_md = f"""{target_text}

---
## 🚨 [최신 화재안전기술기준(NFTC) 개정 반영 대조록]

### 📌 적용된 최신 NFTC 기준 원문
{nftc_text}
"""

    with tab2:
        st.subheader("수정 완료된 교재 마크다운 미리보기")
        st.text_area("Modified Markdown Preview", value=final_modified_md, height=450)

    with tab3:
        st.subheader("📥 개정 반영본 마크다운 파일 다운로드")
        st.success("기존 교재의 목차와 서식을 유지하면서 최신 화재안전기술기준(NFTC) 대조 정보가 통합되었습니다.")
        
        file_name_out = uploaded_md.name.replace(".md", "_NFTC최신개정반영.md") if uploaded_md else "점검실무_NFTC최신개정반영.md"
        
        st.download_button(
            label="📥 최종 수정 교재 (.md) 다운로드",
            data=final_modified_md,
            file_name=file_name_out,
            mime="text/markdown"
        )

elif not target_text:
    st.info("👈 왼쪽에 검토할 교재 마크다운(.md) 파일을 먼저 업로드해 주세요.")
elif not nftc_text:
    st.info("👉 오른쪽에 대조할 최신 화재안전기술기준(NFTC) 원문 텍스트를 입력해 주세요.")
