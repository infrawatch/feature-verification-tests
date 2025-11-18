import logging
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Union
from jinja2 import Template

# --- Configure logging with a default level that can be changed ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S+00:00'
)
logger = logging.getLogger()

def _format_timestamp(epoch_seconds: float) -> str:
    """
    Converts an epoch timestamp into a human-readable UTC string.

    Args:
        epoch_seconds (float): The timestamp in seconds since the epoch.

    Returns:
        str: The formatted datetime string (e.g., "2023-10-26T14:30:00+00:00").
    """
    try:
        dt_object = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        return dt_object.isoformat()
    except (ValueError, TypeError):
        logger.warning(f"Invalid epoch value provided: {epoch_seconds}")
        return "INVALID_TIMESTAMP"

def generate_loki_data(
    template_path: Path,
    output_path: Path,
    start_time: datetime,
    end_time: datetime,
    time_step_seconds: int
):
    """
    Generates synthetic Loki log data by first preparing a data list
    and then rendering it with a single template.

    Args:
        template_path (Path): Path to the main log template file.
        output_path (Path): Path for the generated output JSON file.
        start_time (datetime): The start time for data generation.
        end_time (datetime): The end time for data generation.
        time_step_seconds (int): The duration of each log entry in seconds.
    """
    
    # --- Step 1: Generate the data structure first ---
    logger.info(
        f"Generating data from {start_time.strftime('%Y-%m-%d')} to "
        f"{end_time.strftime('%Y-%m-%d')} with a {time_step_seconds}s step."
    )
    start_epoch = int(start_time.timestamp())
    end_epoch = int(end_time.timestamp())
    logger.debug(f"Time range in epoch seconds: {start_epoch} to {end_epoch}")

    log_data_list = [] # This list will hold all our data points

    # Loop through the time range and generate data points
    for current_epoch in range(start_epoch, end_epoch, time_step_seconds):
        end_of_step_epoch = current_epoch + time_step_seconds - 1

        # Prepare replacement values
        nanoseconds = int(current_epoch * 1_000_000_000)
        start_str = _format_timestamp(current_epoch)
        end_str = _format_timestamp(end_of_step_epoch)

        logger.debug(f"Processing epoch: {current_epoch} -> nanoseconds: {nanoseconds}")

        # Create a dictionary for this time step and add it to the list
        log_data_list.append({
            "nanoseconds": nanoseconds,
            "start_time": start_str,
            "end_time": end_str
        })

    logger.info(f"Generated {len(log_data_list)} data points to be rendered.")

    # --- Step 2: Load template and render ---
    try:
        logger.info(f"Loading main template from: {template_path}")
        template_content = template_path.read_text()
        template = Template(template_content, trim_blocks=True, lstrip_blocks=True)

    except FileNotFoundError as e:
        logger.error(f"Error loading template file: {e}. Aborting.")
        raise # Re-raise the exception to be caught in main()

    # --- Render the template in one pass with all the data ---
    logger.info("Rendering final output...")
    # The template expects a variable named 'log_data'
    final_output = template.render(log_data=log_data_list)
    
    # --- Step 3: Write the final string to the file ---
    try:
        with output_path.open('w') as f_out:
            f_out.write(final_output)
        logger.info(f"Successfully generated synthetic data to '{output_path}'")
    except IOError as e:
        logger.error(f"Failed to write to output file '{output_path}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during file write: {e}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic Loki log data from a single main template.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # --- Required File Path Arguments ---
    parser.add_argument("-o", "--output", required=True, help="Path to the output file.")
    # --- Only one template argument is needed now ---
    parser.add_argument("--template", required=True, help="Path to the main log template file (e.g., loki_main.tmpl).")

    # --- Optional Generation Arguments ---
    parser.add_argument("--days", type=int, default=30, help="How many days of data to generate, ending today.")
    parser.add_argument("--step", type=int, default=300, help="Time step in seconds for each log entry.")
    
    # --- Optional Utility Arguments ---
    parser.add_argument("--debug", action="store_true", help="Enable debug level logging for verbose output.")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled.")

    # Define the time range for data generation
    end_time_utc = datetime.now(timezone.utc)
    start_time_utc = end_time_utc - timedelta(days=args.days)
    logger.debug(f"Time range calculated: {start_time_utc} to {end_time_utc}")

    # Run the generator
    try:
        generate_loki_data(
            template_path=Path(args.template),
            output_path=Path(args.output),
            start_time=start_time_utc,
            end_time=end_time_utc,
            time_step_seconds=args.step
        )
    except FileNotFoundError:
        logger.error("Process aborted because the template file was not found.")
    except Exception as e:
        logger.critical(f"A critical, unhandled error stopped the script: {e}")


if __name__ == "__main__":
    main()
