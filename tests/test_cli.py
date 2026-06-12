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


class TestRedshiftDataTypes:
    @pytest.mark.parametrize(
        "field_type",
        [
            "SMALLINT",
            "INTEGER",
            "BIGINT",
            "DECIMAL",
            "REAL",
            "DOUBLE PRECISION",
            "CHAR",
            "VARCHAR",
            "DATE",
            "TIME",
            "TIMETZ",
            "TIMESTAMP",
            "TIMESTAMPTZ",
            "BOOLEAN",
        ],
    )
    def test_each_redshift_type_runs_without_error(self, tmp_path, field_type):
        spec_file = tmp_path / "spec.csv"
        spec_file.write_text(f"field_name,field_type\ncol1,{field_type}")
        output_file = tmp_path / "output.csv"
        result = cli.main(["-n", "1", "-o", str(output_file), "-f", str(spec_file)])
        assert result == 0
        assert output_file.exists()


class TestMultiFieldSchema:
    def test_ten_fields_different_types(self, tmp_path):
        spec_file = tmp_path / "spec.csv"
        spec_file.write_text(
            "field_name,field_type,length\n"
            "id,INTEGER,\n"
            "name,VARCHAR,50\n"
            "amount,DECIMAL,\n"
            "created_date,DATE,\n"
            "is_active,BOOLEAN,\n"
            "score,REAL,\n"
            "notes,VARCHAR,100,\n"
            "big_val,BIGINT,\n"
            "rating,SMALLINT,"
        )
        output_file = tmp_path / "output.csv"
        result = cli.main(["-n", "1", "-o", str(output_file), "-f", str(spec_file)])
        assert result == 0
        content = output_file.read_text()
        assert "id" in content
        assert "name" in content
        assert "amount" in content


class TestSeedReproducibility:
    def test_seed_produces_same_output(self, tmp_path):
        spec_file = tmp_path / "spec.csv"
        spec_file.write_text("field_name,field_type\nid,INTEGER")
        out1 = tmp_path / "out1.csv"
        out2 = tmp_path / "out2.csv"
        cli.main(["-n", "5", "-o", str(out1), "-f", str(spec_file), "--seed", "42"])
        cli.main(["-n", "5", "-o", str(out2), "-f", str(spec_file), "--seed", "42"])
        assert out1.read_text() == out2.read_text()

    def test_different_seed_different_output(self, tmp_path):
        spec_file = tmp_path / "spec.csv"
        spec_file.write_text("field_name,field_type\nid,INTEGER")
        out1 = tmp_path / "out1.csv"
        out2 = tmp_path / "out2.csv"
        cli.main(["-n", "5", "-o", str(out1), "-f", str(spec_file), "--seed", "42"])
        cli.main(["-n", "5", "-o", str(out2), "-f", str(spec_file), "--seed", "99"])
        assert out1.read_text() != out2.read_text()


class TestQuietMode:
    def test_quiet_suppresses_output(self, tmp_path, capsys, fields_spec):
        result = cli.main(
            ["-n", "1", "-o", str(tmp_path / "out.csv"), "-f", str(fields_spec), "--quiet"]
        )
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""


class TestStdoutMode:
    def test_stdout_writes_to_stdout(self, tmp_path, capsys, fields_spec):
        result = cli.main(["-n", "1", "-f", str(fields_spec), "--stdout"])
        assert result == 0
        captured = capsys.readouterr()
        assert "user_id" in captured.out
        assert "name" in captured.out


class TestSmartVarchar:
    def test_email_field_uses_faker_email(self, tmp_path):
        spec = tmp_path / "spec.csv"
        spec.write_text("field_name,field_type,length\nemail,VARCHAR,100")
        out = tmp_path / "out.csv"
        cli.main(["-n", "1", "-o", str(out), "-f", str(spec), "--seed", "42"])
        content = out.read_text()
        assert "@" in content

    def test_name_field_uses_faker_name(self, tmp_path):
        spec = tmp_path / "spec.csv"
        spec.write_text("field_name,field_type,length\nuser_name,VARCHAR,100")
        out = tmp_path / "out.csv"
        cli.main(["-n", "1", "-o", str(out), "-f", str(spec), "--seed", "42"])
        content = out.read_text()
        assert " " in content  # names contain a space

    def test_unknown_field_falls_back_to_text(self, tmp_path):
        spec = tmp_path / "spec.csv"
        spec.write_text("field_name,field_type,length\nnotes,VARCHAR,100")
        out = tmp_path / "out.csv"
        cli.main(["-n", "1", "-o", str(out), "-f", str(spec), "--seed", "42"])
        content = out.read_text()
        assert len(content) > 10

    def test_char_type_also_smart(self, tmp_path):
        spec = tmp_path / "spec.csv"
        spec.write_text("field_name,field_type,length\nemail,CHAR,100")
        out = tmp_path / "out.csv"
        cli.main(["-n", "1", "-o", str(out), "-f", str(spec), "--seed", "42"])
        assert "@" in out.read_text()

    def test_partial_name_match(self, tmp_path):
        spec = tmp_path / "spec.csv"
        spec.write_text("field_name,field_type,length\nhome_phone,VARCHAR,20")
        out = tmp_path / "out.csv"
        cli.main(["-n", "1", "-o", str(out), "-f", str(spec), "--seed", "42"])
        content = out.read_text()
        assert any(c.isdigit() for c in content)

    def test_phone_number_respects_length(self, tmp_path):
        spec = tmp_path / "spec.csv"
        spec.write_text("field_name,field_type,length\nphone,VARCHAR,5")
        out = tmp_path / "out.csv"
        cli.main(["-n", "1", "-o", str(out), "-f", str(spec), "--seed", "42"])
        import csv as csv_mod

        with open(out) as f:
            reader = csv_mod.reader(f)
            rows = list(reader)
        value = rows[1][0]
        assert len(value) <= 5


class TestEdgeCases:
    def test_large_number_of_records(self, tmp_path):
        spec_file = tmp_path / "spec.csv"
        spec_file.write_text("field_name,field_type\nid,INTEGER")
        output_file = tmp_path / "output.csv"
        result = cli.main(["-n", "1000", "-o", str(output_file), "-f", str(spec_file)])
        assert result == 0

    def test_single_record(self, tmp_path):
        spec_file = tmp_path / "spec.csv"
        spec_file.write_text("field_name,field_type\nid,INTEGER")
        output_file = tmp_path / "output.csv"
        result = cli.main(["-n", "1", "-o", str(output_file), "-f", str(spec_file)])
        assert result == 0
