"""Data processing helpers for the Quantium simulation project."""

import csv
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterator, Optional, Union

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_OUTPUT_FILE = DEFAULT_DATA_DIR / "pink_sales_data.csv"
OUTPUT_FIELDNAMES = ["date", "region", "sales"]


def read_sales_rows(
    data_dir: Union[str, Path] = DEFAULT_DATA_DIR,
) -> Iterator[Dict[str, str]]:
    """Yield sales rows from all daily sales CSV files in order."""
    base_path = Path(data_dir)

    for csv_path in sorted(base_path.glob("daily_sales_data_*.csv")):
        with csv_path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            yield from reader


def row_processor(row: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Clean and transform a single raw sales row."""
    if row["product"].strip().lower() != "pink morsel":
        return None

    price = Decimal(row["price"].replace("$", ""))
    quantity = int(row["quantity"])

    return {
        "date": row["date"],
        "region": row["region"].strip().lower(),
        "sales": f"{price * quantity:.2f}",
    }


def sales_processor(
    data_dir: Union[str, Path] = DEFAULT_DATA_DIR,
    output_file: Union[str, Path] = DEFAULT_OUTPUT_FILE,
) -> Path:
    """Read raw sales rows, clean them, and write a processed CSV."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()

        for row in read_sales_rows(data_dir):
            processed_row = row_processor(row)
            if processed_row is not None:
                writer.writerow(processed_row)

    return output_path


def main() -> None:
    """Process the sales data files and print the output path."""
    output_path = sales_processor()
    print(f"Wrote processed data to {output_path}")


if __name__ == "__main__":
    main()
