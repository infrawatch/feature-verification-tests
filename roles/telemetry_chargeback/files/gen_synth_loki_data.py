"""Generate synthetic Loki log data from a Jinja2 template."""
import logging
import argparse
import json
import yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Union
from jinja2 import Environment


def _get_value_for_step(
    values: List[Union[int, float]],
    step_idx: int,
    num_steps: int
) -> Union[int, float]:
    """
    Get the appropriate value from a list based on the current step index.

    Values are distributed evenly across all steps. For example, if there are
    12 steps and 4 values, each value covers 3 steps:
    - Steps 0-2: values[0]
    - Steps 3-5: values[1]
    - Steps 6-8: values[2]
    - Steps 9-11: values[3]

    Args:
        values: List of values to choose from.
        step_idx: Current step index (0-based).
        num_steps: Total number of steps.

    Returns:
        The value corresponding to the current step.
    """
    num_values = len(values)
    if num_values == 1:
        return values[0]

    # Calculate how many steps each value covers
    steps_per_value = num_steps / num_values
    # Determine which value index to use, clamping to valid range
    value_idx = min(int(step_idx // steps_per_value), num_values - 1)
    return values[value_idx]


# --- Configure logging with a default level that can be changed ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S+00:00'
)
logger = logging.getLogger()


def _format_timestamp(epoch_seconds: float, invalid_timestamp: str) -> str:
    """
    Convert an epoch timestamp into a human-readable UTC string.

    Args:
        epoch_seconds (float): The timestamp in seconds since the epoch.
        invalid_timestamp (str): String to return for invalid timestamps.

    Returns:
        str: The formatted datetime string (e.g., "2023-10-26T14:30:00+00:00").
    """
    try:
        dt_object = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        return dt_object.isoformat()
    except (ValueError, TypeError):
        logger.warning(f"Invalid epoch value provided: {epoch_seconds}")
        return invalid_timestamp


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the config file.

    Returns:
        Dict containing configuration values.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file cannot be parsed.
    """
    if not config_path.exists():
        logger.error(f"Config file not found at {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with config_path.open('r') as f:
            config = yaml.safe_load(f)
        logger.debug(f"Loaded config from {config_path}")
        if not config:
            raise ValueError(f"Config file {config_path} is empty")
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file {config_path}: {e}")
        raise ValueError(f"Error parsing config file: {e}")


def generate_loki_data(
    template_path: Path,
    output_path: Path,
    start_time: datetime,
    end_time: datetime,
    time_step_seconds: int,
    config: Dict[str, Any]
):
    """
    Generate synthetic Loki log data by preparing a data list and rendering.

    Args:
        template_path (Path): Path to the main log template file.
        output_path (Path): Path for the generated output JSON file.
        start_time (datetime): The start time for data generation.
        end_time (datetime): The end time for data generation.
        time_step_seconds (int): The duration of each log entry in seconds.
        config (Dict[str, Any]): Configuration dictionary loaded from file.
    """
    # Hardcoded constant for invalid timestamps
    invalid_timestamp = "INVALID_TIMESTAMP"

    # --- Step 1: Generate the data structure first ---
    logger.info(
        f"Generating data from {start_time.strftime('%Y-%m-%d')} to "
        f"{end_time.strftime('%Y-%m-%d')} with a {time_step_seconds}s step."
    )
    start_epoch = int(start_time.timestamp())
    end_epoch = int(end_time.timestamp())
    logger.debug(f"Time range in epoch seconds: {start_epoch} to {end_epoch}")

    log_data_list = []  # This list will hold all our data points

    # Loop through the time range and generate data points
    for current_epoch in range(
        start_epoch,
        end_epoch - time_step_seconds,
        time_step_seconds
    ):
        end_of_step_epoch = min(
            current_epoch + time_step_seconds - 1, end_epoch - 1)

        # Prepare replacement values
        nanoseconds = int(current_epoch * 1_000_000_000)
        start_str = _format_timestamp(current_epoch, invalid_timestamp)
        end_str = _format_timestamp(end_of_step_epoch, invalid_timestamp)

        logger.debug(
            f"Processing epoch: {current_epoch} -> nanoseconds: {nanoseconds}"
        )

        # Create a dictionary for this time step and add it to the list
        log_data_list.append({
            "nanoseconds": nanoseconds,
            "start_time": start_str,
            "end_time": end_str
        })

    # Add final entry that ends at end_epoch (current time)
    if log_data_list and end_epoch > start_epoch:
        # Calculate start of final entry based on end of last generated entry
        last_entry_end = log_data_list[-1]["end_time"]
        # Parse the last entry's end time to get the epoch
        last_end_dt = datetime.fromisoformat(last_entry_end)
        final_start_epoch = int(last_end_dt.timestamp()) + 1
        final_nanoseconds = int(final_start_epoch * 1_000_000_000)

        # Only add if the final entry would have a valid duration
        if final_start_epoch < end_epoch:
            log_data_list.append({
                "nanoseconds": final_nanoseconds,
                "start_time": _format_timestamp(
                    final_start_epoch, invalid_timestamp
                ),
                "end_time": _format_timestamp(end_epoch - 1, invalid_timestamp)
            })

    logger.info(f"Generated {len(log_data_list)} data points to be rendered.")

    # --- Step 2: Load log type configurations from config ---
    log_types_config = config.get("log_types", [])
    if not log_types_config:
        logger.error("No log_types configuration found in config.")
        raise ValueError("log_types section is required in config")

    if not isinstance(log_types_config, list):
        logger.error("log_types must be a list in config")
        raise ValueError("log_types must be a list")

    # Get required fields from config
    required_fields = config.get("required_fields", [])
    if not required_fields:
        logger.error("No required_fields configuration found in config")
        raise ValueError("required_fields section is required in config")

    # Get date field names from config
    date_field_names = config.get("date_fields", [])
    if not date_field_names:
        logger.error("No date_fields configuration found in config")
        raise ValueError("date_fields section is required in config")

    # Build log_types dictionary from config
    log_types = {}
    for log_type_config in log_types_config:
        if not isinstance(log_type_config, dict):
            logger.error(f"Invalid log type configuration: {log_type_config}")
            raise ValueError("Each log type in log_types must be a dictionary")

        log_type_name = log_type_config.get("name")
        if not log_type_name:
            logger.error("Each log type must have a 'name' field")
            raise ValueError("Each log type must have a 'name' field")

        # Validate required fields
        missing = [f for f in required_fields if f not in log_type_config]
        if missing:
            logger.error(
                f"Missing required fields in {log_type_name} config: {missing}"
            )
            raise ValueError(
                f"Missing required fields in {log_type_name}: {missing}"
            )

        # Build groupby from config
        groupby = log_type_config.get("groupby", {})
        if not isinstance(groupby, dict):
            logger.error(
                f"groupby must be a dictionary for {log_type_name}"
            )
            raise ValueError(
                f"groupby must be a dictionary for {log_type_name}"
            )

        # Ensure qty and price are lists for step-based distribution
        qty_val = log_type_config["qty"]
        price_val = log_type_config["price"]
        qty_list = qty_val if isinstance(qty_val, list) else [qty_val]
        price_list = price_val if isinstance(price_val, list) else [price_val]

        log_types[log_type_name] = {
            "type": log_type_config["type"],
            "unit": log_type_config["unit"],
            "description": log_type_config.get("description"),
            "qty": qty_list,
            "price": price_list,
            "groupby": groupby.copy(),
            "metadata": log_type_config.get("metadata", {})
        }

    # --- Step 3: Load template and render ---
    try:
        logger.info(f"Loading main template from: {template_path}")
        template_content = template_path.read_text()

        # Create Jinja2 environment with custom filter
        def tojson_preserve_order(obj):
            """Convert object to JSON string preserving dictionary order."""
            return json.dumps(obj, sort_keys=False, ensure_ascii=False)

        env = Environment(trim_blocks=True, lstrip_blocks=True)
        env.filters['tojson'] = tojson_preserve_order
        template = env.from_string(template_content)

    except FileNotFoundError as e:
        logger.error(f"Error loading template file: {e}. Aborting.")
        raise

    # --- Render the template in one pass with all the data ---
    logger.info("Rendering final output...")

    # Calculate total number of steps for value distribution
    num_steps = len(log_data_list)
    logger.debug(f"Total number of time steps: {num_steps}")

    # Pre-calculate log types with date fields for each time step
    log_types_list = []
    for idx, item in enumerate(log_data_list):
        epoch_seconds = item["nanoseconds"] / 1_000_000_000
        dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)

        iso_year, iso_week, _ = dt.isocalendar()
        day_of_year = dt.timetuple().tm_yday

        # Build date fields dynamically from config
        date_field_mapping = {
            "week_of_the_year": str(iso_week),
            "day_of_the_year": str(day_of_year),
            "month": str(dt.month),
            "year": str(dt.year)
        }

        date_fields = {}
        for field_name in date_field_names:
            if field_name in date_field_mapping:
                date_fields[field_name] = date_field_mapping[field_name]
            else:
                logger.warning(
                    f"Unknown date field name in config: {field_name}"
                )

        # Create log types with date fields for this time step
        log_types_with_dates = {}
        for log_type_name, log_type_data in log_types.items():
            log_type_with_dates = log_type_data.copy()
            log_type_with_dates["groupby"] = log_type_data["groupby"].copy()
            log_type_with_dates["groupby"].update(date_fields)
            # Select qty and price based on step index distribution
            log_type_with_dates["qty"] = _get_value_for_step(
                log_type_data["qty"], idx, num_steps
            )
            log_type_with_dates["price"] = _get_value_for_step(
                log_type_data["price"], idx, num_steps
            )
            log_types_with_dates[log_type_name] = log_type_with_dates

        log_types_list.append(log_types_with_dates)

    # Get loki_stream configuration
    loki_stream = config.get("loki_stream", {})
    if not loki_stream:
        logger.warning("No loki_stream configuration found, using defaults")
        loki_stream = {"service": "cloudkitty"}

    # Build template context with generic log type information
    template_context = {
        "log_data": log_data_list,
        "log_type_names": list(log_types.keys()),
        "all_log_entries": log_types_list,
        "loki_stream": loki_stream
    }

    final_output = template.render(**template_context)

    # --- Step 4: Write the final string to the file ---
    try:
        with output_path.open('w') as f_out:
            f_out.write(final_output)
        logger.info(
            f"Successfully generated synthetic data to '{output_path}'"
        )
    except IOError as e:
        logger.error(f"Failed to write to output file '{output_path}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during file write: {e}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic Loki log data from a main template.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # --- Required Arguments ---
    parser.add_argument(
        "--tmpl",
        required=True,
        help="Path to the main log template file."
    )
    parser.add_argument(
        "-t", "--test",
        type=Path,
        required=True,
        help="Path to YAML config file (e.g., scenario.yml)."
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Path to the output file."
    )

    # --- Optional Utility Arguments ---
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug level logging for verbose output."
    )
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled.")

    # Load config first to get generation parameters
    try:
        config = load_config(args.test)
    except (FileNotFoundError, ValueError) as e:
        logger.critical(f"Failed to load config: {e}")
        return

    # Get generation parameters from config
    generation_config = config.get("generation", {})
    days = generation_config.get("days", 30)
    step_seconds = generation_config.get("step_seconds", 300)

    # Define the time range for data generation
    end_time_utc = datetime.now(timezone.utc)
    start_time_utc = end_time_utc - timedelta(days=days)
    logger.debug(f"Time range calculated: {start_time_utc} to {end_time_utc}")

    # Run the generator
    try:
        generate_loki_data(
            template_path=Path(args.tmpl),
            output_path=Path(args.output),
            start_time=start_time_utc,
            end_time=end_time_utc,
            time_step_seconds=step_seconds,
            config=config
        )
    except FileNotFoundError:
        logger.error(
            "Process aborted because the template file was not found."
        )
    except Exception as e:
        logger.critical(f"A critical, unhandled error stopped the script: {e}")


if __name__ == "__main__":
    main()
