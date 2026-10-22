"""뉴욕 맨해튼의 지금 날씨를 웹 화면(Streamlit)으로 보여 줘요.

실행: conda activate camp → streamlit run weather.py
      (python weather.py 가 아니에요! 브라우저가 자동으로 열려요)
준비: .env 파일에 OPENWEATHER_API_KEY=내키 (값은 .env에만!)
"""

import os
from datetime import datetime, timedelta, timezone

import requests
import streamlit as st
from dotenv import load_dotenv

API = {
    "weather": "https://api.openweathermap.org/data/2.5/weather",  # 🔌 OpenWeather 현재 날씨
}

# 뉴욕 맨해튼 위치 (위도·경도)
MANHATTAN = {"lat": 40.7831, "lon": -73.9712}


def c_to_f(c):
    """섭씨 → 화씨"""
    return c * 9 / 5 + 32


def fmt_time(t):
    """datetime → '10월 22일 (수) 오전 9:05' 처럼 읽기 쉬운 한국어로"""
    weekday = "월화수목금토일"[t.weekday()]
    ampm = "오전" if t.hour < 12 else "오후"
    hour = t.hour % 12 or 12
    return f"{t.month}월 {t.day}일 ({weekday}) {ampm} {hour}:{t.minute:02d}"


# Streamlit은 버튼을 누를 때마다 파일 전체를 처음부터 다시 실행해요.
# 그때마다 API를 부르면 429(너무 많이 부름)가 나기 쉬워서, 10분 동안은 받아 둔 결과를 재사용해요.
@st.cache_data(ttl=600)
def get_weather(key):
    """맨해튼 현재 날씨를 받아 와요. (데이터, 에러 메시지) 두 개를 돌려줘요."""
    params = {**MANHATTAN, "appid": key, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(API["weather"], params=params, timeout=10)  # 🔌 API 호출
    except requests.exceptions.Timeout:
        return None, "날씨 서버가 10초 안에 대답하지 않았어요. 잠시 뒤에 다시 눌러 주세요."
    except requests.exceptions.RequestException:
        return None, "날씨 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요."

    if res.status_code == 401:
        return None, "날씨 키가 틀렸거나 아직 켜지지 않았어요 (가입 후 최대 2시간 걸려요)."
    if res.status_code == 404:
        return None, "그 위치를 찾지 못했어요."
    if res.status_code == 429:
        return None, "1분에 너무 많이 불렀어요. 잠시 뒤에 다시 눌러 주세요."
    if res.status_code != 200:
        return None, f"날씨를 가져오지 못했어요 (응답 코드 {res.status_code})."
    return res.json(), None


def main():
    st.set_page_config(page_title="맨해튼 날씨", page_icon="🗽")
    st.title("🗽 뉴욕 맨해튼 지금 날씨")

    load_dotenv()
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        st.error("❌ .env에 OPENWEATHER_API_KEY가 없어요. .env.example을 보고 채워 주세요.")
        st.stop()  # 여기서 화면 그리기를 멈춰요 (터미널 버전의 return 역할)

    if st.button("🔄 새로고침"):
        get_weather.clear()  # 저장해 둔 결과를 지우고 새로 받아 와요

    data, error = get_weather(key)
    if error:
        st.error(f"❌ {error}")
        st.stop()

    temp_c = data["main"]["temp"]                # data["main"]["temp"] = 지금 기온 (섭씨)
    feels_c = data["main"]["feels_like"]         # data["main"]["feels_like"] = 체감 온도 (섭씨)
    humidity = data["main"]["humidity"]          # data["main"]["humidity"] = 습도 (%)
    desc = data["weather"][0]["description"]     # data["weather"][0]["description"] = 날씨 설명 (lang=kr 이라 한국어)
    ny_tz = timezone(timedelta(seconds=data["timezone"]))  # data["timezone"] = 뉴욕이 세계 표준시보다 몇 초 느린지 (서머타임 자동 반영)
    measured = datetime.fromtimestamp(data["dt"], ny_tz)   # data["dt"] = 날씨를 측정한 시각

    # 시계 2개: 뉴욕 지금 시각, 한국 지금 시각
    now = datetime.now(timezone.utc)
    kst = timezone(timedelta(hours=9))
    t1, t2 = st.columns(2)
    t1.metric("🗽 뉴욕 지금", fmt_time(now.astimezone(ny_tz)))
    t2.metric("🇰🇷 한국 지금", fmt_time(now.astimezone(kst)))

    # 카드 4개를 가로로 나란히 놓아요
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️ 기온", f"{temp_c:.1f}°C", f"{c_to_f(temp_c):.1f}°F", delta_color="off")
    col2.metric("🤗 체감 온도", f"{feels_c:.1f}°C", f"{c_to_f(feels_c):.1f}°F", delta_color="off")
    col3.metric("💧 습도", f"{humidity}%")
    col4.metric("☁️ 날씨", desc)

    st.caption(f"🕒 측정 시각(뉴욕): {fmt_time(measured)} · 출처: 날씨 OpenWeather")


main()
