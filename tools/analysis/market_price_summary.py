"""Market price summary for marketplace search results.

Given the listings a marketplace returns for one search query (title, price,
status), compute the price a buyer can expect to pay: median, interquartile
range and the sample behind them. Built from the benchmark of the Daangn web
search, where users otherwise skim sold posts by hand to judge a fair price.

Pure computation: no network, no scraping. Feed it listings from any source.
"""

from __future__ import annotations

import json
import math
import re
import statistics
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolStability,
    ToolTier,
)

# Title words that mean one listing sells several items; its price is not a unit price.
BUNDLE_WORDS = ("일괄", "세트", "묶음", "대량", "패키지", "풀세트", "일괄판매")
# Statuses treated as "still for sale"; anything else is reported separately, never mixed in.
AVAILABLE_STATUSES = ("ongoing", "available", "selling", "reserved")
FREE_WORDS = ("나눔", "무료")
UNPRICED_WORDS = ("문의", "협의", "제안")

_KR_UNITS = {"만": 10_000, "천": 1_000, "백": 100}


def parse_price(raw: Any) -> int | None:
    """Return won as int, 0 for free, None when the price cannot be read.

    Accepts numbers, digit strings ("10000", "10,000원", "10000.0") and common
    Korean spellings ("만원", "5천원", "1만5천원"). Never guesses at text with
    no number in it.
    """
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return int(raw) if raw >= 0 else None
    text = str(raw).strip().replace(",", "").replace(" ", "")
    if not text:
        return None
    if any(w in text for w in UNPRICED_WORDS):
        return None
    if any(w in text for w in FREE_WORDS):
        return 0
    m = re.fullmatch(r"(\d+)(?:\.\d+)?원?", text)
    if m:
        return int(m.group(1))
    m = re.fullmatch(r"((?:\d*[만천백])+)(\d*)원?", text)
    if m:
        total = 0
        for num, unit in re.findall(r"(\d*)([만천백])", m.group(1)):
            total += (int(num) if num else 1) * _KR_UNITS[unit]
        return total + (int(m.group(2)) if m.group(2) else 0)
    return None


def _quartiles(values: list[int]) -> tuple[float, float, float]:
    if len(values) == 1:
        v = float(values[0])
        return v, v, v
    q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return q1, q2, q3


def _stats(values: list[int]) -> dict[str, Any]:
    q1, med, q3 = _quartiles(values)
    return {
        "n": len(values),
        "median": round(med),
        "p25": round(q1),
        "p75": round(q3),
        "min": min(values),
        "max": max(values),
    }


def _confidence(n: int) -> str:
    if n < 8:
        return "low"
    if n < 30:
        return "medium"
    return "high"


def won(value: int | float) -> str:
    return f"{int(round(value)):,}원"


def _nice(value: float) -> int:
    """Round to a price people say out loud: 500원 under 1만, then 1천, 5천, 1만 steps."""
    if value < 10_000:
        step = 500
    elif value < 50_000:
        step = 1_000
    elif value < 200_000:
        step = 5_000
    else:
        step = 10_000
    return int(round(value / step) * step)


def price_presets(
    prices: list[int],
    *,
    count_prices: list[int] | None = None,
    min_samples: int = 8,
) -> list[dict[str, Any]]:
    """Quantile presets for a price filter: cheap quarter / middle half / top quarter.

    Fixed presets ("5천원 이하") ignore what the query actually sells for. These
    follow the result set, so each preset leaves roughly 25% / 50% / 25% of
    listings. Returns [] when the sample is too small to trust.

    Boundaries come from `prices` (outliers already removed). Counts come from
    `count_prices` (default: `prices`) because a filter returns every listing in
    range, outliers included, and the number shown must match what it returns.
    """
    if len(prices) < min_samples:
        return []
    q1, _, q3 = _quartiles(sorted(prices))
    lo, hi = _nice(q1), _nice(q3)
    if lo >= hi:  # prices bunched together: quartiles round to one value
        return []
    counted = prices if count_prices is None else count_prices
    cheap = [p for p in counted if p <= lo]
    middle = [p for p in counted if lo < p <= hi]
    top = [p for p in counted if p > hi]
    return [
        {"label": f"{won(lo)} 이하", "min": None, "max": lo, "count": len(cheap)},
        {"label": f"{won(lo)}~{won(hi)}", "min": lo, "max": hi, "count": len(middle)},
        {"label": f"{won(hi)} 이상", "min": hi, "max": None, "count": len(top)},
    ]


