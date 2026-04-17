# synthetic-data-generator

CLI tool for generating synthetic test data in CSV format.

## Usage

```bash
syngen [options]
```

## Examples

```bash
syngen                              # Generate 10 records to output.csv
syngen -n 100                       # Generate 100 records
syngen -n 50 -o data.csv           # Generate 50 records to data.csv
syngen -n 20 -s "|"                # Use pipe separator
syngen -n 5 -o data.csv -s "\t"    # Use tab separator
```

## CLI Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `-n`, `--number` | Number of records to generate | 10 |
| `-o`, `--output` | Output file path | output.csv |
| `-s`, `--separator` | CSV field separator | , |

## Changelog

### v0.1.0 (2025-04-17)
- Initial release
- Generate CSV with: names, UK addresses, telephone numbers, IDs
- Configurable record count, output file, and separator

## Known Bugs

None currently known.

## Known Limitations

- UK phone numbers use generic formats, not real prefixes
- UK postcodes are sample data, not real valid postcodes
- Names are randomly combined, not real person records