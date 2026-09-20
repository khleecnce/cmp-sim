<!-- V2-SECTION: R4-disk | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: conditioning, 다이아, 컨디셔너 | 정본: ARCHITECTURE-V2.md §3 -->
# 그루브 마모에 따른 유동 특성 변화와 패드 수명 판정

> pad-structure Lv2-2 | 작성일: 2026-09-08
> [[pad-groove-slurry-transport]](Lv1-1, GFQ 정의) · [[pad-groove-geometry-contact-area-flow-resistance]](Lv1-2, Mu 2016 반응기 부피·MRT)
> · [[pad-subpad-stiffness-edge-nonuniformity]](Lv2-1) · [[pad-thickness-groove-depth-monitoring-replacement-economics]](pad-lifecycle Lv2-2,
> 그루브 깊이 **측정·교체 경제성**) · [[pad-conditioning-wear-regeneration-balance]](컨디셔닝 마모율) · [[cmp-slurry-flow-lubrication-film-thickness]] 상호링크.
> 조사범위: `tools/scope.py --agent pad-structure`(2011년 이후 우선, 1차 논문·특허). 형제 노트(pad-lifecycle)가
> "깊이를 어떻게 재고 언제 바꾸는가(경제성)"를 다뤘으므로, 이 노트는 **깊이가 줄면 슬러리 유동이 어떻게
> 바뀌는가(물리)** 와 **유동 관점의 수명 판정 기준(잔존 깊이·잔존 부피 비율)** 에 집중한다.

## 1. 문제 설정 — 그루브 깊이는 컨디셔닝으로 단조 감소하는 "소모 변수"

그루브 폭·피치는 패드 수명 내내 거의 그대로지만(컨디셔너는 land 표면을 깎으므로 폭은 안 변함), **깊이 D는
컨디셔닝 마모(패드 컷레이트)만큼 매 웨이퍼마다 줄어든다.** Lv1-2에서 정량화한 GFQ=W/P(폭/피치)는 수명 내내
불변이고, 변하는 것은 그루브 단면적(W·D)·저류 부피(V_groove ∝ D)·채널 유동 컨덕턴스(∝ D³급)다. 따라서
"그루브 마모 → 유동 변화"는 사실상 **깊이 D 하나의 함수**로 환원된다.

두 1차 문헌이 이 관점을 직접 채택한다:

- **Liu, Kang, Oh, Jeon, Lee, Wang, Jeong, Lee, Kim (성균관대·SK, 2024), "Investigating the Impact of Pad Groove Depth
  Reduction on Process Variation in Oxide Chemical Mechanical Polishing", *ECS J. Solid State Sci. Technol.*,
  doi.org/10.1149/2162-8777/ad83ef.** Bronze OA로 표시되나 IOP 서버가 Radware 캡차로 봇을 차단해 PDF·HTML 본문 확보
  실패(미러 사이트 미러 5종 전부 캡차/무응답, Wayback·fatcat·CORE에 사본 없음) — **초록만 확인**. 초록 내용: 다이아몬드
  컨디셔너 마모로 약 20시간 사용 동안 그루브 깊이가 줄고, 유동 시뮬레이션에서 **t=0.51 s 시점 신선 슬러리 질량분율이
  그루브 깊이 850 μm에서 72.34% → 250 μm에서 100.00%로 증가**. 초기 깊이 250/500/750/850 μm 패드로 산화막 연마 실험;
  일반적으로 **얕은 그루브 패드는 제거율은 높지만 WIWNU는 나쁘다**. 패드 표면 최대온도를 보조 지표로 기록.