def summarize(
    listings: list[dict[str, Any]],
    *,
    query: str = "",
    exclude_bundles: bool = False,
    iqr_fence: float = 1.5,
) -> dict[str, Any]:
    """Summarize prices of listings that share one search query.

    Each listing: {"title", "price", "status"}; extra keys are ignored.
    Outliers (placeholder 111원, typo 2,030,000원) fall outside the log-space IQR
    fences and are dropped from the headline range but counted and listed.
    """
    status_counts: dict[str, int] = {}
    priced: list[tuple[int, dict]] = []
    free = unreadable = bundles = 0
    for item in listings:
        status = str(item.get("status", "")).strip() or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        price = parse_price(item.get("price"))
        if price is None:
            unreadable += 1
            continue
        if price == 0:
            free += 1
            continue
        title = str(item.get("title", ""))
        is_bundle = any(w in title for w in BUNDLE_WORDS)
        bundles += is_bundle
        if exclude_bundles and is_bundle:
            continue
        priced.append((price, item))

    result: dict[str, Any] = {
        "query": query,
        "listing_count": len(listings),
        "priced_count": len(priced),
        "free_count": free,
        "unreadable_price_count": unreadable,
        "bundle_count": bundles,
        "bundles_excluded": exclude_bundles,
        "status_counts": status_counts,
        "outliers": [],
        "overall": None,
        "price_presets": [],
        "by_availability": {},
        "confidence": "none",
        "headline": "",
    }
    if not priced:
        result["headline"] = f"'{query}' 시세를 계산할 가격 데이터가 없습니다."
        return result

    # Prices are multiplicative (1천원 vs 20만원 listings are both real), so fence in
    # log space: a linear lower fence goes negative and never catches 111원 placeholders.
    log_q1, _, log_q3 = _quartiles([math.log(p) for p, _ in priced])
    spread = iqr_fence * (log_q3 - log_q1)
    # exp(log(p)) is not exactly p; without slack a zero-width fence (one price, or all
    # equal) would reject the price it was built from.
    slack = 1 + 1e-9
    low, high = math.exp(log_q1 - spread) / slack, math.exp(log_q3 + spread) * slack
    kept = [(p, i) for p, i in priced if low <= p <= high]
    result["outliers"] = [
        {"price": p, "title": str(i.get("title", ""))[:60]}
        for p, i in priced if not low <= p <= high
    ]
    kept_prices = [p for p, _ in kept]
    result["overall"] = _stats(kept_prices)
    result["confidence"] = _confidence(len(kept_prices))
    result["price_presets"] = price_presets(
        kept_prices, count_prices=[p for p, _ in priced]
    )

    groups: dict[str, list[int]] = {"available": [], "other": []}
    for price, item in kept:
        status = str(item.get("status", "")).strip().lower()
        groups["available" if status in AVAILABLE_STATUSES else "other"].append(price)
    result["by_availability"] = {k: _stats(v) for k, v in groups.items() if v}
    if not groups["other"]:
        result["note"] = (
            "모든 매물이 판매중 상태라 거래완료 시세와의 비교는 제공하지 않습니다 "
            "(호가 기준 요약)."
        )

    o = result["overall"]
    label = f"'{query}' " if query else ""
    result["headline"] = (
        f"{label}판매중 호가 중앙값 {won(o['median'])} "
        f"(25~75%: {won(o['p25'])}~{won(o['p75'])}, n={o['n']}, 신뢰도 {result['confidence']})"
    )
    return result


class MarketPriceSummary(BaseTool):
    name = "market_price_summary"
    version = "0.1.0"
    tier = ToolTier.ANALYZE
    capability = "analysis"
    provider = "local"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = []
    install_instructions = "No external dependencies."
    agent_skills = []

    capabilities = ["price_median_iqr", "outlier_filtering", "bundle_detection"]

    input_schema = {
        "type": "object",
        "properties": {
            "listings": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Listings with title, price, status",
            },
            "listings_path": {
                "type": "string",
                "description": "JSON file holding a list of listings (alternative to listings)",
            },
            "query": {"type": "string"},
            "exclude_bundles": {"type": "boolean", "default": False},
            "iqr_fence": {"type": "number", "default": 1.5, "minimum": 0},
            "output_path": {"type": "string", "description": "Optional file to write the summary JSON"},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=1, ram_mb=128, disk_mb=1)
    side_effects = ["writes summary JSON to output_path when given"]
    user_visible_verification = ["Spot-check median against a few listings in the sample"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        listings = inputs.get("listings")
        if listings is None and inputs.get("listings_path"):
            path = Path(inputs["listings_path"])
            if not path.is_file():
                return ToolResult(success=False, error=f"Listings file not found: {path}")
            listings = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(listings, list):
            return ToolResult(success=False, error="Provide listings (list) or listings_path (JSON list)")

        summary = summarize(
            listings,
            query=inputs.get("query", ""),
            exclude_bundles=inputs.get("exclude_bundles", False),
            iqr_fence=inputs.get("iqr_fence", 1.5),
        )
        artifacts = []
        if inputs.get("output_path"):
            out = Path(inputs["output_path"])
            out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            artifacts.append(str(out))
        return ToolResult(
            success=True, data=summary, artifacts=artifacts,
            duration_seconds=round(time.time() - start, 3),
        )
