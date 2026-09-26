# CMP-Sim — STATUS

## 🎯 완성 기준 (사용자 확정 2026-09-25) — 이 줄을 매 실행 갱신하라

### ⛔ 순서 변경 (사용자 2026-09-26): 시뮬레이터가 먼저다
**모델링이 완성되지 않아도 시뮬레이터부터 만든다.** 1차(median)를 기다리지 말고
**지금 이 순간의 모델식을 반영한** 시뮬레이터를 먼저 완성한다.

**작업 구조: 시뮬레이터에서 "모델링만" 수정 가능해야 한다.**
- 3D·패널·라우트(껍데기)와 물리 모델을 **분리**
- 물리식·상수는 팩 YAML / `cmp_sim/models/` **한 곳**에만. UI는 읽기만 한다
- 모델을 고칠 때 UI를 건드릴 필요가 없어야 하고, 그 반대도 마찬가지
- UI에서 모델 파라미터를 출처와 함께 보고·수정 → 즉시 재예측
- **테스트로 고정**: 웹 파일에 물리 상수가 하드코딩되면 실패하는 테스트

#### ✅ 2차 완성 — 2026-09-26 달성 (943 tests). 4개 입력부 전부 동작·모델 연동
**공개 주소(어느 네트워크에서나 열린다 — 2026-09-26 19:4x 배포·검증):**
`https://cmp-sim.vercel.app/tool?t=<token>`
⚠ **이 저장소는 public이다 — 토큰을 여기에 적지 마라.** 값은 `~/.fabsim-demo-token`과
Vercel 프로덕션 환경변수 `CMPSIM_TOKEN`에만 있다(사용자에겐 텔레그램으로 전달).
로컬: `python -m cmp_sim.api` → http://127.0.0.1:8765/tool (또는 `./CMP-Sim.command`).

