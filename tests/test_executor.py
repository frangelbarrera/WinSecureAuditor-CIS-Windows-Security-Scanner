"""Cross-platform tests for the sub-rule executor.

Registry happy-path execution only works on Windows; on other platforms we
still exercise dispatch, parsing helpers and error handling. Hive mapping is
tested on every platform by injecting a fake ``winreg`` module.
"""

import sys
import types

import pytest

import executor
from executor import check_file, execute_subrule, get_hive, read_registry, run_command, split_hive

IS_WINDOWS = sys.platform.startswith("win")


class TestDispatch:
    def test_file_check_existing(self, tmp_path):
        target = tmp_path / "app.dll"
        target.write_bytes(b"MZ")
        result = execute_subrule(f"f:{target} -> exists")
        assert result.value == "exists"
        assert result.error == ""

    def test_file_check_missing(self, tmp_path):
        target = tmp_path / "ghost.dll"
        result = execute_subrule(f"f:{target} -> exists")
        assert result.value == "missing"
        assert result.error == ""

    def test_unknown_prefix_returns_error(self):
        result = execute_subrule("x:whatever -> exists")
        assert result.value == ""
        assert "Unknown prefix" in result.error

    @pytest.mark.skipif(IS_WINDOWS, reason="non-Windows behaviour")
    def test_registry_unsupported_on_non_windows(self):
        result = execute_subrule("r:HKLM\\SOFTWARE -> ProductName -> r:^Windows")
        assert result.value == ""
        assert "not supported on non-Windows" in result.error

    def test_command_check(self):
        result = run_command("cmd:echo winsecureauditor")
        assert result.error == ""
        assert result.value.lower().startswith("echo") is False
        assert "winsecureauditor" in result.value.lower()


class TestCheckFile:
    def test_exists(self, tmp_path):
        f = tmp_path / "f.txt"
        f.write_text("x", encoding="utf-8")
        assert check_file(f"f:{f} -> exists").value == "exists"

    def test_missing(self, tmp_path):
        assert check_file(f"f:{tmp_path / 'no.txt'} -> exists").value == "missing"


class TestReadRegistryParsing:
    def test_missing_arrow_reports_invalid_format(self):
        result = read_registry("r:HKLM\\SOFTWARE\\Microsoft")
        assert result.value == ""
        assert "Invalid registry rule format" in result.error

    def test_unsupported_hive_reports_error(self):
        result = read_registry("r:HKEY_WEIRD\\Some\\Path -> ValueName -> r:^x")
        assert "Unsupported hive" in result.error


class TestSplitHive:
    def test_splits_hive_and_path(self):
        assert split_hive("HKLM\\SOFTWARE\\Microsoft") == ("HKLM", "SOFTWARE\\Microsoft")

    def test_path_without_backslash(self):
        assert split_hive("HKLM") == ("HKLM", "")


class TestGetHive:
    @pytest.fixture(autouse=True)
    def fake_winreg(self, monkeypatch):
        fake = types.SimpleNamespace(
            HKEY_LOCAL_MACHINE=0x80000002,
            HKEY_CURRENT_USER=0x80000001,
            HKEY_USERS=0x80000003,
            HKEY_CLASSES_ROOT=0x80000000,
        )
        monkeypatch.setattr(executor, "winreg", fake, raising=False)
        return fake

    def test_short_names(self):
        assert get_hive("HKLM") == 0x80000002
        assert get_hive("HKCU") == 0x80000001
        assert get_hive("HKU") == 0x80000003
        assert get_hive("HKCR") == 0x80000000

    def test_long_names(self):
        assert get_hive("HKEY_LOCAL_MACHINE") == 0x80000002
        assert get_hive("HKEY_CURRENT_USER") == 0x80000001

    def test_case_insensitive(self):
        assert get_hive("hklm") == 0x80000002

    def test_unsupported_hive_raises(self):
        with pytest.raises(ValueError, match="Unsupported hive"):
            get_hive("HKEY_PERFORMANCE_DATA")
