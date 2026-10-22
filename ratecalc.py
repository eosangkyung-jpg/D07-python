"""환율 계산기 — 금액과 통화를 고르면 바꾼 금액을 웹 화면(Streamlit)으로 보여 줘요.

실행: conda activate camp → streamlit run ratecalc.py
      (python ratecalc.py 가 아니에요! 브라우저가 자동으로 열려요)
준비: .env 파일에 EXCHANGERATE_API_KEY=내키 (값은 .env에만!)

어제와 비교: ExchangeRate-API 무료 플랜은 '오늘 환율'만 줘요.
그래서 실행할 때마다 오늘 환율을 rate_history.json 에 적어 두고, 이전 기록과 비교해요.
(처음 실행한 날은 비교할 기록이 없어서 색이 안 나와요)
"""

import json
import os
from datetime import datetime, timedelta, timezone

import requests
import streamlit as st
from dotenv import load_dotenv

API = {
    "rates": "https://v6.exchangerate-api.com/v6/latest/USD",  # 🔌 ExchangeRate-API 최신 환율 (1달러 기준)
}

# 날짜별 환율 기록 (이 파일 옆에 저장, GitHub엔 안 올림)
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rate_history.json")
KEEP_DAYS = 7                       # 기록은 최근 7개만 남겨요
KST = timezone(timedelta(hours=9))

# 계산기에서 고를 수 있는 통화 (코드: 이름)
CURRENCIES = {
    "KRW": "🇰🇷 한국 원",
    "USD": "🇺🇸 미국 달러",
    "JPY": "🇯🇵 일본 엔",
    "EUR": "🇪🇺 유로",
    "CNY": "🇨🇳 중국 위안",
    "GBP": "🇬🇧 영국 파운드",
    "AUD": "🇦🇺 호주 달러",
    "CAD": "🇨🇦 캐나다 달러",
    "HKD": "🇭🇰 홍콩 달러",
    "SGD": "🇸🇬 싱가포르 달러",
    "TWD": "🇹🇼 대만 달러",
    "THB": "🇹🇭 태국 바트",
    "VND": "🇻🇳 베트남 동",
    "PHP": "🇵🇭 필리핀 페소",
}

# 위쪽 '주요 환율' 칸: (통화, 몇 단위 기준) — 엔은 보통 100엔 기준으로 봐요
BOARD = [("USD", 1), ("JPY", 100), ("EUR", 1), ("CNY", 1), ("GBP", 1)]

# 깔끔한 무채색 검정 베이스 + 오르면 빨강, 내리면 파랑 (한국 주식·환율 화면 관례)
UP, DOWN, FLAT = "#FF5A5F", "#4C9AFF", "#8A8A8A"
CSS = """
<style>
.card {background:#141414; border:1px solid #2A2A2A; border-radius:12px; padding:16px 18px;}
.card .label {color:#8A8A8A; font-size:0.85rem;}
.card .value {color:#F5F5F5; font-size:1.5rem; font-weight:600; margin-top:4px;}
.card .delta {font-size:0.85rem; margin-top:2px;}
.result {background:#141414; border:1px solid #2A2A2A; border-radius:12px; padding:22px; text-align:center;}
.result .big {color:#F5F5F5; font-size:2.2rem; font-weight:700;}
.result .small {color:#8A8A8A; font-size:0.9rem; margin-top:6px;}
</style>
"""


# Streamlit은 입력이 바뀔 때마다 파일 전체를 다시 실행해요.
# 무료 플랜은 한 달 1,500번이고 환율은 하루 한 번만 바뀌어서, 1시간 동안은 받아 둔 결과를 재사용해요.
@st.cache_data(ttl=3600)
def get_rates(key):
    """1달러 기준 환율을 받아 와요. (데이터, 에러 메시지) 두 개를 돌려줘요."""
    headers = {"Authorization": f"Bearer {key}"}  # 키는 주소가 아니라 헤더로 보내요
    try:
        res = requests.get(API["rates"], headers=headers, timeout=10)  # 🔌 API 호출
    except requests.exceptions.Timeout:
        return None, "환율 서버가 10초 안에 대답하지 않았어요. 잠시 뒤에 다시 열어 주세요."
    except requests.exceptions.RequestException:
        return None, "환율 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요."

    try:
        data = res.json()
    except ValueError:
        return None, f"환율을 가져오지 못했어요 (응답 코드 {res.status_code})."

    if data.get("result") != "success":
        error_type = data.get("error-type")  # data["error-type"] = 실패 이유
        if error_type == "invalid-key":
            return None, "환율 키가 틀렸어요. .env의 EXCHANGERATE_API_KEY를 확인해 주세요."
        if error_type == "inactive-account":
            return None, "환율 사이트 가입 인증 메일을 확인해 주세요."
        if error_type == "quota-reached":
            return None, "이번 달 무료 사용량(1,500번)을 다 썼어요."
        return None, f"환율을 가져오지 못했어요 ({error_type or res.status_code})."
    return data, None


