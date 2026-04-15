import streamlit as st
import anthropic
import requests
import csv
import io
import re
from datetime import datetime

# ── 페이지 설정 ────────────────────────────────────────
st.set_page_config(
    page_title="POTENUP 블로그 피드백",
    layout="wide",
    page_icon="📝",
    initial_sidebar_state="collapsed"
)

# ── WDS 스타일 ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

:root {
    --blue:       #355DF9;
    --blue-dark:  #2347D4;
    --blue-light: #EEF2FF;
    --bg:         #F4F6FA;
    --surface:    #FFFFFF;
    --border:     #E1E2E4;
    --text1:      #1D2A3B;
    --text2:      #5C687A;
    --text3:      #AAAAAA;
    --green:      #00B761;
    --green-bg:   #E8F9F0;
    --red:        #F03B3B;
    --red-bg:     #FFF0F0;
    --radius:     12px;
    --radius-sm:  8px;
}

html, body, [class*="css"] {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text1);
}
.stApp { background: var(--bg) !important; }
.main .block-container {
    background: var(--bg);
    padding-top: 1.8rem;
    max-width: 1300px;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* Primary 버튼 */
button[kind="primary"] {
    background: var(--blue) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    height: 48px !important;
    transition: background 0.15s !important;
}
button[kind="primary"]:hover { background: var(--blue-dark) !important; }
button[kind="primary"]:disabled {
    background: var(--border) !important;
    color: var(--text3) !important;
}
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-weight: 600 !important;
}

/* Input */
input, [data-testid="stTextInput"] input {
    background: var(--bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 14px !important;
    color: var(--text1) !important;
    transition: border-color 0.15s !important;
}
input:focus, [data-testid="stTextInput"] input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px var(--blue-light) !important;
}
textarea, [data-testid="stTextArea"] textarea {
    background: var(--bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 13.5px !important;
    line-height: 1.7 !important;
    color: var(--text1) !important;
    transition: border-color 0.15s !important;
}
textarea:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px var(--blue-light) !important;
}

/* Label */
label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--text2) !important;
    font-family: 'Pretendard', sans-serif !important;
}

/* Progress */
[data-testid="stProgressBar"] > div > div { background: var(--blue) !important; }

/* Alert */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 14px !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: var(--bg) !important;
    border-bottom: 2px solid var(--border) !important;
    padding-bottom: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--text2) !important;
    padding: 10px 18px !important;
    border: none !important;
    transition: all 0.15s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius) var(--radius) !important;
    padding: 24px !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 14px 0 !important; }

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text3) !important;
    font-size: 12px !important;
    font-family: 'Pretendard', sans-serif !important;
}

/* Code */
pre, code { font-size: 13px !important; border-radius: var(--radius-sm) !important; }

/* h3 — 패널 소제목 */
h3 {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: var(--text2) !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid var(--border) !important;
    margin-bottom: 16px !important;
    font-family: 'Pretendard', sans-serif !important;
}

/* 컬럼 카드 */
[data-testid="column"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px 22px 26px !important;
}

/* 헤더 */
.wds-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 28px;
    margin-bottom: 20px;
}
.wds-badge {
    display: inline-block;
    background: var(--blue);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.07em;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}
.wds-title { font-size: 21px; font-weight: 800; color: var(--text1); margin: 0 0 5px 0; }
.wds-sub   { font-size: 14px; color: var(--text2); margin: 0; }

