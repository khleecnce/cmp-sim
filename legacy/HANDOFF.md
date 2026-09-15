# FabSim 상속 패키지 — 다른 프로파일에서 즉시 적용

> 이 파일 하나를 새 프로파일의 첫 메시지에 붙이거나 `AGENTS.md`에서 참조하면 된다.
> 원본 저장소: `~/fab-sim` (private, GitHub khleecnce/fab-sim). 이 문서는 2026-09-15 기준.

## 0. 30초 요약

CMP(화학기계연마) 시뮬레이터. 문헌(특허·논문)만으로 물리·화학 모델을 만들고, 문헌 held-out
데이터로 검증하며, 7개 크론이 자율로 갭을 채운다. **재직사 데이터 0건.**

| 지표 | 값 |
|---|---|
| 모델링 완성 격자 | **49/50** (10팩터 × 5재료계; 남은 1칸 + 9칸은 "문헌 부재 종결"로 정직 표기) |
| 테스트 | 767 collected, 전부 통과 |
| held-out 검증 | 26 데이터셋, 유의 7개 평균 Spearman ρ **+0.944**, 격리 1 |
| 문헌 코퍼스 | 8,960건 색인, 전문 1,526건 |
| 연구 노트 | 192편 (전부 출처 + 재현 verify 블록) |
| 비공개 데모 | https://fabsim-demo.vercel.app/?t=<토큰> (토큰 `~/.fabsim-demo-token`) |

## 1. 즉시 쓸 수 있는 산출물

| 무엇 | 경로 | 용도 |
|---|---|---|
| **근거 보고서** | `~/fab-sim/validation/MODEL-BASIS.md` | 팩터 10개의 모델 정의 근거 + 파라미터 도출 근거. 코드 docstring·팩 YAML에서 **자동 생성** — 손으로 안 씀. 자소서·면접 준비의 1차 자료 |
| 아키텍처 정본 | `~/fab-sim/ARCHITECTURE-V2.md` | 5파트(Tool/Slurry/Pad/Disk/Wafer) + 병합 파라미터 정의 |
| 완성 기준 | `~/fab-sim/COMPLETION.md` | C1~C8, 팩터 재정의 허용 규칙 |
| 검증 결과 | `~/fab-sim/validation/RESULTS.md`, `ledger.jsonl` | 데이터셋별 ρ/p/MAPE, 커밋별 추이 |
| 영어 데모 랜딩 | `~/fab-sim/sim/web/demo.html` | 팩터 표·검증 수치·**Honest limits** — 면접관용 문구 그대로 재사용 가능 |
| 증거 규칙 | `~/fab-sim/EVIDENCE-RULES.md` | confidence 등급(verified/literature/estimated/unverified) 판정 규칙, 판정 #1~#38 |

## 2. 10개 팩터 (한 줄씩 — 화이트보드 재현용)

MRR(r) = Kp · P(r) · V(r) · **κ · χ · ψ · τ** (기준 조건에서 전부 1.0). 나머지는 진단축.

| | 팩터 | 물리 | 1차 근거 |
|---|---|---|---|
| Λ | Mechanical load | Preston P·V, 헤드/플래튼 운동학, r_cc | Preston 1927 |
| Π | Load profile | 존 압력 → 반경별 하중 → WIWNU | 다중존 캐리어 특허 |
| Θ | Thermal/flow | 마찰열 vs 슬러리 냉각 → 패드 온도, Stribeck COF | Sundararajan 1999, Thakurta 2001 |
| Γ | Conditioning | 디스크 하중×스윕×duty, 그릿 노화 τ=27h | Kwon 2013, Tsai 2014 |
| κ | Contact | 입자 C^(1/3), Shore D, asperity 밀도 | 표면적 지배 접촉 모델 |
| χ | Chemical reactivity | **연마재별 pH 항**: 실리카 pH 11 정점 / 세리아 IEP 창 2.5<pH<6.8; Langmuir 산화제(자유 파라미터 1개) | Li 2021, Dandu 2009, Kaufman 1991 |
| ψ | Adsorption shield | 금속 부동태(BTA)에서 **표면 흡착 보호로 확장**: SiN Hill형 억제, 실리카/산화막은 "검증된 영" | Kim 2003, Penta 2013 |
| τ | Transport | 그루브 폭(비단조)·기공률 → 슬러리 전달 | Mu 2016, Prasad 2013 |
| Δ | Damage | (D99/D99_ref)^n × 응집; 임계 680nm; Eusner 스크래치 치수 상한 | Hitachi US8439995, Remsen 2006, Eusner 2009 |
| S | Stability | 글레이징↔컨디셔닝 정상상태 R_ss=k_c·G/(k_g+k_c·G); **실장비 PHM2016 드레서-MRR ρ 0.70 재현** | Jeong 2022/2024, Lawing 2004 |

## 3. 면접에서 반드시 먼저 말할 한계 (숨기면 무너진다)