### 2026-09-26(10회차): "UI가 거지같다"의 원인은 **기하가 없었던 것** — 예전 LK 모델을 베이스로 정교화
사용자가 두 번 반려했다(17:52 "실제 LK3.0 참고해라", 19:19 "예전에 맥에서 만든
lk3.0 모사 3d모델 베이스로 만들라고"). **그 모델을 찾았다**:
`~/fab-sim/sim/web/studio3d.html`(2969줄, "AMAT Reflexion LK-class 300mm CMP tool").
9회차는 셸(외장)만 사양서에 맞췄고 **기계 부품 자체는 여전히 맨 실린더였다.**
거기서 기하 헬퍼를 이식: `chamferCyl` / `chamferRing` / `boltCircle`(→`boltRing`).

**왜 챔퍼가 색보다 중요한가(핵심 진단):** 맨 `CylinderGeometry`의 림은 수학적으로
날카로워서 법선이 **불연속**으로 튄다 → 스페큘러 하이라이트를 **하나도** 못 잡고
색 경계로만 렌더된다. 실제 기계가공 부품은 전부 모서리를 깎는다(디버링 = 가공
요구사항이지 멋이 아니다). 그 챔퍼선이 눈이 "금속"으로 읽는 단서다. 즉 이전 빌드가
플라스틱으로 보인 이유는 **재질 색이 아니라 기하**였다 — 9회차에 색을 고쳐도
"거지같다"가 남은 이유가 이것이다.

정교화한 것(전부 껍데기·기하, 물리 0):
- **패드**: 평면 채움+회색 링 → 다공성(닫힌셀 6%) 노이즈 베이스 + 그루브 **범프맵**.
  그루브가 플래튼 회전에 따라 빛을 잡았다 놓아 **깎인 홈**으로 읽힌다(이전엔 인쇄된 줄).
- **캐리어 헤드**: 실린더 1개 → 멤브레인/하우징/씰 플랜지+볼트/짐벌/스핀들 스택 +
  **존압력 배관 3줄**. 배관은 장식이 아니라 Operation 폼의 zone P 입력과 실물을 잇는다.
- **리테이너 링**: 강철 토러스 → **PPS**(크림색 무광). 헤드의 유일한 비금속 대형
  부품이고, 엔지니어가 사진에서 이걸로 헤드를 식별한다. 슬러리 슬롯 36개 추가.
- **컨디셔너**: 막대+퍽 → 베이스 플랜지·스윕 모터·암 캡·린스 라인·다운포스 실린더.
- **플래튼**: 샤프 실린더 → 챔퍼 바디 + 베어링 하우징 + 하부 볼트 원.
- **factory interface(EFEM)**: 매끈한 흰 박스 → **패널 심(seam) + 서비스 도어 + 손잡이**.
  화면에서 가장 밝은 대면적이라 눈이 여기 먼저 닿는데, 무늬 없는 흰 덩어리는
  기계 쪽을 아무리 잘 만들어도 **스티로폼 포장재**로 읽힌다. 실제 팹 판금은
  전부 볼트로 조인 서비스 패널이라 심이 보인다(정비하려면 다 열려야 하므로).
  심은 텍스처가 아니라 **돌출된 얇은 막대**로 그려 자체 그림자를 만든다 —
  이것이 "패널로 나뉜 캐비닛"과 "선이 그려진 상자"를 가르는 차이다.
  ※ 이건 **내가 렌더 결과를 직접 보고** 잡았다. e2e는 전 항목 통과였지만
  통과가 곧 "잘 보인다"는 아니다.

⚠ **정직성 1건 — 만들다 지웠다.** 첫 시도에 패드 위에 **클램프 링 + 볼트 24개**를
넣었다. 플래튼이 "가공된 것처럼" 보이게 하는 디테일인데 **실물에 없다**: 이 등급
패드는 PSA(감압접착) 부착이라 연마면 위에 조여진 부품이 없다. 그림을 그럴듯하게
만들면서 **장비에 없는 하드웨어를 보여주는 것은 파라미터 값을 지어내는 것과 같은
오류**다 → 삭제하고, 실제로 보이는 위치(베어링 하우징 플랜지)로 옮겼다. 코드에
사유를 남겼다.

**새 테스트 2개**(28 → 30). "보기 좋다"는 검증 불가이므로 **렌더된 픽셀에서
측정되는 결과**만 주장했고, 임계값은 **변경 전/후를 실측해서** 교정했다:
- `test_the_pad_is_not_the_brightest_thing_on_the_machine` — 물리적 주장이다.
  패드는 다공성 폴리우레탄 폼(무광), 웨이퍼는 연마된 막적층(유일한 거울면)이므로
  패드가 웨이퍼보다 밝을 수 없다. **반려된 빌드는 정확히 거꾸로였다: 패드 202 vs
  웨이퍼 166** — 패드가 화면에서 가장 밝은 대면적이라 눈을 장비에서 끌어냈다.
  지금 **142 vs 166**. 절대 휘도가 아니라 **두 부품의 순서**로 주장한다(노출·환경맵이
  바뀌어도 순서는 안 바뀌므로 재튜닝 불필요).
- `test_the_carrier_head_reads_as_machined_metal` — 밝기가 아니라 **동적 범위**
  (p90−p10)를 잰다. 균일하게 밝은 헤드는 "더 밝다" 주장을 통과하면서도 여전히
  플라스틱이다. 금속의 조건은 **어두운 면과 하이라이트가 동시에** 있는 것.
  변경 전 **85** → 후 **185**, 기준 130(양쪽에서 충분히 떨어뜨림).
- **버그로 교정 확인**: tool3d.js만 stash하면 **두 테스트가 모두 실패**한다
  (헤드 범위 85 < 130, 패드가 웨이퍼보다 밝음).
⚠ **median은 의도대로 18.9% 불변**(`tools/score_report.py` 재실행 확인, 427점).
움직였다면 껍데기 작업이 물리를 건드렸다는 뜻이므로 버그다.

### 2026-09-26(10회차-A): 폰에서 장비가 안 보였다 — 패널이 뷰포트 전체였다
데스크톱 레이아웃은 캔버스 주위에 고정 패널 3개(390px 서랍·결과 카드·파트 범례)를
박는다. **390px 폰에서는 그 3개가 곧 뷰포트다** — 서랍이 장비를 완전히 덮고, 닫아도
범례+카드가 대부분을 가렸다. 브리프의 핵심인 3D가 **보여주기 가장 쉬운 기기에서
안 보였다.** `@media (max-width:720px)`로 패널을 **씬 위 시트**로 바꾸고 로드 시
서랍 자동 열기를 폰에서만 껐다. 캔버스는 항상 전체 뷰포트를 유지하므로 오빗·클릭은
동일하다. 테스트는 CSS 텍스트가 아니라 `elementFromPoint`로 **실제로 보이는 비율**을
잰다(전체 크기 캔버스가 불투명 패널에 완전히 덮여도 통과하는 테스트를 막는다).
⚠ 시트 높이 62vh는 **13%만 보이게** 만들었다(결과 카드와 겹침) → 52vh + 서랍 열릴 때
결과 카드 한 줄로 축소. 한 스크린샷에서 맞춘 값은 레이아웃이 아니다.

⚠ **"안 열려 / 같은 와이파이가 아니야"(사용자 17:03·17:04·19:29)의 진짜 원인은
와이파이가 아니라 배포본이 없었던 것이다.** 두 가지가 겹쳐 있었다:
1. 안내한 주소가 **127.0.0.1**이었다 — 정의상 사용자 기기에서 열릴 수 없다.
   trycloudflare 터널은 이 맥이 깨어 있고 그 프로세스가 살아 있는 동안만 산다.
2. 상설 호스팅(`cmp-sim.vercel.app`)은 **존재했지만 전 경로 401**이었다.
   `CMPSIM_TOKEN`이 프로덕션 환경변수로 **존재는 하는데 값이 붙지 않은** 상태라
   토큰을 붙여도 통과하지 못했다. 게다가 도메인 `fabsim-demo.vercel.app`은
   아직 **구 legacy 앱**을 가리킨다(401 문구가 한글 — 현재 앱은 영문 JSON을 낸다.
   응답 본문이 어느 빌드인지를 알려준 단서다).
   → 토큰을 지우고 다시 주입한 뒤 `vercel --prod` 재배포.
**검증은 200 코드가 아니라 실제 브라우저로 했다**: `tools/tool3d_e2e.py --base
https://cmp-sim.vercel.app --token …` 가 배포본을 상대로 전 항목 통과 —
캔버스 점등 55.2%, 10개 메시 클릭→해당 서랍, 3개 뷰포트 프레이밍,
6 psi에서 rate 1559.6→3119.1 Å/min 이동. 로컬 통과와 별개 종목이다.

검증 스크립트 `tools/web_smoke.py`가 실제 서버를 띄워 전 라우트를 찍는다(한글 0자).
**3D는 `tools/tool3d_e2e.py`가 실제 Chromium으로 검증**한다 — 캔버스 픽셀, 8개 메시를
진짜 마우스로 클릭, 프레이밍 3개 뷰포트, 압력 변경 시 rate 이동까지 한 번에 찍는다.

**"UI가 거지같다 — 실제 LK3.0 같은 CMP 장비 참고해라"(사용자 17:52) — 사진을 추측하는
대신 실물 1대의 사양서를 찾아 껍데기를 거기에 맞췄다.**
출처: Macquarie/wotol 자산목록 "AMAT Reflexion LK Copper, 13759"(300mm, 2006년식) —
사진이 아니라 **글로 적힌 구성표**라 검증 가능한 주장이 4개 나온다:
1. **"Polisher Skins : Dark"** — 폴리셔 외장은 **어둡다.** 기존 빌드는 밝은 회색이라
   장비 전체가 한 덩어리 연회색으로 뭉개졌고, 이것이 "플라스틱 장난감"으로 보인
   가장 큰 이유였다. 밝은 쪽은 **factory interface(EFEM)**이고 폴리셔가 어두운 쪽이다.
   (대비를 **거꾸로** 칠하고 있었다.)
2. **"Dry in Dry out"** — 플랫폼은 폴리셔만이 아니다. 웨이퍼가 젖어서 나와 말라서
   나가므로 **세정/건조 모듈**이 FI와 폴리시 베이 사이에 있다. 이게 없어서 "턴테이블
   옆에 상자 하나" 실루엣이었다. 브러시2 + 스핀드라이어 리드 3개로 추가.
3. **"Light Tower: Factory Interface and Polisher Sides"** — 시그널 타워는 **2개**다.
   1개는 근거 없는 추측이었다.
4. **"Monitor 2 Location : Ergo Arm type"** — 모니터는 받침대가 아니라 **관절형
   에르고암**에 매달린다. 실루엣 단서가 커서 포스트→상완→전완→화면으로 구성.
※ 전부 **껍데기 전용**: 물리도 클릭 대상도 건드리지 않았다(942→943, 기존 전부 통과).
※ 배치는 눈대중 반지름 3개가 아니라 **깊이 누적**으로 유도했다 — 첫 시도는 세정기를
   베이 드럼 **안쪽** 반지름에 놓아 아예 안 보였다. 한 스크린샷에서 맞춘 간격은 배치가 아니다.

**새 테스트 1개**(`test_the_polisher_is_darker_than_its_factory_interface`, 23→24):
대비를 **렌더된 픽셀에서** 잰다 — tool3d.js의 색 상수를 grep하지 않는다. 상수 검사는
톤매핑·환경맵·조명이 화면상 대비를 지워도 통과하는데, 주장 대상은 바로 그 화면이다.
픽셀 분류는 씬 자체의 레이캐스트로 하므로(frame=폴리셔 몸체, loadcup=FI) 리모델링에도
살아남는다. **버그로 교정 확인**: 옛 색으로 되돌리면 118 vs 122(구분 불가)로 실패한다.
양쪽 표본 40픽셀 미만이면 "비교 대상이 화면에 없음"으로 먼저 실패 — 무(無)를 무와
비교하며 통과하는 테스트를 막는다.

**⚠ 로컬은 통과하는데 실제 터널에서만 깨지는 것을 e2e가 잡았고, 그 셋은 하네스
버그였다**(`tools/tool3d_e2e.py`). 배포본 검증은 localhost 검증과 다른 종목이다:
1. **판정이 직전 값을 읽고 있었다.** 클릭 후 `#dtitle`을 읽는데, 클릭이 캔버스에
   닿지 않으면 **이전 메시의 제목이 그대로** 남아 "slurry가 Operation을 연다"는
   그럴듯한 오진이 나온다(로컬 동일 실행은 통과). → 클릭 직전에 제목을 `<<stale>>`로
   **먼저 지운다**. 낡은 판독은 그럴듯하면 안 되고 명백해야 한다.
2. **고정 sleep은 터널에서 안 통한다.** 250ms·700ms는 localhost에서 교정된 값이다.
   → 제목 변경/서랍 닫힘을 `wait_for_function`으로 **상태를 기다린다**.
3. **프로브 좌표가 소수였다.** `x=1119.75`에서 레이캐스트는 맞다고 답하지만 실제
   마우스는 픽셀로 **반올림**된다. 웨이퍼처럼 전체뷰에서 **클릭 가능 픽셀이 16개뿐인**
   표적에선 이 반올림이 곧 배경 클릭이다 → 정수 좌표로 프로브. 더해서 서랍 개폐가
   스테이지를 리사이즈→카메라 재프레이밍하므로 **클릭 직전에 좌표를 재확인**한다.
**검증**: 실제 터널(trycloudflare) 대상 `--base` 실행에서 10개 메시 전부 OK.

**"장비 3D가 제대로 안 보인다"(사용자 17:08) — 원인은 카메라였고, 버그 3건을 더 잡았다:**
1. **카메라가 하드코딩된 한 좌표였다.** 1440x900 스크린샷 하나로 맞춘 값이라 다른 창
   비율에서는 장비가 구석의 작은 어두운 덩어리였다. → `fitView()`가 매 resize마다
   장비 실루엣에서 거리를 유도한다. bounding **sphere**도 **box**도 아니고(둘 다 이
   둥글납작한 장비에선 허공을 프레이밍한다) 서브샘플된 **점군을 NDC로 투영**해 반복 수렴.
   프레임 점유 span 0.38~0.40 → **0.62~0.76**.
2. **freeze()가 반쪽이었다.** dt는 0으로 만들었지만 컨디셔너 sweep이 `clock.elapsedTime`
   (벽시계)를 읽어 계속 움직였다 → 클릭 좌표를 찾은 뒤 클릭이 닿기 전에 디스크가 비켜나
   **엉뚱한 서랍이 열렸다.** 주기적인 것은 전부 누적 `simT`로 구동하도록 고쳤다.
3. **레이캐스트는 DOM을 모른다.** 서랍·TOOL PARTS 패널이 캔버스 위에 떠 있어서, 3D상
   웨이퍼 위이면서 화면상 패널 아래인 점이 나온다 — 진짜 마우스 클릭은 캔버스에 닿지도
   않는다. `elementFromPoint`로 "사용자가 실제로 클릭 가능한 점"만 채택.

**새 테스트 4개**(`tests/test_tool_ui_3d.py` 19 → 23):
- `test_the_machine_fills_the_frame_at_every_window_shape` (desktop/laptop/phone)
  — 판정 기준은 **큰 쪽 span + 실루엣 밀도**다. 프레임 점유율 하한은 프레이밍 기준이
  아니다(가로로 납작한 장비는 세로 긴 폰에서 어떤 거리에서도 4%를 못 넘는다 — 화면비를
  벌주는 셈). 임계값은 잡으려는 버그로 교정: 구 sphere-fit은 전 뷰포트에서 실패한다.
- `test_freezing_stops_every_moving_part` — 정지는 파트맵으로, 생동은 **픽셀 체크섬**으로
  본다. 회전체는 어느 각도에서나 같은 파트로 찍히므로 파트맵은 회전에 눈이 멀었다.

| 입력부 | 클릭 대상 | 입력 | 상태 |
|---|---|---|---|
| wafer cart / loading | `loadcup` | film stack (cu/w/oxide/poly_si/si/sic/snag) | ✅ |
| operation | `platen`·`carousel`·`head`·`frame` | pressure, platen/head rpm, flow, time, **slurry T**, platen T, ring, zone P | ✅ |
| slurry supply | `slurry`·`nozzle` | abrasive 종류·D50·D99·wt%, pH, T, 첨가제 2종 | ✅ |
| polishing unit | `pad`·`disk` | **패드·디스크를 제품명으로 선택** | ✅ |

**분리 구조(사용자 요구의 핵심):**
- 물리 상수 → `cmp_sim/data/params/*.yaml` · `cmp_sim/models/` → **`GET /api/model?film=`**
- 소모품 물성(패드·디스크) → **`cmp_sim/data/consumables.yaml`**(신규, 출처·신뢰도 필수)
  → `GET /api/meta` · 이름→물성 해석은 `cmp_sim/pad/catalog.py`
- 공정 조건만 UI가 소유. **tool.html에 물리 상수 0개.**
- UI에 **모델 파라미터 인스펙터**: 현재 막질의 상수 전부를 출처·신뢰도와 함께 표시
  → 편집 → `recipe.params` 경로로 즉시 재예측(owner-supplied로 기록됨).
- 이 분리를 **테스트가 강제**(`tests/test_web_holds_no_physics_constants.py`, 11개):
  금지 어휘를 팩에서 실행시점에 뽑으므로, 팩에 상수를 추가하면 그 상수의 UI 하드코딩이
  **테스트 수정 없이 자동으로** 실패가 된다.

**이 작업이 잡은 실제 버그 3건**(전부 테스트로 고정):
1. `tool.html`이 groove pitch 2.0 / width 0.5 mm를 하드코딩 — 출처값(3.05 / 0.6 mm)과
   불일치했고 **비교하는 게 없어서 아무도 실패하지 않았다.** 그림이 측정되지 않은 패드를
   그리고 있었다.
2. **팩이 캘리브레이션한 패드를 고르면 rate가 1.9배 뛰었다.** kappa는 reference pad와의
   비(比)인데, 카탈로그의 Shore D 60 → Qi 상관식 E*=2.5e8 Pa vs 팩의 직접 측정
   1.0e9 Pa(Jeong 2024). **같은 패드의 두 기술(記述) 불일치가 물리 차이로 곱해졌다** —
   드롭다운으로 들어온 피팅 상수. → 팩이 `reference_pad_name`을 선언하면 kappa≡1.0.
3. `Pad.name`의 기본값 "IC1000"에 카탈로그가 반응해서, 패드를 고르지 않은 모든 레시피에
   IC1000 물성이 채워졌다 → 팩 reference와 달라져 **kappa_contact가 조용히 사라지며
   기존 테스트 3개가 깨졌다.** → `name_was_chosen` 기본 False(=불활성).

**정직성 규칙 3개**(abrasive_effects와 동일한 규율):
- **Politex·Suba IV는 Shore D가 문헌에 없다** → 선택해도 rate 불변 + 경고. Shore A→D
  환산표는 비선형 근사이므로 숫자를 만들지 않았다.
- **컨디셔너 그릿 설계는 `wired: false`** — grit→asperity 비례상수가 미확정
  (`legacy/knowledge/performance/disk.yaml` status pack_only)이라 연결하면 그 상수를
  피팅하는 것이다. 테스트가 "디스크 2종의 rate가 같음"을 assert하고, 언젠가 근거 있는
  상수로 연결되면 **시끄럽게 실패**한다.
- 카탈로그의 미공개 물성은 `null` + 사유. 그럴듯한 값 금지.

⚠ **median은 의도대로 18.9% 불변** — 팩 물리를 하나도 바꾸지 않았다. 움직였다면 버그다.

### 1차 완성 — 모델링 정확도 (2차 완료, 이제 여기로 복귀)
- **목표: 예측 오차 median ≤ 10.0%** (이력서에 쓸 수 있는 수준)
- **현재: median 18.9% shape / 21.3% LOO** (코퍼스 46/50, 427점) — **938 tests**.
  2026-09-26(9회차): **속도지수 탐색 종결 — b_V는 상수가 아니고, 심지어 b_V(P)도 아니다.**
  8회차까지 세 회차가 전부 `MRR ~ P·V^b_V`의 **단일 상수**를 찾고 있었다. 이번엔 식을
  또 제안하기 전에 **설명 대상의 모양**을 먼저 측정했다. 추정자는 의도적으로 가장 약한
  것: **압력 고정**이면 Preston의 P선형성은 상수배이므로 *측정* rate의 log-log 기울기가
  곧 b_V다 — 모델을 개입시키지 않으므로 감사 대상인 시뮬레이터의 아티팩트를 물려받을 수 없다
  (`tools/velocity_pressure_interaction_probe.py`).
  · Sorooshian 2005 열산화막(사다리 29개): 2/4/6 psi에서 **+0.370 / +0.687 / +0.764**
    — **단조 증가**, 양 끝이 중앙값 표준오차의 약 4배만큼 떨어져 있다.
  · `mariscal2020_peteos_ceria`(정식 3×3): 2/3/4 psi에서 **+1.105 / +0.857 / +0.625**
    — **단조 감소**.
  · `us6918821b2_cu_ic1000`(정식 2×3): 1.5 psi **−0.416** → 4 psi **+0.863** — **부호 반전**.
    Borucki/Philipossian(ECS 2023, DOI 10.1149/2162-8777/accaa6)의 Cu 관측
    (1/1.5/2 psi에서 −0.81/−0.62/+0.33)을 **독립 재현**했다.
  ⇒ **결론 1: b_V는 상수가 아니다.** 깨끗한 요인배치 하나가 압력에 따라 부호를 바꾸므로
  전역 지수는 유도든 피팅이든 불가능하다 — 세 회차의 탐색이 **대상을 잘못 겨눴다**.
  ⇒ **결론 2(더 중요): 상호작용의 방향조차 보편적이지 않다.** 산화막/실리카는 압력과
  함께 오르고 PETEOS/세리아는 내린다. 즉 매개화를 기다리는 단일 마스터곡선 b_V(P)가
  **아니다** — `V^f(P)` 형태의 어떤 법칙도 단일 f로는 이 두 데이터셋에 **동시에** 못 맞는다.
  지수가 압력의존임을 발견한 뒤의 뻔한 다음 수(팩별 b_V(P) 피팅)는 **상수를 함수로 바꾼
  피팅**일 뿐이고, 그것을 동기부여한 바로 그 측정이 그것을 금지한다.
  ⇒ 그래서 "속도지수를 찾는다" 노선을 **pH축처럼 닫았다.** 열린 질문을 재정의한다:
  **무엇이 P와 V를 결합시키는데 그 결합이 소모품 조합에 따라 뒤집힐 수 있는가?**
  (접촉면적 진화·패드 asperity flash heating은 원리상 둘 다 가능하나, 아직 자유상수
  0개 형태가 없다.)
  ⚠ 정직성 2건(둘 다 테스트로 고정): (1) **사전등록 기준(across/within ≥ 2배)은
  Sorooshian에서 발화하지 않았다 — 0.99배.** 압력당 사다리가 10개면 이 규칙은 *중앙값*의
  산포를 *단일* 사다리의 산포와 비교하므로 구조적으로 둔감하다(원래 size·conc 프로브용으로
  교정된 기준). 그래서 단조성은 **사후(post-hoc) 통계로 명시**하고 약한 형태(양 끝이
  표준오차 여러 배)만 assert했다. 보고 나서 고른 통계는 **바꿔치기하지 않고 공시**한다.
  (2) **이 프로브의 첫 판은 22배라는 허위 상호작용을 냈다** — 서로 무관한 데이터셋에서
  압력당 사다리 하나씩을 모아버려, across-pressure 산포가 실은 막질·슬러리·장비 간
  차이였다. 이제 채점은 **데이터셋 단위**이고, 사다리를 내는 데이터셋은 전부 명시적
  admit/exclude 사유를 달아야 하며, 미검토 데이터셋이 새로 나타나면 테스트가 실패한다.
  `sic2023_shear_rheological_L9`는 **답이 아니라 설계 때문에** 제외: 입경·농도가 행마다
  바뀌는데 그 값이 행 **label**에만 적혀 있어 그룹화 키가 볼 수 없다(그래서 사다리 하나가
  b_V=+6.76을 냈다).
  **아무것도 채택하지 않았으므로 median은 의도대로 18.9% 불변.**
  `tests/test_velocity_exponent_is_not_constant.py`(8 tests).
  2026-09-26(8회차-B): **속도축 결판 — 기아 법칙 기각, 그러나 지수 자체는 입증됐다.**
  8회차-A가 요청한 데이터셋을 같은 실행에서 찾았다: **Sorooshian 2005**(애리조나대
  박사논문, Philipossian 그룹) — 열산화막에서 **유량 40/120 cc/min × 속도
  0.32/0.64/0.96 m/s × 압력 2/4/6 psi 완전요인배치**, 즉 기아 법칙이 구속하는 세
  변수 전부. 무엇보다 **yang2023이 떨어진 Preston 감사를 통과**하므로 심판 자격이 있다.
  `tools/sorooshian_flow_probe.py`가 측정(117점):
  · **b_P = +1.165**(사다리 30개) — Preston +1.000 요구, **감사 통과**
  · **b_V = +0.655**(사다리 29개) — 기아 예측 +0.667, **거의 정확히 일치**
  · **b_Q = −0.010**(**매칭쌍 47개**: groove·두께·압력·속도 동일, 유량만 상이)
    — 기아 예측 +0.333, **완전 부재**. 유량 3배가 rate를 **−1.1%** 움직이는데
    법칙은 **+44.2%**를 요구한다. 쌍별 부호도 동전던지기(22/47 양수).
  ⇒ **두 다리는 맞고 한 다리는 없다. 그래서 지수를 넣지 않았다.** b_V와 b_Q는
  **같은 물질수지**에서 나온다(Q/V는 하나의 양이다). 유도를 반쪽만 채택할 수는 없다 —
  맞는 속도항만 취하고 틀린 유량항을 버리면, 유도식이 **분수 모양을 한 피팅상수**로
  전락한다. median은 **선택에 의해** 18.9% 유지.
  ✅ **그래도 큰 소득이 있다: sub-linear 속도응답이 코퍼스 아티팩트가 아니라
  실험적 사실로 확정됐다** — Sorooshian +0.655, Tseng & Wang 1997이 열산화막에서
  **유도**한 +0.5, Park/Lee/Jeong 2005이 Cu에서 피팅한 +0.74. 없는 것은 증거가
  아니라 **메커니즘**이다.
  ⚠ **학계 주류 가설을 우리가 이미 기각했음도 확인**: Borucki/Philipossian(ECS 2023,
  DOI 10.1149/2162-8777/accaa6)은 비-Preston 거동을 **Stribeck 혼합윤활 COF 감소**로
  설명하는데, COF가 V/p의 함수면 두 로그계수가 **크기 같고 부호 반대**여야 한다.
  코퍼스 측정은 (−0.036, −0.549). 8회차-A의 기각이 곧 현 주류 가설의 기각이다.
  ⚠ **유량항의 부호는 문헌이 오히려 반대로 측정한다**: Li/Philipossian(JES 2004,
  DOI 10.1149/1.1758818)은 Cu에서 *"고정 p×V에서 유량이 늘면 rate가 감소"*(대류냉각
  탓)라 하고, Park 2015(DOI 10.1007/s40684-015-0041-8)가 이를 재현한다. 우리 b_Q≈0과
  합쳐, 기아 법칙은 독립 3중으로 반증됐다.
  💡 **다음 수의 실마리 2개**(provenance 파일에 기록): (1) 슬러리 이용효율이
  **2~22%**에 불과하고 그 자체가 V에 의존한다(Philipossian & Mitchell 2003) —
  즉 **분사 유량 Q는 애초에 틀린 변수**였을 수 있다. (2) Borucki의 Cu 데이터에서
  속도지수가 **압력에 따라 부호가 바뀐다**(1/1.5/2 psi에서 −0.81/−0.62/+0.33) —
  전역 단일지수로는 유도든 피팅이든 재현 불가. **이 압력의존성 측정이 다음 수다.**
  데이터: `research/digitized/sorooshian2005_ild_cmp.csv` + 추출코드 + PROVENANCE.md.
  ⚠ 정직성: rate는 **표가 아니라 그림 판독**이다(논문이 p·V에 대해서만 플롯). 그래서
  **상수 피팅에 쓰지 않고 기각에만 썼다** — 3배 스팬의 로그기울기 부호/크기만 묻는다.
  판독오차 5~10%로는 +44% vs −1%를 만들거나 감출 수 없다. 축 보정 자체 검증:
  117개 마커 전부가 공칭 (psi×m/s) 곱에 0.5% 이내로 안착(보정이 틀렸으면 불가능).
  가드 4개(`tests/test_sorooshian_flow_falsifies_starvation.py`): Preston 감사·
  sub-linear·b_Q≈0을 assert하고, 팩이 `velocity_exponent`류를 선언하면 실패한다.
  2026-09-26(8회차-A): **속도축을 처음으로 측정했다 — 법칙 3개 동시 기각, 그리고
  P/V 비대칭이라는 실질적 발견.** 압력축은 이미 조사했지만(포화 기각) 속도축은
  한 번도 프로브된 적이 없었다. `tools/velocity_thermal_probe.py`가 속도 사다리
  5개(≥3수준)에서 잔차 기울기를 측정:
  (1) **마찰발열 Arrhenius 기각** — 발열이 화학항을 가속하면 고속에서 모델이
  **과소**예측해야 하므로 기울기가 양수여야 하는데, median d(lnR)/d(lnV) =
  **−0.549**로 부호가 정반대(5개 중 1개만 양수). R_th 상수 도입 금지.
  (2) **진짜 발견은 joint fit이다.** 같은 잔차를 ln P·ln V에 **동시** 회귀하면
  median **b_P = −0.036, b_V = −0.549** — 즉 잔차는 **압력에 평평하고 속도에만
  급격히 떨어진다**. 이 비대칭 하나가 후보 법칙 둘을 동시에 죽인다:
  · Stribeck 윤활(Sommerfeld수 ηV/P)은 b_P = −b_V(합=0)를 요구 → 합 −0.585, 기각.
  · P·V **곱**에 대한 모든 직렬저항형은 b_P = b_V를 요구(곱은 두 인자를 구분
    못 한다) → b_P≈0 vs b_V≈−0.55, 기각. 이는 압력 프로브의 포화 기각을
    **반대 축에서 독립 재확인**한 것이다.
  ⇒ **Preston의 P 선형성은 더 날카로운 검증을 또 통과했다**(압력 잔차 보정 불필요).
  V 선형성은 통과하지 못했다.
  (3) **그런데 상수를 넣지 않았다.** 뻔한 수는 sub-linear 속도지수이고, 유혹의
  크기를 숨기지 않으려 스크립트가 반사실을 직접 출력한다: V^(2/3-1) 사후보정이
  코퍼스 median을 **16.7% → 14.5%**로 옮긴다. 그래도 보류한 이유 — 2/3을 **유도**하는
  유일한 법칙이 반응물 기아(Q/V 재고 × 이 저장소가 이미 유도한 세제곱근 농도법칙
  ⇒ MRR ~ P·V^(2/3)·Q^(1/3), **자유상수 0개**)인데, 이 법칙은 예측을 3개 하고
  그중 **b_Q = +1/3**이 독립 검증이다. 유량을 변화시키는 유일한 코퍼스 데이터셋에서
  측정값은 **b_Q = −0.201로 부호가 반대**다. 유도가 자기 검증에 실패했으므로
  지수만 떼어 쓰는 것은 피팅이다 → 보류.
  ⚠ **반대 방향으로도 과장하지 않았다**: 그 유일한 유량 데이터셋
  `yang2023_quartz_ceria_L25`는 코퍼스 최악(69%)이고 자체 b_P가 −1.276으로 나머지
  4개가 깨끗이 세운 P 선형성과 모순된다. Preston의 가장 확립된 축을 재현 못 하는
  데이터가 약한 축을 심판할 수는 없다. 그래서 기아 법칙의 정직한 판정은
  **"신뢰할 유량 스윕 부재로 판정불가"**이지 기각이 아니다.
  결정시킬 것: **P 선형성을 재현하는 데이터셋에서 나온, 유량 2수준 이상의 속도
  스윕 1개.** 그러면 기아 법칙이 자유상수 0개로 median 약 2%p를 벌거나, 아니면
  pH축처럼 V축이 닫힌다. 그때까지 median은 **선택에 의해** 18.9%다.
  가드 4개(`tests/test_velocity_thermal_falsified.py`): 기각된 세 법칙의 부호·
  비대칭·b_Q를 assert하고, 팩이 `thermal_resistance`/`velocity_exponent`류 상수를
  선언하면 실패한다. 측정이 뒤집히면 조용히 낡지 않고 시끄럽게 실패한다.
  2026-09-26(7회차): **Cu 항복 임계 = NULL(음성 결과)**. W에서 통한 전단 임계를
  Cu/BTA로 옮기라는 예측을 Cu 자체 압력 사다리 12개로 측정했는데, 절편 부호가
  동전던지기(5/12 양수)이고 중앙값이 −0.094·P_mid로 **부호가 반대**였다. 상수를
  추가하지 않았으므로 median은 의도대로 18.9% 불변. 얻은 것은 음성 지식 + 가드:
  테스트가 Cu 팩의 `yield_pressure`류 상수를 금지하고, 새 데이터가 Cu 억제제
  2수준을 만들면(=Q2가 답할 수 있게 되면) 시끄럽게 실패해 재검토를 강제한다.
  함정 2개 회피: 2점 사다리는 2-파라미터 임계가 **정의상 정확히 맞으므로**(SSE=0)
  Q3에서 제외했고(안 했으면 12개 중 9개가 "임계 입증"으로 보였다), 사다리 그룹화가
  행별 기록 필드(`measured_mrr_angstrom_per_min`)를 무시하게 고쳤다(안 고쳤을 때
  `us6918821b2` 전 행이 단독 그룹이 되어 데이터셋 하나가 조용히 빠졌다).
  2026-09-26(6회차): **responsive_miss 버킷 공격 1건 성공 — 코퍼스 median이
  19.5% → 18.9%로 내려갔다(정체 이후 첫 이동).** 최악의 반응성 데이터셋
  `ep3161098b1_w`(54.9%)를 **54.9% → 12.9%**로 고쳤다. 원인은 STATUS가 예측한
  대로 배관이 아니라 **빠진 법칙**이었다.
  유도: W는 Kaufman 순환(JES 138(1991)3460)으로 제거되므로, WOx 부동태층을
  **전단해 뜯어내기 전에는 아무것도 안 떨어진다** → Preston에 항복 오프셋이 붙는다
  `RR = K·V·max(P − P0, 0)`. 그리고 P0는 억제제의 **벌크 농도가 아니라 표면
  피복률**로 정해진다 → `P0 = P_y·θ`, `θ = K_L·C/(1+K_L·C)`(Langmuir).
  상수 2개(P_y=4.76 psi, K_L=0.00562 /ppm), 18점·억제제 3수준 → 과결정.
  `cmp_sim/models/passivation_threshold.py` + `tools/w_passivation_threshold_probe.py`
  + `tests/test_w_passivation_threshold.py`(7 tests).
  **상수 회계상 이득이다**: 같은 곡률을 피팅 압력지수 1개(n=2.15)로 흉내내면
  26.9%에 그치고 메커니즘이 없다. 46.1%(순수 Preston) / 26.9%(지수 1개) /
  **12.4%(유도식 2개)** — 테스트가 이 세 숫자를 매 실행 재유도해서, 유도식이
  피팅지수를 10%p 이상 못 이기면 "곡률 재매개화일 뿐"이라며 실패한다.
  죽어 있던 `inhibitor_ppm` 축이 살아났다(축 테이블에 12.9%로 신규 등장).
  ⚠ **부분 반증을 숨기지 않았다**: 조성별로 P0를 따로 피팅하면 37/50/63 ppm에서
  0.52/1.19/1.08 psi로 **단조가 아니다**(상위 두 수준이 서로의 산포 안). 피팅된
  K_L에서 θ가 0.17→0.26밖에 안 움직이므로 Langmuir 포화와 모순은 아니지만,
  데이터는 피복률의 **시작부만** 제약한다 → P_y는 외삽된 절편이며 WOx의 전단강도로
  인용하면 안 된다(팩 노트·테스트 양쪽에 고정).
  ⚠ **Fe 축은 일부러 비워 뒀다**: Fenton은 촉매에 1차이므로 `[Fe]/[Fe]_ref` 인자가
  같은 적합을 12.4%→11.5%로 더 개선하고 **형상 상수를 늘리지도 않는다**. 그런데
  이 팩의 Kp는 US2011/0186542A1에 앵커돼 있고 그 특허는 **자기 Fe 농도를 안 적는다**.
  항을 작동시키는 유일한 방법이 기준농도를 지어내는 것이므로 침묵을 택했고,
  테스트가 "Fe를 바꿔도 rate가 변하지 않음"을 assert해 미래의 날조를 막는다.
  2026-09-28(5회차): **19.5%의 정체를 분해했다 — 완성 기준 논쟁의 답이 나왔다.**
  `tools/residual_census.py`가 채점된 46개를 원인별로 한 버킷씩 배정한다(반응성은
  선언이 아니라 **실측** — 첫 행을 각 축의 min/max로 재구성해 실제 시뮬레이터를
  돌려 rate가 0.5% 넘게 움직이는지 본다):
  noise_floor(원리적 불가) 3개/59점 26.8% · no_constant(선언된 공백) 4개/14점
  27.7% · **responsive_miss(더 좋은 법칙이 먹히는 유일한 버킷) 35개/342점 20.2%**
  · few_levels 4개/12점 7.1%.
  **결론: ≤15% 완화는 아직 정당화되지 않는다.** 측정점의 80%가 개선 가능한
  버킷에 있으므로 19.5%는 측정 노이즈나 데이터 공백으로 막힌 수치가 아니다
  (테스트가 이 다수성을 assert — 뒤집히면 시끄럽게 실패한다).
  같은 실행에서 **압력 포화 법칙도 반증**(네 번째 법칙 기각):
  `1/RR = 1/(kPV) + 1/RR_chem`(Kaufman 1991)은 팩당 상수 1개를 요구하는데,
  잔차 기울기 중앙값이 **+0.08**(10개 중 음수 5개)이고 **압력대가 겹치는
  데이터셋들이 부호가 반대**다(같은 특허 ep3161098b1의 teos -0.06 vs w +1.04).
  공통 곡률로는 같은 압력에서 반대 부호가 나올 수 없다 → Preston의 P 선형성 유지,
  상수 추가 없음.
  2026-09-28(4회차): **농도 지수의 피팅 상수를 유도식으로 제거했다**(상수 감소).
  `tools/conc_derived_probe.py`로 농도 스윕 18개(r2≥0.5는 16개)를 측정한 결과:
  (1) size축에서 통했던 **재질 가설은 반증** — between/within 1.6x로 사전에 정한
  2x 기준 미달이고, 잘 샘플된 세 재질이 0.04 이내로 **일치**한다(diamond +0.30,
  silica +0.33, ceria +0.34). 대칭성 때문에 재질표를 만드는 것은 금지했고 안 했다.
  (2) 대신 **유도식 m = +1/3**(Li 2021 표면적 지배 / Cook 1990 공급한계, 간극이
  단층만 수용 → n_gap ~ C^(2/3), 입자당 하중 ~ 1/n_gap → MRR ~ C^(1/3), **피팅
  상수 0개**)이 코퍼스 median +0.33과 정확히 일치. 16개 중 13개가 ±0.25 내.
  (3) Langmuir 포화형도 **반증** — 포화라면 스윕 평균농도가 높을수록 기울기가
  떨어져야 하는데 상관계수 +0.06(0.01~9 wt% 범위).
  팩 5개가 각자 피팅했던 값(+0.227/+0.3333/+0.3333/-0.4295/-0.406)이 법칙 1개로
  대체됐다 — **상수를 줄이면서** swap 조합의 농도축이 실수치로 살아났다.
  이견 3건(모두 SiC)은 제외하지 않고 기록했다: 경한 막질에서는 반응층 공급이 아니라
  압입이 율속일 수 있다는 가설(테스트가 "비-SiC 이견이 나오면 실패"로 고정).
  ⚠ 이 과정에서 **잠재 버그 1건을 잡았다**: 기존 withdraw 게이트가 "override가
  하나도 없을 때"만 작동해서, 농도 법칙이 항상 값을 공급하자 게이트가 꺼지고
  **철회된 size축이 null로 떨어져 반증된 유도값 -0.84를 타게 됐다**(diamond 런의
  rate가 10배 입경 변화에 6.8배 움직였다). `solver._abrasive_hook`을 축별 철회로
  고쳤다. 코퍼스 median은 의도대로 불변 — 채점 행은 모두 팩의 reference 연마재다.
  2026-09-27(3회차): abrasive-size 지수를 **팩별 피팅 상수에서 재질 상수로 재귀속**
  (`SIZE_EXPONENT_BY_ABRASIVE`, silica -0.13 k=3 / alumina +0.28 k=2 / ceria +1.00 k=1).
  상수 개수가 줄었다(팩 6개가 각자 피팅 → 재질 3개 공유). 코퍼스 median은 불변이
  **정상** — 이 경로는 팩의 reference abrasive와 다른 연마재를 넣었을 때만 타므로
  코퍼스 행(모두 reference)에는 닿지 않는다. 얻은 것: alumina·ceria로 swap하면
  이전엔 size축이 `withdrawn`(무반응)이었는데 이제 자기 재질의 측정 지수로 움직인다.
  conc축은 여전히 withdraw — 재질간 전이 검증을 안 했으므로 빌려오지 않는다.
  2026-09-27(2회차): abrasive-size 축 측정 완료. 단일 유도 지수는 **반증**(세 번째),
  그러나 산포가 **연마입자 재질로 정리된다**(재질간 0.51 vs 재질내 0.16) — 피팅
  상수를 재질 상수로 재귀속할 근거. 코퍼스 median은 의도대로 불변(측정만 함).
  2026-09-27: pH 유도식 **반증됨**(두 번째). 법칙 기반 kinetic leg를 빼면 오히려
  좋아진다(60.4%→35.3%) — 튜닝 부족이 아니라 항 자체가 틀렸다. 부수효과가 더
  중요: 현행 Gaussian의 11.0%는 **in-sample 보간**이고, leave-one-pH-level-out은
  **52.9%**다. pH축의 공식 25%는 그만큼 뒷받침되지 않는다. 자세한 내용은 NEXT.
  MERGED to main 2026-09-27, **863 tests pass**.
  `python tools/score_report.py` (scores) / `python tools/readme_numbers.py`
  (every number the README claims) — both inside `.venv`.
  Absolute-scale misses >3x: **13 -> 9**; the four largest silica misses were ONE
  extrapolation artefact, not four physics gaps. Shape median deliberately
  UNMOVED at 19.5% — a pure scale factor divides out of the shape metric, so a
  moved shape would have meant a bug.
  ⚠ 인터프리터: `source .venv/bin/activate` 먼저. 시스템 python3에는 pint가 없다.
- **10%가 물리적으로 불가능하다고 판단되면 15%까지 허용**(사용자 승인 2026-09-25).
  단 그 판단은 **근거를 STATUS.md에 적고** 나서만 인정된다 —
  "어렵다"가 아니라 "무엇이 남은 오차의 하한을 만드는가"를 써라.
  측정 재현성 자체가 N%라면 그 아래로는 물리적으로 못 내려간다는 식의 논증.
- 문헌에 데이터가 없어 못 푸는 BLOCKED(나노인덴테이션·SnAg Preston 등)는
  **완성의 조건이 아니다.** 기록만 하고 넘어간다.

### 2차 완성 — ✅ 달성 2026-09-26 (상세는 이 파일 최상단)
4개 입력부 전부 동작 + 현재 모델과 연결 + 껍데기/물리 분리를 테스트가 강제.
남은 3D 정교화 여지는 **완성 조건이 아니라 개선 항목**으로 아래 NEXT 하단에 둔다.

**UI 언어 = 영어**(사용자 확정 2026-09-25). 전부 영어 유지 중 — `tools/web_smoke.py`가
매 실행 `/tool`의 한글 문자 수를 세어 0임을 찍는다. 이 상태를 유지한다.

현 상태: `cmp_sim/web/tool.html`(약 830줄) + `vendor/tool3d.js`(669줄),
클릭 대상 10종. **뼈대는 있으니 갈아엎지 말고 정교화하라.**

### 멈추지 않는다
**1차·2차가 모두 끝날 때까지 멈추지 마라**(사용자 명시 2026-09-25).
중간에 "완성했다"고 선언하고 대기하는 것은 위반이다. → 2차는 끝났고 1차는 남았으므로
**계속 진행한다.**

## 🔬 방법론 (사용자 확정 2026-09-25) — 물리화학 법칙 중심
- **실측 데이터를 늘려 맞추는 것보다, 물리화학 법칙에서 유도한 모델식을 세운다.**
- 데이터 수집은 **모델식을 검증·반증하는 용도**로만. 그 자체는 목표가 아니다.
- 피팅 상수를 늘려 오차를 낮추지 마라. **상수를 줄이면서 오차를 낮춰야 진짜다.**
- 모든 항은 유도 과정을 주석에 남긴다(어느 법칙, 어떤 가정).
  `cmp_sim/models/first_principles.py`(Archard↔Preston, Kp=k/H)가 모범이다.
- 자유 파라미터 1개를 물리 유도로 대체할 때마다 `ranking_only` 조합이
  실수치 예측으로 바뀐다 — **median을 내리는 가장 큰 레버**.

## DONE (phase, module, tests)
- **2차 완성: the simulator's SHELL is now separated from its PHYSICS, and the
  separation is enforced by test rather than by convention.**
  `cmp_sim/data/consumables.yaml` + `cmp_sim/pad/catalog.py` +
  `GET /api/model` + `tests/test_web_holds_no_physics_constants.py` (11 tests)
  + 8 new browser tests in `tests/test_tool_ui_3d.py` + `tools/web_smoke.py`.
  Physics constants live in the packs and are published with their sources at
  `/api/model?film=`; named pad/disk properties live in `consumables.yaml` and
  are published at `/api/meta`; the UI owns only operating conditions. The
  forbidden-vocabulary test derives its word list FROM THE PACKS at test time,
  so adding a pack constant makes hard-coding it in the browser a failure with
  no test edit. Three real bugs fell out, all now pinned: (a) `tool.html`
  hard-coded groove pitch 2.0 / width 0.5 mm against sourced 3.05 / 0.6 mm and
  nothing compared them; (b) selecting the pad a pack was CALIBRATED ON
  multiplied the rate 1.9x, because the catalogue's Shore D 60 → Qi correlation
  (2.5e8 Pa) disagreed with the pack's own direct measurement of that same
  physical pad (1.0e9 Pa, Jeong 2024) — a fitted constant arriving through a
  dropdown, fixed by letting a pack declare `reference_pad_name` and pinning
  kappa ≡ 1.0 there; (c) `Pad.name`'s "IC1000" default made the catalogue fill
  properties into recipes that never chose a pad, silently deleting
  `kappa_contact` from 3 existing tests — `name_was_chosen` now defaults False.
  Honesty preserved: Politex and Suba IV publish no Shore D anywhere held here,
  so choosing them changes nothing and says so rather than inventing a hardness
  to make the control feel responsive; conditioner GRIT design stays
  `wired: false` with a test asserting two disks predict the same rate, because
  the grit→asperity constant is undetermined and wiring it would mean fitting
  it. **Median unmoved at 18.9% by construction — no pack physics changed.**
- **The abrasive-size exponent is a MATERIAL property, not a per-pack handle.**
  `tools/size_derived_probe.py` + `tests/test_size_exponent_is_material_property.py`
  (5 tests). Two findings, opposite directions, both recorded: a SINGLE derived
  exponent is FALSIFIED (11 groups span n = -0.45..+1.00, 48% of the -1..+2
  Luo-Dornfeld branch range — the branch would be picked by the data, same
  verdict as pH), but the scatter is ORGANISED BY ABRASIVE: silica -0.13 <
  alumina +0.28 < ceria/silica +0.80 < ceria +1.00, between-material stdev 0.51
  vs within-material 0.16 (3.2x), holding across three different films for
  silica and across 15 years / 20x in size for alumina. Corpus UNMOVED (19.5%
  shape / 21.8% LOO) — this run measured, it changed no pack. **871 tests.**
  ⚠ Two traps found and pinned by tests: (1) grouping conditions by a BLACKLIST
  of axes split every group into singletons, because provenance fields
  (`read_method`, `digitization_uncertainty_*`, `source_detail`) differ row by
  row — only 2 groups survived instead of 11; a whitelist of process axes is
  correct. (2) Taking the abrasive from the PACK name labels wei2026 (silica)
  and su2011 (alumina) as ceria, because both borrow `sic_ceria_h2o2` and say
  PLACEHOLDER in their own headers — that manufactures a fake within-ceria
  spread of 0.10..1.00 and would have destroyed the finding. Filename is
  authoritative. The ordering is NOT explained by hardness (alumina 20 > silica
  8 > ceria 6 GPa is the wrong order), so it is recorded as a re-attribution
  with a chemical-tooth hypothesis, not as derived physics.

- **`si` finally has a validation dataset — BLOCKED #0 measured, not closed.**
  The si pack was the ONLY film scored against nothing: its Kp came from one
  back-calculated point ([ZHU25], 0.62 psi on a 125 mm single-side lapper) and
  nothing independent ever tested it. Added bae2022_si_wafer_alkali_ph
  (doi:10.3390/nano12213893, rates printed in the body text, not digitised):
  a different tool, a 9x higher down force (5.7 psi), a SUBA 600 pad.
  Shape 12.6% vs its own 4.3% replicate floor. ⚠ It does NOT beat
  predict-the-mean (12.6% both ways) and that is the honest reading — the pack
  has no pH term, so it predicts one number for a ladder that moves 1.27-1.38x.
  Absolute comparison is switched OFF: the paper never states the carrier-
  platen centre distance, so relative velocity — and therefore the Preston
  rate — cannot be formed from it. What the absolute numbers DO buy is the
  first INDEPENDENT confirmation of sanity.py's 100-3,000 A/min Si envelope,
  which until now rested on the same source as the Kp it was checking.
  Deliberately NOT fitted: two pH levels cannot determine a unimodal peak+width
  (two free constants → exact interpolation). Recorded as a THIRD audit state,
  `DECLARED_UNFITTABLE`, distinct from a null result — the effect is REAL but
  under-determined — and the test re-derives the level count and the 1.1-2.0x
  gain from the file rather than trusting the table.
  Also declined: the same figure's three AMINE rows (EDA 552.8, DETA 617.2,
  TETA 499.1 nm/min at pH 10.8-10.9 vs NaOH's 177.1 at pH 10.90). 3x the rate
  at the SAME pH is the paper's own evidence that pH does not set the Si rate;
  scoring them on a pH term would manufacture a failure out of chemistry the
  pack never claimed. That gain already lives in additives.yaml.
  Corpus 46/50 scored, 427 points; medians UNMOVED (19.5%/22.6%). pH axis
  14 → 15 datasets and 29.1% → 26.8%. 849 tests.
  ⚠ Fixed a latent hole while here: test_readme_numbers_are_computed hardcoded
  the denominator ("of 49 datasets"), so adding a dataset made the README's own
  total wrong while the test that guards the README still passed. Now computed.

- P1 Preston · P2 GW contact · P3 Luo-Dornfeld · P4 chemistry (pH/oxidizer/
  inhibitor + Arrhenius) · P5 radial uniformity · P6 pattern dishing/erosion
  · P7 pad glazing & conditioner ageing · P8 defect proxy. **846 tests pass.**
- Model selection by SITUATION not film (`core/regime.py`, `core/profiles.py`);
  maturity grading (`core/maturity.py`) — a pack may lower its grade, never
  raise it; Kp from first principles (`models/first_principles.py`).
- Learning from data: `core/calibration.py`, `core/factor_fit.py` (LOO-gated),
  `core/measurement_io.py`. **Scored on every measured axis**
  (`core/predictive_score.py`, `cmp-sim accuracy`): 41/49 datasets, 388 points.
- **pH belongs to the slurry SYSTEM, not the film** — US9422456B2's cationic
  core-shell silica peaks at pH 4.9 on the SAME TEOS film where plain silica
  peaks at pH 11. Split into `oxide_silica_aminosilane` rather than widening
  the bell: 126.6% → 25.3% on its 22 points, pH axis 49.2% → 39.3%.
- **Abrasive TYPE reaches the rate** (`slurry/abrasive_effects.py`): a swap
  rescales only by a published matched-condition ratio, withdraws the pack's
  measured exponents, says `ranking_only` when unanchored.
- **`cmp-sim accuracy` now prints `repl%` — each dataset's own reproducibility.**
  Reporting only: medians (19.5%/22.6%), scored count (43) and beats-mean (33) all
  unmoved, asserted by test. Three datasets marked `floor` (already at their own
  noise) so they stop reading as model failures. Audit of all 49 files found the
  blank column covers THREE states, not one: rates-are-averages-with-spread-
  withheld (du2004 says so), digitized-with-stated-read-error (bouvet2002_w 1.0%,
  _ti 2.7%), and nothing-stated. That separates bouvet2002_w (2.3% vs 1.0% floor,
  finished) from bouvet2002_ti (30.7% vs 2.7%, a real miss) — previously
  indistinguishable. `at_noise_floor` is None, never False, when unmeasured.
- **3D tool UI now TESTED end-to-end (was 0 tests).** The owner's brief asks for a
  simulator operated by CLICKING an AMAT-style polisher, not a form — and the UI
  had no test at all while the engine had 834. Now driven in headless Chromium
  (SwiftShader, no GPU): canvas 1280x808 with 1,027,557 lit pixels, 0 console
  errors; 10 parts hit-testable by scanning the canvas with the scene's own
  raycaster (frame/pad/head/carousel/slurry/nozzle/disk/platen/loadcup/wafer);
  click -> correct drawer (wafer/pad/disk/slurry); film changes the prediction
  (cu 5458.5 / w 1091.7 / poly_si 1668.7 / oxide 1559.6 A/min).
  ⚠ alumina & zirconia return the PACK rate (1559.6) — not a bug: no published
  same-recipe ratio exists, so abrasive_effects refuses to invent a scale and
  warns the run is a RANKING. Test asserts the WARNING, not a rate difference —
  demanding a difference would demand a fabricated number.
  playwright is an optional extra ('.[ui-test]'); tests skip without it.
- **DEFINITION OF DONE MET (checked, not assumed).** 9/10 examples run; the 10th
  (snag_solder) exits 3 BY DESIGN — SnAg is unestablished and the model refuses
  rather than inventing a pH window (the one primary report eliminated both
  windows it tried). Its pair snag_solder_screening.yaml supplies that input and
  runs. Literature gate: 4 in-scope datasets within 15% (need 3) -> PASS, and the
  gate counts WHOLE datasets — 2 are explicitly excluded for passing only on
  their best group. Every running example emits 4-5 warnings; none silenced,
  each is a disclosed gap. Kept as tests/test_definition_of_done.py, not a
  scrollback.
- **Calibration for limit 11 ALREADY EXISTED — `cmp-sim fit`.** Checked before
  building: no new command needed. Verified it recovers an injected 2.5x tool
  factor to 0.3%. ⚠ Near-miss: fitted Kp 2.3289e-13 vs pack 1e-13 looks like
  2.33x (7% short) — but `fit` regresses BARE Preston while simulate() applies
  chemistry/contact factors netting 0.929, so the target is 0.929*2.5*1e-13 =
  2.322e-13. A fitted Kp is an EFFECTIVE Preston constant, not pack*factor;
  testing against the pack constant would invent a 7% bug. Test also pins that
  calibration never touches corpus scores (else validation is circular).
- **README now states what 19.5% supports (limit 11).** Badges said 688 tests/394
  points (actual 822/424) and the axis table held stale medians. Worse, "19.5%
  median prediction error" reads as a promise to predict absolute rate to 20% —
  false on 13/34 datasets. Page now leads with "ranking claim, not a rate claim",
  carries the concrete 7.1%-shape/139x-scale case, and gives the 1-experiment fix
  (one calibration wafer re-anchors Kp). EVERY README number is now recomputed by
  a test — totals, per-axis medians, counts, scale counts, both badges.
- **`scale` column in accuracy report + JSON (reporting only).** Shape says the
  model RANKS conditions well; scale says whether the rate is right at all, and
  they fail independently — ep3161098b1 is 7.1% shape but 139x off in absolute
  rate, previously invisible. 13/34 comparable datasets are off >3x. 11 datasets
  print "-" because their own notes forbid absolute comparison (Kp-audit rule; a
  test pins the dashes to exactly that set so a silent failure can't hide there).
  Wrongness ranked both directions — us6918821b2 at 0.08x over-predicts 12x.
  Medians unchanged 19.5%/22.6%, 45 datasets, 424 points, pinned by test.
- **One acidic oxide dataset was mis-assigned; two others were NOT.** us9499721b2's
  own notes say the abrasive is 아미노실란 양전하(cationic) silica at pH 4.7 — the
  exact system oxide_silica_aminosilane was built for. Reassigned: scale 98.25x ->
  2.68x, shape 22.9% UNCHANGED. Shape can't move (axes are pressure/conc, no pH
  constant touches them), which is why "fits better" could not decide this —
  ep3161098b1 (139x) and bouvet2002_oxide (39x) improve 4-11x too but neither
  source states abrasive charge, so they were LEFT mis-scaled. ⚠ Exposed a
  circularity: oxide_silica's abrasive_conc_exponent(0.3333) was regressed from
  THIS cationic file's 3psi row; all 3 silica packs share it so nothing moved.
- **Inherited Kp is NOT the problem — hypothesis falsified.** Backed out the scale
  each pack's data implies (11 datasets excluded, each by its own 'absolute values
  incomparable' flag). The 2 packs that INHERIT kp unchanged are among the best
  calibrated (anionic 0.51x, aminosilane 2.04x); the worst is their PARENT
  oxide_silica at 38.7x. Cause: pH position, not Kp — inside the pack's fitted
  range [10,12.5] li2021=0.60x / taguchi=0.85x, but at pH 3-4.7 the same pack is
  39x/98x/139x. The pH term drives the prediction to its floor and the deficit
  lands on Kp, the last free scale. Refitting Kp would bake in an extrapolation
  error. First measurement of this limit's MAGNITUDE (2 orders, not a few %).
- **What a pack split buys (limit 10).** The 2 thinnest packs are justified — but
  in pH ONLY. Re-scoring their datasets with the parent oxide_silica: anionic
  32.1%->94.7%, aminosilane 25.3%->126.6%. So keep the split. But the diff vs
  parent is 6/124 and 7/125 parameters and EVERY one is pH — Kp, pad, abrasive
  exponents all inherited. A 62-parameter file implies independent
  characterisation it does not have; both packs now say so in their headers.
  ⚠ First diff used pack.get() (returns None for all keys) and reported the packs
  as IDENTICAL; correct accessor is pack.param(). Guarded by a test.
- **Parameter-evidence inventory (README table + test).** Per pack, how many
  fitted constants does the data actually exercise? **290/628 = 46%; 338 are
  not.** Spread matters more: cu_h2o2_bta 68% (86 rows/11 axes) vs
  oxide_silica_anionic 11% (7 rows/1 axis) — two packs with similar shape errors
  are NOT equally supported. 46% is an UPPER bound (one pH sweep credits 4 pH
  constants; 'exercised' != 'validated'; 512 user inputs excluded). Not an
  argument to delete the 338 — an argument against reading one median as
  certifying the model.
- **sic_alumina_kmno4: a score can be real and validate nothing you assumed.** Its
  two (newly scorable) datasets both sit BELOW its fitted pH range [9.0,11.0] —
  entegris2022 at pH 2.3, gong2024 at pH 2-6 — so neither validates the pH term;
  sweeping pH 3->13 on a gong row swings 94.7->7889->919 A/min across a peak no
  dataset visits. Evidenced: abrasive loading (entegris 14.1% vs mean 65.1%).
  NOT: pH (extrapolation), oxidizer (gong LOSES to its mean, 24.9 vs 15.0 — the
  data span only 99-119 A/min), abrasive size (never varied). No term is inert.
  Recorded as a documentation-only pack override; medians unchanged.
- **Every dataset now declares its film** (`scripts/declare_dataset_films.py`,
  evidence string per dataset). Transcription from each source, not inference.
  Corpus 43->45 scored, 394->424 points (entegris2022/gong2024 were unscorable
  without a film); medians UNCHANGED at 19.5%/22.6% and no existing error moved.
  Borrowings visible 7->14. Only null left: phm2016 (film never disclosed;
  'unknown' made the scorer drop it). ⚠ First attempt wrote into legacy/ —
  reverted and redone as overrides under cmp_sim/data/validation/datasets/.
- **Borrowed-pack audit** (`tests/test_borrowed_pack_audit.py`): 7 datasets score a
  film with another film's pack, in 3 kinds — justified by mechanism (5: sti_ceria
  on oxide, since its exponents split by ABRASIVE not film), deliberate negative
  controls (2: carbide2023/sic2023 on the oxide pack on purpose, each noting the
  gap its bad number documents), and placeholder packs on unsupported films (2).
  **New find: us8142675b2_pt scores 12.3% on an oxide pack — a PLAUSIBLE number
  from another material's constants**, which is more dangerous than Ti's visible
  30.7%. Audit's own blind spot named: 23/49 datasets declare no film at all, so
  prose inference was needed to surface both negative controls. No packs created.