/* 시트 미리보기 카드 */
.wds-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin: 16px 0;
}
.wds-count-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--blue-light);
    color: var(--blue);
    font-size: 13px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 20px;
    margin-bottom: 12px;
}
.wds-student-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
}
.wds-student-row:last-child { border-bottom: none; }
.wds-student-name { font-weight: 600; color: var(--text1); min-width: 80px; }
.wds-student-url  { color: var(--text2); font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 피드백 탭 내부 */
.fb-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.fb-url {
    font-size: 12px;
    color: var(--blue);
    text-decoration: none;
    padding: 4px 10px;
    background: var(--blue-light);
    border-radius: 20px;
    font-weight: 600;
}
.fb-status-ok {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    font-weight: 700;
    color: var(--green);
    background: var(--green-bg);
    padding: 3px 10px;
    border-radius: 20px;
}
.fb-status-err {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    font-weight: 700;
    color: var(--red);
    background: var(--red-bg);
    padding: 3px 10px;
    border-radius: 20px;
}

/* 사이드바 */
.sidebar-section {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text3);
    margin: 4px 0 10px 0;
}
.api-ok {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--green-bg);
    color: var(--green);
    font-size: 13px;
    font-weight: 600;
    padding: 10px 14px;
    border-radius: var(--radius-sm);
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── 시스템 프롬프트 ────────────────────────────────────
SYSTEM_PROMPT = """
너는 카카오, 토스, 배민 수준의 현업 시니어 백엔드 개발자이자,
채용팀의 시각을 겸비한 기술 블로그 리뷰어야.

POTENUP(포텐업) 부트캠프 수강생들의 프로젝트 회고 및 기술 블로그를 리뷰하고,
슬랙 DM 형식의 피드백을 작성하는 역할을 해.

수강생들은 AI 기반 백엔드 개발자 취업을 준비 중인 입문~중급 레벨이야.
피드백 목적: 채용팀이 인상받는 블로그로 발전시키는 것.

## 레벨 판단 기준 (블로그를 보고 직접 판단)
- 입문: 기술 선택 이유 없음, 단순 나열, 결과만 기술, 회고가 감상문 수준
- 중급: WHY 설명 시도, 문제-해결 흐름 있음, 트레이드오프 언급

## 평가 기준 (POTENUP 가이드라인)
1. 서론에서 문제 배경·맥락·목적이 명확히 드러나는가?
2. 이 글을 통해 독자가 얻을 핵심 메시지를 한 문장으로 정의할 수 있는가?
3. 문제 → 시도 → 실패 → 해결 → 개선의 흐름이 자연스럽게 이어지는가?
4. 기능/구현 방식 선택에 대한 이유·근거가 설명되어 있는가?
5. 참고 링크·문서·레퍼런스를 명확히 제시했는가?
6. 결과만 나열하지 않고 사고의 흐름이 전개되는 글인가?
7. 이미지·코드·다이어그램 등을 활용해 가독성을 높였는가?
8. 마지막에 배운 점, 아쉬움, 다음 개선 계획까지 정리했는가?

## 현업 기준선
- 수치/데이터: 모든 결정에 숫자 (예: "왕복 2회→1회", "응답 시간 230ms→95ms")
- 트레이드오프: 선택한 기술의 장점뿐 아니라 단점과 대안도 명시
- 레퍼런스: 공식 문서, RFC 링크 포함
- 다이어그램: Before/After 아키텍처, 시퀀스 다이어그램
- 핵심 메시지: 제목만 봐도 무슨 글인지 알 수 있음

## 출력 포맷 — 중급자 (직접형 → 격려형)
안녕하세요 *[이름]*님! [블로그를 실제로 읽고 느낀 진짜 인상 한 줄] 😄
피드백 드릴게요!

📌 *[블로그 제목]*
[URL]

━━━━━━━━━━
🔧 *먼저 개선하면 레벨업할 부분들이에요*
━━━━━━━━━━

• *[개선점 제목]*
   → [구체적으로 무엇이 부족한지]
   → [어떻게 고치면 되는지 — Before/After 예시 포함]

(2~4개 개선점 작성)

━━━━━━━━━━
✅ *이건 진짜 잘했어요*
━━━━━━━━━━

• *[강점 제목]*
   → [왜 잘했는지 — 현업 기준과 연결해서]

(2~4개 강점 작성)

━━━━━━━━━━
🎯 *한마디*
━━━━━━━━━━
[핵심 개선 방향 1~2줄]
[면접에서 받을 예상 질문 1개] 💪

## 출력 포맷 — 입문자 (격려형 → 직접형)
안녕하세요 *[이름]*님! [블로그를 실제로 읽고 느낀 진짜 인상 한 줄] 🙂
피드백 드릴게요!

📌 *[블로그 제목]*
[URL]

━━━━━━━━━━
✅ *진심으로 잘 썼다고 느낀 부분들이에요*
━━━━━━━━━━

• *[강점 제목]*
   → [왜 잘했는지]
   → [현업/채용팀 관점에서 왜 의미 있는지]

(2~3개 강점 작성)

━━━━━━━━━━
🔧 *이 부분들만 채워주면 훨씬 더 좋아져요*
━━━━━━━━━━

• *[개선점 제목]*
   → [무엇이 부족한지]
   → [어떻게 고치면 되는지 — 구체적으로]

(2~4개 개선점 작성)

━━━━━━━━━━
🎯 *한마디*
━━━━━━━━━━
[핵심 강점 인정 + 다음 단계 방향 1~2줄]
[응원 메시지] 🙌

## 톤 규칙 (반드시 지킬 것)
- 첫 줄 인사는 블로그를 실제로 읽은 사람이 쓰는 것처럼 — 블로그 내용에서 느낀 진짜 인상 한 줄
- 불릿 주제는 *굵게* 짧게, 설명은 → 들여쓰기(3칸)로 분리
- 문장은 짧게 — 한 → 당 1~2줄 이내
- 개선점은 Before/After 예시 또는 구체적 방향으로 — "추가하세요"만으론 부족
- 채용팀 관점 연결: "면접관은 이렇게 물어봐요", "채용팀은 이걸 보고 ~로 읽어요"
- 절대 하지 말 것: 점수 매기기, 과도한 칭찬 반복, 형식적인 마무리
"""