- **Irfan, Lee, Muzumdar, Aryanfar, Wu (국립성공대, 2025), "Improvement of Material Removal Rate and Within Wafer
  Non-Uniformity in Chemical Mechanical Polishing Using Computational Fluid Dynamic Modeling", *J. Manuf. Mater. Process.*
  9(3), 95, doi.org/10.3390/jmmp9030095.** MDPI CC-BY, mdpi-res.com CDN에서 PDF 원문 전체 확보
  (`papers/irfan2025-jmmp-cfd-groove-depth-lifetime.pdf`, PyMuPDF로 21쪽 전문 확인). ANSYS Fluent VOF+DPM 3D CFD.
  §2.3: 그루브 폭 w=0.5 mm, 깊이 d=0.75 mm, 피치 p=3 mm, 패드-웨이퍼 간극 0.1 mm, **"수명 말기 그루브 깊이는 0.5 mm
  낮아진 0.25 mm"** 로 정의하고 d=0.75/0.50/0.25 mm 세 단계로 벽면 전단응력·유선을 비교(Fig. 9, 10a, 10b).

## 2. 깊이 감소가 유동에 미치는 세 가지 효과 (문헌 + 형제 노트 결합)

### 2.1 저류(hold-up) 부피 감소 → 체류시간 단축 → 슬러리 교체가 **빨라진다**

Lv1-2 노트의 Mu et al.(2016, doi.org/10.1016/j.mee.2016.02.035, `papers/mee-2016-mu-groove-width-residence-time.pdf` 원문)
반응기 모델: MRT τ = V_total/q_actual, V_total = V_land + V_groove. 논문 Table 2(3 PSI, 필름두께 15 μm 가정)의
V_groove는 2.66/4.41/5.64 cm³(Pad A/B/C)로 V_land(0.38/0.31/0.27 cm³)의 7.0~20.9배 — 논문 본문 그대로
"h_groove(400 μm) ≫ h_land(10–15 μm)이므로 V_groove가 지배적". 그루브 깊이가 400→250 μm로 줄면 V_groove는 비례해
0.625배가 되고, q_actual이 같다면 τ도 거의 그 비율로 짧아진다(§5 verify D 투영: Pad A 3 PSI τ 9.2 s → 약 6.2 s,
**자체 계산·미검증**).

이것이 Liu 2024 초록의 "깊이 850→250 μm에서 신선 슬러리 분율 72.34%→100%"와 **같은 방향**이다: 얕은 그루브일수록
갈아 끼워야 할 묵은 슬러리 부피가 작아 교체가 빠르다. §5 verify B에서 1차 혼합(CSTR, τ ∝ V_groove ∝ D) 가정만으로
850 μm의 72.34%를 앵커 삼아 250 μm를 외삽하면 98.7%가 나온다 — 문헌 100.00%와 1.3%p 차이(정합이지만 완전 일치는
아님; 100.00%를 정확히 맞추려면 τ ∝ D^1.7 정도의 더 급한 스케일링이 필요 — 이는 부피뿐 아니라 채널 컨덕턴스(§2.3)까지
바뀐다는 뜻으로 해석, **모델 해석이며 미검증**).

역설적 귀결: "슬러리 교체가 빨라진다"는 것은 **반응기 관점에서는 이점**이고 Liu 2024가 얕은 패드에서 제거율이 높다고
보고한 것과 부합한다. 그런데도 얕은 패드가 수명 말기인 이유는 §2.2·§2.3 때문이다.

### 2.2 슬러리 분배 불균일 → WIWNU 악화 (Irfan 2025 CFD, Liu 2024 실험 초록, Park 2008 실험 초록)

Irfan 2025 §2.3·§3.2(원문): 깊이가 0.75→0.25 mm로 줄면 "패드가 웨이퍼 전면에 슬러리를 붙들어 분배하는 능력이 떨어지고",
"수명 말기에는 연마액이 **웨이퍼 중심 쪽으로 더 이상 흐르지 않는다**"(원문 p.10). 벽면 전단응력은 d=0.75 → 0.50 →
0.25 mm로 갈수록 감소(Fig. 9→10a→10b, 논문은 등고선 그림만 제시하고 **수치표는 없음** — 크기는 미검증). 논문이 쓴
전단응력식은 "τ = μ/h"로 인쇄돼 있는데(p.10) 차원이 맞지 않으며 뉴턴 유체 Couette 관계 τ = μV/h의 오기로 판단(자체 판단).