- **Ti declared UNSUPPORTED (limit 9).** bouvet2002_ti was the largest miss vs its
  own floor (30.7% vs 2.7% digitisation). Cause found: three sweeps from ONE figure
  (Ti/W/oxide, same tool+slurry) have exponents -0.454 / -0.049 / +0.001, and the
  shared pack carries -0.05 = W's value. Fitting Ti's -0.45 was REJECTED: it is the
  only Ti data in the corpus, so the constant would be tested on its own fitting
  set (and R^2 is only 0.89 on 4 digitised points). Miss kept visible in the score.
- **`docs/limits.md` — one page for what the model REFUSES to predict.** 9 entries,
  each with the measurement that establishes the limit, the refit that was rejected
  and its cost, and the experiment that would lift it. Distinct from
  open-questions.md (undecided items): these are DECIDED refusals. Guarded by
  tests/test_limits_doc.py (11 tests) both ways — a limit-enforcing test not cited
  on the page fails, and a cited test that no longer exists fails. README's
  validation table now points at it and states the noise-floor caveat: only 5
  datasets have replicates, so elsewhere the achievable floor is UNKNOWN.
- **Two ceria datasets demand OPPOSITE pH terms; the pack keeps the right one.**
  netzband2020 (49.2%) has a VALLEY — 198/113/200/213 over pH 4/6/8/10, two IEPs
  (oxide 2-3, ceria ~8) with pH 6 optimal for neither — and `ph_response` is
  unimodal, so no constant produces it. Ruled out first: NOT a scale offset (the
  benchtop 2.25 cm2 coupon puts absolute rate 8x out, but 49.2% is already
  scale-free, k=0.128) and NOT out-of-range. A netzband-only refit reaches 15.0%
  by going nearly FLAT — and costs dandu2009 (81x swing, the set the constants
  were fitted to) 31.5% -> 492.6%. Left alone, deliberately.
