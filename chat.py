"""AI 챗봇 — 아래 입력칸에 말을 걸면 OpenAI 모델이 대답해요. 웹 화면(Streamlit)으로 보여 줘요.

실행: conda activate camp → streamlit run chat.py
      (python chat.py 가 아니에요! 브라우저가 자동으로 열려요)
준비: .env 파일에 OPENAI_API_KEY=내키 (값은 .env에만!)
"""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

API = {
    "chat": "https://api.openai.com/v1/chat/completions",  # 🔌 OpenAI 채팅 (대화 → 대답)
}

# 🤖 AI 모델은 여기 한 줄만 바꾸면 돼요. (예: "gpt-4o-mini" → "gpt-4o")
MODEL = "gpt-4o-mini"

# AI에게 먼저 알려 주는 '역할 설명'. 화면에는 안 보여요.
SYSTEM_PROMPT = (
    "너는 친절한 한국어 도우미야. 개발 초보자도 이해할 수 있게 쉽고 짧게 대답해. "
    "반말로 친근하게 대답해. "
    "두괄식으로 답변해: 첫 문장에 결론부터 말하고, 이유나 설명은 그다음에 붙여."
)

MAX_TURNS = 20  # AI에게 보낼 최근 대화 개수 (너무 길면 느려지고 요금이 늘어요)


def ask_ai(key, messages):
    """대화 기록을 보내고 AI의 대답을 받아 와요. (대답, 에러 메시지) 두 개를 돌려줘요.

    날씨·환율과 달리 @st.cache_data를 붙이지 않아요.
    같은 질문에도 매번 새로 대답해야 하고, 입력칸에 보냈을 때만 부르기 때문이에요.
    """
    headers = {"Authorization": f"Bearer {key}"}  # 키는 주소가 아니라 헤더로 보내요
    body = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages[-MAX_TURNS:],
    }
    try:
        res = requests.post(API["chat"], headers=headers, json=body, timeout=30)  # 🔌 API 호출
    except requests.exceptions.Timeout:
        return None, "AI가 30초 안에 대답하지 않았어요. 잠시 뒤에 다시 보내 주세요."
    except requests.exceptions.RequestException:
        return None, "OpenAI 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요."

    if res.status_code == 200:
        data = res.json()
        return data["choices"][0]["message"]["content"], None  # data["choices"][0]["message"]["content"] = AI의 대답 글

    try:
        code = res.json().get("error", {}).get("code")  # data["error"]["code"] = 실패 이유
    except ValueError:
        code = None
    if res.status_code == 401:
        return None, "OpenAI 키가 틀렸어요. .env의 OPENAI_API_KEY를 확인해 주세요."
    if res.status_code == 429 and code == "insufficient_quota":
        return None, "OpenAI 사용 크레딧이 없어요. 결제(Billing) 페이지에서 충전이 필요해요."
    if res.status_code == 429:
        return None, "너무 빨리 많이 보냈어요. 잠시 뒤에 다시 보내 주세요."
    if res.status_code == 404:
        return None, f"'{MODEL}' 모델을 쓸 수 없어요. 모델 이름을 확인해 주세요."
    return None, f"AI 대답을 받지 못했어요 (응답 코드 {res.status_code})."


def main():
    st.set_page_config(page_title="AI 챗봇", page_icon="🤖")
    st.title("🤖 AI 챗봇")
    st.caption(f"모델: {MODEL} · 출처: OpenAI")

    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        st.error("❌ .env에 OPENAI_API_KEY가 없어요. .env.example을 보고 채워 주세요.")
        st.stop()

    # Streamlit은 입력할 때마다 파일 전체를 다시 실행해서 변수가 초기화돼요.
    # 대화 기록은 session_state(브라우저 탭마다 따로 있는 기억 상자)에 넣어 둬야 사라지지 않아요.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.subheader("⚙️ 설정")
        st.write(f"모델: `{MODEL}`")
        if st.button("🧹 대화 지우기", use_container_width=True):
            st.session_state.messages = []

    # 지금까지의 대화를 말풍선으로 그려요
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("무엇이든 물어보세요")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("생각하는 중..."):
            answer, error = ask_ai(key, st.session_state.messages)
        if error:
            st.error(f"❌ {error}")
            st.session_state.messages.pop()  # 실패한 질문은 기록에서 빼요 (다시 보낼 수 있게)
            return
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})


main()
