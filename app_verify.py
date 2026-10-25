import difflib
import re
import streamlit as st

st.set_page_config(page_title="소방 점검실무행정 NFTC 개정 대조 앱", layout="wide")

st.title("🔥 소방 점검실무행정 & NFTC 상호 비교 및 개정 단권화 MD 생성기")
st.caption(
    "구판 점검실무행정 노트와 최신 NFTC 원문 MD들(복수 선택 가능)을 비교하여 신설·개정·삭제 내역 및 최종 단권화 .md 문서를 생성합니다."
)


# ---------------------------------------------------------
# Helper Functions: 정밀 조문 파싱 및 비교
# ---------------------------------------------------------
def safe_decode(uploaded_file):
    """UTF-8 및 CP949 인코딩 안전 디코딩 (포인터 꼬임 방지)"""
    content = uploaded_file.getvalue()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("cp949")


def parse_markdown_by_sections(text):
    """마크다운 텍스트에서 명확한 법령 조문 체계(예: 1.1, 2.1.1 등) 단위로 섹션 분할"""
    lines = text.splitlines()
    sections = {}
    current_key = "0. 개요 및 총칙"
    current_content = []

    # 조문 번호 패턴 엄격화 (예: 1.1, 2.1.1, 2.2.1.13 등만 타겟팅하여 일반 숫자 혼동 방지)
    section_pattern = re.compile(r"^(?:#+\s*)?(\d+(?:\.\d+)+)(?:\s+|$)(.*)")

    for line in lines:
        stripped = line.strip()
        match = section_pattern.match(stripped)
        if match:
            # 이전 섹션 저장
            if current_content:
                sections[current_key] = "\n".join(current_content).strip()
            current_key = match.group(1)  # 조문 번호만 키로 사용 (예: 2.1.1)
            current_content = [line]
        else:
            current_content.append(line)

    if current_content:
        sections[current_key] = "\n".join(current_content).strip()

    return sections


def get_text_diff(old_text, new_text):
    """구판과 신판의 줄 단위 변경점(+/-) 추출"""
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff = difflib.unified_diff(
        old_lines, new_lines, lineterm="", fromfile="구판", tofile="최신판(병합)"
    )
    diff_list = list(diff)
    if len(diff_list) > 2:
        return "\n".join(diff_list[2:])
    return "(텍스트 구조적 변경으로 인한 전체 교체 또는 서식 차이)"


def compare_sections(old_sections, new_sections):
    """구판과 신판 조문별 대조 분석"""
    all_keys = sorted(
        list(set(list(old_sections.keys()) + list(new_sections.keys()))),
        key=lambda x: [
            int(p) if p.isdigit() else 0 for p in x.replace("조", "").split(".")
        ],
    )
    comparison_results = []

    for k in all_keys:
        in_old = k in old_sections
        in_new = k in new_sections

        if in_old and in_new:
            old_text = old_sections[k]
            new_text = new_sections[k]
            if old_text.strip() == new_text.strip():
                status = "유지"
                diff_text = ""
            else:
                status = "개정(수정)"
                diff_text = get_text_diff(old_text, new_text)

            comparison_results.append({
                "section": k,
                "status": status,
                "old_text": old_text,
                "new_text": new_text,
                "diff_text": diff_text,
            })
        elif in_new:
            new_text = new_sections[k]
            comparison_results.append({
                "section": k,
                "status": "신설(추가)",
                "old_text": "-",
                "new_text": new_text,
                "diff_text": "",
            })
        elif in_old:
            old_text = old_sections[k]
            comparison_results.append({
                "section": k,
                "status": "삭제",
                "old_text": old_text,
                "new_text": "-",
                "diff_text": "",
            })

    return comparison_results