def load_history():
    """저장해 둔 날짜별 환율 기록을 읽어요. 없거나 깨졌으면 빈 기록."""
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_history(history, day, rates):
    """오늘 환율을 기록에 추가해요. 이미 오늘 기록이 있으면 그대로 둬요."""
    if day in history:
        return
    history[day] = {code: rates[code] for code in CURRENCIES if code in rates}
    for old in sorted(history)[:-KEEP_DAYS]:  # 오래된 기록은 지워요
        del history[old]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # 저장이 안 돼도 계산기는 그대로 보여 줘요


def cross(rates, frm, to):
    """1 frm 이 to 로 얼마인지. 1달러 기준 환율 두 개를 나눠서 계산해요."""
    return rates[to] / rates[frm]


def fmt_num(x):
    """큰 숫자는 소수 2자리, 아주 작은 숫자(예: 1원 → 달러)는 6자리까지"""
    return f"{x:,.2f}" if abs(x) >= 1 else f"{x:,.6f}"


def delta_html(now, before, prev_label):
    """이전 기록보다 올랐으면 빨간 ▲, 내렸으면 파란 ▼"""
    if before is None:
        return f'<div class="delta" style="color:{FLAT}">비교할 이전 기록 없음</div>'
    diff = now - before
    pct = diff / before * 100
    if abs(pct) < 0.005:
        return f'<div class="delta" style="color:{FLAT}">– {prev_label} 대비 변동 없음</div>'
    color, arrow = (UP, "▲") if diff > 0 else (DOWN, "▼")
    return f'<div class="delta" style="color:{color}">{arrow} {fmt_num(abs(diff))} ({pct:+.2f}%) · {prev_label} 대비</div>'


def main():
    st.set_page_config(page_title="환율 계산기", page_icon="💱")
    st.markdown(CSS, unsafe_allow_html=True)
    st.title("💱 환율 계산기")

    load_dotenv()
    key = os.getenv("EXCHANGERATE_API_KEY")
    if not key:
        st.error("❌ .env에 EXCHANGERATE_API_KEY가 없어요. .env.example을 보고 채워 주세요.")
        st.stop()

    data, error = get_rates(key)
    if error:
        st.error(f"❌ {error}")
        st.stop()

    rates = data["conversion_rates"]                  # data["conversion_rates"] = 1달러가 각 통화로 얼마인지 ({"KRW": 1380.5, ...})
    updated = datetime.fromtimestamp(data["time_last_update_unix"], KST)  # data["time_last_update_unix"] = 기준 시각 (time_last_update_utc 와 같은 시각)
    today = updated.strftime("%Y-%m-%d")

    # 오늘 기록 저장 + 바로 이전 기록 찾기
    history = load_history()
    save_history(history, today, rates)
    prev_days = [d for d in sorted(history) if d < today]
    prev = history[prev_days[-1]] if prev_days else None
    if prev_days:
        prev_date = datetime.strptime(prev_days[-1], "%Y-%m-%d").date()
        prev_label = "어제" if (updated.date() - prev_date).days == 1 else f"{prev_date.month}/{prev_date.day}"
    else:
        prev_label = ""

    # ── 주요 환율 (원화 기준) ──
    st.subheader("주요 환율")
    cols = st.columns(len(BOARD))
    for col, (code, unit) in zip(cols, BOARD):
        now = cross(rates, code, "KRW") * unit
        before = cross(prev, code, "KRW") * unit if prev and code in prev else None
        col.markdown(
            f'<div class="card"><div class="label">{CURRENCIES[code]} {unit}</div>'
            f'<div class="value">{fmt_num(now)}원</div>{delta_html(now, before, prev_label)}</div>',
            unsafe_allow_html=True,
        )

    # ── 계산기 ──
    st.subheader("계산기")
    codes = list(CURRENCIES)
    c1, c2, c3 = st.columns([2, 2, 2])
    amount = c1.number_input("금액", min_value=0.0, value=1.0, step=1.0)
    frm = c2.selectbox("이 통화를", codes, index=codes.index("USD"), format_func=lambda c: f"{CURRENCIES[c]} ({c})")
    to = c3.selectbox("이 통화로", codes, index=codes.index("KRW"), format_func=lambda c: f"{CURRENCIES[c]} ({c})")

    rate_now = cross(rates, frm, to)
    rate_before = cross(prev, frm, to) if prev and frm in prev and to in prev else None
    st.markdown(
        f'<div class="result"><div class="big">{fmt_num(amount * rate_now)} {to}</div>'
        f'<div class="small">{fmt_num(amount)} {frm} · 1 {frm} = {fmt_num(rate_now)} {to}</div>'
        f'{delta_html(rate_now, rate_before, prev_label)}</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        f"🕒 기준 시각: {updated.strftime('%Y-%m-%d %H:%M')} (한국 시간) · 하루 한 번 갱신돼요 · "
        "빨강 ▲ 올랐어요 / 파랑 ▼ 내렸어요 · 출처: 환율 ExchangeRate-API"
    )


main()
