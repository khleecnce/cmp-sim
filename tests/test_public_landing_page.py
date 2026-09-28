"""The hosted page is a public CV artifact, so its claims are tested.

The owner links `https://cmp-sim.vercel.app` from a LinkedIn profile and from job
applications. That changes what the landing page is: no longer a local launcher
for someone who already cloned the repository, but the first — and for most
readers the only — thing they will see. Two failure modes follow, and both are
silent without a test.

1. **A stranger arrives with no context.** If the result pane says only "Set a
   recipe and press Simulate", the reader learns nothing about what the model
   does, how wrong it is, or who wrote it, and leaves. The page must state all
   three above the fold.

2. **A number in the shop window drifts from the number the model scores.** A CV
   claim is checkable in thirty seconds, so a hard-coded "18.9%" in the HTML
   becomes a false claim the moment the engine moves. The accuracy sentence is
   therefore rendered from `/api/accuracy` at load time and must never be a
   literal in the markup — the same discipline
   `test_web_holds_no_physics_constants.py` applies to physics constants,
   applied to the honesty numbers.

The confidentiality clause is tested too. The owner works for a slurry supplier
and this project is read by competitors and by the employer; the page asserting
"no employer data, no constant calibrated against internal results" is what makes
publishing it safe, and a later edit that tidies the byline away removes that
protection without anyone noticing.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "cmp_sim" / "web" / "index.html"


def _html() -> str:
    return INDEX.read_text(encoding="utf-8")


def test_the_landing_pane_says_what_the_model_is_before_any_input():
    """The default right-hand pane is an explanation, not an empty prompt."""
    html = _html()
    body = html.split("<body>", 1)[1]
    pane = body.split('<div id="out">', 1)[1].split("</main>", 1)[0]

    assert 'class="about"' in pane, (
        "the result pane's default state is not the explanatory panel; a "
        "visitor arriving from a CV link sees no description of the project")
    for phrase in ("removal rate", "uniformity", "literature source"):
        assert phrase in pane.lower(), (
            f"the landing pane never mentions {phrase!r} — it has to say what "
            f"the model predicts and on what authority")


def test_the_landing_pane_states_the_limits_not_only_the_capabilities():
    """A simulator page that only advertises is not defensible in an interview."""
    pane = _html().split('<div id="out">', 1)[1].split("</main>", 1)[0].lower()
    assert "trend" in pane and "absolute" in pane, (
        "the page does not distinguish trend prediction from absolute rate; "
        "that distinction is the model's single most important limitation")
    assert "leave-one-out" in pane, (
        "leave-one-out is how the accuracy figure avoids grading its own "
        "homework, and a reader cannot judge the number without it")
    assert "limits.md" in _html(), (
        "nothing links to the list of things the model refuses to predict")


def test_the_accuracy_figure_is_fetched_live_and_never_hard_coded():
    """No literature-accuracy percentage may be typed into the markup.

    Guards the exact drift this page invites: a reader checks the quoted error
    against `/api/accuracy` and finds two different numbers.
    """
    html = _html()
    body = html.split("<body>", 1)[1]
    markup = re.sub(r"<script.*?</script>", "", body, flags=re.S)

    # Percentages in prose. Any of them in the about panel would be a claim.
    pane = markup.split('<div id="out">', 1)[1].split("</main>", 1)[0]
    literals = re.findall(r"\b\d{1,3}(?:\.\d+)?\s*%", pane)
    assert not literals, (
        f"a hard-coded percentage in the landing pane: {literals}. Render it "
        f"from /api/accuracy through paintAboutAccuracy() instead, or it will "
        f"outlive the number it describes.")

    assert "paintAboutAccuracy" in html, (
        "the live-accuracy renderer is gone; the pane can no longer report the "
        "measured error")
    assert 'id="aboutacc"' in html, "nothing for paintAboutAccuracy to fill"


def test_the_page_carries_the_authorship_and_confidentiality_statement():
    """Publishing this safely depends on one sentence staying in the page."""
    pane = _html().split('<div id="out">', 1)[1].split("</main>", 1)[0]
    low = pane.lower()
    assert "keehwan lee" in low, "the page does not say who built it"
    assert "no employer data" in low, (
        "the page no longer states that it contains no employer data — that "
        "clause is what makes a supplier employee's public CMP model publishable")
    assert "calibrated against internal" in low, (
        "'no constant calibrated against internal results' is the specific "
        "claim a reviewer needs; 'no employer data' alone does not cover a "
        "constant tuned on internal measurements")
    assert "github.com/khleecnce/cmp-sim" in pane, (
        "no link to the source; the artifact's whole value is that it can be "
        "read")


def test_the_page_is_reachable_without_a_token_by_default():
    """A CV link that returns 401 reads as a broken claim, not as security.

    The token gate stays available (`CMPSIM_TOKEN`), but it must be OFF unless
    the environment sets it — the hosted demo had it on, so every visitor to the
    advertised URL got `Unauthorized`.
    """
    import os

    from cmp_sim.api import _expected_token

    had = os.environ.pop("CMPSIM_TOKEN", None)
    try:
        assert _expected_token() == "", (
            "a token is configured in this environment, so the public URL "
            "would refuse anonymous visitors")
    finally:
        if had is not None:
            os.environ["CMPSIM_TOKEN"] = had


def test_the_deploy_bundle_keeps_every_dataset_the_score_reads():
    """The hosted score must equal the repository score, dataset for dataset.

    Measured, not assumed: `.vercelignore` excluded `legacy/validation/`, and
    because `core/validation.py` reads BOTH that folder and the package's own,
    the deployed `/api/accuracy` reported 47 datasets / 435 points while
    `tools/score_report.py` reported 48 / 440. Two different honest-looking
    numbers for the same claim, one of them printed on a CV.

    This checks the ignore rules the way Vercel applies them, so re-adding a
    broad `legacy/validation/` line fails here rather than in production.
    """
    from cmp_sim.core.validation import dataset_paths

    rules = [ln.strip() for ln in
             (ROOT / ".vercelignore").read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.startswith("#")]

    dropped = []
    for path in dataset_paths():
        rel = path.relative_to(ROOT).as_posix()
        for rule in rules:
            if rule.endswith("/") and rel.startswith(rule):
                dropped.append((rel, rule))
            elif "*" in rule:
                from fnmatch import fnmatch
                if fnmatch(rel, rule):
                    dropped.append((rel, rule))
            elif rel == rule:
                dropped.append((rel, rule))

    assert not dropped, (
        "a validation dataset the scorer reads is excluded from the deploy "
        "bundle, so the hosted /api/accuracy will report fewer datasets than "
        "tools/score_report.py:\n  "
        + "\n  ".join(f"{p}  (excluded by {r!r})" for p, r in dropped))


def test_the_text_report_reconciles_with_the_published_beat_count():
    """Two counts of one fact must add up, or a reader distrusts both.

    `/api/accuracy` publishes `beat_predicting_the_mean` over every scored
    dataset (36 of 48). The text report's "does NOT beat predicting the mean"
    line excludes datasets already at their measured noise floor, where beating
    the mean would mean fitting noise — so it printed 11, and 36 + 11 = 47, one
    short of 48. Both numbers were correct and the pair was not checkable. The
    report now states the exclusion and the resulting total in the same
    sentence; this pins that to the real scores.
    """
    import re

    from cmp_sim.core.predictive_score import report, score_all

    scores = [s for s in score_all() if s.shape_mape is not None]
    beat = sum(1 for s in scores if s.beats_flat)
    text = report(score_all())

    line = next((ln for ln in text.splitlines()
                 if "does NOT beat predicting the mean" in ln), None)
    assert line, "the report no longer states which datasets lose to the mean"

    lost_m = re.search(r"mean on (\d+)", line)
    assert lost_m, f"cannot read the lost count from: {line!r}"
    lost = int(lost_m.group(1))
    floored = sum(1 for s in scores if not s.beats_flat and s.at_noise_floor)
    assert beat + lost + floored == len(scores), (
        f"the report's counts do not partition the scored datasets: "
        f"{beat} beat + {lost} lost + {floored} at floor != {len(scores)}")

    m = re.search(r"so (\d+)/(\d+) beat it", line)
    if floored:
        assert m, (
            "datasets are excluded from the lost-count but the line does not "
            "say so, so the published beat count cannot be reconciled with it")
        assert (int(m.group(1)), int(m.group(2))) == (beat, len(scores)), (
            f"the report says {m.group(1)}/{m.group(2)} beat the mean but the "
            f"scores say {beat}/{len(scores)}")


def test_the_document_head_describes_the_project_for_link_previews():
    """Recruiters and chat clients see the meta description, not the page."""
    head = _html().split("</head>", 1)[0]
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', head)
    assert m, "no meta description; a shared link previews as a bare URL"
    desc = m.group(1)
    assert 60 < len(desc) < 320, f"description length {len(desc)} is unusable"
    assert "CMP" in desc, "the description never names the domain"
    assert "<title>CMP-Sim" in head, "the title no longer names the product"
    title = re.search(r"<title>([^<]+)</title>", head)
    assert title and len(title.group(1)) > 20, (
        "the title is a bare product name; it has to carry what the product is")