# ── 헬퍼 함수 ──────────────────────────────────────────
def parse_sheet_id(url: str) -> tuple[str, str]:
    """Google Sheets URL → (sheet_id, gid)"""
    m = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if not m:
        raise ValueError("올바른 Google Sheets URL이 아니에요")
    sheet_id = m.group(1)
    gid_m = re.search(r'gid=(\d+)', url)
    gid = gid_m.group(1) if gid_m else '0'
    return sheet_id, gid


def load_sheet(sheet_url: str) -> list[dict]:
    """Google Sheet CSV 내보내기로 데이터 로드 (이름, URL 2열 구조)"""
    sheet_id, gid = parse_sheet_id(sheet_url)
    csv_url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/export?format=csv&gid={gid}"
    )
    resp = requests.get(csv_url, timeout=15)
    if resp.status_code != 200:
        raise ValueError(
            f"시트를 불러오지 못했어요 (상태 {resp.status_code}). "
            "'링크가 있는 모든 사용자 — 뷰어' 공개 설정을 확인해주세요."
        )

    reader = csv.reader(io.StringIO(resp.text))
    rows = list(reader)

    # 헤더 행 건너뛰기 (첫 셀이 URL처럼 안 생겼으면 헤더로 간주)
    url_pattern = re.compile(r'https?://', re.IGNORECASE)
    start = 0
    if rows and not url_pattern.match(str(rows[0][1]).strip() if len(rows[0]) > 1 else ''):
        start = 1

    students = []
    for row in rows[start:]:
        if len(row) < 2:
            continue
        name = row[0].strip()
        url  = row[1].strip()
        if url_pattern.match(url) and name:
            students.append({"name": name, "url": url})

    return students


def fetch_blog_content(url: str) -> str:
    try:
        resp = requests.get(
            f"https://r.jina.ai/{url}",
            headers={"Accept": "text/plain", "X-Timeout": "20"},
            timeout=25,
        )
        if resp.status_code == 200:
            return resp.text[:10000]
        return f"[블로그 내용을 가져오지 못했어요. 상태: {resp.status_code}]"
    except Exception as e:
        return f"[오류: {e}]"


