# 파이썬 API 규칙 (D7 오전)

> 이 내용을 **`git-practice/d7-python/CLAUDE.md`** 에 붙여 넣으세요. (폴더 CLAUDE.md = 이 폴더에서만 지킬 규칙)
> 오늘은 **파이썬**이 오픈API에 주문해요. 순서: **① 날씨(OpenWeather) → ② 환율(ExchangeRate-API) → ③ 이어 붙이기 → ④ 검색(카카오)**. 전부 키가 필요해요.
> 줄마다 (왜)와 → 검사가 있어요. 규칙 한 줄 = 검사 한 줄.

---

## 키 금고 규칙
- API 키는 `.env` 파일에만 둔다. 코드에는 `os.getenv("OPENWEATHER_API_KEY")`처럼 **이름만** 쓴다. 키 값을 코드·주석·README·출력 예시에 적지 않는다. (왜: 코드는 GitHub에 올라감) → 검사: 키 앞 6글자로 찾기 → `.env` 말고 0건
- `.env`를 만들거나 열어서 내용을 보여 주지 않는다. `.env`는 사용자가 직접 만든다. 키가 있는지는 코드로 "있다/없다"만 확인한다. (왜: 대화 기록에도 키가 남으면 안 됨) → 검사: 대화에 키 값이 한 번도 안 나옴
- `.gitignore`에 `.env`, `__pycache__/` 를 넣는다. (왜: 금고·임시 파일은 올리지 않음) → 검사: `git status`에 `.env` 안 보임, `git check-ignore -v .env`에 줄이 나옴
- `.env.example`에 키 **이름만** 적고 값은 비운다 (`OPENWEATHER_API_KEY=`, `EXCHANGERATE_API_KEY=`, `KAKAO_REST_API_KEY=`). (왜: 다른 사람이 어떤 키가 필요한지 알게) → 검사: `=` 뒤가 모두 빈칸
- **요청 주소(URL)·요청 헤더·`response.url`을 화면이나 로그에 출력하지 않는다.** 화면에 API를 보여 줄 때는 키를 뺀 기본 주소만. (왜: OpenWeather는 키가 주소 안 `appid=`에, ExchangeRate-API·카카오는 헤더에 들어 있음) → 검사: 키를 틀리게 하고 실행해 출력 전체 확인
- 키가 없으면 "`.env`에 ○○_API_KEY가 없어요. `.env.example`을 보고 채워 주세요"라고 알리고 그 API만 건너뛴다. (왜: 하나 없다고 다 멈추지 않게) → 검사: `.env`에서 한 줄 지우고 실행

## 공통 규칙 (모든 .py 파일)
- 파일 하나 = 하는 일 하나. `python 파일이름.py` 한 줄로 실행된다. (왜: 미션마다 따로 실행·검사) → 검사: 터미널에서 실행됨
- API 주소는 파일 맨 위 `API = { ... }` 한 곳에 모으고 각 줄에 `# 🔌` 주석, 요청하는 줄에 `# 🔌 API 호출`. (왜: 어디가 API인지 바로 찾으려고) → 검사: Ctrl+F 🔌
- 요청은 `requests.get(..., timeout=10)`. 실패하면 영어 에러 덩어리(Traceback) 대신 한국어 한 줄로 알린다. (왜: 초보자가 다음 행동을 알게) → 검사: 🔌 주소 한 글자 지우고 실행
- 여러 API를 차례로 부를 때는 하나가 실패해도 나머지는 계속 보여 준다. (왜: API는 가끔 멈추고, 키 하나가 아직 안 켜졌을 수 있음) → 검사: 하나만 주소를 틀리게 하고 실행
- 받은 JSON에서 값을 꺼내는 줄에 어느 칸인지 주석을 단다. 예: `# data["main"]["temp"] = 지금 기온` (왜: JSON 읽기 연습) → 검사: 꺼내는 줄마다 주석
- 출력 맨 아래에 데이터 출처를 적는다 ("날씨: OpenWeather", "환율: ExchangeRate-API"). 환율은 응답의 **기준 시각**(`time_last_update_utc`)을 한국 시간으로 바꿔 함께 보여 주고 "실시간"이라고 쓰지 않는다. (왜: 무료 플랜 환율은 하루 한 번 갱신) → 검사: 출처·기준 시각 있음, "실시간" 없음
- 파이썬 패키지는 conda 가상환경 `camp` 안에서만 `pip install` 하고, 새 패키지를 쓰면 `requirements.txt`에 한 줄 추가한다. 설치 명령은 실행하지 말고 제안만 한다. (왜: 조원·서버가 `pip install -r requirements.txt` 한 줄로 똑같이 준비하게) → 검사: import와 requirements.txt가 짝이 맞음
- 반복문·자동 새로고침으로 API를 계속 부르지 않는다. 한 번 실행에 API마다 한 번. (왜: ExchangeRate-API 무료는 한 달 1,500번) → 검사: 코드에 `while True` 없음
- 커밋·푸시는 하지 말고 커밋 메시지만 제안한다. 커밋 전에는 `git status` 결과를 보여 준다. (왜: `.env`가 섞여 있지 않은지 내가 확인) → 검사: 내가 직접 커밋

