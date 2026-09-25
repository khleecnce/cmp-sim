"""Print the validation-corpus score report (median shape / leave-one-out error).

Usage: python tools/score_report.py
Thin wrapper over cmp_sim.core.predictive_score so a session can read the
current median without retyping an inline snippet.
"""
from cmp_sim.core.predictive_score import score_all, report

if __name__ == "__main__":
    print(report(score_all()))
