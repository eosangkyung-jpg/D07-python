"""하루 3번 날씨 도우미 — 아침·점심·저녁마다 날씨에 맞는 할 일을 웹 화면(Streamlit)으로 알려 줘요.

실행: conda activate camp → streamlit run weather_proj.py
      (python weather_proj.py 가 아니에요! 브라우저가 자동으로 열려요)
준비: .env 파일에 OPENWEATHER_API_KEY=내키 (weather.py와 같은 키, 값은 .env에만!)

미리보기: 주소 뒤에 ?t=morning / ?t=lunch / ?t=evening 을 붙이면 그 시간대 화면이 바로 열려요.
"""

import html
import os
import random
from datetime import datetime, timedelta, timezone

import requests
import streamlit as st
from dotenv import load_dotenv

API = {
    "weather": "https://api.openweathermap.org/data/2.5/weather",       # 🔌 OpenWeather 현재 날씨
    "forecast": "https://api.openweathermap.org/data/2.5/forecast",     # 🔌 OpenWeather 3시간 간격 예보 (비 올 확률)
    "air": "https://api.openweathermap.org/data/2.5/air_pollution",     # 🔌 OpenWeather 미세먼지
}

KST = timezone(timedelta(hours=9))

# 고를 수 있는 도시 (위도·경도)
CITIES = {
    "서울": {"lat": 37.5665, "lon": 126.9780},
    "부산": {"lat": 35.1796, "lon": 129.0756},
    "인천": {"lat": 37.4563, "lon": 126.7052},
    "대구": {"lat": 35.8714, "lon": 128.6014},
    "대전": {"lat": 36.3504, "lon": 127.3845},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "제주": {"lat": 33.4996, "lon": 126.5312},
}

# 상단 메뉴: 주소용 이름 → 화면에 보이는 이름
TIMES = {"morning": "🌅 아침", "lunch": "🍱 점심", "evening": "🌙 저녁"}

# 비·눈으로 치는 날씨 (data["weather"][0]["main"] 값)
WET = {"Rain", "Drizzle", "Thunderstorm", "Snow"}

CSS = """
<style>
.card {background:#141414; border:1px solid #2A2A2A; border-radius:12px; padding:18px; height:100%;}
.card .emoji {font-size:2.2rem;}
.card .name {color:#F5F5F5; font-size:1.25rem; font-weight:700; margin-top:6px;}
.card .why {color:#8A8A8A; font-size:0.88rem; margin-top:4px;}
.hero {background:#141414; border:1px solid #2A2A2A; border-radius:12px; padding:24px; text-align:center;}
.hero .big {color:#F5F5F5; font-size:1.6rem; font-weight:700;}
.hero .small {color:#8A8A8A; font-size:0.95rem; margin-top:8px;}
</style>
"""


def now_slot():
    """지금 한국 시각으로 아침(06~11시)·점심(11~16시)·저녁(그 외) 중 하나를 골라요."""
    hour = datetime.now(KST).hour
    if 6 <= hour < 11:
        return "morning"
    if 11 <= hour < 16:
        return "lunch"
    return "evening"


