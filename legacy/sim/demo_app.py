"""
FabSim Phase 0 — Streamlit 데모 UI.

탭1: 압력·RPM·존압력 슬라이더로 sim/engine.py의 Recipe/simulate()를 구동해 반경별 MRR
     프로파일과 요약 지표를 보여준다. 모델은 available_models()로 등록된 것 중에서
     사용자가 고른다(기본값 tier2.gw_physical_kp). 2026-09-06 BACKLOG S5 재작성으로
     tier1_empirical(preston.py/kinematics.py) 직접 호출을 engine.simulate()로 교체했다.
     "공정시간 적분" 섹션만 예외: engine.py에 시간축 스윕 API가 없어
     tier1_empirical.process_time을 직접 호출하는 기존 방식을 유지한다.
탭2: WIWNU(반경 스케일) × 패턴밀도(다이 스케일) 결합 제거율 맵
     (wiwnu.py + pattern_density.py + wiwnu_pattern_combined.py, 이미 self-test/pytest
     통과된 기존 모듈을 그대로 노출 — 이 탭 추가로 세 모듈 파일은 수정하지 않음).
     ⚠ 이 탭은 이번 S5 재작성에서 engine 이관 대상에서 제외했다 — pattern_density를
     Recipe에 반영하려면 die 레이아웃/유효밀도맵 스키마 확장이 필요하고 이는
     sim-architect 담당 + S6 게이트다(docs/ARCHITECTURE.md §3c 참고). tab2는
     tier1_empirical 모듈(wiwnu/pattern_density/wiwnu_pattern_combined)을 계속
     직접 호출한다.

실행: source .venv/bin/activate && streamlit run sim/demo_app.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

_TIER1_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tier1_empirical")
if _TIER1_DIR not in sys.path:
    sys.path.insert(0, _TIER1_DIR)

import sim.models  # noqa: E402  — import 시 tier2.gw_physical_kp 등 모델 자동등록
from sim.engine import Recipe, simulate, available_models
from sim.params import available_packs, load_pack  # noqa: E402

from process_time import endpoint_time, removed_thickness  # noqa: E402  — tab1 시간축 전용, 아래 주석 참고
from wiwnu import p_uniform, p_edge_concentration  # noqa: E402
from pattern_density import effective_density  # noqa: E402
from wiwnu_pattern_combined import combined_removal_map, _area_weighted_2d  # noqa: E402

st.set_page_config(page_title="FabSim — CMP MRR 데모", layout="wide")

st.title("FabSim — CMP MRR 데모")
st.caption(
    "Tier1 경험식(Preston), 균일/존압력 가정, 문헌 재현 검증된 v0 모델 — "
    "실제 공정 예측 정밀도 보증 아님"
)

tab1, tab2 = st.tabs(["Preston MRR v0", "WIWNU × 패턴밀도 결합 맵"])

with tab1:
    PSI_PER_KPA = 1000.0 / 6894.757  # kPa 슬라이더(UI 관행) → Recipe.pressure_psi 단위 변환

    st.sidebar.header("공정 변수")
    model_names = available_models()
    default_model = "tier2.gw_physical_kp" if "tier2.gw_physical_kp" in model_names else model_names[0]
    model_name = st.sidebar.selectbox(
        "모델", model_names, index=model_names.index(default_model),
        help="tier2.gw_physical_kp = GW 접촉역학에서 Kp를 유도(기본, 가장 물리적 근거 있음)",
    )
    # 팩이 물성(막질·슬러리·패드)을 소유한다 — film 드롭다운을 대체한다.
    # 예전엔 film을 골라도 Kp가 그대로라 아무것도 안 바뀌었다(거짓 UI).
    pack_name = st.sidebar.selectbox(
        "파라미터 팩 (물성)", available_packs(),
        index=available_packs().index("oxide_silica") if "oxide_silica" in available_packs() else 0,
        help="막질·슬러리·패드 물성 묶음. knowledge/params/*.yaml — 여기를 바꾸면 다른 공정이 된다",
    )
    _pk = load_pack(pack_name)
    st.sidebar.caption(f"{_pk.description}\n\n상속: {' → '.join(_pk.lineage)}")
    wafer_type = st.sidebar.selectbox("wafer 타입", ["NPW", "PTW"])
    film = None   # 팩이 결정
    R_w_mm = st.sidebar.slider("웨이퍼 반경 R_w (mm)", 50.0, 300.0, 150.0, step=1.0)
    r_cc_mm = st.sidebar.slider("회전축 간 거리 r_cc (mm)", 50.0, 400.0, 200.0, step=1.0)
    rpm_w = st.sidebar.slider("RPM (웨이퍼)", 1.0, 200.0, 60.0, step=1.0)
    rpm_p = st.sidebar.slider("RPM (패드)", 1.0, 200.0, 60.0, step=1.0)
    _kp_pack = float(_pk.get("kp_m_per_pa"))
    kp = st.sidebar.number_input(
        f"Kp (Preston 계수, m^2/N) — 팩값 {_kp_pack:.2e}",
        min_value=1e-15, max_value=1e-10,
        value=_kp_pack, step=1e-14, format="%.2e",
        help="팩의 값이 기본으로 들어온다. 손대면 이번 런만 덮어쓴다",
    )
    time_s = st.sidebar.slider("공정시간 time_s (s)", 1.0, 300.0, 60.0, step=1.0)

    st.sidebar.header("압력")
    pressure_mode = st.sidebar.radio("압력 모드", ["균일", "존압력 (center/mid/edge)", "엣지집중"])

    R_w = R_w_mm / 1000.0
    r_cc = r_cc_mm / 1000.0

    zone_pressures_psi = None
    zone_edges_norm = None
    edge_pressure_amp = 0.0
    if pressure_mode == "존압력 (center/mid/edge)":
        p_center = st.sidebar.slider("압력 — center (kPa)", 1.0, 100.0, 20.7, step=0.1)
        p_mid = st.sidebar.slider("압력 — mid (kPa)", 1.0, 100.0, 20.7, step=0.1)
        p_edge = st.sidebar.slider("압력 — edge (kPa)", 1.0, 100.0, 20.7, step=0.1)
        zone_pressures_psi = [p_center * PSI_PER_KPA, p_mid * PSI_PER_KPA, p_edge * PSI_PER_KPA]
        # engine.PrestonRadialModel이 0을 앞에 붙이는 계약이므로 끝점만 준다(1/3, 2/3, 1.0)
        zone_edges_norm = [1.0 / 3.0, 2.0 / 3.0, 1.0]
        P_kpa = p_center  # Recipe.pressure_psi는 존압력 미사용 시에만 의미 있음, 폴백용
    elif pressure_mode == "엣지집중":
        P_kpa = st.sidebar.slider("기준 압력 P0 (kPa)", 1.0, 100.0, 20.7, step=0.1)
        edge_pressure_amp = st.sidebar.slider("엣지 압력집중 amp", 0.0, 1.0, 0.15, step=0.01)
    else:
        P_kpa = st.sidebar.slider("압력 P (kPa)", 1.0, 100.0, 20.7, step=0.1)

    recipe = Recipe(
        pack=pack_name,
        wafer=wafer_type, film=film, wafer_radius_m=R_w,
        pressure_psi=P_kpa * PSI_PER_KPA, rpm_wafer=rpm_w, rpm_platen=rpm_p,
        center_offset_m=r_cc, zone_pressures_psi=zone_pressures_psi,
        zone_edges_norm=zone_edges_norm, edge_pressure_amp=edge_pressure_amp,
        time_s=time_s, kp_m_per_pa=kp,
    )
    res = simulate(recipe, model=model_name)

    rs = res.radius_m
    mrr_nm_min = res.mrr_nm_per_min

    col_plot, col_metrics = st.columns([2, 1])

    with col_plot:
        st.subheader("반경별 MRR 프로파일")
        fig, ax = plt.subplots()
        ax.plot(rs * 1000.0, mrr_nm_min)
        ax.set_xlabel("반경 (mm)")
        ax.set_ylabel("MRR (nm/min)")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    with col_metrics:
        st.subheader("요약 지표")
        st.metric("웨이퍼 평균 MRR", f"{float(np.mean(mrr_nm_min)):.1f} nm/min")
        st.metric("TTV", f"{res.metrics.ttv_nm:.2f} nm")
        st.metric("radial range (문헌)", f"{res.metrics.radial_range_pct:.2f} %")
        st.metric("CV", f"{res.metrics.cv_pct:.2f} %")
        st.metric("WIWNU half-range", f"{res.metrics.wiwnu_halfrange_pct:.2f} %")

    for note in res.notes:
        st.warning(note)

    # 공정시간 적분: engine.py에 시간축 스윕 API가 없어 tier1_empirical.process_time을
    # 직접 호출하는 기존 방식을 유지한다(위 파일 상단 docstring 참고). 이 섹션만 예외.
    st.sidebar.header("공정시간 (유량 축은 미포함 — 지식 부재로 별도 구현 예정)")
    target_nm = st.sidebar.slider("목표 제거두께 (nm)", 1.0, 2000.0, 200.0, step=1.0)
    target_m = target_nm * 1e-9
    avg_mrr_m_s = float(np.mean(mrr_nm_min)) * 1e-9 / 60.0
    mrr_m_s = mrr_nm_min * 1e-9 / 60.0
    t_end_sec = endpoint_time(target_m, avg_mrr_m_s)

    st.subheader("공정시간 적분")
    col_time_plot, col_time_metrics = st.columns([2, 1])
    with col_time_plot:
        fig2, ax2 = plt.subplots()
        ax2.plot(rs * 1000.0, removed_thickness(rs, mrr_m_s, t_end_sec) * 1e9)
        ax2.set_xlabel("반경 (mm)")
        ax2.set_ylabel("제거두께 (nm)")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
    with col_time_metrics:
        st.metric("목표두께 도달 예상시간 (웨이퍼 평균 MRR 기준)", f"{t_end_sec:.1f} s")

with tab2:
    st.caption(
        "반경-패턴 분리가능(separable) 1차 근사 — 반경별 blanket 제거율 K(r)과 "
        "다이내부 유효밀도 rho_eff(x)가 서로 독립이라고 가정하며, 엣지에서 패턴 영향이 "
        "증폭되는 것과 같은 교차항은 포함하지 않는다. 모든 반경 위치의 다이가 동일한 "
        "내부 패턴 분포를 갖는다고 가정(엣지 다이의 스크라이브 절단·회전 효과 미반영), "
        "패턴밀도 유효화 필터는 실제 탄성패드 굽힘 유래 타원형(elliptic) 커널 대신 "
        "가우시안으로 근사한 미검증 근사다 — MASTER-PLAN.md 진행 로그 참조."
    )

    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        st.markdown("**웨이퍼/공정 변수**")
        R_w2_mm = st.slider("웨이퍼 반경 R_w (mm)", 50.0, 300.0, 150.0, step=1.0, key="t2_rw")
        r_cc2_mm = st.slider("회전축 간 거리 r_cc (mm)", 50.0, 400.0, 200.0, step=1.0, key="t2_rcc")
        rpm_w2 = st.slider("RPM (웨이퍼)", 1.0, 200.0, 50.0, step=1.0, key="t2_rpmw")
        rpm_p2 = st.slider("RPM (패드)", 1.0, 200.0, 60.0, step=1.0, key="t2_rpmp")
        kp2 = st.number_input(
            "Kp (Preston 계수, m^2/N)", min_value=1e-15, max_value=1e-10,
            value=1e-13, step=1e-14, format="%.2e", key="t2_kp",
        )

    with col_in2:
        st.markdown("**압력 프로파일**")
        profile_mode = st.radio(
            "프로파일 종류", ["균일 (uniform)", "엣지 압력집중 (edge-concentration)"],
            key="t2_profile_mode",
        )
        P_kpa2 = st.slider("기준 압력 P0 (kPa)", 1.0, 100.0, 20.7, step=0.1, key="t2_p0")
        if profile_mode == "균일 (uniform)":
            p_norm_fn = p_uniform(P_kpa2 * 1e3)
        else:
            amp_edge = st.slider("엣지 압력집중 amp", 0.0, 1.0, 0.30, step=0.01, key="t2_amp_edge")
            n_edge = st.slider("엣지 집중도 n", 1.0, 20.0, 8.0, step=1.0, key="t2_n_edge")
            p_norm_fn = p_edge_concentration(P_kpa2 * 1e3, amp=amp_edge, n=n_edge)

    with col_in3:
        st.markdown("**다이 패턴밀도 (합성 예시)**")
        amp_pattern = st.slider("패턴밀도 진폭", 0.0, 0.45, 0.20, step=0.01, key="t2_amp_pat")
        period_mm = st.slider("패턴 주기 (mm)", 1.0, 10.0, 4.0, step=0.5, key="t2_period")
        PL_mm = st.slider("평탄화 길이 PL (mm)", 0.5, 10.0, 3.0, step=0.5, key="t2_pl")

    x_die = np.linspace(0.0, 20.0, 401)  # mm — wiwnu_pattern_combined._selftest() 예시 재현
    rho_local = 0.5 + amp_pattern * np.sin(2 * np.pi * x_die / period_mm)
    rho_eff_die = effective_density(x_die, rho_local, PL=PL_mm)

    R_w2 = R_w2_mm / 1000.0
    r_cc2 = r_cc2_mm / 1000.0
    radial_positions = np.linspace(1e-6, R_w2, 81)

    result = combined_removal_map(
        radial_positions, rho_eff_die, R_w2, r_cc2, rpm_w2, rpm_p2, kp2, p_norm_fn,
    )
    metrics_2d = _area_weighted_2d(result["rs"], result["RR"])

    col_map, col_metrics2 = st.columns([2, 1])
    with col_map:
        st.subheader("결합 제거율 맵 RR(r, x)")
        fig3, ax3 = plt.subplots()
        im = ax3.imshow(
            result["RR"],
            extent=[x_die.min(), x_die.max(), radial_positions.min() * 1000.0,
                    radial_positions.max() * 1000.0],
            origin="lower", aspect="auto", cmap="viridis",
        )
        ax3.set_xlabel("다이내부 위치 x (mm)")
        ax3.set_ylabel("웨이퍼 반경 r (mm)")
        fig3.colorbar(im, ax=ax3, label="제거율 (m/s, K 단위 그대로)")
        st.pyplot(fig3)

    with col_metrics2:
        st.subheader("결합 WIWNU 지표 (면적가중)")
        st.metric("sigma_pct (CV)", f"{metrics_2d['sigma_pct']:.2f} %")
        st.metric("half_range_pct", f"{metrics_2d['half_range_pct']:.2f} %")
        st.metric("평균 제거율", f"{metrics_2d['mean']:.3e} m/s")
