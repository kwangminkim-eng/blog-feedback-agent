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

st.markdown("""
<style>
    .main-title { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
    .sub-caption { color: #888; font-size: 14px; margin-bottom: 20px; }
    .history-card {
        padding: 10px 14px;
        border-left: 3px solid #4CAF50;
        background: #f8f9fa;
        border-radius: 0 6px 6px 0;
        margin-bottom: 8px;
        font-size: 13px;
    }
    .history-card b { font-size: 14px; }
    .history-card small { color: #999; }
    div[data-testid="stTextArea"] textarea {
        font-size: 13.5px;
        line-height: 1.6;
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

## 레벨 판단 기준 (레벨이 "자동 판단"인 경우 블로그를 보고 직접 판단)
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


def generate_feedback(url: str, content: str, name: str, level: str, api_key: str) -> str:
    """Claude API로 피드백 생성"""
    client = anthropic.Anthropic(api_key=api_key)

    level_map = {
        "🤖 자동 판단": "블로그 내용을 보고 직접 레벨을 판단해줘",
        "🌱 입문": "입문 레벨 — 입문자 포맷(격려형→직접형) 사용",
        "🚀 중급": "중급 레벨 — 중급자 포맷(직접형→격려형) 사용",
    }

    prompt = f"""
아래 블로그를 리뷰하고 슬랙 DM 피드백을 작성해줘.

수강생 이름: {name}
수강생 레벨: {level_map.get(level, '자동 판단')}
블로그 URL: {url}

블로그 내용:
{content}

시스템 프롬프트의 출력 포맷을 그대로 따라서 작성해줘.
첫 줄 인사는 반드시 이 블로그 내용에서 느낀 진짜 인상을 한 줄로 써줘 — 형식적인 인사 금지.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ── API 키: Secrets에서 자동 로드 ─────────────────────
# Streamlit Cloud Secrets에 CLAUDE_API_KEY가 있으면 자동 사용
# 없으면 사이드바 입력란 표시 (로컬 테스트용)
_secret_key = ""
try:
    _secret_key = st.secrets.get("CLAUDE_API_KEY", "")
except Exception:
    pass

# ── 사이드바 ───────────────────────────────────────────
with st.sidebar:
    # Secrets에 키가 있으면 입력란 숨김 (팀원들에게 노출 안 됨)
    if _secret_key:
        claude_api_key = _secret_key
        st.markdown("## 📚 히스토리")
    else:
        st.markdown("## ⚙️ API 설정")
        claude_api_key = st.text_input(
            "Claude API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Anthropic Console에서 발급 — Secrets 설정 후 이 칸은 사라져요",
        )
        st.caption("🔒 키는 이 세션에서만 사용되고 저장되지 않아요")
        st.divider()
        st.markdown("## 📚 히스토리")

    st.divider()

    # ── 히스토리 ──────────────────────────────────────
    st.markdown("## 📚 히스토리")

    if "history" not in st.session_state:
        st.session_state.history = []

    if st.session_state.history:
        if st.button("전체 초기화", use_container_width=True):
            st.session_state.history = []
            st.rerun()

        for item in reversed(st.session_state.history):
            st.markdown(
                f"""<div class="history-card">
                    <b>{item['name']}</b> ✅<br>
                    <small>{item['date']} · {item['level']}</small>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.caption("아직 생성된 피드백이 없어요")


# ── 메인 헤더 ──────────────────────────────────────────
st.markdown('<p class="main-title">📝 POTENUP 블로그 피드백 에이전트</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-caption">블로그 링크 하나로 수강생 피드백 자동 생성</p>', unsafe_allow_html=True)
st.divider()

# ── 2컬럼 레이아웃 ─────────────────────────────────────
col1, col2 = st.columns([1, 1.5], gap="large")

# ── 좌측: 입력 패널 ────────────────────────────────────
with col1:
    st.subheader("📥 정보 입력")

    blog_url = st.text_input(
        "블로그 URL *",
        placeholder="https://velog.io/@...",
        help="velog, tistory, medium 등 지원",
    )
    student_name = st.text_input(
        "수강생 이름 *",
        placeholder="성균",
        help="피드백 첫 줄 인사에 사용돼요",
    )
    level = st.radio(
        "수강생 레벨",
        ["🤖 자동 판단", "🌱 입문", "🚀 중급"],
        help="모르면 자동 판단 — Claude가 블로그 보고 결정해요",
    )

    st.divider()

    can_generate = bool(blog_url and student_name and claude_api_key)
    generate_btn = st.button(
        "✨ 피드백 생성하기",
        type="primary",
        use_container_width=True,
        disabled=not can_generate,
        help="" if can_generate else "URL, 이름, Claude API Key를 모두 입력해주세요",
    )

    if not claude_api_key and not _secret_key:
        st.warning("⬅️ 사이드바에 Claude API Key를 먼저 입력해주세요")

# ── 우측: 피드백 프리뷰 ────────────────────────────────
with col2:
    st.subheader("📤 피드백 프리뷰")

    if "feedback_text" not in st.session_state:
        st.session_state.feedback_text = ""

    # 피드백 생성 실행
    if generate_btn and can_generate:
        progress = st.progress(0, text="블로그 읽는 중...")
        blog_content = fetch_blog_content(blog_url)
        progress.progress(40, text="Claude가 피드백 작성 중...")
        feedback = generate_feedback(blog_url, blog_content, student_name, level, claude_api_key)
        st.session_state.feedback_text = feedback
        progress.progress(100, text="완료!")
        progress.empty()
        st.success(f"✅ {student_name}님 피드백 생성 완료!")

    # 수정 가능한 텍스트 영역
    edited_feedback = st.text_area(
        "생성된 피드백 ✏️ (직접 수정 가능해요)",
        value=st.session_state.feedback_text,
        height=430,
        placeholder="왼쪽에서 정보를 입력하고 '피드백 생성하기'를 눌러주세요",
    )

    # 복사 버튼
    if st.session_state.feedback_text:
        st.divider()
        if st.button("📋 복사용으로 보기", use_container_width=True):
            st.code(edited_feedback, language=None)
            st.caption("위 텍스트를 전체 선택(Ctrl+A) 후 복사해서 슬랙에 붙여넣어 주세요")

        # 히스토리 저장
        names_in_history = [h["name"] for h in st.session_state.history]
        if student_name not in names_in_history:
            st.session_state.history.append({
                "name": student_name,
                "url": blog_url,
                "level": level,
                "date": datetime.now().strftime("%m/%d %H:%M"),
            })
