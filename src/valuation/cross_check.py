"""Cross-check of my engine against the expert's disclosed scenario A (task P3-17).

The expert printed no cash flows, only the inputs of its scenario A (booklet pp. 141 to 143) and
a chart of the value of business operations at each end of its discount rate range (p. 144). I
run my engine on the expert's inputs and compare with the two bar ends, which I read from the
chart (about plus or minus A$5m), under both discounting conventions.
"""

from __future__ import annotations

from dataclasses import dataclass

from valuation.dcf import dcf_value
from valuation.forecast import forecast_from_inputs
from valuation.gap_bridge import expert_case_inputs
from valuation.inputs import Inputs

READING_PRECISION_AUD_M = 5.0


@dataclass(frozen=True)
class ScenarioAPoint:
    convention: str
    discount_rate_pct: float
    bound: str
    engine_aud_m: float
    expert_read_aud_m: float

    @property
    def difference_aud_m(self) -> float:
        return self.engine_aud_m - self.expert_read_aud_m

    @property
    def difference_pct(self) -> float:
        return self.difference_aud_m / self.expert_read_aud_m * 100


def scenario_a_check(inputs: Inputs) -> list[ScenarioAPoint]:
    """Engine value of business operations at each end of the expert's range, both conventions.

    The low bound of the expert's bar is the value at its highest discount rate.
    """
    expert = expert_case_inputs(inputs)
    cash_flows = forecast_from_inputs(expert)
    growth = expert.number("expert_terminal_growth_pct")
    ends = (
        ("low", expert.number("expert_discount_rate_high_pct")),
        ("high", expert.number("expert_discount_rate_low_pct")),
    )
    points: list[ScenarioAPoint] = []
    for convention, mid_year in (("mid-year", True), ("year end", False)):
        for bound, rate in ends:
            value = dcf_value(expert, cash_flows, rate, growth, mid_year).enterprise_value_aud_m
            read = expert.table_number(
                "dcf_npv_chart_reads", "value_aud_m", scenario="A", bound=bound
            )
            points.append(ScenarioAPoint(convention, rate, bound, value, read))
    return points
