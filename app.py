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

# ── WDS (Wanted Design System) 스타일 ────────────────────
st.markdown("""
<style>
    /* ── Pretendard 폰트 ── */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

    /* ── WDS 색상 토큰 ── */
    :root {
        --wds-blue:       #355DF9;
        --wds-blue-dark:  #2347D4;
        --wds-blue-light: #EEF2FF;
        --wds-bg:         #F4F6FA;
        --wds-surface:    #FFFFFF;
        --wds-border:     #E1E2E4;
        --wds-text1:      #1D2A3B;
        --wds-text2:      #767676;
        --wds-text3:      #AAAAAA;
        --wds-success:    #00B761;
        --wds-error:      #F03B3B;
        --wds-radius-sm:  6px;
        --wds-radius:     10px;
        --wds-radius-lg:  16px;
    }

    /* ── 전체 배경 & 폰트 ── */
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: var(--wds-text1);
    }
    .stApp {
        background-color: var(--wds-bg) !important;
    }

    /* ── 메인 콘텐츠 배경 ── */
    .main .block-container {
        background-color: var(--wds-bg);
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* ── 사이드바 ── */
    [data-testid="stSidebar"] {
        background-color: var(--wds-surface) !important;
        border-right: 1px solid var(--wds-border);
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* ── 헤더 카드 ── */
    .wds-header {
        background: var(--wds-surface);
        border: 1px solid var(--wds-border);
        border-radius: var(--wds-radius-lg);
        padding: 28px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .wds-header-badge {
        background: var(--wds-blue);
        color: #fff;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .wds-header-title {
        font-size: 22px;
        font-weight: 800;
        color: var(--wds-text1);
        margin: 0 0 4px 0;
        line-height: 1.3;
    }
    .wds-header-sub {
        font-size: 14px;
        color: var(--wds-text2);
        margin: 0;
    }

    /* ── 카드 ── */
    .wds-card {
        background: var(--wds-surface);
        border: 1px solid var(--wds-border);
        border-radius: var(--wds-radius);
        padding: 24px;
        margin-bottom: 16px;
    }
    .wds-card-title {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: var(--wds-text2);
        text-transform: uppercase;
        margin-bottom: 16px;
    }

    /* ── 히스토리 아이템 ── */
    .wds-history-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 12px;
        border-radius: var(--wds-radius-sm);
        background: var(--wds-bg);
        border: 1px solid var(--wds-border);
        margin-bottom: 8px;
        transition: border-color 0.15s;
    }
    .wds-history-item:hover { border-color: var(--wds-blue); }
    .wds-history-name {
        font-size: 13px;
        font-weight: 600;
        color: var(--wds-text1);
    }
    .wds-history-meta {
        font-size: 11px;
        color: var(--wds-text3);
        margin-top: 2px;
    }
    .wds-badge-done {
        background: #E8F9F0;
        color: var(--wds-success);
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 20px;
    }

    /* ── 빈 히스토리 ── */
    .wds-empty {
        text-align: center;
        padding: 20px 0;
        color: var(--wds-text3);
        font-size: 13px;
    }

    /* ── 섹션 라벨 ── */
    .wds-label {
        font-size: 12px;
        font-weight: 700;
        color: var(--wds-text2);
        letter-spacing: 0.04em;
        margin-bottom: 6px;
        text-transform: uppercase;
    }

    /* ── input 오버라이드 ── */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background: var(--wds-bg) !important;
        border: 1.5px solid var(--wds-border) !important;
        border-radius: var(--wds-radius-sm) !important;
        font-family: 'Pretendard', sans-serif !important;
        font-size: 14px !important;
        color: var(--wds-text1) !important;
        transition: border-color 0.15s !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: var(--wds-blue) !important;
        box-shadow: 0 0 0 3px var(--wds-blue-light) !important;
    }
    div[data-testid="stTextArea"] textarea {
        font-size: 13.5px !important;
        line-height: 1.65 !important;
    }

    /* ── 기본 버튼 (Primary) ── */
    div[data-testid="stButton"] button[kind="primary"] {
        background: var(--wds-blue) !important;
        color: #fff !important;
        border: none !important;
        border-radius: var(--wds-radius-sm) !important;
        font-family: 'Pretendard', sans-serif !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        padding: 12px 0 !important;
        transition: background 0.15s !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: var(--wds-blue-dark) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:disabled {
        background: var(--wds-border) !important;
        color: var(--wds-text3) !important;
    }

    /* ── secondary 버튼 ── */
    div[data-testid="stButton"] button[kind="secondary"] {
        background: var(--wds-surface) !important;
        color: var(--wds-blue) !important;
        border: 1.5px solid var(--wds-blue) !important;
        border-radius: var(--wds-radius-sm) !important;
        font-family: 'Pretendard', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        transition: all 0.15s !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        background: var(--wds-blue-light) !important;
    }

    /* ── 기본 버튼(초기화 등) ── */
    div[data-testid="stButton"] button {
        border-radius: var(--wds-radius-sm) !important;
        font-family: 'Pretendard', sans-serif !important;
        font-weight: 600 !important;
    }

    /* ── progress bar ── */
    div[data-testid="stProgressBar"] > div > div {
        background-color: var(--wds-blue) !important;
    }

    /* ── success / warning 박스 ── */
    div[data-testid="stAlert"] {
        border-radius: var(--wds-radius-sm) !important;
        font-family: 'Pretendard', sans-serif !important;
        font-size: 14px !important;
    }

    /* ── divider ── */
    hr { border-color: var(--wds-border) !important; }

    /* ── 사이드바 타이틀 ── */
    .wds-sidebar-title {
        font-size: 13px;
        font-weight: 800;
        color: var(--wds-text2);
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0 0 10px 0;
        border-bottom: 1px solid var(--wds-border);
        margin-bottom: 14px;
    }

    /* ── 컬럼 카드 래퍼 ── */
    .wds-panel {
        background: var(--wds-surface);
        border: 1px solid var(--wds-border);
        border-radius: var(--wds-radius-lg);
        padding: 24px 24px 28px;
        height: 100%;
    }
    .wds-panel-header {
        font-size: 15px;
        font-weight: 700;
        color: var(--wds-text1);
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--wds-border);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── 코드 블록 ── */
    pre, code {
        font-size: 13px !important;
        border-radius: var(--wds-radius-sm) !important;
    }

    /* ── label 글꼴 ── */
    label {
        font-family: 'Pretendard', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: var(--wds-text2) !important;
    }

    /* ── 서브헤더 숨김 (커스텀으로 대체) ── */
    h3 { display: none !important; }
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
    """Jina Reader API로 블로그 내용 무료 추출"""
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
    """Claude API로 피드백 생성"""
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


# ── API 키: Secrets에서 자동 로드 ─────────────────────
_secret_key = ""
try:
    _secret_key = st.secrets.get("CLAUDE_API_KEY", "")
except Exception:
    pass

# ── 사이드바 ───────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="wds-sidebar-title">⚙️ 설정</div>', unsafe_allow_html=True)

    if _secret_key:
        claude_api_key = _secret_key
        st.markdown(
            '<div style="font-size:13px;color:#00B761;font-weight:600;padding:8px 12px;'
            'background:#E8F9F0;border-radius:6px;margin-bottom:16px;">🔒 API 키 설정됨</div>',
            unsafe_allow_html=True
        )
    else:
        claude_api_key = st.text_input(
            "Claude API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Anthropic Console에서 발급 — Secrets 설정 후 이 칸은 사라져요",
        )
        st.caption("🔒 키는 이 세션에서만 사용되고 저장되지 않아요")

    st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="wds-sidebar-title">📚 히스토리</div>', unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    if st.session_state.history:
        if st.button("전체 초기화", use_container_width=True):
            st.session_state.history = []
            st.rerun()
        st.markdown("<div style='margin-top:10px;'>", unsafe_allow_html=True)
        for item in reversed(st.session_state.history):
            st.markdown(
                f"""<div class="wds-history-item">
                    <div>
                        <div class="wds-history-name">{item['name']}</div>
                        <div class="wds-history-meta">{item['date']}</div>
                    </div>
                    <span class="wds-badge-done">완료</span>
                </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="wds-empty">아직 생성된 피드백이 없어요</div>',
            unsafe_allow_html=True
        )