Liu 2024 초록: 얕은 그루브 패드는 WIWNU가 나쁘다(정량치는 본문에 있어 미확보). Park, Oh, Jeong(부산대, 2008), "Pad
Characterization and Experimental Analysis of Pad Wear Effect on Material Removal Uniformity in CMP", *Jpn. J. Appl.
Phys.* 47, 7812, doi.org/10.1143/jjap.47.7812 (**초록만 확인**, 유료): 접촉식 프로파일러로 매 런 후 패드 프로파일을
측정, "컨디셔닝으로 마모된 패드에서 WIWNU가 악화"됐다고 보고 — 그루브 깊이만 분리한 실험은 아니지만(패드 두께
프로파일 전체 마모) 방향은 일치.

세 문헌의 공통 메시지: **깊이 감소는 평균 유량(§2.1)보다 유량의 공간 분포(중심부 공급 부족)를 먼저 망가뜨린다.**
이 때문에 유동 관점의 수명 종료 신호는 "MRR 저하"가 아니라 "WIWNU 상승·중심부 결핍·온도 상승"으로 나타난다.

### 2.3 채널 컨덕턴스 급감 — 깊이의 3승급 (자체 유도, 문헌 대조값 없음)

폭 w·깊이 d 직사각 채널의 압력구동(Poiseuille) 유량은 Q ∝ (w d³/12)·[1 − 192d/(π⁵w)·Σ tanh(nπw/2d)/n⁵] (짧은 변을
d로 취함; 표준 직사각 덕트 해). Irfan 2025 기하(w=0.5, d=0.75→0.25 mm)에 넣으면 d=0.25 mm의 컨덕턴스는 d=0.75 mm의
약 9.7%로, 깊이비(1/3)보다 훨씬 급하게 떨어진다(§5 verify E). 즉 그루브가 "슬러리를 웨이퍼 밑으로 밀어 넣는 배관"
으로서의 능력은 수명 말기에 한 자릿수 %로 줄어든다. 이것이 §2.2의 "중심부로 안 흐른다"의 정량적 배경으로 해석되나,
**CFD 논문이 컨덕턴스 수치를 주지 않아 대조 불가(미검증)**.

## 3. 수명 판정 — 유동 관점의 잔존 깊이·잔존 부피 기준 (특허 2건)

- **US8192257B2 (Micron Technology, "Method of manufacture of constant groove depth pads", 등록 2012;** freepatentsonline
  전문 확인. pad-lifecycle 노트가 인용한 공개출원 US20120225612A1과 같은 계열): "패드 수명(패드당 처리 웨이퍼 수)을 결정하는
  한 요인은 그루브 깊이 D다. 초기 깊이 D1≈250 μm(10 mil), 패드 마모 약 0.25 μm/wafer(0.01 mil/wafer)인 공정이면 수명은
  **약 600–800 wafers**에 그친다. 표준 두께 T1≈50–80 mil(1.3–2 mm) 패드에 더 깊은 초기 그루브를 주면 약 6000–8000
  wafers." 여기서 산술적 소진 한계는 250/0.25 = 1000 wafers인데 특허는 600–800이라 했으므로, **깊이가 0이 되기 전
  (잔존 50–100 μm, 초기의 20–40%)에 수명 종료**로 보는 셈이다(§5 verify A).
- **US11938584B2 (CMC Materials/Cabot Microelectronics, "Chemical mechanical planarization pads with constant groove volume",
  등록 2024;** freepatentsonline 전문 확인): "종래 패드는 그루브 높이(따라서 부피)의 **약 80%만 사용 가능**하며 그 뒤
  CMP 성능이 급락한다"; "그루브 부피가 초기 부피의 **20% 미만**으로 얕아지면 (예: 과열 때문에) 결과가 나빠지기 시작해
  WIWNU 증가·결함밀도 증가로 이어진다"; 반대로 너무 깊은 그루브는 "slurry starving"(그루브에 슬러리를 다 뺏겨 표면 공급
  부족). 즉 **잔존 부피비 20%가 하한, 과대 부피는 상한**으로, 유동 관점의 수명 창(window)이 양쪽에서 닫힌다.

