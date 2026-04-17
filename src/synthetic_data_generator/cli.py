import argparse
import csv
import sys

from faker import Faker

DEFAULT_LOCALE = "en_GB"
VALID_LOCALES = "https://faker.readthedocs.io/en/latest/locales.html"

REDSHIFT_TYPES = {
    "SMALLINT": "smallint",
    "INTEGER": "integer",
    "BIGINT": "bigint",
    "DECIMAL": "decimal",
    "REAL": "real",
    "DOUBLE PRECISION": "double",
    "CHAR": "text",
    "VARCHAR": "text",
    "DATE": "date",
    "TIME": "time",
    "TIMETZ": "time",
    "TIMESTAMP": "datetime",
    "TIMESTAMPTZ": "datetime",
    "BOOLEAN": "boolean",
}


def get_generator(field_type: str):
    return REDSHIFT_TYPES.get(field_type.upper())


def parse_fields_spec(fields_file: str, delimiter: str) -> list[dict]:
    with open(fields_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)

    if not rows:
        raise ValueError("Fields spec file is empty")

    required = {"field_name", "field_type"}
    first_row = rows[0]
    if not required.issubset(first_row.keys()):
        missing = required - set(first_row.keys())
        raise ValueError(f"Missing required columns: {missing}")

    return rows


def generate_value(faker: Faker, field_type: str, length: str | None) -> str:
    rs_type = get_generator(field_type)
    if rs_type is None:
        raise ValueError(f"Unsupported field type: {field_type}")

    if rs_type == "smallint":
        return str(faker.pyint(min_value=-32768, max_value=32767))
    elif rs_type == "integer":
        return str(faker.pyint(min_value=-2147483648, max_value=2147483647))
    elif rs_type == "bigint":
        return str(faker.pyint(min_value=-9223372036854775808, max_value=9223372036854775807))
    elif rs_type == "decimal":
        return str(faker.pydecimal(left_digits=10, right_digits=2, positive=True))
    elif rs_type == "real":
        return str(faker.pyfloat(positive=True))
    elif rs_type == "double":
        return str(faker.pyfloat(positive=True))
    elif rs_type == "text":
        max_len = int(length) if length else 255
        return faker.text(max_nb_chars=max_len)[:max_len]
    elif rs_type == "date":
        return str(faker.date())
    elif rs_type == "time":
        return str(faker.time())
    elif rs_type == "datetime":
        return str(faker.date_time())
    elif rs_type == "boolean":
        return str(faker.boolean()).lower()

    raise ValueError(f"Unsupported Redshift type: {rs_type}")


def generate_record(faker: Faker, fields_spec: list[dict], record_id: int) -> dict:
    record = {}
    for field in fields_spec:
        field_name = field["field_name"]
        field_type = field["field_type"]
        length = field.get("length")
        record[field_name] = generate_value(faker, field_type, length)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="syngen")
    parser.add_argument(
        "-n", "--number", type=int, default=10, help="Number of records to generate (default: 10)"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output.csv",
        help="Output file path (default: output.csv)",
    )
    parser.add_argument(
        "-s", "--separator", type=str, default=",", help="CSV field separator (default: ,)"
    )
    parser.add_argument(
        "-l",
        "--locale",
        type=str,
        default=DEFAULT_LOCALE,
        help=f"Faker locale (default: {DEFAULT_LOCALE}). See {VALID_LOCALES}",
    )
    parser.add_argument(
        "-f",
        "--fields-file",
        type=str,
        required=True,
        help="Path to fields spec CSV file (required)",
    )
    parser.add_argument(
        "--input-separator",
        type=str,
        default=",",
        help="Separator for input spec CSV (default: ,)",
    )
    args = parser.parse_args(argv)

    if args.number < 1:
        print("Error: number must be at least 1", file=sys.stderr)
        return 1

    try:
        faker = Faker(args.locale)
    except Exception:
        print(f"Error: Invalid locale '{args.locale}'. See {VALID_LOCALES}", file=sys.stderr)
        return 1

    try:
        fields_spec = parse_fields_spec(args.fields_file, args.input_separator)
    except FileNotFoundError:
        print(f"Error: Fields spec file not found: {args.fields_file}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    fieldnames = [field["field_name"] for field in fields_spec]

    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=args.separator)
            writer.writeheader()
            for i in range(1, args.number + 1):
                try:
                    writer.writerow(generate_record(faker, fields_spec, i))
                except ValueError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    return 1
        print(f"Generated {args.number} records to {args.output}")
    except OSError as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
