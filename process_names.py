"""
Note: Claude wrote this code for me.

process_names.py

Reads all SSA baby name files (yob1880.txt through yob2025.txt) and
combines them into a single JSON file (names_data.json) for use by
the web app.

USAGE:
  1. Place this script in the same folder as your "names/" directory
     (or adjust DATA_DIR below to point at wherever your yobYYYY.txt
     files live).
  2. Run:  python process_names.py
  3. It will create names_data.json in the same folder.
  4. Copy names_data.json into your GitHub repo's web app folder.

REQUIREMENTS:
  Python 3.6+. No third-party libraries needed.

OUTPUT FORMAT:
  A JSON object keyed by 4-digit year strings. Each year contains
  two keys, "M" and "F", each holding a list of [name, count] pairs.
  Counts are integers. Example:

  {
    "1880": {
      "F": [["Mary", 7065], ["Anna", 2604], ...],
      "M": [["John", 9655], ["William", 9532], ...]
    },
    "1881": { ... },
    ...
  }

  Within each sex, names are in their original order (descending by
  count, ties broken alphabetically) — this matches the source files.
  Order doesn't affect the weighted random selection but preserves
  rank information if you ever want it.
"""

import os
import json

# --- Configuration ---

# Folder containing your yobYYYY.txt files.
# "." means the same directory as this script.
# Change this if your files are in a subfolder, e.g. "names" or "data/ssa".
DATA_DIR = "national-data"

# Year range to process. Adjust if you ever get updated files.
FIRST_YEAR = 1880
LAST_YEAR = 2025

# Where to write the output.
OUTPUT_FILE = "names_data.json"

# --- Main logic ---

def parse_year(filepath):
    """
    Reads one yobYYYY.txt file and returns a dict with keys "M" and "F",
    each containing a list of [name, count] pairs.

    Each line in the file looks like:  Emma,F,20355
    The file has no header row.
    """
    result = {"M": [], "F": []}

    with open(filepath, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue  # skip any blank lines

            parts = line.split(",")

            # Basic sanity check: every line should have exactly 3 fields.
            if len(parts) != 3:
                print(f"  WARNING: unexpected format on line {line_number} of {filepath}: {line!r}")
                continue

            name, sex, count_str = parts

            # Sex should be M or F. Skip anything else with a warning.
            if sex not in ("M", "F"):
                print(f"  WARNING: unknown sex {sex!r} on line {line_number} of {filepath}")
                continue

            # Count should be a positive integer.
            try:
                count = int(count_str)
            except ValueError:
                print(f"  WARNING: non-integer count {count_str!r} on line {line_number} of {filepath}")
                continue

            result[sex].append([name, count])

    return result


def main():
    all_data = {}
    missing = []

    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        filename = f"yob{year}.txt"
        filepath = os.path.join(DATA_DIR, filename)

        if not os.path.exists(filepath):
            # You told me there are no missing files, but this catches
            # any future gaps or misconfigured DATA_DIR.
            missing.append(year)
            print(f"MISSING: {filepath}")
            continue

        year_data = parse_year(filepath)

        # Warn if either sex has zero names for a year (shouldn't happen).
        for sex in ("M", "F"):
            if not year_data[sex]:
                print(f"  WARNING: no {sex} names found for {year}")

        all_data[str(year)] = year_data  # JSON keys must be strings

    # Summary
    processed = len(all_data)
    print(f"\nProcessed {processed} year(s).")
    if missing:
        print(f"Missing files for years: {missing}")

    # Write output
    print(f"Writing {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # separators=(",", ":") removes whitespace for a smaller file.
        # Remove that argument if you want human-readable output for debugging.
        json.dump(all_data, f, separators=(",", ":"))

    print("Done.")

    # Print a rough size estimate so you know what to expect.
    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"Output file size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