def generate_diff_markdown(comparison_results):
    """단권화 마크다운 보고서 생성"""
    md = "# 📋 소방 점검실무행정 / NFTC 최신 개정 반영 단권화 노트\n\n"
    md += "## 1. 조문별 개정 현황 요약표\n\n"
    md += "| 조문 번호 | 상태 | 주요 반영 내용 요약 |\n"
    md += "| :--- | :---: | :--- |\n"

    for r in comparison_results:
        if r["status"] == "유지":
            icon = "🟢"
        elif r["status"] == "신설(추가)":
            icon = "🔴"
        elif r["status"] == "개정(수정)":
            icon = "🟡"
        else:
            icon = "⚪"

        summary = (
            r["new_text"].split("\n")[0][:40]
            if r["status"] != "삭제"
            else r["old_text"].split("\n")[0][:40]
        )
        md += f"| {r['section']} | {icon} {r['status']} | {summary}... |\n"

    md += "\n---\n\n## 2. 세부 조문별 상호 비교 및 단권화 노트\n\n"

    for r in comparison_results:
        if r["status"] == "유지":
            continue
        md += f"### [{r['status']}] 조문: {r['section']}\n\n"

        if r["status"] == "개정(수정)":
            md += (
                "**[변경 대조 (Diff)]**\n```diff\n" + r["diff_text"] + "\n```\n\n"
            )
            md += "**[최신 NFTC 원문 반영]**\n```markdown\n" + r["new_text"] + "\n```\n\n"
        elif r["status"] == "신설(추가)":
            md += "**[신설 조문]**\n```markdown\n" + r["new_text"] + "\n```\n\n"
        elif r["status"] == "삭제":
            md += "**[삭제된 구판 조문]**\n```markdown\n" + r["old_text"] + "\n```\n\n"
        md += "---\n\n"

    return md


# ---------------------------------------------------------
# UI Layout
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 구판 점검실무행정 MD 업로드")
    old_file = st.file_uploader("구판 .md 파일 선택", type=["md", "txt"], key="old")

with col2:
    st.subheader("2. 최신 개정 NFTC 원문 MD 업로드 (복수 선택 가능)")
    # accept_multiple_files=True 옵션을 추가하여 2개 이상의 파일 업로드 허용
    new_files = st.file_uploader(
        "최신 .md 파일들 선택 (여러 개 선택 가능)", 
        type=["md", "txt"], 
        key="new_multiple", 
        accept_multiple_files=True
    )

if old_file and new_files:
    old_text = safe_decode(old_file)
    
    # 여러 개의 최신 NFTC 파일을 하나로 병합
    combined_new_texts = []
    for f in new_files:
        combined_new_texts.append(safe_decode(f))
    new_text = "\n\n".join(combined_new_texts)

    st.success(f"구판 파일 1개와 최신 NFTC 파일 {len(new_files)}개가 성공적으로 로드 및 병합되었습니다.")

    if st.button("🔍 상호 비교 및 단권화 MD 생성 실행", type="primary"):
        with st.spinner("정밀 조문 분석 및 개정 대조 중..."):
            old_sections = parse_markdown_by_sections(old_text)
            new_sections = parse_markdown_by_sections(new_text)

            results = compare_sections(old_sections, new_sections)
            final_md = generate_diff_markdown(results)

            st.markdown("### 📊 개정 대조 분석 결과")

            added = sum(1 for r in results if r["status"] == "신설(추가)")
            modified = sum(1 for r in results if r["status"] == "개정(수정)")
            deleted = sum(1 for r in results if r["status"] == "삭제")
            unchanged = sum(1 for r in results if r["status"] == "유지")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("신설(추가)", f"{added} 건")
            m2.metric("개정(수정)", f"{modified} 건")
            m3.metric("삭제", f"{deleted} 건")
            m4.metric("유지", f"{unchanged} 건")

            st.divider()
            st.subheader("📄 생성된 단권화 마크다운 미리보기")
            st.markdown(
                final_md[:2000]
                + "\n\n*(이하 생략 - 전체 내용은 아래 다운로드 버튼 이용)*"
            )

            st.download_button(
                label="📥 단권화 개정정리 파일 다운로드 (.md)",
                data=final_md,
                file_name="점검실무행정_NFTC_최신개정대조_단권화.md",
                mime="text/markdown",
            )
