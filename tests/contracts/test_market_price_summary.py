"""Contracts for the marketplace price summary tool."""

import json
from pathlib import Path

import pytest

from tools.analysis.market_price_summary import MarketPriceSummary, parse_price, summarize, won


@pytest.mark.parametrize("raw,expected", [
    ("10000", 10000),
    ("10,000원", 10000),
    ("10000.0", 10000),
    (15000, 15000),
    ("만원", 10000),
    ("5천원", 5000),
    ("1만5천원", 15000),
    ("2만 5천원", 25000),
    ("나눔", 0),
    ("무료나눔", 0),
    ("가격 문의", None),
    ("", None),
    (None, None),
    ("abc", None),
    (-5, None),
    (True, None),
])
def test_parse_price(raw, expected) -> None:
    assert parse_price(raw) == expected


def _items(prices, status="Ongoing", title="접시"):
    return [{"title": title, "price": str(p), "status": status} for p in prices]


def test_median_iqr_and_outliers_dropped() -> None:
    prices = [8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 111, 2_030_000]
    s = summarize(_items(prices), query="접시")
    assert s["priced_count"] == 10
    assert {o["price"] for o in s["outliers"]} == {111, 2_030_000}
    assert s["overall"]["n"] == 8
    assert s["overall"]["median"] == 11500
    assert s["overall"]["p25"] < s["overall"]["median"] < s["overall"]["p75"]
    assert "11,500원" in s["headline"]


def test_placeholder_price_caught_in_skewed_sample() -> None:
    # Right-skewed like a real search: a linear IQR lower fence goes negative and keeps 111원.
    prices = [1000] * 6 + [3000] * 6 + [5000] * 8 + [10000] * 8 + [20000] * 6 + [60000] * 4 + [111]
    s = summarize(_items(prices))
    assert 111 in {o["price"] for o in s["outliers"]}
    assert s["overall"]["min"] >= 1000


def test_free_and_unreadable_counted_not_priced() -> None:
    s = summarize(_items(["나눔", "가격 문의", 5000, 6000, 7000]))
    assert s["free_count"] == 1
    assert s["unreadable_price_count"] == 1
    assert s["priced_count"] == 3


def test_bundles_flagged_and_optionally_excluded() -> None:
    items = _items([5000, 6000, 7000]) + _items([90000], title="접시 일괄 세트")
    flagged = summarize(items)
    assert flagged["bundle_count"] == 1 and flagged["priced_count"] == 4
    excluded = summarize(items, exclude_bundles=True)
    assert excluded["priced_count"] == 3 and excluded["overall"]["max"] == 7000


def test_only_ongoing_gives_no_sold_comparison() -> None:
    s = summarize(_items([5000, 6000, 7000]))
    assert set(s["by_availability"]) == {"available"}
    assert "거래완료" in s["note"]


def test_sold_comparison_when_data_has_it() -> None:
    items = _items([10000, 12000, 14000]) + _items([7000, 8000, 9000], status="Completed")
    s = summarize(items)
    assert s["by_availability"]["available"]["median"] == 12000
    assert s["by_availability"]["other"]["median"] == 8000
    assert "note" not in s


def test_confidence_tracks_sample_size() -> None:
    assert summarize(_items([1000, 2000, 3000]))["confidence"] == "low"
    assert summarize(_items(range(1000, 21000, 1000)))["confidence"] == "medium"
    assert summarize(_items(range(1000, 61000, 1000)))["confidence"] == "high"


def test_single_and_empty_inputs() -> None:
    one = summarize(_items([5000]))
    assert one["overall"]["median"] == 5000 and one["overall"]["p25"] == 5000
    empty = summarize([])
    assert empty["overall"] is None and empty["confidence"] == "none"


def test_presets_follow_quartiles_and_cover_every_listing() -> None:
    prices = list(range(1000, 21000, 1000))  # 20 listings, 1천~2만
    presets = summarize(_items(prices))["price_presets"]
    # ~25/50/25, give or take what rounding the boundaries to round numbers moves
    assert all(abs(p["count"] - want) <= 2 for p, want in zip(presets, [5, 10, 5]))
    assert presets[0]["min"] is None and presets[-1]["max"] is None
    assert presets[0]["max"] == presets[1]["min"] and presets[1]["max"] == presets[2]["min"]
    assert sum(p["count"] for p in presets) == len(prices)


def test_presets_use_round_boundaries() -> None:
    prices = [4_970, 5_130, 5_300, 6_100, 7_400, 8_900, 12_300, 14_800, 15_200, 24_700]
    bounds = [p["max"] for p in summarize(_items(prices))["price_presets"] if p["max"]]
    assert all(b % 500 == 0 for b in bounds)


def test_presets_skipped_for_small_or_bunched_samples() -> None:
    assert summarize(_items([1000, 2000, 3000]))["price_presets"] == []
    assert summarize(_items([5000] * 20))["price_presets"] == []


def test_won_format() -> None:
    assert won(12345.6) == "12,346원"


def test_tool_reads_file_and_writes_output(tmp_path: Path) -> None:
    src = tmp_path / "l.json"
    src.write_text(json.dumps(_items([5000, 6000, 7000])), encoding="utf-8")
    out = tmp_path / "summary.json"
    r = MarketPriceSummary().execute(
        {"listings_path": str(src), "query": "접시", "output_path": str(out)}
    )
    assert r.success and r.data["overall"]["median"] == 6000
    assert json.loads(out.read_text(encoding="utf-8"))["query"] == "접시"


def test_tool_rejects_missing_input(tmp_path: Path) -> None:
    assert not MarketPriceSummary().execute({}).success
    assert not MarketPriceSummary().execute({"listings_path": str(tmp_path / "x.json")}).success