- **The oxidizer term's SIGN flips with PRESSURE, inside one experiment.**
  Diagnosed the worst remaining miss (jani2025 RSM heldout, 51.2%): oxidizer
  correlates +0.76 with measurement but +0.04 with prediction — the term is blind,
  not mis-scaled (ratio spread 4.1x rules out a Kp offset). Cu sweeps contradict:
  ihnfeldt2008 peaks ~0.1 wt%, jani2025 still rising at 6, us8501625b2 shows BOTH
  signs. "Sign tracks BTA" FALSIFIED (both signs at the same 0.08 mM). The two
  groups differ ONLY in down force: 2 psi falls 8200->6300, 1 psi rises
  1900->3900. Left UNFITTED — two pressures cannot fit a coupling — so 51.2%
  stays an honest miss with a named cause. Confound: GT07's peak is ALUMINA,
  jani2025 is silica; abrasive type and pressure co-vary and cannot be separated.
- **Some datasets cannot be predicted better than they were measured.**
  hong2007's three IDENTICAL zero-inhibitor rows report 2650/2400/1850 A/min =
  13.0% replicate scatter, so 13% is the FLOOR on achievable error; the model's
  14.8% is at it. Also a correction: STATUS recorded hong2007's flat baseline as
  12.6%; it is 14.8%, identical to the model — it ties the mean, never lost to
  it. Corpus-wide, 3 datasets sit at/below their own replicate scatter, incl.
  sic2026 DOE50 (34.0% vs 38.5% scatter) — this session's pH refit crossed it
  from above the noise floor to below, so further fitting there is fitting noise.
  Only 5 datasets have replicates at all; the rest have an UNKNOWN floor.