두 특허의 기준은 서로 독립인데 정량적으로 맞물린다: Cabot의 "80% 사용 가능"을 Micron 수치에 넣으면 0.8×250/0.25 =
**800 wafers = Micron이 말한 600–800의 상한**(§5 verify A). Liu 2024·Irfan 2025가 수명 말기 깊이를 250 μm로 잡은 것은
초기 850/750 μm의 29%/33% 잔존 — Cabot 하한(20%)보다 조금 이르다. 종합하면 **유동 관점 교체 기준 = 잔존 깊이 ≈
초기의 20–33%**, 그리고 그 근거는 MRR이 아니라 WIWNU·결함·온도(§2.2)다.

**정직한 불일치 기록**: Micron 특허(US8192257B2)의 "표준 패드 6000–8000 wafers"에 같은 0.25 μm/wafer를 곱하면 누적 마모 1.5–2.0 mm로,
특허 자신이 말한 패드 두께(1.3–2 mm) 전체이자 형제 노트가 확보한 통상 초기 그루브 깊이(0.75–1.25 mm)를 넘는다. 즉 그
수치는 "그루브 깊이 소진" 기준으로는 재현되지 않으며(§5 verify A에서 불일치를 assert로 기록), 다른 마모율이나 다른
종료 기준을 전제한 것으로 보인다 — **미해결·미검증**.

## 4. 이 에이전트의 종합 — 수명 내 유동 상태 3단계 (모델 제안, sim 구현은 PROFILE "구현 요청")

| 단계 | 잔존 깊이비 D/D0 | 지배 현상 | 유동 신호 | 근거 |
|---|---|---|---|---|
| 초기 | 1.0–0.7 | V_groove 큼, 긴 τ, (과대 시 slurry starving) | 교체 느림, 분배 균일 | Mu 2016 Table 2, US11938584 |
| 중기 | 0.7–0.35 | τ 단축, 컨덕턴스 ∝D³급 감소 시작 | 교체 빨라짐, 분배 아직 유지 | Liu 2024 초록, Irfan 2025 Fig.10a |
| 말기 | <0.35 (Liu·Irfan 0.29–0.33, Cabot 0.20, Micron 0.2–0.4) | 컨덕턴스 <10%, 중심부 공급 부족 | WIWNU↑, 온도↑, 결함↑ | Irfan 2025 p.10, US11938584, US8192257 |

Lv3-2(sim/tier2) 구현 시 필요한 최소 파라미터: D0, 컷레이트(μm/h 또는 μm/wafer, [[pad-conditioning-wear-regeneration-balance]]),
GFQ(불변), 필름두께 h_land, q_actual. 출력: τ(D), 컨덕턴스비 G(D)/G(D0), 잔존비 D/D0 → 3단계 플래그.

## 5. 정량 재현 (python verify)

재현 요약(한 줄): (US8192257B2) 250 μm/0.25 μm·wafer⁻¹=1000 wafers 산술한계 vs 특허 600–800 → 잔존 20–40%에서 종료, (US11938584B2) 80% 사용 기준 대입 시 800 wafers로 Micron 상한과 일치; (Liu 2024, doi.org/10.1149/2162-8777/ad83ef) CSTR·τ∝D 외삽 98.7% vs 초록 100.00%(1.3%p 차); (Irfan 2025, doi.org/10.3390/jmmp9030095) SST 오차 첫 쌍 3.30% vs 논문 3.33% 재현, 둘째 쌍 2.05% vs 논문 3.35% **재현 실패**; (Mu 2016, doi.org/10.1016/j.mee.2016.02.035) Table 2 V_total=V_land+V_groove 6/6, V_land 기하 재현 ≤3%, V_groove 4.7–5.8% 잔차.

