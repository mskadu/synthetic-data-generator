# synthetic-data-generator

CLI tool for generating synthetic test data in CSV format for database loading.

## Installation

```bash
uv pip install -e .
```

## Usage

```bash
syngen [options]
```

Or use `uv run syngen` if not installed globally:

```bash
uv run syngen [options]
```

## Examples

```bash
syngen -f fields.csv                          # Generate 10 records using spec file
syngen -f fields.csv -n 100                   # Generate 100 records using spec file
syngen -f fields.csv -o data.csv              # Use spec file, output to data.csv
syngen -f fields.csv -s "|"                   # Use pipe separator in output
syngen -f fields.csv --input-separator "|"     # Use pipe separator in input spec
syngen -f fields.csv -o data.csv -s "|" -n 50 # All options combined
```

## CLI Parameters

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

## Fields Spec CSV Format

Create a CSV file with the following columns:

| Column | Required | Description |
|--------|----------|-------------|
| `field_name` | Yes | Name of the field in output |
| `field_type` | Yes | Redshift data type |
| `length` | No | Length constraint (for VARCHAR) |

### Example fields spec

```csv
field_name,field_type,length
user_id,INTEGER,
first_name,VARCHAR,50
last_name,VARCHAR,50
email,VARCHAR,100
signup_date,DATE,
is_active,BOOLEAN,
salary,DECIMAL,
```

VARCHAR and CHAR fields with names like `email`, `first_name`, `phone`, or `city` automatically generate realistic values (emails, names, phone numbers, cities) instead of random text. Unknown field names fall back to text. See the [smart VARCHAR](#smart-varchar) section for the full mapping.

## Supported Redshift Data Types

| Category | Types |
|----------|-------|
| Numeric | SMALLINT, INTEGER, BIGINT, DECIMAL, REAL, DOUBLE PRECISION |
| String | CHAR, VARCHAR |
| DateTime | DATE, TIME, TIMETZ, TIMESTAMP, TIMESTAMPTZ |
| Boolean | BOOLEAN |

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

Matching is case-insensitive and partial (`home_phone` matches `phone`, `user_email` matches `email`). The `length` column still applies — values are truncated to fit.

## Changelog

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

- Generated data is synthetic and not real person records
- Phone numbers may not match real prefixes