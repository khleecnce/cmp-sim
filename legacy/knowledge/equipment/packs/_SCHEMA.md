# 장비팩 스키마 — 컨디셔너 디스크

이 디렉토리는 `knowledge/params/*.yaml`(화학 팩)과 형식은 같지만(value/unit/source/
confidence/note) **완전히 별도의 축**을 담는다. `sim/equipment.py::load_equipment_pack()`
로만 로드되고, `sim/params.py::load_pack()`(화학 팩 로더)의 `available_packs()`에는
절대 섞이지 않는다.

## 왜 화학 팩과 분리했는가

컨디셔너 디스크 사양(그릿 크기·밀도·배열·돌출)은 화학 팩이 선언할 값이 아니다.
`knowledge/params/base.yaml`의 `pad_asperity_radius_m` note가 이미 "R은 소재 물성이
아니라 **컨디셔닝(디스크 grit·하중)이 만드는 기하량**"이라고 명시했다. 화학 팩에 디스크
필드를 넣으면 "Cu 화학을 바꿨는데 디스크 사양이 같이 바뀌는" 잘못된 결합이 생긴다.
같은 디스크로 Cu 팩도, 산화막 팩도 돌릴 수 있어야 하므로 장비 축을 별도 팩으로 뗀다
(백로그 ㉺, `validation/S12-RESIDUAL-JUDGMENT.md` §2-2).

## 필드 목록

근거: `knowledge/equipment/conditioner-disk-spec-recipe-industrial.md` §2
(3M E187 TDS, 자료번호 60-5002-0211-8, June 2014).

| 필드 | 단위 | 의미 | 출처 등급 | 필수/선택 |
|---|---|---|---|---|
| `grit_nominal_size_um` | µm | 다이아몬드 그릿 공칭 크기 | literature | 필수 |
| `grit_type_grade` | (문자열) | 그릿 등급 (예: "Type 4, semi-sharp") | literature | 필수 |
| `grit_array_pattern` | (문자열) | 그릿 배열 패턴 (예: "square_array") | literature | 필수 |
| `carrier_diameter_mm` | mm | 캐리어 공칭 직경 | literature | 필수 |
| `carrier_material` | (문자열) | 캐리어 재질 (예: "SS304") | literature | 필수 |
| `carrier_form` | (문자열) | 캐리어 형태 (예: "ring") | literature | 필수 |
| `working_face_form` | (문자열) | 작업면 형태 (예: "segmented") | literature | 필수 |
| `disk_flatness_max_um` | µm | 디스크 평탄도 상한 | literature | 필수 |
| `aggressiveness_value_bl_min` | (무차원) | Aggressiveness Value(BL) 하한 | literature | 필수 |
| `aggressiveness_value_bl_max` | (무차원) | Aggressiveness Value(BL) 상한 | literature | 필수 |

Aggressiveness Value(BL)는 TDS 표기 그대로 범위값이라 min/max 두 키로 나눈다
(원표기는 note에 병기). 무차원 정의식 자체는 어느 출처에도 없다(노트 §2, §7 미해결).

## 현재 비어 있는 필드와 그것이 막고 있는 것

아래 세 값은 3M E187 TDS에 없다. **지어내지 않고 빈 채로 둔다** — 조회 시
`ParamMissing`이 뜨는 것이 정답이다.

| 비어 있는 필드 | 막고 있는 것 |
|---|---|
| `grit_density_per_cm2` (N, 단위면적당 그릿 개수) | `disk_active_grit_fraction` — 활성 그릿 비율 계산이 N 없이는 불가능 |
| `Rpk` (그릿 첨두부 통계 파라미터) | `disk_cutrate_coupling` — 디스크→패드 절삭률 결합 모델이 Rpk 없이는 불가능 |
| `engage_depth_um` (그릿 패드 침투 깊이) | `disk_cutrate_coupling` — 위와 동일 축, 깊이 항이 없으면 절삭 접촉역학을 못 세운다 |

SEMICON West 2000 DOE(노트 §3, 출처 2)가 그릿 크기 100–425 µm·exposure 0–60% 범위를
주지만, 이건 DOE 탐색범위지 E187 제품 스펙이 아니다 — 팩 값으로 넣지 않는다.