# Streamlit은 메뉴를 누를 때마다 파일 전체를 다시 실행해요.
# 그때마다 API를 부르면 429(너무 많이 부름)가 나기 쉬워서, 10분 동안은 받아 둔 결과를 재사용해요.
@st.cache_data(ttl=600)
def fetch(name, key, lat, lon):
    """API[name] 을 불러요. (데이터, 에러 메시지) 두 개를 돌려줘요. 하나가 실패해도 나머지는 계속 써요."""
    label = {"weather": "현재 날씨", "forecast": "예보", "air": "미세먼지"}[name]
    params = {"lat": lat, "lon": lon, "appid": key, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(API[name], params=params, timeout=10)  # 🔌 API 호출
    except requests.exceptions.Timeout:
        return None, f"{label} 서버가 10초 안에 대답하지 않았어요."
    except requests.exceptions.RequestException:
        return None, f"{label} 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요."

    if res.status_code == 401:
        return None, f"{label}: 날씨 키가 틀렸거나 아직 켜지지 않았어요 (가입 후 최대 2시간 걸려요)."
    if res.status_code == 429:
        return None, f"{label}: 1분에 너무 많이 불렀어요. 잠시 뒤에 다시 눌러 주세요."
    if res.status_code != 200:
        return None, f"{label}을(를) 가져오지 못했어요 (응답 코드 {res.status_code})."
    try:
        return res.json(), None
    except ValueError:
        return None, f"{label} 서버의 대답을 읽지 못했어요."


def rain_chance(forecast, hours=9):
    """앞으로 몇 시간 안에 가장 높은 비 올 확률(%)을 돌려줘요. 예보가 없으면 None."""
    if not forecast:
        return None
    count = max(1, hours // 3)                                   # 예보는 3시간 간격이에요
    pops = [item.get("pop", 0) for item in forecast["list"][:count]]  # item["pop"] = 비 올 확률 (0~1)
    return round(max(pops) * 100)


def air_grade(air):
    """미세먼지를 한국 기준(좋음·보통·나쁨·매우 나쁨)으로 바꿔요. 둘(PM10, PM2.5) 중 나쁜 쪽을 따라요."""
    if not air:
        return None
    comp = air["list"][0]["components"]   # components["pm10"], ["pm2_5"] = 미세먼지·초미세먼지 (㎍/㎥)
    pm10, pm25 = comp["pm10"], comp["pm2_5"]
    level10 = 0 if pm10 <= 30 else 1 if pm10 <= 80 else 2 if pm10 <= 150 else 3
    level25 = 0 if pm25 <= 15 else 1 if pm25 <= 35 else 2 if pm25 <= 75 else 3
    level = max(level10, level25)
    names = ["좋음 😊", "보통 🙂", "나쁨 😷", "매우 나쁨 🚨"]
    return {"level": level, "name": names[level], "pm10": pm10, "pm25": pm25}


def morning_checklist(w, pop, air):
    """출근길 체감온도·비 확률·미세먼지로 챙길 것 목록을 만들어요."""
    items = []
    if w:
        feels = w["main"]["feels_like"]
        if feels <= 0:
            items.append("🧣 패딩 + 장갑 + 목도리 (체감 영하예요)")
        elif feels <= 5:
            items.append("🧥 두꺼운 외투")
        elif feels <= 12:
            items.append("🧥 자켓이나 트렌치코트")
        elif feels <= 20:
            items.append("👕 가디건 하나 걸치기")
        elif feels >= 28:
            items.append("🩳 반팔 + 손선풍기")
            items.append("💧 물 한 병")
        if w["wind"]["speed"] >= 8:                     # w["wind"]["speed"] = 바람 세기 (m/s)
            items.append("💨 바람이 세요 — 모자·우산 날아가지 않게")
        if w["weather"][0]["main"] == "Snow":
            items.append("👟 미끄럼 안 타는 신발")
    if pop is not None:
        if pop >= 60:
            items.append(f"☔ 장우산 꼭! (비 올 확률 {pop}%)")
        elif pop >= 30:
            items.append(f"🌂 접이식 우산 가방에 (비 올 확률 {pop}%)")
    if air and air["level"] >= 2:
        items.append("😷 KF94 마스크")
    items.append("🔋 휴대폰 충전 확인")
    return items


def lunch_menus(w, pop, air):
    """날씨·미세먼지에 맞는 점심 메뉴 3개를 (이모지, 이름, 이유) 로 돌려줘요."""
    if w and w["weather"][0]["main"] == "Snow":
        return [("🍜", "우동", "눈 오는 날엔 뜨끈한 국물"),
                ("🍲", "어묵탕", "몸이 사르르 녹아요"),
                ("🥟", "만둣국", "김 모락모락")]
    if (w and w["weather"][0]["main"] in WET) or (pop is not None and pop >= 60):
        return [("🍜", "짬뽕", "비 오는 날엔 얼큰한 국물"),
                ("🥞", "파전", "빗소리엔 지글지글 전"),
                ("🍲", "칼국수", "따끈하고 든든하게")]
    if air and air["level"] >= 2:
        return [("🥓", "삼겹살", "미세먼지엔 삼겹살? (속설이에요) 실내에서 든든하게"),
                ("🍲", "삼계탕", "나가지 말고 가까운 실내 식당으로"),
                ("🍱", "도시락 배달", "오늘은 밖에 덜 나가는 게 좋아요")]
    temp = w["main"]["temp"] if w else None
    if temp is not None and temp >= 27:
        return [("🍜", "냉면", "더운 날엔 시원한 물냉면"),
                ("🥣", "콩국수", "고소하고 시원하게"),
                ("🐟", "물회", "더위 싹 가시는 새콤함")]
    if temp is not None and temp <= 5:
        return [("🍲", "국밥", "추운 날엔 뜨끈한 국밥 한 그릇"),
                ("🥘", "부대찌개", "얼큰하게 몸 데우기"),
                ("🍢", "순대국", "속까지 든든하게")]
    if air and air["level"] == 0 and (pop is None or pop < 30):
        return [("🥪", "샌드위치 피크닉", "공기 좋은 날, 밖에서 먹어 봐요"),
                ("🍙", "김밥 + 산책", "먹고 한 바퀴 걷기 딱 좋아요"),
                ("🥗", "샐러드", "가볍게 먹고 햇볕 쬐기")]
    return [("🍚", "비빔밥", "무난한 날엔 골고루"),
            ("🍛", "돈까스", "실패 없는 점심"),
            ("🍜", "쌀국수", "깔끔하게 한 그릇")]


# 날짜마다 다른 문구가 나오되, 같은 날엔 메뉴를 눌러도 바뀌지 않게 날짜를 씨앗으로 써요
CHEERS = [
    "오늘 하루도 정말 수고 많았어요.",
    "잘 버틴 나, 오늘은 일찍 쉬어도 돼요.",
    "완벽하지 않아도 충분히 잘했어요.",
    "내일의 나에게 맡기고 오늘은 푹 쉬어요.",
    "퇴근길 노래 한 곡, 오늘의 작은 보상이에요.",
]


def evening_plan(w, pop, air):
    """퇴근길 날씨에 맞는 할 일 1개와 이유를 돌려줘요."""
    if (w and w["weather"][0]["main"] in WET) or (pop is not None and pop >= 60):
        return "🎬 오늘은 집에서 영화 한 편 어때요?", "비 소식이 있어요. 따뜻한 집이 최고예요."
    if air and air["level"] >= 2:
        return "🧘 오늘은 집에서 홈트 어때요?", f"미세먼지 {air['name']} — 창문 닫고 실내 운동이 좋아요."
    feels = w["main"]["feels_like"] if w else None
    if feels is not None and feels <= 3:
        return "🛁 따뜻한 차 한 잔과 반신욕 어때요?", "밖이 많이 추워요. 몸 녹이는 저녁으로."
    if feels is not None and feels >= 28:
        return "🍉 시원한 수박 먹으며 쉬는 저녁 어때요?", "아직 더워요. 무리한 운동은 내일로."
    if air:
        return "🌳 오늘은 공원 산책 어때요?", f"미세먼지 {air['name']} — 바깥 공기 마시기 좋은 날이에요."
    return "🚶 가볍게 동네 한 바퀴 어때요?", "미세먼지 정보는 못 받았지만 날씨는 괜찮아요."


def card(emoji, name, why):
    return (f'<div class="card"><div class="emoji">{emoji}</div>'
            f'<div class="name">{name}</div><div class="why">{why}</div></div>')


def main():
    st.set_page_config(page_title="하루 3번 날씨", page_icon="🌤️")
    st.markdown(CSS, unsafe_allow_html=True)

    # ── 1. 상단 메뉴 (작게): 주소 ?t= 가 있으면 그걸, 없으면 지금 시각에 맞춰 골라 둬요 ──
    slot = st.query_params.get("t")
    if slot not in TIMES:
        slot = now_slot()
    picked = st.segmented_control("시간대", list(TIMES), default=slot,
                                  format_func=TIMES.get, label_visibility="collapsed")
    slot = picked or slot                 # 같은 버튼을 한 번 더 눌러 선택이 풀려도 그대로 유지
    st.query_params["t"] = slot

    head, pick = st.columns([3, 1], vertical_alignment="bottom")
    head.title("🌤️ 하루 3번 날씨")
    city = pick.selectbox("도시", list(CITIES), label_visibility="collapsed")

    load_dotenv()
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        st.error("❌ .env에 OPENWEATHER_API_KEY가 없어요. .env.example을 보고 채워 주세요.")
        st.stop()

    # ── 2. API 3개를 따로 불러요: 하나가 실패해도 나머지로 화면을 만들어요 ──
    loc = CITIES[city]
    w, err_w = fetch("weather", key, loc["lat"], loc["lon"])
    fc, err_f = fetch("forecast", key, loc["lat"], loc["lon"])
    aq, err_a = fetch("air", key, loc["lat"], loc["lon"])
    for err in (err_w, err_f, err_a):
        if err:
            st.warning(f"⚠️ {err}")
    if err_w and err_f and err_a:
        st.button("🔄 다시 불러오기", on_click=fetch.clear)
        st.stop()

    pop = rain_chance(fc)
    air = air_grade(aq)

    # ── 3. 지금 날씨 한눈에 ──
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌡️ 기온", f"{w['main']['temp']:.1f}°C" if w else "-")       # w["main"]["temp"] = 지금 기온
        c2.metric("🤗 체감", f"{w['main']['feels_like']:.1f}°C" if w else "-")  # w["main"]["feels_like"] = 체감 온도
        c3.metric("☔ 비 확률", f"{pop}%" if pop is not None else "-")
        c4.metric("😷 미세먼지", air["name"] if air else "-")
        desc = html.escape(w["weather"][0]["description"]) if w else "정보 없음"  # lang=kr 이라 한국어 설명
        updated = datetime.now(KST).strftime("%H:%M")
        st.caption(f"{city} · {desc} · 비 확률은 앞으로 9시간 중 최대값 · {updated} 기준 (10분마다 새로 받아요)")
        st.button("🔄 새로고침", on_click=fetch.clear)

    st.write("")

    # ── 4. 시간대별 화면 ──
    if slot == "morning":
        st.subheader("🌅 출근길 체크리스트")
        st.caption("챙긴 건 눌러서 체크해요.")
        for i, item in enumerate(morning_checklist(w, pop, air)):
            st.checkbox(item, key=f"check_{i}")

    elif slot == "lunch":
        st.subheader("🍱 오늘의 점심 추천")
        cols = st.columns(3)
        for col, (emoji, name, why) in zip(cols, lunch_menus(w, pop, air)):
            col.markdown(card(emoji, name, why), unsafe_allow_html=True)

    else:
        st.subheader("🌙 퇴근길 한마디")
        plan, why = evening_plan(w, pop, air)
        cheer = random.Random(datetime.now(KST).date().toordinal()).choice(CHEERS)
        st.markdown(f'<div class="hero"><div class="big">{plan}</div>'
                    f'<div class="small">{why}</div></div>', unsafe_allow_html=True)
        st.write("")
        st.info(f"💛 {cheer}")

    st.caption("출처: 날씨·예보·미세먼지 OpenWeather · 미세먼지 등급은 한국 환경부 기준으로 바꿔 보여 줘요")


main()