- **순위 예측이지 절대값이 아님.** Kp가 문헌 한 점에서 역산돼 레짐 벗어나면 40배 틀림(실리카 pH 11 캘리브 → pH 4.7). 절대값은 사용자 실측 ≥3건 → Kp 보정으로만.
- 코드 상당 부분이 AI 에이전트 산출. **본인 결정** = 팩터 설계, "출처 없는 숫자 금지"(`ParamMissing`), held-out/순열검정/퇴보 게이트/가짜데이터 감사 규율. 이건 설명 가능해야 함.
- 클리닝 물리 없음(시각화만), 입자 형상·D10/D90 기록만, 모터 K_t 비공개라 전류 미산출.
- 테슬라·퀄컴은 팹리스 — CMP 내용이 아니라 **"공정 물리를 검증 가능한 SW로 만들고 자율 파이프라인으로 운영"** 프레임으로. 테슬라는 SiC 팩(`sic_ceria_h2o2`) 각도, 퀄컴은 Foundry/Process Integration 각도.

## 4. 엔지니어링 규율 (다른 프로젝트에도 그대로 이식 가능)

1. **출처 없는 숫자 금지** — 파라미터마다 value/unit/source/confidence, 없으면 즉사. CI 강제.
2. **held-out** — 피팅에 쓴 데이터셋 `used_for_calibration: true`로 채점 제외. 유의성은 순열검정(n=3 ρ=1.0은 p=0.17, 안 셈).
3. **퇴보 게이트** — 매 변경 전 데이터셋 재실행, 유의 데이터셋 ρ 0.05↓ 또는 유의→비유의면 커밋 차단. 실제로 그럴듯한 모델(D^-1.5 입경 항, p 0.0007→0.76)을 기각한 전례.
4. **가짜 데이터 감사** — 원문 대조(특허 표·PMC XML), 등차수열·자기채점·"너무 완벽한" 디지타이즈 격리. 해제는 사람만.
5. **근거 보고서 자동 생성** — 문서가 코드와 어긋날 수 없음.
6. **위임 결과 자기보고는 이수로 안 셈** — 총괄이 검증기 직접 실행.

## 5. 운영 교훈 (재발 방지 — 다른 프로파일 크론 설계 시 그대로 적용)

- **API 한도 공유**: 서브에이전트 병렬 3 + 크론 7 = Anthropic 429 → 전부 사망. 위임은 **1개씩 직렬**, 큰 도구 호출 소수로.
- **`hermes gateway restart`는 실행 중 delegate_task를 죽인다.** 위임 중 재시작 금지.
- **동반 변경 누락**: 크론이 `git add <명시 경로>`로 테스트만 커밋 → 로컬 통과, CI 실패. `.githooks/pre-push`가 HEAD를 클린 export해 검사. 새 clone은 `git config core.hooksPath .githooks`.
- **GitHub Actions 과금**: private 저장소 무료 2000분/월. 크론 push 65%가 문서만인데 `on: [push]`로 전부 돌아 한 달 만에 소진 → 결제 차단 → 이후 모든 run "payments failed"(테스트 실패 아님). 트리거 `paths` 한정 + `concurrency: cancel-in-progress` + 품질 게이트 주 1회.
- **Vercel 자동연결 금지**: `vercel link`가 저장소 전체를 물어 크론 push마다 빌드 실패 알림. 데모는 `deploy/demo/sync.sh && vercel deploy --prod` 수동만.
- **Google Patents 직접 접속은 503 잦음** — 코퍼스 fetch는 PMC→특허→OA URL 순(무료 전문 보장 순), 8/150 → 25/25.
- **위임 프로세스는 MCP(Exa) 상속 안 됨** — 서브에이전트엔 내장 검색만.
- **pH 항은 재료계별로 다르다** — 실리카 IEP 2.5 vs 세리아 6.8, 같은 항을 쓰면 부호까지 틀림.
- 검색은 Exa MCP(`web_search_exa`/`web_fetch_exa`, 키 불필요). Python은 반드시 `~/fab-sim/.venv/bin/python`.

## 6. 즉시 실행 명령

```bash
cd ~/fab-sim
.venv/bin/python tools/completion.py check          # 완성 격자 N/50 + 미충족
.venv/bin/python tools/completion.py report         # MODEL-BASIS.md 재생성
.venv/bin/python tools/qa_loop.py run --strict      # 퇴보 게이트
.venv/bin/python tools/accuracy_gaps.py --next      # 다음 갭 1건
.venv/bin/python -m pytest -q                       # 767 tests, ~200s
./fabsim.command                                    # 로컬 3D http://localhost:8848/3d
cd deploy/demo && ./sync.sh && vercel deploy --prod # 데모 갱신
```

## 7. 이 프로파일이 하지 않은 것 (다른 프로파일 몫)

- 자소서·이력서 문안 작성 (career 프로파일). 이 문서 §2·§3·§4가 재료.
- 코드 공개 — **하지 않기로 결정**(직무발명 리스크). 데모는 비공개 링크만.
- 실데이터 적용 — 사용자 실측 확보 후 `⑥ Data` 탭 업로드 → Kp 보정.
