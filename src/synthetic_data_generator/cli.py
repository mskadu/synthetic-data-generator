import argparse
import csv
import random
import sys

FIRST_NAMES = [
    "James",
    "Mary",
    "John",
    "Patricia",
    "Robert",
    "Jennifer",
    "Michael",
    "Linda",
    "William",
    "Elizabeth",
    "David",
    "Barbara",
    "Richard",
    "Susan",
    "Joseph",
    "Jessica",
    "Thomas",
    "Sarah",
    "Charles",
    "Karen",
    "Christopher",
    "Nancy",
    "Daniel",
    "Lisa",
    "Matthew",
    "Margaret",
    "Anthony",
    "Betty",
    "Mark",
    "Sandra",
    "Donald",
    "Ashley",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
    "Harris",
    "Sanchez",
    "Clark",
    "Ramirez",
    "Lewis",
    "Robinson",
    "Walker",
]

UK_CITIES = [
    ("London", "SW1A 1AA"),
    ("Birmingham", "B1 1AA"),
    ("Manchester", "M1 1AA"),
    ("Leeds", "LS1 1AA"),
    ("Glasgow", "G1 1AA"),
    ("Liverpool", "L1 1AA"),
    ("Bristol", "BS1 1AA"),
    ("Sheffield", "S1 1AA"),
    ("Leicester", "LE1 1AA"),
    ("Edinburgh", "EH1 1AA"),
    ("Cardiff", "CF10 1AA"),
    ("Belfast", "BT1 1AA"),
    ("Newcastle", "NE1 1AA"),
    ("Nottingham", "NG1 1AA"),
    ("Southampton", "SO14 1AA"),
]

STREET_NAMES = [
    "High Street",
    "Station Road",
    "London Road",
    "Manor Road",
    "Church Lane",
    "Victoria Road",
    "Albert Street",
    "Park Avenue",
    "Kings Road",
    "Queens Way",
    "St Marys Road",
    "Windsor Road",
    "Oxford Street",
    "Cambridge Road",
    "York Road",
]


def generate_name() -> tuple[str, str]:
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


def generate_uk_address() -> dict:
    house_number = random.randint(1, 200)
    city, postcode = random.choice(UK_CITIES)
    return {
        "house_number": house_number,
        "street": random.choice(STREET_NAMES),
        "city": city,
        "postcode": postcode,
    }


def generate_telephone() -> str:
    prefixes = ["07", "01onal", "01onb", "01onf", "011x", "0121", "0131", "0141", "0151", "0161"]
    prefix = random.choice(prefixes)
    if prefix.startswith("07"):
        return f"07{random.randint(100000000, 999999999)}"
    return f"01{random.randint(1000000, 9999999)}"


def generate_record(record_id: int) -> dict:
    first_name, last_name = generate_name()
    address = generate_uk_address()
    return {
        "id": record_id,
        "first_name": first_name,
        "last_name": last_name,
        "house_number": address["house_number"],
        "street": address["street"],
        "city": address["city"],
        "postcode": address["postcode"],
        "telephone": generate_telephone(),
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
    args = parser.parse_args(argv)

    if args.number < 1:
        print("Error: number must be at least 1", file=sys.stderr)
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
                writer.writerow(generate_record(i))
        print(f"Generated {args.number} records to {args.output}")
    except OSError as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
