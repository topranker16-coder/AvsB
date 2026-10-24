import streamlit as st
import re

st.set_page_config(page_title="소방 법령 해설서 개정 검증기", layout="wide")

st.title("🔍 소방시설 점검실무행정 개정 검증 및 분석기")
st.write("추출된 마크다운(`.md`) 교재 파일을 업로드하여 주요 법령, 기준, 수치(보행거리, 면적 등)를 검색하고 검증하세요.")

# 1. 마크다운 파일 업로드
uploaded_file = st.file_uploader("추출된 마크다운 파일(.md)을 업로드하세요", type=["md"])

if uploaded_file is not None:
    # 텍스트 디코딩
    content = uploaded_file.read().decode("utf-8")
    st.success(f"파일 로드 성공! (총 글자 수: {len(content):,}자)")

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["🔎 키워드/조문 검색", "📊 주요 수치·기준 추출", "💡 개정 검증 노트"])

    with tab1:
        st.subheader("교재 내 특정 조문 및 키워드 검색")
        keyword = st.text_input("검색할 키워드를 입력하세요 (예: 보행거리, 내용연수, 시행령, 능력단위)")
        
        if keyword:
            lines = content.split('\n')
            matched_lines = [line for line in lines if keyword in keyword or keyword in line]
            
            st.info(f"'{keyword}' 관련 검색 결과: 총 {len(matched_lines)}개 항목 발견")
            
            # 상위 결과 출력 (최대 50개)
            for idx, match in enumerate(matched_lines[:50]):
                st.markdown(f"**{idx+1}.** {match}")

    with tab2:
        st.subheader("주요 법령 및 기준명 자동 스캔")
        st.write("텍스트 내에 언급된 법률, 시행령, 기술기준 명칭을 찾아줍니다.")
        
        # 정규식을 이용해 '법', '시행령', '기준' 등이 포함된 문장 추출
        law_keywords = ["법률", "시행령", "시행규칙", "기준", "별표", "제조", "조항"]
        lines = content.split('\n')
        law_matches = []
        for line in lines:
            if any(lk in line for lk in law_keywords) and len(line.strip()) > 5:
                law_matches.append(line.strip())
                
        st.write(f"총 {len(law_matches)}개의 법령 관련 조항 라인 발견 (일부 표시):")
        for lm in law_matches[:30]:
            st.text(f"• {lm}")

    with tab3:
        st.subheader("📝 소방시설관리사 수험/점검 개정 체크포인트")
        st.markdown("""
        - **소방시설법 분법 사항**: 「소방시설설치유지법」이 **「소방시설 설치 및 관리에 관한 법률」** 및 **「화재의 예방 및 안전관리에 관한 법률」**로 분법·시행된 이후의 조문 번호와 명칭이 정확한지 확인하세요.
        - **화재안전기준 개편**: 성능기준(NFPC)과 기술기준(NFTC)으로 분리된 최신 고시 기준과 대조가 필요합니다.
        - **수치 기준 검증**: 소형소화기 보행거리(20m), 대형소화기 보행거리(30m), 분말소화기 내용연수(10년) 등의 핵심 수치가 2025년판 교재와 최신 기준에 일치하는지 교차 확인하세요.
        """)