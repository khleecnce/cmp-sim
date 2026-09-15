"""Reading a polishing log from CSV.

Big data does not arrive as a YAML block: it is a spreadsheet with whatever
column names the person who made it chose. This tolerates the spellings people
actually use, and — importantly — refuses loudly rather than dropping rows it
cannot read, because a silently dropped row changes the fit invisibly.
"""
import pytest

from cmp_sim.core.measurement_io import TEMPLATE, read_measurements

CANONICAL = """label,pressure_psi,rpm_platen,rate_A_per_min
a,2.0,60,2380
b,4.0,60,4690
"""


def test_a_canonical_csv_reads():
    rows = read_measurements(CANONICAL)
    assert len(rows) == 2
    assert rows[0]["pressure_psi"] == 2.0
    assert rows[0]["rate_A_per_min"] == 2380.0
    assert rows[0]["label"] == "a"


@pytest.mark.parametrize("header", [
    "Label,Pressure (psi),Platen RPM,MRR (A/min)",
    "run,DownForce,table_rpm,removal_rate",
    "ID,PRESSURE,PLATEN,RR",
    "name,psi,rpm,rate",
])
def test_the_column_names_people_actually_use_are_understood(header):
    rows = read_measurements(header + "\nx,2.0,60,2380\ny,4.0,60,4690\n")
    assert len(rows) == 2
    assert rows[0]["pressure_psi"] == 2.0
    assert rows[0]["rate_A_per_min"] == 2380.0


def test_angstrom_and_nanometre_columns_are_not_confused():
    """They differ only by their unit, and merging them is a silent 10x error
    in every fitted rate - the worst possible failure of a lenient parser."""
    in_angstrom = read_measurements(
        "pressure_psi,rpm_platen,MRR (A/min)\n3.0,60,1450\n4.0,60,1900\n")
    in_nm = read_measurements(
        "pressure_psi,rpm_platen,MRR (nm/min)\n3.0,60,145\n4.0,60,190\n")
    assert in_angstrom[0]["rate_A_per_min"] == pytest.approx(
        in_nm[0]["rate_A_per_min"])


def test_nm_per_min_is_converted():
    rows = read_measurements(
        "pressure_psi,rpm_platen,rate_nm_per_min\n3.0,60,145\n4.0,60,190\n")
    assert rows[0]["rate_A_per_min"] == pytest.approx(1450.0)


def test_slurry_columns_are_carried_through():
    rows = read_measurements(
        "pressure_psi,rpm_platen,rate,abrasive_wt_pct,H2O2,temp,pH\n"
        "3.0,60,1450,3.0,2.0,25,10.5\n4.0,60,1900,6.0,4.0,40,10.5\n")
    assert rows[0]["abrasive_wt_pct"] == 3.0
    assert rows[0]["oxidizer_wt_pct"] == 2.0
    assert rows[0]["temperature_c"] == 25.0
    assert rows[0]["ph"] == 10.5


def test_thousands_separators_and_blanks_are_handled():
    rows = read_measurements(
        "pressure_psi,rpm_platen,rate,abrasive_wt_pct\n"
        '3.0,60,"1,450",\n4.0,60,"1,900",3.0\n')
    assert rows[0]["rate_A_per_min"] == 1450.0
    assert "abrasive_wt_pct" not in rows[0]


def test_comment_lines_are_ignored():
    rows = read_measurements(
        "# a polishing log\npressure_psi,rpm_platen,rate\n"
        "# first campaign\n3.0,60,1450\n4.0,60,1900\n")
    assert len(rows) == 2


# ── refusing rather than silently dropping ───────────────────────────
def test_a_missing_rate_column_is_named_in_the_error():
    with pytest.raises(ValueError) as exc:
        read_measurements("pressure_psi,rpm_platen\n3.0,60\n")
    msg = str(exc.value)
    assert "removal rate" in msg
    assert "Columns found" in msg, "the error does not show what it did see"


def test_a_missing_pressure_column_is_refused():
    with pytest.raises(ValueError, match="pressure_psi"):
        read_measurements("rpm_platen,rate\n60,1450\n")


def test_unusable_rows_are_reported_not_dropped():
    """A dropped row changes the fit invisibly, which is worse than an error."""
    with pytest.raises(ValueError) as exc:
        read_measurements(
            "pressure_psi,rpm_platen,rate\n3.0,60,1450\n4.0,,1900\n5.0,60,\n")
    msg = str(exc.value)
    assert "NOT silently dropped" in msg
    assert "row 3" in msg and "row 4" in msg


def test_an_entirely_unusable_file_says_so():
    with pytest.raises(ValueError, match="no usable rows"):
        read_measurements("pressure_psi,rpm_platen,rate\n,,\n,,\n")


def test_the_template_is_itself_readable():
    """A template that does not parse is a trap."""
    rows = read_measurements(TEMPLATE)
    assert len(rows) == 4
    assert all("rate_A_per_min" in r for r in rows)


def test_the_template_varies_something_so_a_factor_can_unlock():
    """Otherwise the first thing a new user sees is 'nothing is identifiable'."""
    from cmp_sim.core.calibration import from_dicts
    from cmp_sim.core.factor_fit import fit_factors

    fit = fit_factors(from_dicts(read_measurements(TEMPLATE)))
    assert fit.kp_m_per_pa is not None