def generate_feedback(name: str, url: str, content: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""
아래 블로그를 리뷰하고 슬랙 DM 피드백을 작성해줘.

수강생 이름: {name}
블로그 URL: {url}
수강생 레벨: 블로그 내용을 보고 직접 판단해줘 (입문/중급 기준은 시스템 프롬프트 참고)

블로그 내용:
{content}

시스템 프롬프트의 출력 포맷을 그대로 따라서 작성해줘.
첫 줄 인사는 반드시 이 블로그 내용에서 느낀 진짜 인상을 한 줄로 써줘 — 형식적인 인사 금지.
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── API 키 로드 ────────────────────────────────────────
_secret_key = ""
try:
    _secret_key = st.secrets.get("CLAUDE_API_KEY", "")
except Exception:
    pass

# ── Session state 초기화 ──────────────────────────────
for k, v in {
    "students": [],       # [{name, url}]
    "feedbacks": {},      # {name: str | None | "error"}
    "sheet_loaded": False,
    "generation_done": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── 사이드바 ───────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-section">⚙️ 설정</p>', unsafe_allow_html=True)

    if _secret_key:
        claude_api_key = _secret_key
        st.markdown('<div class="api-ok">🔒 API 키 설정됨</div>', unsafe_allow_html=True)
    else:
        claude_api_key = st.text_input(
            "Claude API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Anthropic Console에서 발급",
        )
        st.caption("🔒 이 세션에서만 사용, 저장 안 됨")

    st.divider()

    # 진행 현황
    if st.session_state.students:
        done = sum(1 for v in st.session_state.feedbacks.values() if v and v != "error")
        total = len(st.session_state.students)
        st.markdown('<p class="sidebar-section">📊 진행 현황</p>', unsafe_allow_html=True)
        st.progress(done / total if total else 0,
                    text=f"{done} / {total} 완료")
        for s in st.session_state.students:
            status = st.session_state.feedbacks.get(s["name"])
            if status and status != "error":
                icon = "✅"
            elif status == "error":
                icon = "❌"
            else:
                icon = "⏳"
            st.caption(f"{icon} {s['name']}")

    if st.session_state.generation_done:
        st.divider()
        if st.button("🔄 처음부터 다시", use_container_width=True):
            st.session_state.students = []
            st.session_state.feedbacks = {}
            st.session_state.sheet_loaded = False
            st.session_state.generation_done = False
            st.rerun()


# ── 메인 헤더 ──────────────────────────────────────────
st.markdown("""
<div class="wds-header">
    <span class="wds-badge">POTENUP AI</span>
    <p class="wds-title">블로그 피드백 에이전트</p>
    <p class="wds-sub">구글 시트 링크 하나로 수강생 전체 피드백을 한 번에 생성해요</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# STEP 1 — 시트 입력
# ══════════════════════════════════════════════════════
if not st.session_state.sheet_loaded:
    col_a, col_b = st.columns([1, 1.5], gap="medium")

    with col_a:
        st.subheader("📋 구글 시트 연결")
        sheet_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="시트 공유 설정: '링크가 있는 모든 사용자 — 뷰어'로 변경해주세요",
        )
        st.caption("📌 시트 형식: A열 수강생 이름 | B열 블로그 URL")

        load_btn = st.button(
            "📥 수강생 목록 불러오기",
            type="primary",
            use_container_width=True,
            disabled=not bool(sheet_url),
        )

        if not claude_api_key:
            st.warning("⬅️ 사이드바에 Claude API Key를 먼저 입력해주세요")

        if load_btn and sheet_url:
            with st.spinner("시트 불러오는 중..."):
                try:
                    students = load_sheet(sheet_url)
                    if not students:
                        st.error("유효한 수강생 데이터가 없어요. 시트 형식을 확인해주세요.")
                    else:
                        st.session_state.students = students
                        st.session_state.sheet_loaded = True
                        st.rerun()
                except Exception as e:
                    st.error(str(e))

    with col_b:
        st.subheader("📌 시트 형식 안내")
        st.markdown("""
<div style="background:#F4F6FA;border:1px solid #E1E2E4;border-radius:8px;padding:16px;font-size:13px;">
<b>A열 (이름)</b> &nbsp;&nbsp; <b>B열 (블로그 URL)</b><br>
<hr style="margin:8px 0;border-color:#E1E2E4;">
홍길동 &nbsp;&nbsp;&nbsp;&nbsp; https://velog.io/@...<br>
김철수 &nbsp;&nbsp;&nbsp;&nbsp; https://blog.tistory.com/...<br>
이영희 &nbsp;&nbsp;&nbsp;&nbsp; https://medium.com/@...<br>
</div>
<div style="margin-top:12px;font-size:13px;color:#5C687A;">
💡 헤더 행(이름, URL 등)이 있어도 자동으로 건너뛰어요
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# STEP 2 — 시트 로드 완료, 확인 후 생성
# ══════════════════════════════════════════════════════
elif st.session_state.sheet_loaded and not st.session_state.generation_done:
    students = st.session_state.students
    n = len(students)

    # 수강생 목록 미리보기
    st.markdown(f"""
<div class="wds-card">
    <div class="wds-count-badge">👥 수강생 {n}명 발견</div>
    {''.join(f'''
    <div class="wds-student-row">
        <span class="wds-student-name">{s["name"]}</span>
        <span class="wds-student-url">{s["url"]}</span>
    </div>''' for s in students)}
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2], gap="medium")
    with col1:
        go_btn = st.button(
            f"✨ {n}명 피드백 생성 시작",
            type="primary",
            use_container_width=True,
            disabled=not bool(claude_api_key),
        )
        if st.button("← 다시 입력", use_container_width=True):
            st.session_state.sheet_loaded = False
            st.session_state.students = []
            st.rerun()

    if go_btn and claude_api_key:
        overall = st.progress(0, text=f"0 / {n} 처리 중...")
        status_box = st.empty()

        for i, s in enumerate(students):
            name, url = s["name"], s["url"]
            status_box.info(f"⏳ [{i+1}/{n}] {name} 블로그 읽는 중...")
            try:
                content = fetch_blog_content(url)
                status_box.info(f"✍️ [{i+1}/{n}] {name} 피드백 작성 중...")
                feedback = generate_feedback(name, url, content, claude_api_key)
                st.session_state.feedbacks[name] = feedback
            except Exception as e:
                st.session_state.feedbacks[name] = "error"

            overall.progress((i + 1) / n, text=f"{i+1} / {n} 처리 중...")

        overall.progress(1.0, text="✅ 모두 완료!")
        status_box.success(f"🎉 {n}명 피드백 생성 완료!")
        st.session_state.generation_done = True
        st.rerun()


# ══════════════════════════════════════════════════════
# STEP 3 — 탭으로 결과 표시
# ══════════════════════════════════════════════════════
elif st.session_state.generation_done:
    students  = st.session_state.students
    feedbacks = st.session_state.feedbacks

    done_n = sum(1 for v in feedbacks.values() if v and v != "error")
    err_n  = sum(1 for v in feedbacks.values() if v == "error")

    # 요약 배너
    col_s1, col_s2, col_s3 = st.columns(3, gap="small")
    with col_s1:
        st.metric("전체 수강생", len(students))
    with col_s2:
        st.metric("✅ 생성 완료", done_n)
    with col_s3:
        st.metric("❌ 오류", err_n)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # 탭 생성
    tab_labels = [
        ("✅ " if feedbacks.get(s["name"]) and feedbacks[s["name"]] != "error"
         else "❌ ") + s["name"]
        for s in students
    ]
    tabs = st.tabs(tab_labels)

    for tab, s in zip(tabs, students):
        name = s["name"]
        url  = s["url"]
        fb   = feedbacks.get(name, "")

        with tab:
            # 상단 메타
            st.markdown(
                f'<div class="fb-header">'
                f'  <a class="fb-url" href="{url}" target="_blank">🔗 블로그 열기</a>'
                f'  {"<span class=\'fb-status-ok\'>✅ 완료</span>" if fb and fb != "error" else "<span class=\'fb-status-err\'>❌ 오류</span>"}'
                f'</div>',
                unsafe_allow_html=True,
            )

            if fb == "error":
                st.error("피드백 생성 중 오류가 발생했어요. 다시 생성해주세요.")
            elif fb:
                # 수정 가능한 피드백 영역
                edited = st.text_area(
                    f"피드백 — {name}",
                    value=fb,
                    height=450,
                    key=f"fb_{name}",
                    label_visibility="collapsed",
                )
                # 복사용 보기
                if st.button("📋 슬랙 복사용으로 보기", key=f"copy_{name}", use_container_width=True):
                    st.code(edited, language=None)
                    st.caption("전체 선택(Ctrl+A) 후 슬랙에 붙여넣으세요")
            else:
                st.info("피드백 데이터 없음")
