# synthetic-data-generator

CLI tool for generating synthetic test data in CSV format.

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
syngen -f fields.csv -n 100               # Generate 100 records using spec file
syngen -f fields.csv -o data.csv          # Use spec file, output to data.csv
syngen -f fields.csv -s "|"               # Use pipe separator in output
syngen -f fields.csv --input-separator "|" # Use pipe separator in input spec
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

## Supported Redshift Data Types

| Category | Types |
|----------|-------|
| Numeric | SMALLINT, INTEGER, BIGINT, DECIMAL, REAL, DOUBLE PRECISION |
| String | CHAR, VARCHAR |
| DateTime | DATE, TIME, TIMETZ, TIMESTAMP, TIMESTAMPTZ |
| Boolean | BOOLEAN |

## Changelog

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

GitHub Actions runs on push and PRs. See `.github/workflows/ci.yml`.

## Known Limitations

- Generated data is synthetic and not real person records
- Phone numbers may not match real prefixes