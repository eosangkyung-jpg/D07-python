# API 키 받기 · 회원 카드 3장 (10:00 가입 → 10:50 .env에 넣기)

> 오늘 쓰는 오픈API는 전부 **회원 카드(API 키)**가 필요해요.
> ⚠️ **OpenWeather 키는 가입 후 최대 2시간 뒤에 켜져요.** 그래서 수업 시작하자마자(가능하면 수업 전에) 가입부터 해요.

| 순서 | 카드 | 어디서 | 키 이름 (`.env`) | 언제 켜지나 |
| --- | --- | --- | --- | --- |
| ① | OpenWeather (날씨) | openweathermap.org | `OPENWEATHER_API_KEY` | 가입 후 **최대 2시간** |
| ② | ExchangeRate-API (환율) | exchangerate-api.com | `EXCHANGERATE_API_KEY` | **이메일 인증** 후 바로 |
| ③ | 카카오 (Daum 검색, ★★) | developers.kakao.com | `KAKAO_REST_API_KEY` | 바로 |

---

## ① OpenWeather (날씨)
1. **openweathermap.org** → 오른쪽 위 **Sign in → Create an Account** (이름·이메일·비밀번호, 사용 목적은 Education)
2. 메일함에서 **인증 메일 확인** 클릭
3. 로그인 → 오른쪽 위 내 이름 → **My API keys** → `Default` 키 복사
4. 무료 플랜이면 충분해요 (1분에 60번까지). **카드 등록이 필요한 "One Call API" 구독은 하지 마세요** — 오늘은 무료인 현재 날씨 API만 써요
- 막 받은 키로 부르면 **401 Invalid API key** → 키가 틀린 게 아니라 **아직 안 켜진 것**일 수 있어요. 기다리는 동안은 미션 ②부터

## ② ExchangeRate-API (환율)
1. **exchangerate-api.com** → **Get Free Key** → 이메일 입력 (카드 필요 없음)
2. 메일함 **인증 메일 확인** → 대시보드에 **API Key** 보임 → 복사
3. 무료 플랜: **한 달 1,500번**, 환율은 **하루 한 번** 갱신 → 반복문으로 계속 부르지 않기
- 인증 메일을 안 누르면 응답에 `inactive-account` 가 와요

## ③ 카카오 (Daum 검색) — 미션 ④ ★★
1. **developers.kakao.com** → 로그인 → **앱** → 앱 만들기 (`ax-camp-내이름`)
2. 만든 앱 → 왼쪽 **플랫폼 키** → **REST API 키** 복사 (2025년 12월에 "앱 키" 메뉴가 **플랫폼 키**로 바뀌었어요)

---

## 받은 키는 바로 `.env` 금고로
`d7-python/.env` 를 **VS Code에서 내가 직접** 만들고 (띄어쓰기·따옴표 없이):
```
OPENWEATHER_API_KEY=여기에_날씨키
EXCHANGERATE_API_KEY=여기에_환율키
KAKAO_REST_API_KEY=여기에_카카오키
```

## 키를 받으면 이것만 기억
| 하지 마 | 왜 |
| --- | --- |
| Slack·카톡·메모장에 붙여 넣기 | 받은 사람 모두가 내 카드로 주문할 수 있음 |
| Claude Code 대화창에 붙여 넣기 | 대화 기록에 남아요. "키는 .env의 OPENWEATHER_API_KEY에 있어"라고만 |
| 코드·HTML에 넣기 | GitHub에 올라가면 누구나 봄 |
| 요청 주소를 통째로 출력하기 | OpenWeather는 키가 **주소 안**(`appid=`)에 들어가요. 주소를 찍으면 키가 찍혀요 |
| 화면 공유 중에 `.env` 열기 | 녹화에 남아요. 줌 공유 전에 `.env` 탭 닫기 |

## 키가 새어 나갔다면 (사고 대응 3단계)
1. **바로** 그 사이트에서 새 키를 만들고 새어 나간 키는 **삭제/재발급** (OpenWeather: My API keys에서 새 키 Generate 후 옛 키 Delete · ExchangeRate-API: 대시보드에서 키 재발급 · 카카오: 플랫폼 키에서 삭제)
2. `.env`의 값을 새 키로 바꾸고 다시 돌아가는지 확인
3. GitHub에 올렸다면 → 커밋을 지워도 **기록에 남아요.** 그래서 1번(키 교체)이 먼저. 그다음 `git rm --cached .env` + `.gitignore` 확인

## 왜 네이버 API는 안 써요?
네이버 검색 API는 **2026년 7월 31일부터** 개발자센터에서 신규 발급이 끝나고 네이버 클라우드로 옮겨 갔어요(가입·결제 수단 등록 필요). Claude가 옛 주소(`openapi.naver.com`)로 코드를 짜면 → **AI 실수**