```python verify
import math

# ── (A) US8192257B2 (Micron) 그루브 깊이 수명 산술 × US11938584B2 (Cabot) 80%/20% 기준 교차
D1_um = 250.0            # 초기 그루브 깊이, US8192257B2 원문 "about 250 μm (about 10 mil)"
wear_um_per_wafer = 0.25 # US8192257B2 원문 "about 0.25 μm/wafer (about 0.01 mil/wafer)"
life_lo, life_hi = 600, 800   # US8192257B2 원문 "only about 600-800 wafers"
N_full = D1_um / wear_um_per_wafer
assert abs(N_full - 1000) < 1e-9, "산술 소진 한계 1000 wafers"
remain_hi = D1_um - life_lo * wear_um_per_wafer   # 600장 시점 잔존 깊이
remain_lo = D1_um - life_hi * wear_um_per_wafer   # 800장 시점 잔존 깊이
assert (remain_lo, remain_hi) == (50.0, 100.0)
frac_lo, frac_hi = remain_lo / D1_um, remain_hi / D1_um
assert abs(frac_lo - 0.20) < 1e-9 and abs(frac_hi - 0.40) < 1e-9, "특허 수명은 잔존 20-40%에서 종료를 뜻함"
usable_frac_cabot = 0.80   # US11938584B2 원문 "only about 80% of a groove height ... is useable"
N_cabot = usable_frac_cabot * D1_um / wear_um_per_wafer
assert life_lo <= N_cabot <= life_hi and N_cabot == life_hi, "Cabot 80% 기준 → 800 wafers = Micron 상한"
print(f"[A] 산술한계 {N_full:.0f}, Micron 600-800 → 잔존 {remain_lo:.0f}-{remain_hi:.0f} μm ({frac_lo:.0%}-{frac_hi:.0%}); "
      f"Cabot 80% 기준 → {N_cabot:.0f} wafers (Micron 상한과 일치)")
# 불일치 기록: 표준 패드 6000-8000 wafers × 0.25 μm = 1.5-2.0 mm > 통상 초기 그루브 깊이 상한 1.25 mm(형제 노트, US20120225612A1)
std_lo, std_hi = 6000, 8000
cum_lo, cum_hi = std_lo * wear_um_per_wafer, std_hi * wear_um_per_wafer
assert cum_lo > 1250, "6000-8000 wafers는 같은 마모율로는 그루브 깊이 소진 기준으로 재현되지 않음 — 미해결로 기록"
print(f"[A'] 표준패드 6000-8000 wafers × 0.25 μm = {cum_lo/1000:.1f}-{cum_hi/1000:.1f} mm 누적마모 → 그루브 깊이(≤1.25 mm) 초과, 불일치 명시")

# ── (B) Liu 2024 초록: 신선 슬러리 분율 72.34%(850 μm) → 100.00%(250 μm) @ t=0.51 s — 1차 혼합(CSTR) τ∝V_groove∝D 외삽
t_s = 0.51; f_850 = 0.7234; f_250_lit = 1.0000
tau_850 = -t_s / math.log(1 - f_850)          # f = 1 - exp(-t/τ) 역산
tau_250 = tau_850 * 250 / 850                  # 저류 부피 ∝ 깊이 (Mu 2016: V_groove 지배)
f_250 = 1 - math.exp(-t_s / tau_250)
assert 0.98 < f_250 <= 1.0, f"CSTR·선형 부피 스케일링 외삽 {f_250:.4f}가 문헌 100%와 자릿수 다름"
gap_pp = (f_250_lit - f_250) * 100
assert gap_pp < 2.0, "1.3%p 안팎의 차이여야 함"
# 100.00%(≥99.995%로 해석)를 정확히 맞추려면 필요한 깊이 스케일링 지수 n (τ ∝ D^n)
tau_need = t_s / math.log(1 / (1 - 0.99995))
n_need = math.log(tau_need / tau_850) / math.log(250 / 850)
print(f"[B] τ(850)={tau_850:.3f}s → τ(250)={tau_250:.3f}s → f(250)={f_250:.4f} (문헌 1.0000, 차 {gap_pp:.2f}%p); "
      f"100.00% 정확 일치에는 n≈{n_need:.2f} 필요(선형 1보다 급함) — 모델 해석, 미검증")

# ── (C) Irfan 2025 초록: SST 실험 21.52/16.06 s vs 시뮬 22.23/15.73 s, 논문 표기 오차 3.33%/3.35%
sst_exp = (21.52, 16.06); sst_sim = (22.23, 15.73); err_lit = (3.33, 3.35)
err_calc = [abs(s - e) / e * 100 for e, s in zip(sst_exp, sst_sim)]
assert abs(err_calc[0] - err_lit[0]) < 0.1, "동심원 패드 SST 오차 3.30% ≈ 논문 3.33%"
assert abs(err_calc[1] - err_lit[1]) > 1.0, "방사형 패드 SST 오차는 2.05%로 논문 3.35%와 불일치 — 재현 실패를 기록"
print(f"[C] SST 오차 계산 {err_calc[0]:.2f}%/{err_calc[1]:.2f}% vs 논문 {err_lit[0]}%/{err_lit[1]}% → 첫째 재현, 둘째 불일치(논문 표기 오류 추정)")

# ── (D) Mu 2016 Table 2 (3 PSI 필름 15 μm / 5 PSI 10 μm, 200 mm 웨이퍼, 깊이 400 μm) 재현 + 깊이 250 μm 투영
table2 = {  # pad: (P, Vland3, Vgroove3, Vtotal3, Vland5, Vgroove5, Vtotal5) [cm3]
    'A': (0.38, 2.66, 3.04, 0.25, 2.63, 2.88),
    'B': (0.31, 4.41, 4.72, 0.21, 4.35, 4.56),
    'C': (0.27, 5.64, 5.91, 0.18, 5.57, 5.75)}
gfq = {'A': 300 / 1500, 'B': 600 / 1800, 'C': 900 / 2100}
A_w = math.pi * 0.100 ** 2  # m2, 200 mm 웨이퍼
for pad, (vl3, vg3, vt3, vl5, vg5, vt5) in table2.items():
    assert abs(vl3 + vg3 - vt3) < 0.011 and abs(vl5 + vg5 - vt5) < 0.011, f"{pad}: V_total = V_land + V_groove"
    for film, vl, vg in ((15e-6, vl3, vg3), (10e-6, vl5, vg5)):
        vl_calc = (1 - gfq[pad]) * A_w * film * 1e6
        vg_calc = gfq[pad] * A_w * 400e-6 * 1e6
        assert abs(vl_calc - vl) / vl < 0.03, f"{pad} V_land 기하 재현 ≤3%"
        resid = abs(vg_calc - vg) / vg
        assert 0.03 < resid < 0.07, f"{pad} V_groove 잔차 4.7-5.8% — 완전 일치 아님을 기록"
    assert vg3 / vl3 >= 6.9, "V_groove ≫ V_land, 7.0~20.9배 (논문 본문 '지배적')"
# 투영: Pad A 3 PSI, 깊이 400→250 μm, q_actual 불변 가정 → τ 9.2 s → ?
tau_A3 = 9.2; vl, vg, vt = table2['A'][:3]
tau_250 = (vl + vg * 250 / 400) / vt * tau_A3
assert 6.0 < tau_250 < 6.4
print(f"[D] Mu Table 2 합 6/6, V_land ≤3%, V_groove 잔차 ~5%; 깊이 400→250 μm 투영 τ {tau_A3} → {tau_250:.2f} s (자체 계산, 미검증)")

# ── (E) 직사각 채널 Poiseuille 컨덕턴스 (Irfan 2025 기하 w=0.5 mm, d=0.75→0.50→0.25 mm) — 자체 유도, 문헌 대조값 없음
def cond(w, h):
    if h > w: w, h = h, w
    s = sum(math.tanh(n * math.pi * w / (2 * h)) / n ** 5 for n in range(1, 199, 2))
    return w * h ** 3 / 12 * (1 - 192 * h / (math.pi ** 5 * w) * s)
g0 = cond(0.5, 0.75); r50 = cond(0.5, 0.50) / g0; r25 = cond(0.5, 0.25) / g0
assert r25 < r50 < 1 and r25 < 0.25 / 0.75, "깊이비(1/3)보다 급하게 감소"
assert 0.09 < r25 < 0.11 and 0.45 < r50 < 0.50
print(f"[E] 컨덕턴스비 d=0.50: {r50:.3f}, d=0.25: {r25:.3f} (깊이비 0.667/0.333보다 급감) — 자체 유도")
```