- **Out-of-range pH is a WARNING, not a gate — measured, not assumed.** Fully
  in-range datasets (n=19) median 18.9%; fully out-of-range (n=11) 19.4%;
  Mann-Whitney z=-0.15. No separation, and the out-of-range group holds some of
  the best results (bouvet2002_w 2.3%, ep3161098b1 7.1%, lai2001 8.7%). A gate
  would discard working predictions. Differs from the oxidizer gate, which WAS
  justified: there the term's SIGN reversed (confidently wrong); here the model
  is merely less constrained. Gate = "would be wrong", warning = "rests on
  fewer measurements".
- **A validity range is the FITTING EXPERIMENT's span, never the union.** All 7
  pH-active packs now declare `ph_valid_range` (+ oxide_silica_calibrated_pad,
  which the enumerating test caught). oxide_silica is served by 9 datasets
  spanning pH 1.75-12.5 but 8 hold pH fixed and constrain nothing, so its range
  is li2021's 10-12.5 — the union would claim support no experiment gives.
  Consequence stated, not hidden: bouvet2002/us8142675b2/ep3161098b1/us9499721b2/
  carbide2023/mo2026/yang2023 now warn as out-of-range. No rate changed.
- **An inert constant that looks active is worse than no constant.**
  `sic_ceria_h2o2` had `ph_response_width: null` (to block the inherited acid
  ceria optimum) but still declared the inherited `ph_peak: 4.5` — a constant
  that looks like a SiC optimum and does nothing; the engine's own INERT warning
  had been firing. Its stated reason ("DOE50 cannot isolate the pH axis") was
  checkable and false: 5 groups isolate pH 9/10/11. Fitted peak 10.5 / width
  1.25 / floor 0.10 = 27.5% vs 57.1% inert, and ALKALINE, as the pack's own
  mechanism argument predicted. Interior to its range (unlike the bound packs).
  Trade recorded: DOE50 39.3->34.0, three held-out SiC sets worsen ~0.1-1.3.
