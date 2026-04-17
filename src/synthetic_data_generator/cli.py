import argparse
import csv
import sys


from faker import Faker

DEFAULT_LOCALE = "en_GB"
VALID_LOCALES = "https://faker.readthedocs.io/en/latest/locales.html"


def generate_record(faker: Faker, record_id: int) -> dict:
    return {
        "id": record_id,
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "house_number": faker.building_number(),
        "street": faker.street_address(),
        "city": faker.city(),
        "postcode": faker.postcode(),
        "telephone": faker.msisdn(),
    }


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
    args = parser.parse_args(argv)

    if args.number < 1:
        print("Error: number must be at least 1", file=sys.stderr)
        return 1

    try:
        faker = Faker(args.locale)
    except Exception:
        print(f"Error: Invalid locale '{args.locale}'. See {VALID_LOCALES}", file=sys.stderr)
        return 1

    fieldnames = [
        "id",
        "first_name",
        "last_name",
        "house_number",
        "street",
        "city",
        "postcode",
        "telephone",
    ]

    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=args.separator)
            writer.writeheader()
            for i in range(1, args.number + 1):
                writer.writerow(generate_record(faker, i))
        print(f"Generated {args.number} records to {args.output}")
    except OSError as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
