# legacy 2차 이관 — 2026-09-20 18:36 · fab-sim cb7d7bf

1차(09-15 18:54) 이후 fab-sim 199커밋분. 격자 49/50, 테스트 139파일.

## 이번에 추가된 것
- knowledge/{cmp,materials,equipment}/ 연구 노트 전체(257편) — 파라미터의 "왜"
- validation/MODEL-BASIS.md 근거 보고서(자동 생성물), RESULTS.md, ledger.jsonl(QA 원장 #1~), completion_last.json
- COMPLETION.md(완성 기준 C1~C8), ARCHITECTURE-V2.md, EVIDENCE-RULES.md 최신(판정 #38까지)
- tools/: completion.py·qa_loop.py·accuracy_gaps.py·check_knowledge.py·verify_claims.py — **그대로 실행**(legacy/ 기준 경로로 돌리려면 ROOT 조정 필요)
- tests/ 전체 — 기준 1.0 계약·ParamMissing·격리 규칙이 코드로
- papers/*.txt — QA 감사 F1이 대조하는 원문(PDF 제외)

## 이관 안 한 것
- 3D UI(sim/web/studio3d.html), 크론 프롬프트(agents/), 코퍼스 DB(data/corpus 173MB), 논문 PDF(678MB), 런 DB
- 비공개 데모: https://fabsim-demo.vercel.app (토큰 ~/.fabsim-demo-token, deploy/demo/sync.sh) — fab-sim 트리 그대로 유지