- **Validity ranges: a bounded peak has an UNMEASURED side.** The three packs
  whose `ph_peak` is a bound at the data edge (oxide_silica_anionic 2.0,
  cu_alkaline_benzenesulfonic 6.2, cu_h2o2_bta 3.0) had no measured limb beyond
  it and an acid floor of 0, so the model decayed to 0.00 A/min at pH 0.5 with
  no warning (the "2.5 widths" check doesn't fire — pH 1.0 is only 2.0 widths).
  Each now declares `ph_valid_range` = its source table's span, and the engine
  warns outside it, naming the floor and calling a ZERO floor a refusal rather
  than a number. cu_h2o2_bta carries TWO ranges (pH constants 3-6, oxidizer
  constants 2-6.25) — different terms, different experiments, not merged.
- **Pack blindness audit (`tests/test_pack_axis_blindness_audit.py`)**: fails
  if any pack declares no response on an axis its own datasets sweep. One hit —
  `w_fe_oxidizer` on pH — and it is a SOURCED NULL RESULT, re-derived by the
  test from 6 matched pairs (pH 3 vs 6 at matched oxidizer+abrasive: mean ratio
  0.958, sign inconsistent, vs an 8x oxidizer effect in the same table). Null
  results and omissions look identical from outside, so silence is now declared
  in the pack with its table and scope (pH 3-6 only).
- **A missing pH term hid inside the OXIDIZER term.**
  `cu_alkaline_benzenesulfonic` declared no pH response at all (only a
  meaningless inherited `ph_ref: 4.0` from the acidic parent), so a measured
  3.4x pH fall predicted one constant = predict-the-mean, 51.0%. Worse, the
  pack's `oxidizer_peak_wt_pct: 1.0` was justified as "rate falls with
  oxidiser" — but that dataset's pH DRIFTS 10.2→8.5 as acidic H2O2 is added,
  while a KOH-BUFFERED one (us20110165777a1, pH 11.1) measures it FLAT and the
  patent says so explicitly. Added the pH term, peak bounded to the lowest
  measured pH 6.2 (free fit prefers 3.3, outside the data). HELD-OUT evidence:
  h2o2_series 51.7%→12.7%, benzenesulfonic 29.6%→26.8%, both now beat the
  mean. Corpus 20.2%→19.5% trend, 22.6%→21.7% LOO.
- **The velocity exponent is UNRESOLVABLE by this corpus — not fitted.**
  Isolated groups give -0.42 / +0.62 / +0.86 / +0.86 / +1.10 where Preston says
  1.0, and the two datasets need OPPOSITE pressure dependences (mariscal falls
  1.10->0.62 with P, us6918821b2 rises -0.42->0.86). The negative group is the
  patent's own point: an IC1000 pad LOSES Cu rate with speed at low down force
  (lubrication regime, no channel in Preston). A global fit would land ~0.86,
  be wrong at both ends of both datasets, and improve the pooled median.
  Nothing fitted; a test fails if any pack ever declares `velocity_exponent`.
- **NO universal "second pH channel" — hypothesis tested and FALSIFIED.**
  The three pH residuals are three different shapes, and two of them share a
  pack: dandu2009 is a BELL (peak pH 4-5.5), netzband2020 is a V (minimum at
  pH 6, both ends high), same `sti_ceria`, same film, same abrasive. A rising
  alkaline term would have to lift netzband 4.3-4.6x at pH 8/10 — exactly where
  dandu already matches to 1.03/0.96. Fixing one breaks the other, so NOTHING
  was added to the model; the contradiction is pinned as a measurement fact.
  Real lead (recorded, not built): Netzband varies the Ce3+/Ce4+ OXIDATION
  STATE, which the pack holds fixed — a ceria-specific coupling, not a pH term.
- **pH is NOT thin (unlike velocity) and the optimum follows the abrasive's
  CHARGE.** Isolated-pH groups: 12 groups / 66 pts (velocity had 29), isolated
  median ~30% vs pooled 39.3% — isolation does not rescue it, so the term is
  genuinely the weakest physics. Worst group (CN109609035B, 94.7%) was a THIRD
  silica system: anionic silica peaks at or below pH 2 on the same TEOS film
  where cationic core-shell peaks at 4.9 and plain silica at 11 — ordered by
  particle charge vs the oxide's IEP. New pack `oxide_silica_anionic`:
  94.7% -> 32.1%, pH axis 39.3% -> 32.1%, li2021 untouched at 0.2%.
  ⚠ Stops at 32%: the measured pH-6 UPTURN needs a second additive pH channel
  (alkaline hydrolysis), a functional-form change — recorded, not fitted around.
- **The Cu pH optimum is a BOUND, from ONE system.** `ph_peak` was 4.0 =
  "the pack's operating pH", with a note asking for a pH 2-6 sweep — which was
  already in the repo. US20080090500A1 T4 falls monotonically pH 3->6 at all
  three silica loadings, so the optimum is at or BELOW pH 3 and 4.0 predicted a
  rise where the patent measures a 10-24% drop. Peak -> 3.0 (edge of data),
  width 4.1 -> 4.45: shape 10.1% -> 4.3% on those 12 points. Refused to pool
  the alkaline US9200180B2 leg for 17 points — it is BTA-free benzenesulfonic
  and has its OWN pack; same trap `oxide_silica_aminosilane` was split to avoid.
  ⚠ Zero effect on the corpus median: that table prints no down force.
- **The oxidizer term's SIGN belongs to the pH branch — regime gate.**
  Miranda's 2x2 moves H2O2 1.5->3.5 wt% and gets +49% at pH 4, -86% at pH 8
  (interaction p=0.0207, Pourbaix: soluble Cu2+ vs hard CuO). One constant
  cannot be both, so `cu_h2o2_bta` declares `oxidizer_ph_window: [2.0, 6.25]`
  — bounds read off the gated constants' own provenance — and OUTSIDE it the
  term is switched off and says so, instead of extrapolating a wrong sign.
  Scoring now separates "declined" from "wrong"; a gate on an axis a dataset
  holds CONSTANT must not silence it (that rule saved 3 good datasets).
  ⚠ Corpus 20.2% -> 19.5% is NOT a physics gain: 2 datasets stopped answering.
- **The oxidizer floor is MECHANICAL, not chemical** — US8070843B2 is a
  fixed-abrasive pad with no free abrasive, so the pack's free-abrasive 0.14
  background is wrong for it; its own table prints 0.040. 51.7% -> 8.7%, but
  the honest number is the 4 oxidizer-bearing rows: 9.5% -> 8.6% (the zero row
  is near-tautological once the floor is declared). Pack keeps its 0.14.
- **Velocity is the THINNEST axis, not the weakest term** — the 44.1% median
  came from Taguchi arrays that never repeat a chemistry at two speeds. Only
  29 points in the whole corpus isolate velocity; on the one in-scope isolated
  sweep (Mariscal 3x3) the error is 11.7% and the exponent +0.86 vs Preston's
  +1.0. Also fixed a data-fidelity bug: the Yang L25 recorded 2 of its 6
  factors, so four chemical factors' scatter was being read as velocity error.
- Size-matched abrasive-ratio hunt CLOSED with 15 honest nulls
  (`research/rate_ratios_matched.yaml`) — 0 of 15 pairs pass both gates, so
  34/35 film×abrasive pairs stay `ranking_only`.
- Films: Cu, W, oxide, STI-ceria, poly-Si, Si, SiC, SnAg. 55 additives ×
  9 films, 11 abrasives × 9 films. Legacy 2nd transfer absorbed.
- Interfaces: CLI (`run`/`fit`/`sweep`/`validate`/`accuracy`/`packs`/
  `profiles`), zero-dep web UI + API, 3D tool view (`/tool`), `.command`
  launcher. **Published**: github.com/khleecnce/cmp-sim (MIT), demo at
  cmp-sim.vercel.app (`CMPSIM_TOKEN`). History scrubbed before going public.

## NEXT
**PHONE LAYOUT + MACHINED DETAIL (09-26, 10회차) — DONE, 아래 물리 질문으로 복귀.**
폰 레이아웃: 데스크톱 패널 3개가 390px 뷰포트를 통째로 덮고 있었다. `@media
(max-width:720px)`로 시트화 → 로드시 27% → **74%** 가시, 시트 올려도 20%+.
`elementFromPoint`로 검증(전체 크기 캔버스가 완전히 덮여도 통과하는 테스트 방지).
기하 정교화: 사용자가 UI를 두 번 반려(17:52·19:19)해서 **예전 LK 모델**
(`~/fab-sim/sim/web/studio3d.html`)에서 챔퍼/볼트/헤드 스택을 이식. 상세는 상단.

⚠ **다음에 UI를 만지면 반드시 렌더 스크린샷을 직접 볼 것.** 10회차에 e2e가
전 항목 통과인데도 EFEM이 무늬 없는 흰 덩어리였다 — **클릭 테스트는 생김새를
보지 않는다.** 스크린샷을 보고서야 잡았다.

Deployment note: prod had been running a 6-day-old build with no CMPSIM_TOKEN
env var. Re-deployed with `--env CMPSIM_TOKEN=...` (cmp-sim.vercel.app, token in
~/.fabsim-demo-token, append `?t=<token>`).

---

**What couples pressure and velocity, given that the coupling INVERTS between
consumable sets? The 9th run closed the search for a velocity exponent: b_V is
not a constant (Cu changes its sign across 1.5 → 4 psi, reproducing Borucki
2023) and it is not a single function b_V(P) either (oxide/silica rises with
pressure, PETEOS/ceria falls). So the missing physics is a P–V INTERACTION whose
sign depends on the film/slurry pair, and the next run must measure what selects
that sign — not propose a functional form.**

Do NOT fit b_V(P) per pack. That is a fitted function replacing a fitted
constant, and `tests/test_velocity_exponent_is_not_constant.py` forbids it for
the reason the measurement itself supplies: no single f covers the two clean
factorials we have.

Measurement plan (one axis, no fitting, uses data already in the repo):
1. **Sort the three clean bodies by what differs between them** and ask which
   property tracks the sign of db_V/dP. Available: abrasive material (fumed
   silica ↑ vs ceria ↓), film (thermal oxide / PETEOS / Cu), pad, pressure
   range. With three bodies this cannot be decided — it can only NARROW, so
   pre-register that the output is a ranked shortlist, not a law.
2. **The most promising mechanism is contact-area evolution, and it is already
   half-built here.** `cmp_sim/models/contact_gw.py` gives A_r(P), and the
   repo's own GW work found the elastic fully-load-sharing regime where
   particle size cancels exactly. If A_r grows sub-linearly in P while the
   per-asperity sliding distance grows linearly in V, the EFFECTIVE velocity
   exponent acquires a P dependence with NO new constant. Derive dln b_V/dln P
   from the existing GW parameters and check its SIGN against the three bodies
   before touching any pack. A derivation that gets the sign right in two bodies
   and wrong in the third is still a result worth recording.
3. **Second candidate, cheaper to test: pad-asperity flash heating.** Contact
   temperature rises with P·V, so an Arrhenius chemical term produces a P–V
   cross term. This was rejected as a pure VELOCITY law in the 8th run (residual
   slope −0.549, wrong sign), but a cross term was never tested; the rejection
   does not carry over automatically and the distinction must be stated, not
   assumed.
4. If neither derivation produces a sign-correct zero-constant cross term,
   record the axis as closed the way pH is closed, and state in
   `docs/limits.md` what the P–V interaction costs the corpus median — that
   number is part of the honest answer to "is ≤10% reachable?".

Secondary, unchanged from the 7th run:

1. **Does the W threshold generalise to a SECOND W pressure sweep?** `bouvet2002_w`
   is at its own noise floor; `us20110186542a1_w` sweeps H2O2/pH at fixed
   pressure and cannot see P0. **The threshold still rests on ONE patent.**
   Find a second W pressure sweep with a stated inhibitor loading before
   promoting P_y past `confidence: fitted`. If none exists, record that as the
   limit and do not widen the claim.
2. ~~The same shear-off logic predicts a threshold on Cu~~ → **measured, NULL.**
3. pH-dominated oxide/ceria (netzband2020 49.2, cn109609035b 32.1, dandu2009
   31.5, us9422456b2 25.3, son2021 25.6): the pH axis is CLOSED to further
   closed-form attempts by the 2026-09-27 two-falsification rule. What is NOT
   closed: all five are ceria or ceria-adjacent on oxide, where the mechanism
   is chemical-tooth (Ce3+ site density), not electrostatic. **Measure whether
   the residual orders by Ce3+ fraction before proposing any functional form.**

Still true, and still the rule: do not fit. Measure first, one axis per run.

### Closed 2026-09-26 (9th run): there is no velocity exponent to find
`tools/velocity_pressure_interaction_probe.py` +
`tests/test_velocity_exponent_is_not_constant.py` (8 tests). Measured b_V at
FIXED pressure (raw log-log slope of measured rate vs speed — no model in the
loop, so the probe cannot inherit an artefact from the simulator it audits):
Sorooshian oxide +0.370/+0.687/+0.764 at 2/4/6 psi (monotone up, endpoints ~4
median-SE apart), mariscal2020 PETEOS +1.105/+0.857/+0.625 at 2/3/4 psi
(monotone down), us6918821b2 Cu −0.416 → +0.863 across 1.5 → 4 psi (SIGN
CHANGE, independently reproducing Borucki 2023). Nothing adopted; median 18.9%
unchanged by choice. Two honesty notes pinned by tests: the pre-registered 2x
ratio bar did NOT fire on Sorooshian (0.99x — it is structurally insensitive
when a pressure holds ~10 ladders), so the monotone trend is labelled post-hoc
and asserted only in its weaker SE form; and the probe's first cut reported a
spurious 22x by pooling one ladder per pressure from UNRELATED datasets, so
scoring is now strictly per dataset with a recorded admit/exclude reason for
every ladder-producing dataset and a test that fails on an unreviewed one.

### Closed 2026-09-26 (7th run): the Cu threshold is a NULL result — do not port P_y across films
`tools/cu_passivation_threshold_probe.py` + `tests/test_cu_passivation_threshold_null.py`
(6 tests). Cu/BTA is the textbook passivation system, so the W shear-off law
PREDICTS a Cu yield offset. Measured on every Cu pressure ladder at frozen
chemistry (12 ladders, 3 datasets; RR = a·(P − P0) fitted per ladder):

| test | pre-registered bar | measured | verdict |
|---|---|---|---|
| Q1 intercept positive | ≥75% of ladders | **5/12 (42%)**, median P0/P_mid **−0.094** | NULL |
| Q2 orders by inhibitor | ≥2 inhibitor levels | **1 level** in the whole Cu corpus | NOT TESTABLE |
| Q3 buys SSE on ≥3-pt ladders | decisive win | median SSE2/SSE1 **0.822** | NULL |

The intercept sign is a coin flip and the median is on the WRONG side of zero,
so the law is not supported on Cu. **Corpus median unchanged at 18.9% — by
design: nothing was added.** The value is negative knowledge plus a guard: the
test asserts no Cu pack declares a `yield_pressure`/`p0_psi`-style constant, and
it fails LOUDLY if a future dataset adds a second Cu inhibitor level (which
would make Q2 answerable) or if the intercepts turn positive. That converts
"we chose not to fit Cu" from a memory into an enforced rule.
Two traps avoided: 2-point ladders are excluded from Q3 because a 2-parameter
threshold fits them exactly by construction (SSE=0 always — reporting those as
wins would have "proved" the threshold on 9 of 12 ladders), and the ladder
grouping ignores per-row bookkeeping keys (`measured_mrr_angstrom_per_min`,
`read_method`) — leaving them in made every `us6918821b2` row its own singleton
and silently dropped a whole dataset before the bug was caught.


### Closed 2026-09-26: W passivation shear threshold — DERIVED, and it moved the corpus
`cmp_sim/models/passivation_threshold.py`, `tools/w_passivation_threshold_probe.py`,
`tests/test_w_passivation_threshold.py` (7 tests). Details in the header block
above. The two inert axes STATUS flagged as "a plumbing gap, not physics" were
half right: `inhibitor_ppm` was a missing LAW (now 12.9%), `fe_ppm` is a
genuine data gap (the anchoring patent never states its Fe loading) and stays
silent by choice.

### Superseded by the above (was NEXT)
The earlier NEXT read "check the wiring before deriving anything" for
`ep3161098b1_w`. The wiring was fine; the pack simply had no term. Recorded
because the diagnosis was wrong in an instructive direction — an axis that does
not reach the rate can mean "unconnected" OR "the pack has nothing to connect",
and those need different fixes.

### Closed 2026-09-28 (2nd run): the residual is DECOMPOSED — 80% of points are improvable
`tools/residual_census.py` + `tests/test_residual_census.py` (7 tests).
Each scored dataset lands in exactly one bucket, with responsiveness MEASURED
(rebuild the first row at each axis' min and max, run the real simulator, ask
whether the rate moved >0.5%) rather than declared by a YAML field:

| bucket | datasets | points | median shape |
|---|---|---|---|
| noise_floor (irreducible) | 3 | 59 | 26.8% |
| no_constant (declared gap, no law can fix) | 4 | 14 | 27.7% |
| **responsive_miss (a better law helps)** | **35** | **342** | **20.2%** |
| few_levels (<=2 levels, one reading dominates) | 4 | 12 | 7.1% |

**Verdict: the ≤15% allowance is NOT justified yet.** The census was built to
test exactly that, and it came back the other way: 80% of measured points sit in
the bucket a better law can move, so the 19.5% median is not floored by
measurement noise or declared gaps. The allowance may only be invoked when this
table says otherwise — the test asserts the improvable bucket is a majority and
fails loudly if that flips.
Two traps avoided: buckets are assigned in priority order (a floored dataset is
never also counted as improvable, so the shares cannot exceed 100%), and
`no_constant` is decided by RUNNING the simulator — four datasets
(lee2021 inhibitor, kenchappa2021 pad hardness, bae2022 Si pH, phm2016 dresser
usage) have a populated axis that provably never reaches the rate, and grading
them as model error would have inflated the improvable bucket.

### Closed 2026-09-28 (2nd run): rate saturation in PRESSURE is FALSIFIED
`tools/pressure_saturation_probe.py` +
`tests/test_pressure_saturation_falsified.py` (4 tests). The standard proposal
for the responsive_miss bucket is the two-resistance form
`1/RR = 1/(k·P·V) + 1/RR_chem` (Kaufman 1991 passivation), which costs one new
per-pack constant. It makes a sharp prediction: after one fitted scale, the
residual ln(measured/predicted) must fall with ln P on every ladder. Over the 10
datasets with >=3 pressure levels the median slope is **+0.08**, only 5/10 are
negative, and pressure-OVERLAPPING datasets disagree in SIGN
(us9499721b2 -0.17 vs us8142675b2 +0.19; ep3161098b1_teos -0.06 vs
ep3161098b1_w +1.04 — the same patent, same pressures, opposite trends).
A shared curvature cannot produce opposite signs at the same pressures, so the
misses belong to the datasets (scale/chemistry/tool), not to the P dependence.
**Preston's linearity in P is kept and no constant was added** — a fourth
derived-law rejection, and the fourth time refusing a handle the data do not
demand.

### Closed 2026-09-28 (was the previous NEXT): decompose the residual
Rationale it was chosen on (kept for the record).
Four consecutive runs improved the model's HONESTY and reduced its constant count
(pH law falsified, size exponent re-attributed to material, conc exponent
replaced by a derived +1/3) and the corpus median did not move once — 19.5% after
all four. That is not a coincidence to work around, it is the finding: **the
scored corpus rows do not exercise the axes being fixed.** Every scored row runs
its pack's reference abrasive, so abrasive-scoped work provably cannot move the
number, and the pH work moved only a shape that was already in-sample.

So before spending another run on a constant, MEASURE where the 19.5% comes from.
Concretely, for the 46 scored datasets produce a per-dataset attribution of the
residual to one of these buckets and count them:
1. **at the dataset's own noise floor** — already 3 marked `floor`; how many more
   would be if `repl%` were measured? (only 6/46 have it). Irreducible.
2. **axis the pack has NO constant for** (declared gap, model declines) — these
   are honest and cannot improve without new literature.
3. **axis the pack HAS a constant for and still misses** — the only bucket where
   a better law helps. THIS is the bucket to size.
4. **single-point / 2-level datasets** where shape error is arithmetically
   dominated by one reading.
Report the four counts and the median WITHIN bucket 3. If bucket 3 is small, the
10% target is arithmetically unreachable on this corpus and the ≤15% allowance
should be invoked WITH THIS TABLE as the required evidence — STATUS.md demands
"what sets the floor", and a bucket census is exactly that argument. If bucket 3
is large, it names the next law to derive instead of guessing.

Do NOT fit anything in this run. It is a measurement, like `ph_derived_probe` and
`conc_derived_probe` were, and it must not touch a pack. Put it in
`tools/residual_census.py` with a test that re-derives the bucket counts from the
dataset files rather than hardcoding them.

### Closed 2026-09-28 (was the previous NEXT): the conc exponent is a DERIVED LAW
Ran exactly the protocol the item specified and it returned a NEGATIVE on the
question asked (material scope, 1.6x < 2x bar) — recorded as required, no
re-attribution made. The probe then tested the next-simplest hypothesis and found
the positive result the item did not anticipate: a single DERIVED +1/3 lands on
the corpus median with zero fitted constants, which removes five per-pack fitted
values instead of renaming them. `abrasive_conc_half_wt_pct` was left alone, as
the item warned. Also fixed the all-or-nothing withdrawal gate this change
exposed in `solver._abrasive_hook` (a withdrawn size axis was falling through to
the falsified derived -0.84). 880 tests.
`tools/conc_derived_probe.py` + `tests/test_conc_exponent_material_scope.py` (6).

### Closed 2026-09-27 (was the previous NEXT): the size exponent is now a MATERIAL constant
Implemented exactly as the item specified, with one deviation recorded: the
ceria/silica composite (+0.80, k=2, US20190127607A1) was left OUT of the table
(`SIZE_EXPONENT_COMPOSITE_NOTE`) because it resolves to neither parent material
and asserting a composition the patent does not state would be inventing a
number. Four tests pin the behaviour in `tests/test_abrasive_type.py`:
alumina/ceria now move the rate with their own measured log-slope (+0.28 /
+1.00, asserted by regressing the simulator itself over a 4x size step), an
abrasive with NO sweep anywhere (diamond) still reports the axis as unapplied
rather than filling it from the falsified derived -0.84, and the table cannot
carry a value whose k or spread contradicts its own sweep list. Three existing
tests changed premise and were rewritten with the superseded reasoning kept in
the docstring rather than deleted.
Corpus UNMOVED at 19.5% / 21.8% (46/50, 427 points), as predicted.

### Closed 2026-09-27 (was the previous NEXT): the pH derived law is FALSIFIED
`tools/ph_derived_probe.py` + `tests/test_ph_derived_law_falsified.py`
(3 tests). In-sample shape medians over the 6 pH sweeps with >=3 levels:
  Gaussian, 4 constants fitted PER GROUP (24 total)      11.0 %
  derived (kinetic x electrostatic), 2 GLOBAL constants  60.4 %
  electrostatic leg ALONE, 2 GLOBAL constants            35.3 %
  kinetic leg ALONE (S**0.5), ZERO constants             93.6 %
The ablation is the result: **removing the law-backed kinetic leg IMPROVES the
fit**, so the half-order hydroxide leg (Brady & Walther 1990) is the half that
is wrong — not under-tuned. Reason: S(pH)**0.5 is monotone rising by
construction, but 4 of 6 measured sweeps PEAK IN ACID. Dissolution kinetics set
the hydrated layer's THICKNESS (which saturates), not the removal rate; the
Cook-1990 softening term already carries that mechanism, so importing it again
double-counts. Forcing it makes the electrostatic constant B flip SIGN per pack
(oxide_silica -5.0 vs +2.25..+6.75 elsewhere) — a fitting handle, not an energy.
**Second falsification of a derived pH form** (the first: 2-pKa surface
complexation, 27.3% vs 17.7% on Dandu). Per the rule written into that item,
the pH axis is CLOSED to further closed-form attempts until the corpus has more
sweeps: 6 usable sweeps with 4 distinct peak positions cannot determine a form
whose peak is free.
⚠ The by-product matters more than the verdict: **the incumbent Gaussian's
11.0% is in-sample interpolation.** Two of the six groups have constants >= pH
levels (li2021 n=3 scores 0.0%). Under leave-one-pH-LEVEL-out it scores
**52.9%** on 42 held-out points, while the 2-constant electrostatic form fitted
on the OTHER FIVE GROUPS scores 66.6% — a harsher protocol, 14 points behind.
So the pH axis's reported 25-26% is not a well-supported 25%; the honest
out-of-sample pH error is ~50%, and that is a real contributor to the corpus
median that no amount of re-deriving the same 4-constant form will remove.
Corpus UNMOVED as predicted (19.5% shape / 21.8% LOO, 46/50, 427 points) — this
run changed no pack, only measured. **866 tests pass.**

### Superseded 2026-09-27 (kept for the reasoning): the pH-law proposal
**Attack the pH axis with a DERIVED rate law instead of the fitted Gaussian.**
The Gaussian is the single largest remaining physics debt: 15 datasets, median
25.3%, and it carries 2-3 fitted constants per pack (`ph_peak`, `ph_response_
width`, `ph_acid_floor`) that come from nowhere but the data. The edge-hold just
proved the form is wrong outside its fitting window — it had to be CLAMPED to
stop producing 139x artefacts. A form that needs a clamp is a form to replace.

Target form (oxide/silica, where the corpus is thickest), all terms derivable:
  r = k_OH * a_OH^n  * f_electrostatic(pH; IEP_abrasive, IEP_film)
  - the OH- catalysed hydrolysis leg is FIRST-ORDER-ish in a_OH^0.5 (Iler 1979
    ch.1; Brady & Walther 1990 measured n = 0.5 on amorphous silica) — that is a
    LITERATURE exponent, not a fitted one, so it REMOVES a constant
  - the electrostatic leg is why the optimum MOVES with abrasive charge, the
    fact already established in this repo (anionic silica peaks <=2, cationic
    core-shell at 4.9, plain silica at 11 on the SAME TEOS film). A Gaussian
    cannot express that; a product of two site-ionisation terms at the two IEPs
    can, and IEPs are MEASURED quantities per material, not free parameters.
⚠ Read the falsification note below first: a 2-pKa surface-complexation product
was ALREADY tried and lost (27.3% vs 17.7% on Dandu). The difference proposed
here is that the pH-dependence enters through a_OH^0.5 kinetics MULTIPLIED by
electrostatics, not as a pure site-product — and that the IEPs are fixed from
literature rather than fitted. If it loses again on held-out data, record the
second falsification and STOP pursuing this form; do not fit around it.

Scoring rule for this item: count CONSTANTS before and after. A form that hits
the same median with fewer free constants is the win; a form that needs more is
a loss even if the median falls.

### Closed 2026-09-27 (was the previous NEXT): `ph-edge-hold` MERGED
The pH Gaussian was being evaluated far outside the pH window its width was
fitted in — oxide_silica's width 3.1 comes from Li 2021's three points over
pH 10-12.5, and evaluating that bell at pH 3-4 multiplies the rate by
exp(-(7/3.1)^2) = 1/61, a number produced by the FUNCTION rather than by any
measurement. `chemical_rate.py` now holds the pH argument at the pack's own
`ph_valid_range` edge (a field that already existed and only printed a warning).
Physically: the amorphous-silica hydrolysis plateau — the rate is OH--catalysed
above the neutral point and flattens below it (Iler 1979 ch.1; Brady & Walther
1990). ZERO new constants.
  ep3161098b1_teos 139.2x -> 2.5x    bouvet2002_w    75.6x -> ~1x
  bouvet2002_oxide  39.2x -> ~1x     bouvet2002_ti   38.2x -> ~1x
  >3x absolute misses 13 -> 9;  LOO 22.6 -> 21.8;  beats-the-mean 34 -> 35
  shape median UNMOVED 19.5% (predicted, and the check that it was a pure scale)
13 pinned-number tests re-baselined, each with the superseded reasoning recorded
rather than deleted. Two were checked properly rather than re-pinned:
  - test_sic_kmno4's "jump across the unvisited peak" — the worry was that the
    clamp hides a peak OUTSIDE the declared range. It does not: sic_alumina_
    kmno4's peak 10.5 is INTERIOR to its range 9.0-11.0, now asserted. The test
    was rewritten to state the sharper fact — both its datasets (pH 2-6) sit
    entirely ON the clamp, so the pH term is one constant factor for every row
    they contain and cannot be evidence for or against it.
  - test_readme's "139" assertion was a HARDCODED headline case, so removing the
    artefact broke the test guarding the README. Now recomputes the current
    worst case from the scorer (lai2001_cu 8.7% shape / 17.5x scale).
New: `tools/readme_numbers.py` regenerates every number the README claims.

### Closed 2026-09-26 (was the previous NEXT): BLOCKED #2, the ceria scale
See BLOCKED #2. The pack's Kp was an unreproduced estimate; four measured ceria
datasets agreed one-sidedly on 1.09e-13 m/Pa (was 2.2e-13). STI example
7,235 -> 1,559 A/min, inside the published envelope. Corpus medians UNMOVED
(19.5%/22.6%) exactly as predicted — Kp is a pure scale and the shape metric
divides it out; a moved shape score would have meant something else changed.
first_principles.py's k = Kp*H correlation was recomputed as a consequence
(WEAR_COEFFICIENT 9.50e-4 -> 8.25e-4, spread 1.8x -> 1.5x) and the module now
states that this tightening is bookkeeping, not evidence for the 1/H form.
863 tests.

### Closed 2026-09-26 (was the previous NEXT): per-film P0 is FALSIFIED
The "fit a per-FILM breakthrough pressure P0" item is DONE and the answer is NO.
`tools/p0_per_film_probe.py` ran the leave-one-dataset-out test on oxide, the
only film with 4 matched-condition pressure datasets. The in-sample optimum is
**P0 = 0.00 psi exactly** — the offset does not want to exist even on the data
it is scored on — and out of sample it LOSES (15.5% -> 16.0% mean, 11.4% ->
12.5% median). Hydrated-silica removal has no breakthrough stress in 0.6-8 psi;
the Cook gel layer is soft and continuously re-formed, so there is no yield
stress to exceed. Cu (2 matched datasets) and W (1) cannot test it at all and
are recorded as data-limited, NOT as support. Pinned by
`tests/test_pv_exponent_confound.py::test_a_per_film_threshold_pressure_does_
not_earn_its_constant_either`; derivation in docs/derivations.md.

Still genuinely unexplained, and NOT caused by the exponent confound:
ep3161098b1_w (a = 2.00 on 3 matched rows), sic2023 (62% at every form tried),
us6918821b2 (the Cu low-pressure velocity inversion, BLOCKED #1).

### Do NOT re-attempt (measured and falsified 2026-09-25, see docs/derivations.md)
- pH term as a 2-pKa surface-complexation site product (Cook Si-O-Ce bond):
  27.3% vs the current bell's 17.7% on Dandu 2009; the best fit inverts the
  pKa order, and Dandu's 15x tail asymmetry is outside the form's reach.
- Preston -> Tseng-Wang P^(5/6)V^(1/2): loses on 6 of 8 P/V datasets.

### Standing context carried forward (was the previous NEXT)
⚠ CORRECTION. A previous session reported the project "complete" against the
P1-P8 engine gates alone. That was the WRONG bar: the owner's actual brief
(desktop, 09-24 10:49) is (1) a simulator that turns inputs into predictions,
(2) a clickable 3D AMAT-style polisher UI, (3) per-WAFER/film learning, (4) per-
ABRASIVE learning (ceria/silica/alumina/zirconia separately). All four now have
passing end-to-end evidence (844 tests, incl. 10 browser-driven UI tests).

OWNER DECISION (09-24): alumina and zirconia are OUT OF THE PICKER. They were
confusing because selecting them changed nothing — abrasives.yaml holds exactly
ONE published same-recipe ratio (ceria/colloidal_silica = 3.0x on oxide), so any
other swap leaves the rate anchored to the pack's own abrasive.

Implemented as a RULE, not a blocklist (cmp_sim/api.py:_selectable_abrasives):
offer an abrasive on a film when it has a published ratio there, or when it IS
that film's pack reference (the anchored 1.0x case). Result —
  oxide -> ceria, colloidal_silica    cu -> alumina    w -> alumina
  sic/sti/oxide_ceria -> ceria        poly_si/si -> colloidal_silica
zirconia is gone everywhere; alumina survives only on Cu/W, the two packs
actually calibrated with it. Nothing was DELETED: alumina still supplies the
measured size exponent +0.29 and still scores in six datasets (su2011 SiC 4.4%,
lai2001 Cu 8.7%, gong2024, entegris2022, us8142675b2 Pt, su2011 6H-SiC). A config
file may still name any abrasive and it resolves with warnings as before.

Remaining gap is DATA, not build: no same-recipe ratio exists for the withheld
abrasives. Do NOT close it by deriving a ratio from hardness; Mohs order does not
predict CMP rate (ceria is softer than alumina and removes oxide faster), and
abrasive_effects.py refuses that on purpose.

## BLOCKED  (numbers + sources: `docs/open-questions.md`)
0. `si` — HALVED, not closed. The film now has one independent dataset
   (bae2022, 12.6% shape) so it is no longer unscored, and its 5.7 psi rates
   confirm the 100-3,000 A/min envelope independently of the Kp source. What
   is STILL missing is the thing the entry originally asked for: a second
   ABSOLUTE point. bae2022 cannot supply one — it never states the carrier-
   platen centre distance, so no relative velocity and no Kp can be recovered
   from it. The 10,776 A/min over-prediction at bare defaults therefore stands
   unexplained, and Kp still rests on one Seidel-era point.
   NEEDED: a bare-Si rate measured at a stated pressure AND a recoverable
   relative velocity (rpm plus carrier-platen geometry, or m/s directly).
   Secondary gap now named: the pack has NO pH term at all
   (tests/test_pack_axis_blindness_audit.py::DECLARED_UNFITTABLE), because two
   pH levels cannot fit a peak and a width. A three-level pH sweep on bare Si
   with colloidal silica would lift that.
1. Velocity inversion is NOT a lubrication effect — no dataset will fix it.
   λ = 0.001401·(rpm/P) exactly, i.e. λ IS the pseudo-Sommerfeld number V/p
   (Wu & Liao 2016, doi:10.5772/64484) up to one constant, so calibrating it
   with measured viscosity/roughness only rescales and cannot reorder. The
   inverting rows (λ .056/.112/.187) OVERLAP the non-inverting ones
   (.021/.042/.070), and mariscal2020 — 9 rows that never invert — sits inside
   that range. A threshold would need to be below .056 and above .070 at once.
   (This corrects the earlier entry asking for a film-thickness dataset.)
   Surviving evidence: λ ORDERING predicts over-prediction independently in
   both datasets (ρ −0.714, −0.517). Pad CONTACT was then tested and also
   fails: `plasticity_index`/`pad_limited_plasticity_lambda` are constant
   within each dataset (consumable properties) and differ between them the
   WRONG way (inverting set is MORE plastic ⇒ predicts more removal), while
   `summit_saturation` = 0.00739·P exactly — down force relabelled. Its clean
   separation (0.0111 inverting vs ≥0.0148) is therefore just "P < 2 psi"
   fitted to one patent's low-force arm. Twice now the candidate criterion was
   the operating point in disguise (λ=V/p, saturation=P).
   NEEDED: pad surface stats (asperity density/radius by confocal or AFM, or
   glazing state) measured beside a rate-vs-speed sweep. Nothing in the corpus
   reports them.
2. `sti_ceria` absolute scale — **CLOSED 2026-09-26.** Diagnosed: the pack's
   Kp was the wrong one of the two cited sources. The inherited 2.2e-13 m/Pa
   was `confidence: estimated`, self-described as a representative,
   unreproduced value, and never back-calculated from any measured run. All
   FOUR absolute-comparable ceria datasets implied a LOWER Kp (one-sided, not
   scatter): kenchappa2021 8.4e-14, netzband2020 7.6e-14, mariscal2020
   1.34e-13, son2021 1.64e-13 → geometric mean **1.09e-13 m/Pa**, LOO range
   9.5e-14–1.23e-13. Re-anchored. examples/sti_ceria.yaml now returns
   **1,559 Å/min**, inside the 200–6,000 envelope. Residual scales moved to
   0.70–1.51x (were 0.35–0.75x). The two ceria-COATED-silica composite
   datasets imply ~2.3e-14 and were EXCLUDED, not averaged in — a ceria shell
   on a silica core is a different abrasive; that disagreement stays open and
   visible (their scale is now 0.19x/0.24x). Guarded by
   tests/test_ceria_kp_backed_out_of_four_datasets.py, which re-derives the
   number from the scorer and asserts no shape score moved.
3. Size exponent splits by ABRASIVE, not film; packs must scope and cite it.
4. P3 exponents still `unverified` — no nanoindentation of a CMP-polished
   surface exists in the corpus.
5. SnAg has no published Preston coefficient (Archard ranking only); SiC
   inherits SiO₂'s modulus — `null` + TODO(owner).
6. Three judgement calls kept as compromises over flattering per-dataset fits.

## VALIDATION
| dataset | n | MAPE | verdict |
|---|---:|---:|---|
| US9499721B2 TEOS/silica | 4 | 1.9% | pass |
| US8142675B2 Pt/alumina | 4 | 12.3% | pass |
| US6564116B2 oxide L25 | 5 | 12.6% | pass |
| Mariscal 2020 PETEOS/ceria | 9 | 12.9% | pass |
| Wang SiC DOE50 | 6 | 31.9% | **kept failing** — chemically limited |
| US6918821B2 Cu/IC1000 | 6 | 44.1% | **kept failing** — lubrication transition |

Gate: 4 in-scope datasets within ±15% (need 3) → **PASS**

All axes (427 pts, 46/50 scored + 4 DECLINED): median **19.5%** trend,
**21.8%** LOO. By axis — size 11.2%, oxidizer 21.3%, loading 22.4%,
pressure 24.1%, pH 25.3%, velocity 39.0%. 35/46 beat predict-the-mean.
⚠ Caveats, all against us: the axis
medians pool datasets that vary several things at once — velocity's 39.0% is
11.7% once isolated (thin axis, 29 pts), while pH's holds up under isolation
(12 groups / 66 pts, ~30%) so it IS the weakest term. Cu datasets are
DECLINED rather than answered wrongly (honesty, not accuracy). The pH axis
moved 29.1 -> 26.8% only because a NEW dataset entered below the median, not
because any prediction improved.
Resume handover: `~/CMP-SIM-FOR-RESUME.md`