## 6. 미검증·한계 표기 (정직성)

- Liu 2024는 **초록만** 확인(IOP Radware 캡차·미러 전멸). 본문의 RR·WIWNU·결함·온도 표, 컷레이트, CFD 조건은 미확보 —
  §2.1의 CSTR 외삽은 초록 두 숫자에만 기댄 모델 해석이다.
- Irfan 2025는 원문 전체를 읽었으나 **깊이별 전단응력·질량분율의 수치표가 없다**(등고선 그림만). "감소한다"는 방향만
  채택. SST 오차 3.35% 표기는 재현되지 않았다(Irfan 2025, §5 C).
- Park 2008(JJAP)은 초록만. 그루브 깊이와 두께 프로파일 마모를 분리하지 않았다.
- §2.3 컨덕턴스 D³급 스케일링과 §4 3단계표는 **이 에이전트의 모델 제안**이며 문헌 대조값이 없다.
- Micron 특허의 6000–8000 wafers는 같은 마모율로는 재현되지 않는다(§3, §5 A').
- 회사 데이터 미사용. 모든 수치는 공개 특허·논문 원문/초록.

## 7. 출처 요약 (한 줄 형식)

- Irfan, H.M.; Lee, C.-Y.; Muzumdar, D.; Aryanfar, Y.; Wu, W. (2025), "Improvement of Material Removal Rate and Within Wafer Non-Uniformity in Chemical Mechanical Polishing Using Computational Fluid Dynamic Modeling", *J. Manuf. Mater. Process.* 9(3), 95, doi.org/10.3390/jmmp9030095 — CC-BY 원문 전체(1차, CFD).
- Liu, P.; Kang, C.; Oh, S.; Jeon, S.; Lee, H.; Wang, Z.; Jeong, H.; Lee, E.; Kim, T. (2024), "Investigating the Impact of Pad Groove Depth Reduction on Process Variation in Oxide Chemical Mechanical Polishing", *ECS J. Solid State Sci. Technol.*, doi.org/10.1149/2162-8777/ad83ef — 초록만(1차, 실험+CFD).
- Mu, Y. et al. (2016), "Effect of pad groove width on slurry mean residence time and slurry utilization efficiency in CMP", *Microelectron. Eng.* 157, 60–63, doi.org/10.1016/j.mee.2016.02.035 — 원문 전체(1차, Lv1-2에서 확보).
- Park, K.-H.; Oh, J.-H.; Jeong, H. (2008), "Pad Characterization and Experimental Analysis of Pad Wear Effect on Material Removal Uniformity in Chemical Mechanical Polishing", *Jpn. J. Appl. Phys.* 47, 7812, doi.org/10.1143/jjap.47.7812 — 초록만(1차).
- US8192257B2, Micron Technology, "Method of manufacture of constant groove depth pads" (등록 2012) — freepatentsonline 전문(특허).
- US11938584B2, CMC Materials, "Chemical mechanical planarization pads with constant groove volume" (등록 2024) — freepatentsonline 전문(특허).

## 8. 자기시험

→ [[../../agents/pad-structure/EXAMS.md]] Lv2-2 문항(Q10–Q12) 참조.
