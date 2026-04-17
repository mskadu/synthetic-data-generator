import pytest
import stat

from synthetic_data_generator import cli


class TestValidExecution:
    def test_basic_generation(self, tmp_path, fields_spec):
        output_file = tmp_path / "output.csv"
        result = cli.main(["-n", "1", "-o", str(output_file), "-f", str(fields_spec)])
        assert result == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "user_id" in content

    def test_multiple_records(self, tmp_path, fields_spec):
        output_file = tmp_path / "multi.csv"
        cli.main(["-n", "5", "-o", str(output_file), "-f", str(fields_spec)])
        import csv

        with open(output_file) as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert len(rows) == 6  # header + 5 records


class TestInvalidExecution:
    def test_invalid_number_returns_one(self, tmp_path, fields_spec):
        result = cli.main(["-n", "-5", "-o", str(tmp_path / "x.csv"), "-f", str(fields_spec)])
        assert result == 1

    def test_invalid_locale_returns_one(self, tmp_path, fields_spec):
        result = cli.main(
            ["-l", "invalid_locale", "-o", str(tmp_path / "x.csv"), "-f", str(fields_spec)]
        )
        assert result == 1

    def test_missing_fields_file(self, tmp_path):
        result = cli.main(["-n", "1", "-o", str(tmp_path / "x.csv"), "-f", "nonexistent.csv"])
        assert result == 1

    def test_invalid_fields_file_columns(self, tmp_path):
        bad_spec = tmp_path / "bad.csv"
        bad_spec.write_text("name,type\nid|BIGINT|")
        result = cli.main(["-n", "1", "-o", str(tmp_path / "x.csv"), "-f", str(bad_spec)])
        assert result == 1

    def test_invalid_field_type(self, tmp_path):
        bad_spec = tmp_path / "bad.csv"
        bad_spec.write_text("field_name,field_type\ncol1,NOT_A_TYPE")
        result = cli.main(["-n", "1", "-o", str(tmp_path / "x.csv"), "-f", str(bad_spec)])
        assert result == 1

    def test_invalid_field_type_error_message(self, tmp_path, capsys):
        bad_spec = tmp_path / "bad.csv"
        bad_spec.write_text("field_name,field_type\ncol1,NOT_A_TYPE")
        cli.main(["-n", "1", "-o", str(tmp_path / "x.csv"), "-f", str(bad_spec)])
        captured = capsys.readouterr()
        assert "Unsupported field type" in captured.err


class TestInputSeparators:
    def test_default_comma_separator(self, tmp_path, fields_spec):
        output_file = tmp_path / "out.csv"
        cli.main(["-n", "1", "-o", str(output_file), "-f", str(fields_spec)])
        assert output_file.exists()

    def test_custom_pipe_separator(self, tmp_path):
        spec_file = tmp_path / "spec.csv"
        spec_file.write_text("field_name|field_type\nid|INTEGER|")
        output_file = tmp_path / "out.csv"
        cli.main(
            ["-n", "1", "-o", str(output_file), "-f", str(spec_file), "--input-separator", "|"]
        )
        assert output_file.exists()


class TestFilePermissions:
    def test_read_only_directory(self, tmp_path, fields_spec):
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)
        output_file = readonly_dir / "output.csv"
        result = cli.main(["-o", str(output_file), "-f", str(fields_spec)])
        assert result == 1


class TestOutputSeparators:
    def test_pipe_separator(self, tmp_path, fields_spec):
        output_file = tmp_path / "pipe.csv"
        cli.main(["-n", "1", "-o", str(output_file), "-f", str(fields_spec), "-s", "|"])
        content = output_file.read_text()
        assert "|" in content

    def test_tab_separator(self, tmp_path, fields_spec):
        output_file = tmp_path / "tab.csv"
        cli.main(["-n", "1", "-o", str(output_file), "-f", str(fields_spec), "-s", "\t"])
        content = output_file.read_text()
        assert "\t" in content


@pytest.fixture
def fields_spec(tmp_path):
    spec = tmp_path / "spec.csv"
    spec.write_text("field_name,field_type,length\nuser_id,INTEGER,\nname,VARCHAR,50")
    return spec
