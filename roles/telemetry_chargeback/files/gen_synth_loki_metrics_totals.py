#!/usr/bin/env python3
"""
Calculate metric totals and aggregate total from a Loki JSON file.

Output is in YAML format.
"""
import json
import argparse
import sys
import yaml
from pathlib import Path


def calculate_totals(json_path: Path, output_path: Path):
    """
    Read Loki JSON, calculate step totals (qty * price), and sum them up.

    Args:
        json_path: Path to the input JSON file.
        output_path: Path to the output YAML file.
    """
    try:
        with json_path.open('r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file {json_path}: {e}")
        sys.exit(1)

    metric_totals = {}
    aggregate_total = 0.0
    time_steps_set = set()
    log_count = 0
    # Per-timestamp start/end from log entries (same for all entries at step)
    time_step_bounds = {}

    # Extract values from the Loki JSON structure
    for stream in data.get('streams', []):
        for val_pair in stream.get('values', []):
            log_count += 1
            try:
                # The first element is the timestamp (nanoseconds)
                timestamp = val_pair[0]
                time_steps_set.add(timestamp)

                # The second element is a JSON string containing the log entry
                entry = json.loads(val_pair[1])

                # Start/end for this time step (same for all entries at step)
                if timestamp not in time_step_bounds:
                    time_step_bounds[timestamp] = {
                        "begin": entry.get("start"),
                        "end": entry.get("end"),
                    }

                m_type = entry.get('type')
                if m_type is None:
                    m_type = 'unknown'

                qty = float(entry.get('qty', 0))
                price = float(entry.get('price', 0))

                step_total = qty * price

                if m_type not in metric_totals:
                    metric_totals[m_type] = 0.0

                metric_totals[m_type] += step_total
                aggregate_total += step_total
            except (json.JSONDecodeError, ValueError, IndexError) as e:
                print(f"Warning: Skipping malformed entry: {e}")
                continue

    # First and last time step timestamps (order by numeric value)
    sorted_ts = (
        sorted(time_steps_set, key=lambda t: int(t)) if time_steps_set else []
    )
    timestamp_begin = (
        time_step_bounds[sorted_ts[0]]["begin"] if sorted_ts else None
    )
    timestamp_end = (
        time_step_bounds[sorted_ts[-1]]["end"] if sorted_ts else None
    )

    # Prepare data for YAML output with time section and rates.
    # log_count = total [timestamp, log_entry] pairs. When each timestep has the
    # same number of metrics, log_count == total_time_steps * metrics_per_step.
    total_time_steps = len(time_steps_set)
    metrics_per_step = (
        log_count // total_time_steps if total_time_steps > 0 else 0
    )
    if total_time_steps > 0 and log_count % total_time_steps != 0:
        print(
            f"Warning: log_count ({log_count}) is not divisible by "
            f"total_time_steps ({total_time_steps}). "
            "Expected log_count = total_time_steps × metrics_per_step."
        )

    synth_rate = {
        m: round(t, 4) for m, t in sorted(metric_totals.items())
    }
    synth_rate["total_rate"] = round(aggregate_total, 4)

    output_data = {
        "time": {
            "begin": timestamp_begin,
            "end": timestamp_end,
        },
        "data_log": {
            "total_time_steps": total_time_steps,
            "metrics_per_step": metrics_per_step,
            "log_count": log_count,
        },
        "synth_rate": synth_rate,
    }

    # Write to output file in YAML format
    try:
        with output_path.open('w') as f_out:
            f_out.write("---\n")
            yaml.dump(
                output_data, f_out, default_flow_style=False, sort_keys=False
            )
        print(
            f"Successfully calculated totals and wrote YAML to {output_path}"
        )
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Calculate totals from Loki JSON data"
    )
    parser.add_argument(
        "-j", "--json", required=True, type=Path,
        help="Path to the input JSON file."
    )
    parser.add_argument(
        "-o", "--output", required=True, type=Path,
        help="Path to the output YAML file."
    )

    args = parser.parse_args()
    calculate_totals(args.json, args.output)


if __name__ == "__main__":
    main()
