#!/usr/bin/env python3
"""
Parse Loki JSON (or text) into [timestep, log_entry] pairs, then emit a YAML
summary: time, data_log, and rate (per-type Σ(qty×price) and total Rating).

Same CLI as gen_synth_loki_metrics_totals.py (-j, -o, --debug).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Optional

import yaml

REQUIRED_KEYS = frozenset(
    {"start", "end", "type", "unit", "qty", "price", "groupby"}
)


def _valid_ts(s: str) -> bool:
    return isinstance(s, str) and s.isdigit() and len(s) >= 19


def _valid_entry(obj: dict) -> bool:
    return REQUIRED_KEYS.issubset(obj.keys())


def _try_pair(ts_str: str, log_str: str) -> Optional[tuple[str, str]]:
    if not _valid_ts(ts_str) or not isinstance(log_str, str):
        return None
    try:
        entry = json.loads(log_str)
    except json.JSONDecodeError:
        return None
    if isinstance(entry, dict) and _valid_entry(entry):
        return (ts_str, log_str)
    return None


def _extract_from_loki_json(data: dict) -> list[tuple[str, str]]:
    streams = data.get("streams")
    if streams is None:
        streams = data.get("data", {}).get("result", [])
    if not isinstance(streams, list):
        return []
    pairs: list[tuple[str, str]] = []
    for stream in streams:
        for val in stream.get("values", []):
            if not isinstance(val, (list, tuple)) or len(val) < 2:
                continue
            p = _try_pair(val[0], val[1])
            if p:
                pairs.append(p)
    return pairs


def extract_and_sort(json_path: Path) -> list[tuple[str, str]]:
    """
    Load JSON from json_path, extract [timestep, log_entry] pairs,
    and return them sorted by timestep (ascending).
    """
    raw = json_path.read_text(encoding="utf-8", errors="replace")

    # Parse as JSON (fail if invalid)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(
            f"Error: Invalid JSON in {json_path}: {e}",
            file=sys.stderr
        )
        sys.exit(1)

    # Extract from known Loki JSON structures
    if not isinstance(data, dict):
        print(
            f"Error: Expected JSON object, got {type(data).__name__} "
            f"in {json_path}",
            file=sys.stderr
        )
        sys.exit(1)

    pairs = _extract_from_loki_json(data)

    if not pairs:
        print(
            f"Error: No valid log entries found in {json_path}. "
            "Expected structure: {{'streams': [...]}} or "
            "{{'data': {{'result': [...]}}}}'",
            file=sys.stderr
        )
        sys.exit(1)

    pairs.sort(key=lambda p: int(p[0]))
    return pairs


def _apply_mutate(qty: float, mutate: str) -> float:
    """
    Apply mutate transformation to qty value.

    Args:
        qty: The quantity value to transform.
        mutate: The mutation type (NONE, CEIL, FLOOR, NUMBOOL, NOTNUMBOOL).

    Returns:
        The transformed quantity.
    """
    mutate_upper = mutate.upper() if isinstance(mutate, str) else "NONE"

    if mutate_upper == "CEIL":
        return math.ceil(qty)
    elif mutate_upper == "FLOOR":
        return math.floor(qty)
    elif mutate_upper == "NUMBOOL":
        # If qty equals 0, leave it at 0. Else, set it to 1.
        return 0.0 if abs(qty) < 1e-9 else 1.0
    elif mutate_upper == "NOTNUMBOOL":
        # If qty equals 0, set it to 1. Else, set it to 0.
        return 1.0 if qty == 0 else 0.0
    else:  # NONE or any unrecognized value
        return qty


def _parse_numeric(value: Any, default: float = 0) -> float:
    """
    Parse a numeric value, supporting fractions like '1/1048576'.

    This function handles the 'factor' field in scenario YAML files which uses
    fraction notation (e.g., '1/1048576' to convert bytes to MiB) to match
    CloudKitty/chargeback documentation standards. Without this parser,
    fraction strings would cause ValueError when passed to float(), silently
    dropping metrics from the output summary.

    Args:
        value: The value to parse (can be number, string, or fraction string)
        default: Default value if parsing fails

    Returns:
        Parsed float value
    """
    if value is None:
        return default

    # If it's already a number, convert directly
    if isinstance(value, (int, float)):
        return float(value)

    # If it's a string, check for fraction notation (e.g., "1/1048576")
    if isinstance(value, str):
        value = value.strip()
        if '/' in value:
            try:
                parts = value.split('/')
                if len(parts) == 2:
                    numerator = float(parts[0].strip())
                    denominator = float(parts[1].strip())
                    if denominator != 0:
                        return numerator / denominator
            except (ValueError, ZeroDivisionError):
                pass
        # Try direct conversion
        try:
            return float(value)
        except ValueError:
            pass

    return default


def aggregate_rates_by_type(
    pairs: list[tuple[str, str]],
) -> tuple[dict, float, dict]:
    rate_sums: defaultdict[str, float] = defaultdict(float)
    qty_sums: defaultdict[str, float] = defaultdict(float)
    for _, log_str in pairs:
        try:
            entry = json.loads(log_str)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        mtype = entry.get("type")
        if not isinstance(mtype, str) or not mtype:
            mtype = "unknown"
        try:
            qty = _parse_numeric(entry.get("qty"), 0)
            price = _parse_numeric(entry.get("price"), 0)
            factor = _parse_numeric(entry.get("factor"), 1)
            offset = _parse_numeric(entry.get("offset"), 0)
            mutate = entry.get("mutate", "NONE")
        except (TypeError, ValueError):
            continue

        # Track raw qty sum (before any transformation)
        qty_sums[mtype] += qty

        # Apply mutate transformation for rating calculation
        qty_mutated = _apply_mutate(qty, mutate)

        # Apply factor and offset
        qty_rate = qty_mutated * factor + offset

        # Calculate rate
        rate_sums[mtype] += qty_rate * price

    by_types = {
        k: {"Rate": round(v, 4)} for k, v in sorted(rate_sums.items())
    }
    qty_by_types = {
        k: {"qty_sum": round(v, 4)} for k, v in sorted(qty_sums.items())
    }
    total = sum(rate_sums.values())
    return by_types, total, qty_by_types


def build_summary(pairs: list[tuple[str, str]]) -> dict[str, Any]:
    log_count = len(pairs)
    per_ts = Counter(ts for ts, _ in pairs)
    n_ts = len(per_ts)
    counts = list(per_ts.values())
    mps: Any = counts[0] if counts else 0
    if counts and len(set(counts)) > 1:
        mps = "ERROR"

    if pairs:
        first = json.loads(pairs[0][1])
        last = json.loads(pairs[-1][1])
        time_block = {
            "begin_step": {
                "nanosec": int(pairs[0][0]),
                "begin": first.get("start"),
                "end": first.get("end"),
            },
            "end_step": {
                "nanosec": int(pairs[-1][0]),
                "begin": last.get("start"),
                "end": last.get("end"),
            },
        }
    else:
        empty = {"nanosec": None, "begin": None, "end": None}
        time_block = {"begin_step": empty.copy(), "end_step": empty.copy()}

    by_types, total_r, qty_by_types = aggregate_rates_by_type(pairs)
    return {
        "time": time_block,
        "data_log": {
            "total_timesteps": n_ts,
            "metrics_per_step": mps,
            "log_count": log_count,
            "qty_by_types": qty_by_types,
        },
        "rate": {
            "by_types": by_types,
            "total": {"Rating": round(total_r, 4)},
        },
    }


def write_yaml(path: Path, doc: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write("---\n")
        yaml.dump(
            doc,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize Loki JSON log entries to YAML (time, data_log, rate)."
        ),
    )
    parser.add_argument(
        "-j", "--json", required=True, type=Path, help="Input JSON.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output YAML (default: <input_stem>_total.yml).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help=(
            "Enable debug mode: write <stem>_diff.txt with one "
            "[ts,log] JSON per line."
        ),
    )
    parser.add_argument(
        "--debug_dir",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "Directory for debug output. If not specified, uses the "
            "directory from -o output path."
        ),
    )
    args = parser.parse_args()

    if not args.json.exists():
        print(f"Error: input file not found: {args.json}", file=sys.stderr)
        sys.exit(1)

    stem = args.json.stem
    out_path = args.output or (args.json.parent / f"{stem}_total.yml")
    pairs = extract_and_sort(args.json)

    if args.debug:
        # Determine debug directory: use --debug_dir if provided,
        # otherwise use output directory
        debug_dir = args.debug_dir if args.debug_dir else out_path.parent
        debug_dir.mkdir(parents=True, exist_ok=True)
        dbg_file = debug_dir / f"{args.json.stem}_diff.txt"
        with dbg_file.open("w", encoding="utf-8") as f:
            for ts, log_str in pairs:
                print(json.dumps([ts, log_str], ensure_ascii=False), file=f)

    doc = build_summary(pairs)
    write_yaml(out_path, doc)

    if doc["data_log"]["metrics_per_step"] == "ERROR":
        per_ts = Counter(ts for ts, _ in pairs)
        exp = next(iter(per_ts.values()), 0)
        for ts in sorted(per_ts, key=int):
            if per_ts[ts] != exp:
                print(ts, per_ts[ts], file=sys.stdout)


if __name__ == "__main__":
    main()
