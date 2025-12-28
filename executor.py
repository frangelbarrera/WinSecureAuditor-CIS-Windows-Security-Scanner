# File: executor.py

import os
import subprocess
import sys
from typing import NamedTuple

# If you're on Windows, you can import winreg. For non-Windows, handle differently.
if sys.platform.startswith("win"):
    import winreg

class ExecResult(NamedTuple):
    sub_rule: str
    value: str
    error: str

def execute_subrule(sub_rule: str) -> ExecResult:
    """
    Decide how to handle the sub_rule based on prefix:
    - r: -> registry check (Windows)
    - f: -> file check
    - cmd: -> run command
    """
    sub_rule = sub_rule.strip().lower()

    if sub_rule.startswith("r:"):
        if sys.platform.startswith("win"):
            return read_registry(sub_rule)
        else:
            return ExecResult(sub_rule, "", "Registry check not supported on non-Windows")
    elif sub_rule.startswith("f:"):
        return check_file(sub_rule)
    elif sub_rule.startswith("cmd:"):
        return run_command(sub_rule)
    else:
        return ExecResult(sub_rule, "", f"Unknown prefix in {sub_rule}")

def read_registry(sub_rule: str) -> ExecResult:
    """
    Example sub_rule: r:HKLM\Software\Microsoft -> SomeKey -> regex:^....
    We'll parse out the hive (HKLM/HKCU/HKU/HKCR/HKEY_LOCAL_MACHINE, etc.)
    """
    # remove "r:"
    rule_body = sub_rule[2:].strip()  # e.g. HKLM\Software\...
    parts = rule_body.split("->")
    if len(parts) < 2:
        return ExecResult(sub_rule, "", "Invalid registry rule format: missing '->'")

    reg_path = parts[0].strip()  # e.g. HKLM\Software\Microsoft
    # We won't parse further logic (regex) here; we'll just read the value name from next chunk
    value_name = parts[1].strip()

    # If there's more -> splitted, you might parse them. For now, let's assume it's a direct read.
    hive_str, path_str = split_hive(reg_path)
    try:
        hive = get_hive(hive_str)
    except ValueError as e:
        return ExecResult(sub_rule, "", str(e))

    # If value_name is missing, we might read the default key
    if not value_name:
        value_name = None  # default

    try:
        with winreg.OpenKey(hive, path_str) as key:
            val, regtype = winreg.QueryValueEx(key, value_name)
        return ExecResult(sub_rule, str(val), "")
    except Exception as e:
        return ExecResult(sub_rule, "", f"Registry error: {e}")

def split_hive(reg_path: str):
    """
    Splits "HKLM\Software\MyKey" into ("HKLM", "Software\MyKey").
    If no backslash found, path_str might be empty.
    """
    parts = reg_path.split("\\", 1)
    if len(parts) == 1:
        return parts[0], ""
    else:
        return parts[0], parts[1]

def get_hive(hive_str: str):
    """
    Maps short/long hive names to winreg constants.
    Accepts: HKLM or HKEY_LOCAL_MACHINE, HKCU or HKEY_CURRENT_USER, etc.
    """
    hive_str_up = hive_str.upper()
    if hive_str_up in ["HKLM", "HKEY_LOCAL_MACHINE"]:
        return winreg.HKEY_LOCAL_MACHINE
    elif hive_str_up in ["HKCU", "HKEY_CURRENT_USER"]:
        return winreg.HKEY_CURRENT_USER
    elif hive_str_up in ["HKU", "HKEY_USERS"]:
        return winreg.HKEY_USERS
    elif hive_str_up in ["HKCR", "HKEY_CLASSES_ROOT"]:
        return winreg.HKEY_CLASSES_ROOT
    else:
        raise ValueError(f"Unsupported hive: {hive_str}")

def check_file(sub_rule: str) -> ExecResult:
    """
    e.g. f:C:\Windows\System32\notepad.exe -> exists
    We'll just see if the file is present. 
    """
    rule_body = sub_rule[2:].strip()
    parts = rule_body.split("->")
    file_path = parts[0].strip()

    if os.path.exists(file_path):
        return ExecResult(sub_rule, "exists", "")
    else:
        return ExecResult(sub_rule, "missing", "")

def run_command(sub_rule: str) -> ExecResult:
    """
    e.g. cmd:whoami
    """
    cmd_str = sub_rule[4:].strip()
    try:
        output = subprocess.check_output(cmd_str, shell=True, universal_newlines=True)
        return ExecResult(sub_rule, output.strip(), "")
    except subprocess.CalledProcessError as e:
        return ExecResult(sub_rule, "", f"Command error: {e}")
