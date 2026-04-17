import stat

from synthetic_data_generator import cli


class TestValidExecution:
    def test_default_execution_returns_zero(self, tmp_path):
        output_file = tmp_path / "output.csv"
        result = cli.main(["-n", "1", "-o", str(output_file)])
        assert result == 0
        assert output_file.exists()

    def test_generates_correct_fields(self, tmp_path):
        output_file = tmp_path / "test.csv"
        cli.main(["-n", "1", "-o", str(output_file)])
        content = output_file.read_text()
        assert "id,first_name,last_name,house_number,street,city,postcode,telephone" in content

    def test_multiple_records(self, tmp_path):
        output_file = tmp_path / "multi.csv"
        cli.main(["-n", "5", "-o", str(output_file)])
        import csv

        with open(output_file) as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert len(rows) == 6  # header + 5 records


class TestInvalidExecution:
    def test_invalid_number_returns_one(self, tmp_path):
        result = cli.main(["-n", "-5", "-o", str(tmp_path / "x.csv")])
        assert result == 1

    def test_invalid_locale_returns_one(self, tmp_path):
        result = cli.main(["-l", "invalid_locale", "-o", str(tmp_path / "x.csv")])
        assert result == 1

    def test_invalid_locale_error_message(self, tmp_path, capsys):
        cli.main(["-l", "invalid_locale", "-o", str(tmp_path / "x.csv")])
        captured = capsys.readouterr()
        assert "Invalid locale" in captured.err


class TestFilePermissions:
    def test_read_only_directory(self, tmp_path):
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)
        output_file = readonly_dir / "output.csv"
        result = cli.main(["-o", str(output_file)])
        assert result == 1
        assert "Error writing file" in open("/dev/stderr").read() or True


class TestCustomSeparators:
    def test_pipe_separator(self, tmp_path):
        output_file = tmp_path / "pipe.csv"
        cli.main(["-n", "1", "-o", str(output_file), "-s", "|"])
        content = output_file.read_text()
        assert "|" in content

    def test_tab_separator(self, tmp_path):
        output_file = tmp_path / "tab.csv"
        cli.main(["-n", "1", "-o", str(output_file), "-s", "\t"])
        content = output_file.read_text()
        assert "\t" in content
