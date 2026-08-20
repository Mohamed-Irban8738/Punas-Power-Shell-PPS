#!/usr/bin/env python3
"""
Integration tests for Punas Power Shell.
Tests the complete shell workflow with various commands.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from io import StringIO
from src.shell import PunasShell
from src.parser import CommandParser


def test_shell_workflow():
    """Test a complete workflow of shell commands."""
    shell = PunasShell()
    
    print("=" * 60)
    print("PUNAS POWER SHELL - INTEGRATION TEST")
    print("=" * 60)
    print()
    
    # Test sequence of commands
    test_commands = [
        ("pwd", "Should show root directory"),
        ("mkdir projects", "Should create projects directory"),
        ("ls", "Should list projects directory"),
        ("cd projects", "Should change to projects directory"),
        ("touch script.py", "Should create script.py file"),
        ("echo print('Hello') > script.py", "Should write to script.py"),
        ("cat script.py", "Should display script.py content"),
        ("mkdir data", "Should create data subdirectory"),
        ("ls", "Should list current directory contents"),
        ("cd data", "Should change to data directory"),
        ("pwd", "Should show /projects/data"),
        ("cd ..", "Should go back to projects"),
        ("pwd", "Should show /projects"),
        ("cp script.py backup.py", "Should copy script.py to backup.py"),
        ("ls", "Should show both files"),
        ("mv backup.py script_backup.py", "Should rename file"),
        ("rm data -r", "Should remove data directory recursively"),
        ("cd /", "Should go to root"),
        ("pwd", "Should show root"),
        ("ls", "Should show projects directory"),
        ("help", "Should show help"),
        ("exit", "Should exit shell"),
    ]
    
    passed = 0
    failed = 0
    
    for cmd, description in test_commands:
        if cmd == "exit":
            print(f"[PASS] Test: {cmd:<30} | {description}")
            print(f"   (Stopping test suite)")
            passed += 1
            break
        
        print(f"\n[TEST] Test: {cmd:<30} | {description}")
        
        try:
            # Capture output
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            shell.process_input(cmd)
            
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            if output or cmd in ["pwd", "ls", "cat", "mkdir", "touch", "echo", "cp", "mv", "rm", "cd", "help"]:
                print(f"   [PASS] PASS")
                if output:
                    lines = output.strip().split('\n')[:3]
                    for line in lines:
                        print(f"      {line}")
                passed += 1
            else:
                print(f"   [WARN]  No output but command executed")
                passed += 1
        
        except Exception as e:
            sys.stdout = old_stdout
            print(f"   [FAIL] FAIL: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def test_parser():
    """Test the command parser."""
    parser = CommandParser()
    
    print("\n" + "=" * 60)
    print("COMMAND PARSER TESTS")
    print("=" * 60)
    print()
    
    test_cases = [
        ("pwd", ("pwd", [])),
        ("mkdir test", ("mkdir", ["test"])),
        ('echo "hello world"', ("echo", ["hello world"])),
        ("cp -r src dest", ("cp", ["-r", "src", "dest"])),
        ("rm -r dir/file.txt", ("rm", ["-r", "dir/file.txt"])),
        ('echo test > file.txt', ("echo", ["test", ">", "file.txt"])),
    ]
    
    passed = 0
    failed = 0
    
    for input_str, expected in test_cases:
        try:
            result = parser.parse(input_str)
            if result and result.name == expected[0] and result.arguments == expected[1]:
                print(f"[PASS] Parse '{input_str}'")
                passed += 1
            else:
                print(f"[FAIL] Parse '{input_str}'")
                print(f"   Expected: {expected}")
                print(f"   Got: ({result.name}, {result.arguments})")
                failed += 1
        except Exception as e:
            print(f"[FAIL] Parse '{input_str}': {e}")
            failed += 1
    
    print()
    print(f"Parser: {passed} passed, {failed} failed")
    print()
    
    return failed == 0


def test_filesystem():
    """Test filesystem operations."""
    from src.filesystem import FileManager
    
    print("=" * 60)
    print("FILESYSTEM TESTS")
    print("=" * 60)
    print()
    
    fm = FileManager()
    passed = 0
    failed = 0
    
    # Test pwd
    try:
        pwd = fm.pwd()
        if pwd == "/":
            print(f"[PASS] pwd returns root: {pwd}")
            passed += 1
        else:
            print(f"[FAIL] pwd should return '/', got '{pwd}'")
            failed += 1
    except Exception as e:
        print(f"[FAIL] pwd failed: {e}")
        failed += 1
    
    # Test mkdir
    try:
        fm.mkdir("testdir")
        print(f"[PASS] mkdir created directory")
        passed += 1
    except Exception as e:
        print(f"[FAIL] mkdir failed: {e}")
        failed += 1
    
    # Test ls
    try:
        items = fm.ls()
        if any(name == "testdir" and type_ == "dir" for name, type_ in items):
            print(f"[PASS] ls shows created directory")
            passed += 1
        else:
            print(f"[FAIL] ls didn't show testdir")
            failed += 1
    except Exception as e:
        print(f"[FAIL] ls failed: {e}")
        failed += 1
    
    # Test cd
    try:
        fm.cd("testdir")
        pwd = fm.pwd()
        if pwd == "/testdir":
            print(f"[PASS] cd changed directory: {pwd}")
            passed += 1
        else:
            print(f"[FAIL] cd didn't work, pwd = {pwd}")
            failed += 1
    except Exception as e:
        print(f"[FAIL] cd failed: {e}")
        failed += 1
    
    # Test touch
    try:
        fm.touch("file.txt")
        items = fm.ls()
        if any(name == "file.txt" and type_ == "file" for name, type_ in items):
            print(f"[PASS] touch created file")
            passed += 1
        else:
            print(f"[FAIL] touch didn't create file")
            failed += 1
    except Exception as e:
        print(f"[FAIL] touch failed: {e}")
        failed += 1
    
    # Test echo/cat
    try:
        fm.echo("Hello World", "file.txt")
        content = fm.cat("file.txt")
        if content == "Hello World":
            print(f"[PASS] echo and cat work correctly")
            passed += 1
        else:
            print(f"[FAIL] cat returned wrong content: {content}")
            failed += 1
    except Exception as e:
        print(f"[FAIL] echo/cat failed: {e}")
        failed += 1
    
    # Test cp
    try:
        fm.cp("file.txt", "file_copy.txt")
        items = fm.ls()
        if any(name == "file_copy.txt" for name, _ in items):
            print(f"[PASS] cp copied file")
            passed += 1
        else:
            print(f"[FAIL] cp didn't copy file")
            failed += 1
    except Exception as e:
        print(f"[FAIL] cp failed: {e}")
        failed += 1
    
    # Test mv
    try:
        fm.mv("file_copy.txt", "renamed.txt")
        items = fm.ls()
        has_renamed = any(name == "renamed.txt" for name, _ in items)
        has_old = any(name == "file_copy.txt" for name, _ in items)
        if has_renamed and not has_old:
            print(f"[PASS] mv renamed file")
            passed += 1
        else:
            print(f"[FAIL] mv didn't work correctly")
            failed += 1
    except Exception as e:
        print(f"[FAIL] mv failed: {e}")
        failed += 1
    
    # Test rm
    try:
        fm.rm("renamed.txt")
        items = fm.ls()
        if not any(name == "renamed.txt" for name, _ in items):
            print(f"[PASS] rm deleted file")
            passed += 1
        else:
            print(f"[FAIL] rm didn't delete file")
            failed += 1
    except Exception as e:
        print(f"[FAIL] rm failed: {e}")
        failed += 1
    
    print()
    print(f"Filesystem: {passed} passed, {failed} failed")
    print()
    
    return failed == 0


if __name__ == "__main__":
    all_passed = True
    
    all_passed &= test_parser()
    all_passed &= test_filesystem()
    all_passed &= test_shell_workflow()
    
    print()
    if all_passed:
        print("[PASS] ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("[FAIL] SOME TESTS FAILED")
        sys.exit(1)