# ── 메인 헤더 ──────────────────────────────────────────
st.markdown("""
<div class="wds-header">
    <div>
        <div class="wds-header-badge">POTENUP AI</div>
        <p class="wds-header-title">블로그 피드백 에이전트</p>
        <p class="wds-header-sub">블로그 링크 하나로 채용팀이 주목하는 피드백을 자동 생성해요</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 2컬럼 레이아웃 ─────────────────────────────────────
col1, col2 = st.columns([1, 1.5], gap="large")

# ── 좌측: 입력 패널 ────────────────────────────────────
with col1:
    st.markdown('<div class="wds-panel">', unsafe_allow_html=True)
    st.markdown('<div class="wds-panel-header">📥 블로그 정보 입력</div>', unsafe_allow_html=True)

    blog_url = st.text_input(
        "블로그 URL",
        placeholder="https://velog.io/@...",
        help="velog, tistory, medium 등 지원",
        label_visibility="visible",
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    can_generate = bool(blog_url and claude_api_key)
    generate_btn = st.button(
        "✨ 피드백 생성하기",
        type="primary",
        use_container_width=True,
        disabled=not can_generate,
        help="" if can_generate else "URL을 입력하고 API 키를 설정해주세요",
    )

    if not claude_api_key and not _secret_key:
        st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
        st.warning("⬅️ 사이드바에 Claude API Key를 먼저 입력해주세요")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── 우측: 피드백 프리뷰 ────────────────────────────────
with col2:
    st.markdown('<div class="wds-panel">', unsafe_allow_html=True)
    st.markdown('<div class="wds-panel-header">📤 피드백 프리뷰</div>', unsafe_allow_html=True)

    if "feedback_text" not in st.session_state:
        st.session_state.feedback_text = ""

    # 피드백 생성 실행
    if generate_btn and can_generate:
        progress = st.progress(0, text="블로그 읽는 중...")
        blog_content = fetch_blog_content(blog_url)
        progress.progress(40, text="Claude가 피드백 작성 중...")
        feedback = generate_feedback(blog_url, blog_content, claude_api_key)
        st.session_state.feedback_text = feedback
        st.session_state.current_url = blog_url
        progress.progress(100, text="완료!")
        progress.empty()
        st.success("✅ 피드백 생성 완료!")

    # 수정 가능한 텍스트 영역
    edited_feedback = st.text_area(
        "생성된 피드백 (직접 수정 가능해요)",
        value=st.session_state.feedback_text,
        height=430,
        placeholder="왼쪽에서 블로그 URL을 입력하고\n'피드백 생성하기'를 눌러주세요 ✨",
        label_visibility="collapsed",
    )

    # 복사 버튼
    if st.session_state.feedback_text:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("📋 슬랙 복사용으로 보기", use_container_width=True):
            st.code(edited_feedback, language=None)
            st.caption("위 텍스트 전체 선택(Ctrl+A) 후 슬랙에 붙여넣어 주세요")

        # 히스토리 저장
        short_url = blog_url.split("/")[-1][:20] if blog_url else "블로그"
        urls_in_history = [h["url"] for h in st.session_state.history]
        if blog_url not in urls_in_history:
            st.session_state.history.append({
                "name": short_url,
                "url": blog_url,
                "level": "🤖 자동 판단",
                "date": datetime.now().strftime("%m/%d %H:%M"),
            })

    st.markdown('</div>', unsafe_allow_html=True)
