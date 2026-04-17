# synthetic-data-generator

CLI tool for generating synthetic test data in CSV format.

## Usage

```bash
syngen [options]
```

## Examples

```bash
syngen                              # Generate 10 records to output.csv (UK locale)
syngen -n 100                       # Generate 100 records
syngen -n 50 -o data.csv           # Generate 50 records to data.csv
syngen -n 20 -s "|"                # Use pipe separator
syngen -n 5 -o data.csv -s "\t"    # Use tab separator
syngen -n 5 -l en_US             # Use US locale
```

## CLI Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `-n`, `--number` | Number of records to generate | 10 |
| `-o`, `--output` | Output file path | output.csv |
| `-s`, `--separator` | CSV field separator | , |
| `-l`, `--locale` | Faker locale (see [supported values](https://faker.readthedocs.io/en/latest/locales.html)) | en_GB |

## Changelog

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