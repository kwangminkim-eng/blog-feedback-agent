import streamlit as st
import anthropic
import requests
from datetime import datetime

# ── 페이지 설정 ────────────────────────────────────────
st.set_page_config(
    page_title="POTENUP 블로그 피드백",
    layout="wide",
    page_icon="📝",
    initial_sidebar_state="expanded"
)

# ── WDS (Wanted Design System) 스타일 ─────────────────
st.markdown("""
<style>
/* ── Pretendard 폰트 ── */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

:root {
    --blue:        #355DF9;
    --blue-dark:   #2347D4;
    --blue-light:  #EEF2FF;
    --bg:          #F4F6FA;
    --surface:     #FFFFFF;
    --border:      #E1E2E4;
    --text1:       #1D2A3B;
    --text2:       #5C687A;
    --text3:       #AAAAAA;
    --green:       #00B761;
    --green-bg:    #E8F9F0;
    --radius:      12px;
    --radius-sm:   8px;
}

/* ── 전체 폰트 & 배경 ── */
html, body, [class*="css"] {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp { background: var(--bg) !important; }
.main .block-container {
    background: var(--bg);
    padding-top: 1.8rem;
    max-width: 1280px;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── 버튼 Primary ── */
button[kind="primary"], .stButton > button[data-testid*="primary"] {
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

/* ── 버튼 Secondary ── */
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-weight: 600 !important;
}

/* ── input / textarea ── */
input, textarea, [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background: var(--bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 14px !important;
    color: var(--text1) !important;
    transition: border-color 0.15s !important;
}
input:focus, textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px var(--blue-light) !important;
}
[data-testid="stTextArea"] textarea {
    font-size: 13.5px !important;
    line-height: 1.7 !important;
}

/* ── label ── */
label, .stTextInput label, .stTextArea label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--text2) !important;
    font-family: 'Pretendard', sans-serif !important;
}

/* ── progress ── */
[data-testid="stProgressBar"] > div > div {
    background: var(--blue) !important;
}

/* ── alert ── */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-family: 'Pretendard', sans-serif !important;
}

/* ── divider ── */
hr { border-color: var(--border) !important; margin: 14px 0 !important; }

/* ── caption ── */
.stCaption, small {
    color: var(--text3) !important;
    font-size: 12px !important;
    font-family: 'Pretendard', sans-serif !important;
}

/* ── code block ── */
pre, code {
    font-size: 13px !important;
    border-radius: var(--radius-sm) !important;
}

/* ── 헤더 카드 ── */
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
.wds-title {
    font-size: 21px;
    font-weight: 800;
    color: var(--text1);
    margin: 0 0 5px 0;
    line-height: 1.3;
}
.wds-sub {
    font-size: 14px;
    color: var(--text2);
    margin: 0;
}

/* ── 패널 제목 (st.subheader → h3) ── */
h3 {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: var(--text2) !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding-bottom: 12px !important;
    border-bottom: 1px solid var(--border) !important;
    margin-bottom: 16px !important;
    font-family: 'Pretendard', sans-serif !important;
}

/* ── 컬럼을 카드처럼 ── */
[data-testid="column"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px 22px 26px !important;
}

/* ── 사이드바 섹션 제목 ── */
.sidebar-section {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text3);
    margin: 4px 0 10px 0;
}

/* ── API 키 상태 뱃지 ── */
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

/* ── 히스토리 아이템 ── */
.hist-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 12px;
    border-radius: var(--radius-sm);
    background: var(--bg);
    border: 1px solid var(--border);
    margin-bottom: 8px;
}
.hist-name { font-size: 13px; font-weight: 600; color: var(--text1); }
.hist-time { font-size: 11px; color: var(--text3); margin-top: 2px; }
.hist-done {
    background: var(--green-bg);
    color: var(--green);
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 20px;
    white-space: nowrap;
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
def fetch_blog_content(url: str) -> str:
    try:
        jina_url = f"https://r.jina.ai/{url}"
        headers = {"Accept": "text/plain", "X-Timeout": "20"}
        response = requests.get(jina_url, headers=headers, timeout=25)
        if response.status_code == 200:
            return response.text[:10000]
        return f"[블로그 내용을 가져오지 못했어요. 상태 코드: {response.status_code}]"
    except Exception as e:
        return f"[오류 발생: {str(e)}]"


def generate_feedback(url: str, content: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""
아래 블로그를 리뷰하고 슬랙 DM 피드백을 작성해줘.

수강생 레벨: 블로그 내용을 보고 직접 레벨을 판단해줘 (입문/중급 기준은 시스템 프롬프트 참고)
블로그 URL: {url}

블로그 내용:
{content}

시스템 프롬프트의 출력 포맷을 그대로 따라서 작성해줘.
수강생 이름은 블로그 글쓴이 이름이나 닉네임에서 직접 파악해서 써줘.
첫 줄 인사는 반드시 이 블로그 내용에서 느낀 진짜 인상을 한 줄로 써줘 — 형식적인 인사 금지.
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ── API 키 로드 ────────────────────────────────────────
_secret_key = ""
try:
    _secret_key = st.secrets.get("CLAUDE_API_KEY", "")
except Exception:
    pass

# ── 사이드바 ───────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-section">⚙️ 설정</p>', unsafe_allow_html=True)

    if _secret_key:
        claude_api_key = _secret_key
        st.markdown(
            '<div class="api-ok">🔒 API 키 설정됨</div>',
            unsafe_allow_html=True
        )
    else:
        claude_api_key = st.text_input(
            "Claude API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Anthropic Console에서 발급",
        )
        st.caption("🔒 키는 이 세션에서만 사용되고 저장되지 않아요")

    st.divider()
    st.markdown('<p class="sidebar-section">📚 히스토리</p>', unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    if st.session_state.history:
        if st.button("전체 초기화", use_container_width=True):
            st.session_state.history = []
            st.rerun()
        for item in reversed(st.session_state.history):
            st.markdown(
                f'<div class="hist-item">'
                f'  <div><div class="hist-name">{item["name"]}</div>'
                f'  <div class="hist-time">{item["date"]}</div></div>'
                f'  <span class="hist-done">완료</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("아직 생성된 피드백이 없어요")


# ── 메인 헤더 ──────────────────────────────────────────
st.markdown("""
<div class="wds-header">
    <span class="wds-badge">POTENUP AI</span>
    <p class="wds-title">블로그 피드백 에이전트</p>
    <p class="wds-sub">블로그 링크 하나로 채용팀이 주목하는 피드백을 자동 생성해요</p>
</div>
""", unsafe_allow_html=True)

# ── 2컬럼 레이아웃 ─────────────────────────────────────
col1, col2 = st.columns([1, 1.5], gap="medium")

with col1:
    st.subheader("📥 블로그 정보 입력")

    blog_url = st.text_input(
        "블로그 URL",
        placeholder="https://velog.io/@...",
        help="velog, tistory, medium 등 지원",
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    can_generate = bool(blog_url and claude_api_key)
    generate_btn = st.button(
        "✨ 피드백 생성하기",
        type="primary",
        use_container_width=True,
        disabled=not can_generate,
        help="" if can_generate else "URL 입력 후 API 키를 설정해주세요",
    )

    if not claude_api_key and not _secret_key:
        st.warning("⬅️ 사이드바에 Claude API Key를 먼저 입력해주세요")


with col2:
    st.subheader("📤 피드백 프리뷰")

    if "feedback_text" not in st.session_state:
        st.session_state.feedback_text = ""

    if generate_btn and can_generate:
        progress = st.progress(0, text="블로그 읽는 중...")
        blog_content = fetch_blog_content(blog_url)
        progress.progress(40, text="Claude가 피드백 작성 중...")
        feedback = generate_feedback(blog_url, blog_content, claude_api_key)
        st.session_state.feedback_text = feedback
        progress.progress(100, text="완료!")
        progress.empty()
        st.success("✅ 피드백 생성 완료!")

    edited_feedback = st.text_area(
        "피드백 (직접 수정 가능해요)",
        value=st.session_state.feedback_text,
        height=430,
        placeholder="왼쪽에서 블로그 URL을 입력하고\n'피드백 생성하기'를 눌러주세요 ✨",
        label_visibility="collapsed",
    )

    if st.session_state.feedback_text:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        if st.button("📋 슬랙 복사용으로 보기", use_container_width=True):
            st.code(edited_feedback, language=None)
            st.caption("위 텍스트 전체 선택(Ctrl+A) 후 슬랙에 붙여넣어 주세요")

        short_url = blog_url.split("/")[-1][:20] if blog_url else "블로그"
        urls_in_history = [h["url"] for h in st.session_state.history]
        if blog_url not in urls_in_history:
            st.session_state.history.append({
                "name": short_url,
                "url": blog_url,
                "level": "🤖 자동 판단",
                "date": datetime.now().strftime("%m/%d %H:%M"),
            })
