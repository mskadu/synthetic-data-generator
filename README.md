# synthetic-data-generator

Generate realistic test data as CSV, ready for database loading. Define your columns in a simple "fields spec" CSV file, and syngen fills in the rows.

```csv
field_name,field_type,length
name,VARCHAR,100
email,VARCHAR,100
signup_date,DATE,
```

Run it:

```bash
syngen -f my-spec.csv -n 5
```

You get back a CSV with realistic names, email addresses, and dates. No configuration, no boilerplate.

## Prerequisites

- **Python 3.10+**
- **uv** (recommended) or pip

## Installation

```bash
uv pip install -e .
```

## Quick start

Write a fields spec CSV. Each row describes one column in your output:

```csv
field_name,field_type,length
first_name,VARCHAR,50
last_name,VARCHAR,50
email,VARCHAR,100
signup_date,DATE,
is_active,BOOLEAN,
salary,DECIMAL,
```

Pass it to syngen:

```bash
syngen -f my-spec.csv
```

That generates 10 rows of realistic data. The output file is `output.csv` by default.

Fields with names like `email`, `first_name`, and `phone` automatically produce matching realistic values. Unknown names fall back to text. More on that in the [smart VARCHAR section](#smart-varchar).

VARCHAR and CHAR also respect the `length` column -- values longer than that get truncated.

## Examples

```bash
syngen -f spec.csv                          # 10 records
syngen -f spec.csv -n 100                   # 100 records
syngen -f spec.csv -o data.csv              # Write to data.csv
syngen -f spec.csv -s "|"                   # Pipe-separated output
syngen -f spec.csv --input-separator "|"    # Pipe-separated input spec
syngen -f spec.csv -o data.csv -s "|" -n 50 # All options together
```

| Flag | Description | Default |
|------|-------------|---------|
| `-n`, `--number` | Number of records to generate | 10 |
| `-o`, `--output` | Output file path | output.csv |
| `-s`, `--separator` | CSV field separator for output | , |
| `-l`, `--locale` | Faker locale (see [supported values](https://faker.readthedocs.io/en/latest/locales.html)) | en_GB |
| `-f`, `--fields-file` | **Required** - Path to fields spec CSV file | - |
| `--input-separator` | Separator for input spec CSV | , |
| `--seed` | Seed for reproducible output (same seed = same data) | - |
| `--quiet` | Suppress "Generated X records to Y" message | - |
| `--stdout` | Write CSV to stdout instead of a file | - |

## Supported data types

| Category | Types |
|----------|-------|
| Numeric | SMALLINT, INTEGER, BIGINT, DECIMAL, REAL, DOUBLE PRECISION |
| String | CHAR, VARCHAR |
| DateTime | DATE, TIME, TIMETZ, TIMESTAMP, TIMESTAMPTZ |
| Boolean | BOOLEAN |
| Enum | ENUM |

For ENUM fields, the `length` column contains pipe-separated choices:

```csv
field_name,field_type,length
status,ENUM,active|inactive|pending
priority,ENUM,low|medium|high|critical
```

Each row gets a random value from the specified choices.

## Smart VARCHAR

VARCHAR and CHAR fields automatically detect field names and generate realistic values using the matching Faker provider:

| Name pattern | Generates | Example |
|-------------|-----------|---------|
| `email` | Email address | `john.doe@example.org` |
| `first_name` | First name | `John` |
| `last_name` | Last name | `Doe` |
| `name`, `full_name` | Full name | `John Doe` |
| `username` | Username | `johndoe` |
| `phone`, `telephone`, `mobile` | Phone number | `+44 7700 900123` |
| `city` | City name | `Manchester` |
| `postcode`, `post_code`, `zip` | Postcode | `M1 1AE` |
| `address` | Full address | `123 High Street\nManchester\nM1 1AE` |
| `street` | Street address | `123 High Street` |
| `country` | Country | `United Kingdom` |
| `company` | Company name | `Acme Ltd` |
| `url`, `website` | URL | `https://www.acme.com/` |
| `job`, `title`, `occupation` | Job title | `Software Engineer` |
| `uuid` | UUID | `550e8400-e29b-...` |
| anything else | Random text | Sentence-like text |

Matching is case-insensitive and partial (`home_phone` matches `phone`, `user_email` matches `email`). The `length` column still applies, values longer than that get truncated.

## Changelog

### v0.5.0 (2026-06-12)
- ENUM type: field generates values from a pipe-separated list of choices

### v0.4.0 (2026-06-12)
- Smart VARCHAR: field-name-aware generation for emails, names, phone numbers, addresses, and more
- `--seed`, `--quiet`, `--stdout` flags
- Add `.DS_Store` to gitignore

### v0.3.0 (2025-04-17)
- Add configurable fields via spec CSV file
- Add `--fields-file` (required) parameter
- Add `--input-separator` for spec file
- Support Amazon Redshift data types

### v0.2.0 (2025-04-17)
- Switch to Faker library for realistic data generation
- Add configurable locale (default: en_GB)
- List supported locales in documentation

### v0.1.0 (2025-04-17)
- Initial release
- Generate CSV with: names, UK addresses, telephone numbers, IDs
- Configurable record count, output file, and separator

## Known Bugs

None currently known.

## Testing

```bash
pytest
```

## CI

Runs on every push and PR to `main`. See `.github/workflows/ci.yml`.

## Known Limitations

- The data is synthetic. Names, addresses, and phone numbers are generated by Faker and don't refer to real people.
- Phone numbers may not match real area codes or prefixes.