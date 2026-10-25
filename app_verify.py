import re
import difflib
import streamlit as st

st.set_page_config(page_title="소방 점검실무행정 NFTC 개정 대조 앱", layout="wide")

st.title("🔥 소방 점검실무행정 & NFTC 상호 비교 및 개정 단권화 MD 생성기")
st.caption(
    "구판 점검실무행정 노트와 최신 NFTC 원문 MD를 비교하여 신설·개정·삭제 내역 및 최종"
    " 단권화 .md 문서를 생성합니다."
)


# ---------------------------------------------------------
# Helper Functions: 조문 파싱 및 비교
# ---------------------------------------------------------
def safe_decode(uploaded_file):
  """UTF-8 및 CP949 인코딩 안전 디코딩"""
  content = uploaded_file.getvalue()  # getvalue()를 사용하여 포인터 문제 방지
  try:
    return content.decode("utf-8")
  except UnicodeDecodeError:
    return content.decode("cp949")


def parse_markdown_by_sections(text):
  """마크다운 텍스트에서 조문 번호(예: 2.1.1, 2.4.2.6 또는 # 헤더) 단위로 섹션을 분할 파싱"""
  lines = text.splitlines()
  sections = {}
  current_key = "0. 개요/기본사항"
  current_content = []

  # 조문 번호 패턴 (예: # 2.1.1, 2.4.2.6, 또는 2.1.1 등)
  section_pattern = re.compile(r"^(?:#+\s*)?(\d+(?:\.\d+)+)")

  for line in lines:
    stripped = line.strip()
    match = section_pattern.search(stripped)
    if match:
      if current_content:
        sections[current_key] = "\n".join(current_content).strip()
      current_key = stripped
      current_content = [line]
    else:
      current_content.append(line)

  if current_content:
    sections[current_key] = "\n".join(current_content).strip()

  return sections


def normalize_key(key_str):
  """조문 번호 추출을 위한 키 정규화"""
  match = re.search(r"(\d+(?:\.\d+)+)", key_str)
  if match:
    return match.group(1)
  return key_str.strip()


def get_text_diff(old_text, new_text):
  """구판과 신판의 줄 단위 변경점(+/-) 추출"""
  old_lines = old_text.splitlines()
  new_lines = new_text.splitlines()
  diff = difflib.unified_diff(
      old_lines, new_lines, lineterm="", fromfile="구판", tofile="최신판"
  )
  return "\n".join(list(diff)[2:])  # 헤더 제외 변경선만 반환


def compare_sections(old_sections, new_sections):
  """구판과 신판 섹션 대조"""
  old_map = {normalize_key(k): (k, v) for k, v in old_sections.items()}
  new_map = {normalize_key(k): (k, v) for k, v in new_sections.items()}

  all_keys = sorted(list(set(list(old_map.keys()) + list(new_map.keys()))))
  comparison_results = []

  for k in all_keys:
    in_old = k in old_map
    in_new = k in new_map

    if in_old and in_new:
      old_title, old_text = old_map[k]
      new_title, new_text = new_map[k]
      if old_text.strip() == new_text.strip():
        status = "유지"
        diff_text = ""
      else:
        status = "개정(수정)"
        diff_text = get_text_diff(old_text, new_text)

      comparison_results.append({
          "section": k,
          "status": status,
          "old_title": old_title,
          "old_text": old_text,
          "new_title": new_title,
          "new_text": new_text,
          "diff_text": diff_text,
      })
    elif in_new:
      new_title, new_text = new_map[k]
      comparison_results.append({
          "section": k,
          "status": "신설(추가)",
          "old_title": "-",
          "old_text": "-",
          "new_title": new_title,
          "new_text": new_text,
          "diff_text": "",
      })
    elif in_old:
      old_title, old_text = old_map[k]
      comparison_results.append({
          "section": k,
          "status": "삭제",
          "old_title": old_title,
          "old_text": old_text,
          "new_title": "-",
          "new_text": "-",
          "diff_text": "",
      })

  return comparison_results


def generate_diff_markdown(comparison_results):
  """개정 분석 보고서 및 최종 단권화 마크다운 생성"""
  md = "# 📋 소방 점검실무행정 / NFTC 상호 비교 및 개정 반영 단권화 노트\n\n"
  md += "## 1. 개정 현황 요약표\n\n"
  md += "| 조문/항목 번호 | 상태 | 기존(구판) 항목명 | 최신(개정) 항목명 |\n"
  md += "| :--- | :---: | :--- | :--- |\n"

  for r in comparison_results:
    if r["status"] == "유지":
      status_icon = "🟢"
    elif r["status"] == "신설(추가)":
      status_icon = "🔴"
    elif r["status"] == "개정(수정)":
      status_icon = "🟡"
    else:
      status_icon = "⚪"
    md += (
        f"| {r['section']} | {status_icon} {r['status']} | {r['old_title']} |"
        f" {r['new_title']} |\n"
    )

  md += "\n---\n\n## 2. 세부 상호 비교 및 단권화 보완 내역\n\n"

  for r in comparison_results:
    if r["status"] == "유지":
      continue
    md += f"### [{r['status']}] 조문: {r['section']}\n\n"

    if r["status"] == "개정(수정)":
      md += (
          "**[라인별 변경점 (Diff)]**\n```diff\n"
          + r["diff_text"]
          + "\n```\n\n"
      )
      md += "**[최신 반영 원문]**\n```markdown\n" + r["new_text"] + "\n```\n\n"
    elif r["status"] == "신설(추가)":
      md += "**[최신 신설 조문]**\n```markdown\n" + r["new_text"] + "\n```\n\n"
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
  st.subheader("2. 최신 개정 NFTC/법령 MD 업로드")
  new_file = st.file_uploader("최신 .md 파일 선택", type=["md", "txt"], key="new")

if old_file and new_file:
  old_text = safe_decode(old_file)
  new_text = safe_decode(new_file)

  st.success("두 파일이 성공적으로 로드되었습니다.")

  if st.button("🔍 상호 비교 및 단권화 MD 생성 실행", type="primary"):
    with st.spinner("조문 분석 및 상호 비교 중..."):
      old_sections = parse_markdown_by_sections(old_text)
      new_sections = parse_markdown_by_sections(new_text)

      results = compare_sections(old_sections, new_sections)
      final_md = generate_diff_markdown(results)

      st.markdown("### 📊 상호 비교 결과 요약")

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
      st.subheader("📄 생성된 단권화 개정 마크다운 미리보기")
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
