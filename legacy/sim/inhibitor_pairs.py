"""억제제-기질 **쌍**의 흡착 자유에너지를 다룬다.

왜 이 파일이 필요한가
────────────────────
팩에는 `inhibitor_dG_ads_kJ` 가 하나뿐이었다. 억제제를 바꿔도 같은 값을 쓴다.
그 결과 한 억제제용 상수가 다른 억제제에 그대로 적용돼, 흡착상수가
5,700 배 어긋난 상태로 예측이 나왔다.

문헌이 말하는 것(knowledge/cmp/inhibitor-beyond-monolayer.md):

    ΔG_ads 는 "억제제의 성질"이 아니라 **"억제제 × 기질 쌍의 성질"**이다.
    같은 논문·같은 방법인데 값이 갈린다 — 기질이 다르면 다른 값이다.

따라서 이것은 계수 하나를 고치는 문제가 아니라 **입력 구조**의 문제다.
쌍을 키로 갖지 않는 한 새 억제제가 올 때마다 같은 실패가 반복된다.

무엇을 하는가
────────────
1) (억제제, 기질) 쌍을 키로 ΔG 를 조회한다. 쌍이 없으면 **거부**한다 —
   비슷한 값으로 대체하지 않는다. 그것이 지금까지의 실패 원인이었다.

2) 쌍이 없을 때 **R8(측정 명세)** 를 발행한다: "이 값을 이렇게 재 오시오."
   문헌에 없다고 멈추는 것도, 아무 값이나 넣는 것도 답이 아니다.

3) 등급을 함께 돌려준다. 다른 기질에서 이식한 값은 절대 verified 가 아니다.

⚠ 하지 않는 것
  · 쌍이 없을 때 유사 분자·유사 기질 값으로 대체 (이것이 5,700배 오차의 원인)
  · 데이터에서 ΔG 역산 (관측 3점으로 미지수 2개는 자유도 0 = 피팅)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

R_GAS = 8.314462618          # J/(mol·K)
WATER_MOLAR = 55.34          # mol/L — 물의 몰농도(표준상태 기준 변환용)

__all__ = ["PairDG", "lookup_dG", "K_from_dG", "measurement_spec", "PAIR_TABLE",
           "NO_ADSORPTION", "adsorption_ruled_out"]


@dataclass(frozen=True)
class PairDG:
    """(억제제, 기질) 쌍의 흡착 자유에너지."""
    inhibitor: str
    substrate: str
    dG_kJ_per_mol: float
    method: str
    source: str
    confidence: str
    notes: Tuple[str, ...] = field(default_factory=tuple)


# ──────────────────────────────────────────────────────────────
# 쌍 표 — 기질이 다르면 다른 줄이다. 이식하지 않는다.
#
# ⚠ 이 표에 값을 추가할 때 지켜야 할 규칙
#   1) 기질을 반드시 적는다. "BTA" 만으로는 줄을 만들 수 없다.
#   2) 측정법을 적는다. 다층 흡착일 때 Langmuir 절편에서 나온 값은
#      ΔG1(첫층)일 뿐 "그 억제제의 ΔG" 가 아니다(문헌 경고).
#   3) 다른 기질에서 가져온 값은 confidence 를 올리지 않는다.
# ──────────────────────────────────────────────────────────────
PAIR_TABLE: Dict[Tuple[str, str], PairDG] = {}


# ──────────────────────────────────────────────────────────────
# 이름 정규화 — 같은 물질이 두 이름으로 불려 쌍이 조용히 안 잡히는 것을 막는다
#
# 왜 필요한가: 산(malonic acid)과 그 음이온(malonate)은 같은 흡착종인데
# 문헌·데이터셋·팩이 서로 다른 이름을 쓴다. 표기가 다르다는 이유로 조회가
# 실패하면 **값이 있는데도 '미확보'로 보고**되고, 다음 회차가 이미 확보한
# 문헌을 다시 찾는다. 반대로 정규화를 남용하면 이식 금지 규칙이 무너지므로
# **같은 흡착종임이 확실한 산/염기 짝·표기 변형만** 넣는다.
# ⚠ 작용기가 다른 인접 분자(TTA↔BTA, succinate↔malonate)는 절대 넣지 마라.
# ──────────────────────────────────────────────────────────────
_INHIB_ALIAS = {
    "malonic": "malonate",          # 산 ↔ 그 음이온 (같은 흡착종)
    "malonic acid": "malonate",
    "benzotriazole": "bta",
    "2-mercaptobenzothiazole": "2-mbt",
}
_SUBST_ALIAS = {
    "oxide": "sio2",                # 검증 데이터셋 표기 ↔ 화학식
    "silica": "sio2",
    "tan": "ta",                    # TaN 배리어도 표면은 Ta 산화물이다
    "copper": "cu",
    "tungsten": "w",
}


def _key(inhibitor: str, substrate: str) -> Tuple[str, str]:
    i = inhibitor.strip().lower()
    s = substrate.strip().lower()
    return (_INHIB_ALIAS.get(i, i), _SUBST_ALIAS.get(s, s))


def register(p: PairDG) -> None:
    PAIR_TABLE[_key(p.inhibitor, p.substrate)] = p


# ── 쌍이 성질임을 보여주는 결정적 증거 ────────────────────────
# 아래 두 줄은 **같은 논문·같은 방법**인데 값이 8 kJ/mol 갈린다.
# 기질만 다르다. 이것이 "이식 금지" 규칙의 실측 근거다.
register(PairDG(
    "bta", "cu", -30.02, "전기화학(분극·EIS)+양자화학, Langmuir",
    "10.2320/matertrans.m2016310", "literature",
    ("K=3294.9 L/mol (모사 수돗물)",
     "같은 논문의 Fe 값과 8.13 kJ/mol 차 — 기질 의존의 직접 증거",),
))
register(PairDG(
    "bta", "fe", -21.89, "전기화학(분극·EIS)+양자화학, Langmuir",
    "10.2320/matertrans.m2016310", "literature",
    ("K=123.62 L/mol — Cu 대비 K 가 27배 작다",
     "⚠ 이 값을 Cu 에 쓰면 안 된다. 같은 논문이 두 값을 따로 보고했다.",),
))
register(PairDG(
    "bta", "cu-ni", -22.093, "중량법, Langmuir (35 °C)",
    "10.4067/s0717-97072010000100035", "literature",
    ("합금은 순금속과 다른 쌍이다",),
))
register(PairDG(
    "2-mbt", "cu", -5.59, "EQCM, Langmuir (R²=0.91–0.98)",
    "DOI 미확인 — 2차 인용", "unverified",
    ("⚠ 물리흡착 영역의 낮은 값 — 이런 크기도 실제로 보고된다",
     "EQCM 은 θ 를 직접 재므로 다층 판별이 가능한 방법이다",),
))
register(PairDG(
    "glycine", "cu", -39.8208,
    "전위동태 분극(Tafel) + Langmuir (K_ads=1.25e5 L/mol, R²=0.991), 30±0.5 °C",
    "10.5281/zenodo.5594539", "literature",
    ("Nandi, Biswas, Jain, Nandi, J. Indian Chem. Soc. 94, 369-380 (2017) "
     "— OA 전문(Zenodo 호스팅) 확보·직접 읽음, 원문 화합물 (1)=순수 글리신 "
     "(N-벤젠설포닐 유도체 (2)~(10)은 이식 금지 대상 — 등록하지 않았다)",
     "0.6 M NaCl 수용액, pH 6, 무산화제 — 이 팩(cu_h2o2_bta, pH 3, H2O2 존재)과 "
     "전해질·pH 다름. 원문 자신도 'at pH 6 ... glycine ... is found to be only "
     "10.1% (zwitter ion). glycine is good inhibitor in HCl/H2SO4 ... where it "
     "exists as protonated species' 라고 pH 의존성을 명시한다 — 부호(억제)는 "
     "교차 corroboration 있으나 크기는 pH 3 조건에 그대로 쓸 수 없다",
     "⚠ 교차확인: 같은 팩·같은 데이터셋(jani2025, doi:10.1149/2162-8777/adc59e, "
     "pH 3)이 독립적으로 '글리신은 억제제'라는 같은 방향을 확인했다(원문: "
     "'glycine functions as a dissolution inhibitor ... effectiveness is limited "
     "at low pH, where its predominantly protonated ... forms reduce its ability "
     "to complex with Cu2+'). 그러나 그 논문은 ΔG_ads(Langmuir)를 보고하지 않고 "
     "통제쌍 2점에서 역산한 지수형 계수(a=1.5119 /M, "
     "knowledge/cmp/psi-glycine-chelator-suppression-cu-jani2025.md)만 가진다 — "
     "이 줄의 값과 그 계수는 서로 다른 함수형·다른 측정법이라 대체하지 않는다",
     "⚠ 참고(등록 금지 — 인접분자): 같은 계열 유도체(bicine/tricine, N-치환 "
     "글리신) ΔG_ads ≈ -28~-32 kJ/mol(물리흡착); Lys-Glu-Asp-Gly 테트라펩타이드 "
     "ΔG_ads=-30.86 kJ/mol — 둘 다 곁사슬이 다른 인접 분자라 이 줄에 쓰지 않았다",),
))
register(PairDG(
    "malonate", "cu", -47.7,
    "in situ 엘립소메트리(θ 직접 환산) + full Temkin 등온식 (f=1.65)",
    "10.17675/2305-6894-2020-9-3-13", "literature",
    ("산화된 Cu 표면(E=0.0 V vs SHE) 기준 ΔG_a,max. CMP 는 산화제를 포함하므로 이쪽이 맞다",
     "환원 표면(E=-0.60 V)에서는 -38.3 kJ/mol — 산화막 유무로 9.4 kJ/mol 갈린다",
     "붕산염 완충 pH 7.40, 22±2 °C. 실제 Cu 슬러리(착화제 공존)에서는 경쟁흡착으로 더 약할 수 있다",
     "다층 아님: plateau + 두께 0.23 nm(분자 길이 미만) 로 평면배향 단층 확인 → 명백한 ΔG1",
     "⚠ Temkin ΔG_a,max 는 '가장 강한 사이트' 값이라 Langmuir 단일 ΔG 보다 체계적으로 더 음수다",
     "⚠ 같은 논문의 succinate(-77.4)·ethylmalonate(-69.4) 를 이 줄에 쓰지 마라 — "
     "같은 기질·같은 방법인데 K 가 10^5 배 갈린다(인접분자 이식 금지의 정량 근거)",),
))


# ──────────────────────────────────────────────────────────────
# 🚫 흡착이 일어나지 않는다고 **선언된** 쌍
#
# 왜 별도 표가 필요한가: `lookup_dG` 가 None 을 돌려주는 경우는 두 가지인데
# 지금까지 구분되지 않았다.
#   ① 아무도 안 쟀다        → 절대값 주장 금지, R8 측정 명세 발행
#   ② 그 메커니즘이 없다     → 억제 항이 없는 것이 **물리적으로 옳다**
# ②를 ①로 취급하면 다음 회차가 존재하지 않는 문헌을 계속 찾는다.
# 반대로 근거 없이 ②로 선언하면 억제를 조용히 0 으로 만드는 것이므로,
# 이 표에 들어오려면 **왜 흡착이 불가능한지**를 반드시 적어야 한다.
# ──────────────────────────────────────────────────────────────
NO_ADSORPTION: Dict[Tuple[str, str], str] = {
    ("bta", "ta"):
        "BTA 억제의 실체는 Cu(I)-BTA 중합착물이고 Ta 표면은 d0 인 Ta2O5 라 "
        "착물 상대가 없다. barrier CMP 에서 BTA 를 쓰는 이유 자체가 'Ta 는 두고 "
        "Cu 만 억제해 선택비를 얻기 위해서'이므로 흡착 부재가 공정 전제다.",
    ("benzenesulfonic", "sio2"):
        "SiO2 IEP ~2–3 이라 CMP pH 대역에서 표면이 음전하이고 설포네이트도 "
        "음이온이다 — 정전 반발. 흡착이 아니라 분산 안정화 방향으로 작용한다.",
    ("benzenesulfonic", "ta"):
        "Ta2O5 IEP ~2.7–3 으로 CMP pH 대역에서 음전하. 위와 같은 정전 반발.",
    ("malonate", "w"):
        "1차 문헌 2편(10.1557/PROC-477-115, S0927775724012974)이 W CMP 에서 "
        "말론산의 역할을 H2O2 안정화 + 알루미나/W 제타전위 조절(입자 오염 저감)로 "
        "규정한다 — 표면 흡착 억제제가 아니다. 이 축은 억제 항이 아니라 산화제 "
        "안정성·분산 항으로 다뤄야 하므로 쌍 등록 자체가 구조적으로 부적절하다.",
    ("oxalic", "cu"):
        "옥살산은 Cu CMP에서 표면 흡착 억제제가 아니라 **착화제(complexing agent)"
        "**로 작용해 Cu2+ 를 가용성 착물로 빼낸다 — 흡착이 아니라 정반대(용해 촉진) "
        "방향이다. jani2025(doi:10.1149/2162-8777/adc59e, CC-BY, 전문 확보·직접 "
        "읽음)가 'HC2O4- dissolved CuO to form soluble complexes like "
        "[Cu(C2O4)2]2-' 라 명시하고, RSM 회귀에서 [oxalic acid] 계수가 +536.63"
        "(p=1.7e-7)로 **가장 강하고 유의한 양(+)의 인자**('oxalic acid had the "
        "most significant positive impact on the response') — 억제제라면 농도가 "
        "오를 때 제거율이 내려야 하는데 정반대다. 독립 1차 문헌(Cabot US6309560B1 "
        "TABLE 1, knowledge/cmp/chi-carboxylate-promoter-cu-oxalate-us6309560.md)"
        "도 옥살산암모늄 농도 증가 → Cu 제거율 단조 증가(최대 12.81배)를 별도로 "
        "확인해 같은 결론(촉진·복합체 형성)에 도달했다 — 그 물리는 이 팩에서 이미 "
        "sim/chemistry.py::_carboxylate_promoter_term(promoter_species=oxalic) "
        "이 맡고 있다. 이 줄이 없으면 갭 리포트가 존재하지 않는 흡착 상수를 "
        "계속 찾으라고 지시한다(benzenesulfonic×cu 줄과 같은 재발 방지 목적).",
    ("benzenesulfonic", "cu"):
        "US9200180B2 명세서가 이 성분을 억제제가 아니라 **산화제 겸 Ta 착화제**로 "
        "규정한다 — corrosion inhibitor 마쿠쉬 군(1,2,4-triazole/benzotriazole/"
        "TINUVIN/CDX)에 들어 있지 않고, 'not only serves as oxidants but complexes "
        "with tantalum ions to form tantalum sulfonate complexes, which results in "
        "high tantalum and/or tantalum nitride removal rates' 로 서술된다. "
        "부호도 반대다: 'both Ta and TaN removal rates are substantially increased "
        "with increasing benzenesulfonic acid concentration' — 억제제라면 농도가 "
        "오를 때 제거율이 내려야 한다. 이 계에서 Cu 제거율이 낮은 이유는 흡착막이 "
        "아니라 알칼리 H2O2 부동태화다('a much higher passivation rate for copper "
        "than tantalum ... in a mixture of hydrogen peroxide and benzenesulfonic "
        "acid'), 그래서 그 물리는 억제 항이 아니라 oxidizer_passivation_K 가 "
        "맡는다(팩 cu_alkaline_benzenesulfonic). "
        "⚠ 이 줄이 없으면 갭 리포트가 이 쌍을 '문헌 조사 목록'에 계속 올려 "
        "다음 회차가 존재하지 않는 흡착 상수를 찾으러 간다 — 실제로 한 회차를 "
        "그렇게 썼다. 구조적으로 대상이 아닌 것과 아직 못 찾은 것은 다르다.",
}


def adsorption_ruled_out(inhibitor: str, substrate: str) -> Optional[str]:
    """이 쌍은 '미측정'이 아니라 '메커니즘 부재'로 선언됐는가.

    반환값이 있으면 그 문자열이 근거다. 호출자는 억제 항을 만들지 않되
    그 사실을 '값 없음'이 아니라 '효과 없음'으로 신고해야 한다.
    """
    return NO_ADSORPTION.get(_key(inhibitor, substrate))


def lookup_dG(inhibitor: str, substrate: str) -> Optional[PairDG]:
    """쌍으로 조회한다. 없으면 None — **대체하지 않는다.**

    None 을 받았을 때 호출자가 할 일은 유사 값으로 채우는 것이 아니라
    measurement_spec() 을 사용자에게 제시하는 것이다.
    """
    return PAIR_TABLE.get(_key(inhibitor, substrate))


def K_from_dG(dG_kJ_per_mol: float, temp_K: float = 298.15) -> float:
    """ΔG → 흡착 평형상수 K [L/mol].

    K = exp(−ΔG/RT) / 55.34

    55.34 로 나누는 이유: 흡착 등온식의 표준상태가 물의 몰농도를 기준으로
    정의된다(문헌 표준). 이 인자를 빼면 K 가 55 배 커진다.
    """
    return float(pow(2.718281828459045, -dG_kJ_per_mol * 1000.0 / (R_GAS * temp_K))
                 / WATER_MOLAR)


def measurement_spec(inhibitor: str, substrate: str) -> List[str]:
    """쌍이 표에 없을 때 발행하는 측정 명세 (R8).

    "문헌에 없다"는 실패가 아니다. 무엇을 어떻게 재면 되는지 말해주는 것은
    제품 기능이다 — 새 슬러리를 넣으려면 이 측정이 필요하다고 알려준다.
    """
    return [
        f"[R8 측정 명세] ({inhibitor} × {substrate}) 쌍의 ΔG_ads 가 없다.",
        "",
        "  ⚠ 다른 기질에서 측정한 값을 쓰면 안 된다. ΔG_ads 는 억제제 단독의",
        "    성질이 아니라 **쌍**의 성질이다 — 기질이 바뀌면 값이 바뀐다.",
        "",
        "  1순위: EIS 농도 스윕",
        "     · 실제 슬러리 pH·산화제 조건에서 억제제 농도를 5점 이상 스윕",
        "     · 전하전달저항 R_ct 로 피복률 θ 를 환산",
        "     · c/θ vs c 플롯의 절편에서 K, K 에서 ΔG",
        "",
        "     ⚠ 함정: c/θ 플롯은 **다층 흡착에서도 거의 직선으로 보인다**.",
        "       'Langmuir R²=0.99' 는 단분자층의 증거가 아니다.",
        "       다층이면 절편에서 나온 값은 ΔG1(첫층)일 뿐이다.",
        "",
        "  2순위: QCM 또는 EQCM",
        "     · θ 를 질량 변화로 **직접** 측정한다",
        "     · 다층 여부를 가릴 수 있는 유일한 결정적 경로다",
        "",
        "  왜 계산으로 대신할 수 없나:",
        "     HOMO-LUMO·Fukui 같은 분자 기술자만으로 ΔG 를 넣는 것은",
        "     문헌이 명시적으로 불충분하다고 경고한다. 표면 흡착에너지를",
        "     직접 계산하는 수준(기질 슬랩 포함)이 필요하며, 그 계산은",
        "     측정보다 비싸다.",
        "",
        "  이 값이 없는 동안 이 모델이 할 수 있는 것:",
        "     · 억제제 농도의 **순위 예측** — 농도가 오르면 제거율이 내린다",
        "     · 절대값 예측 — **할 수 없다**. 축척과 K 가 동시에 미지다.",
    ]
