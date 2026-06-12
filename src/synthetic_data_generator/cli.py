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

FIELD_PROVIDER_MAP: dict[str, str] = {
    "email": "email",
    "first_name": "first_name",
    "last_name": "last_name",
    "name": "name",
    "full_name": "name",
    "username": "user_name",
    "phone": "phone_number",
    "telephone": "phone_number",
    "mobile": "phone_number",
    "city": "city",
    "postcode": "postcode",
    "post_code": "postcode",
    "zip": "postcode",
    "address": "address",
    "street": "street_address",
    "country": "country",
    "company": "company",
    "url": "url",
    "website": "url",
    "job": "job",
    "title": "job",
    "occupation": "job",
    "uuid": "uuid4",
}


def create_generator(field_type: str, length: str | None, field_name: str = ""):
    rs_type = REDSHIFT_TYPES.get(field_type.upper())
    if rs_type is None:
        raise ValueError(f"Unsupported field type: {field_type}")

    if rs_type == "smallint":
        min_val, max_val = -32768, 32767
        return lambda f: str(f.pyint(min_value=min_val, max_value=max_val))
    elif rs_type == "integer":
        min_val, max_val = -2147483648, 2147483647
        return lambda f: str(f.pyint(min_value=min_val, max_value=max_val))
    elif rs_type == "bigint":
        min_val, max_val = -9223372036854775808, 9223372036854775807
        return lambda f: str(f.pyint(min_value=min_val, max_value=max_val))
    elif rs_type == "decimal":
        return lambda f: str(f.pydecimal(left_digits=10, right_digits=2, positive=True))
    elif rs_type == "real":
        return lambda f: str(f.pyfloat(positive=True))
    elif rs_type == "double":
        return lambda f: str(f.pyfloat(positive=True))
    elif rs_type == "text":
        max_len = int(length) if length else 255
        provider = next(
            (v for k, v in FIELD_PROVIDER_MAP.items() if k in field_name.lower()),
            None,
        )
        if provider:
            return lambda f: str(getattr(f, provider)())[:max_len]
        return lambda f: f.text(max_nb_chars=max_len)[:max_len]
    elif rs_type == "date":
        return lambda f: f.date()
    elif rs_type == "time":
        return lambda f: f.time()
    elif rs_type == "datetime":
        return lambda f: str(f.date_time())
    elif rs_type == "boolean":
        return lambda f: str(f.boolean()).lower()

    raise ValueError(f"Unsupported Redshift type: {rs_type}")


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
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for reproducible output",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output message",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Write to stdout instead of a file",
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

    if args.seed is not None:
        faker.seed_instance(args.seed)

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
        generators = [
            create_generator(field["field_type"], field.get("length"), field["field_name"])
            for field in fields_spec
        ]
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        if args.stdout:
            outfile = sys.stdout
        else:
            outfile = open(args.output, "w", newline="", encoding="utf-8")

        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=args.separator)
        writer.writeheader()
        for _ in range(args.number):
            row = {fieldnames[j]: generators[j](faker) for j in range(len(fieldnames))}
            writer.writerow(row)

        if not args.stdout:
            outfile.close()

        if not args.quiet:
            dest = "stdout" if args.stdout else args.output
            print(f"Generated {args.number} records to {dest}")
    except OSError as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