## Streamlit 규칙 (미션 ⑦, app.py)
- Streamlit으로 만든 파일은 실행 명령을 `streamlit run 파일이름.py` 로 안내하고, `python 파일이름.py` 로 안내하지 않는다. 파일을 다 만들면 실행 명령을 한 줄로 알려 준다. (왜: Streamlit 파일을 python으로 실행하면 화면이 안 뜨고 경고만 나옴) → 검사: 안내된 명령으로 실행해 화면이 뜸
- 키·요청 주소·요청 헤더·`res.url`을 `st.write`, `st.json`, `st.code`, `st.exception` 등 **어떤 화면 요소에도** 내보내지 않는다. 에러는 `st.error("한국어 한 줄")`. (왜: 화면은 다른 사람에게 보여 주는 곳) → 검사: 화면 훑기 + 키 앞 6글자 검색
- API를 부르는 함수에는 `@st.cache_data(ttl=초)`를 붙인다. 날씨 600, 환율 3600 이상. "새로 불러오기" 버튼에서만 `st.cache_data.clear()`. (왜: Streamlit은 입력이 바뀔 때마다 파일 전체를 다시 실행 → 환율 무료 월 1,500번) → 검사: 통화를 여러 번 바꿔 봄
- 칸(`st.columns`)마다 따로 불러서 한 칸이 실패해도 다른 칸은 보이게 한다. (왜: 키 하나가 아직 안 켜졌을 수 있음) → 검사: 키 하나만 틀리게
- `streamlit`을 `requirements.txt`에 넣는다. `.streamlit/secrets.toml`을 만들면 `.gitignore`에도 넣는다. (왜: 금고 파일은 올리지 않음) → 검사: requirements.txt, .gitignore

## 쓸 수 있는 API (10/22 문서 확인)
| 순서 | API | 주소 | 키 보내는 법 | 주요 칸 |
| --- | --- | --- | --- | --- |
| ① | OpenWeather 현재 날씨 | `https://api.openweathermap.org/data/2.5/weather` | 주소 옵션 `appid=키` (+ `lat`, `lon`, `units=metric`, `lang=kr`) | `main.temp`, `main.feels_like`, `main.humidity`, `weather[0].description`, `name` |
| ①+ | OpenWeather 지오코딩 (도시 → 위도·경도) | `https://api.openweathermap.org/geo/1.0/direct` | `q=도시`, `limit=1`, `appid=키` | `[0].lat`, `[0].lon`, `[0].local_names.ko` |
| ①+ | OpenWeather 5일 예보 (3시간 간격) | `https://api.openweathermap.org/data/2.5/forecast` | 날씨와 같음 | `list[i].dt_txt`, `list[i].main.temp` |
| ② | ExchangeRate-API 환율 | `https://v6.exchangerate-api.com/v6/latest/USD` | **헤더** `Authorization: Bearer 키` (키를 주소에 넣는 방식은 쓰지 않음) | `result`, `conversion_rates.KRW`, `time_last_update_utc` |
| ③ | Nager.Date 공휴일 | `https://date.nager.at/api/v3/NextPublicHolidays/KR` | 키 없음 | `[0].localName`, `[0].date` |
| ④ | 카카오 Daum 블로그 검색 | `https://dapi.kakao.com/v2/search/blog` | **헤더** `Authorization: KakaoAK 키` | `documents[i].title`, `blogname`, `datetime` |

### 에러 읽는 법
| API | 이럴 때 | 화면 안내 |
| --- | --- | --- |
| OpenWeather | 401 | "날씨 키가 틀렸거나 **아직 켜지지 않았어요**(가입 후 최대 2시간)" |
| OpenWeather | 404 | "그 도시를 찾지 못했어요" |
| OpenWeather | 429 | "1분에 너무 많이 불렀어요. 잠시 뒤에" |
| ExchangeRate-API | `result`가 `"error"`, `error-type`이 `invalid-key` | "환율 키가 틀렸어요" |
| ExchangeRate-API | `error-type`이 `inactive-account` | "환율 사이트 가입 인증 메일을 확인해 주세요" |
| ExchangeRate-API | `error-type`이 `quota-reached` | "이번 달 무료 사용량(1,500번)을 다 썼어요" |
| 카카오 | 401 / 403 | "카카오 키가 틀렸어요" / "사용 설정이 꺼져 있어요" |

- OpenWeather One Call API(카드 등록 필요)는 쓰지 않는다. 네이버 검색 API(`openapi.naver.com`)는 쓰지 않는다. 표에 없는 API는 먼저 이름·주소·키 필요 여부를 말하고 확인받는다. → 검사: 코드에 `onecall`, `naver` 없음

## 실수에서 배운 규칙
<!-- AI 실수를 찾을 때마다 한 줄씩: - (10/22) (해라/하지 마라) ___ (왜: ___) → 검사: ___ -->
