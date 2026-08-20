"""
Test script for VirtualFileSystem implementation.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.virtual_fs import VirtualFileSystem


def test_virtual_fs():
    """Test all virtual filesystem operations."""
    vfs = VirtualFileSystem()
    
    print("=" * 60)
    print("VIRTUAL FILESYSTEM TEST")
    print("=" * 60)
    print()
    
    # Test 1: pwd
    print("Test 1: pwd (print working directory)")
    pwd_result = vfs.pwd()
    print(f"  pwd: {pwd_result}")
    print(f"  ✅ PASS" if pwd_result == "/" else "  ❌ FAIL")
    print()
    
    # Test 2: mkdir
    print("Test 2: mkdir (create directory)")
    success, msg = vfs.mkdir("projects")
    print(f"  mkdir projects: {msg}")
    print(f"  ✅ PASS" if success else "  ❌ FAIL")
    print()
    
    # Test 3: ls (list directory)
    print("Test 3: ls (list directory)")
    ls_result = vfs.ls()
    print(f"  ls: {ls_result}")
    print(f"  ✅ PASS" if ('projects', 'dir') in ls_result else "  ❌ FAIL")
    print()
    
    # Test 4: cd (change directory)
    print("Test 4: cd (change directory)")
    success, msg = vfs.cd("projects")
    print(f"  cd projects: success={success}")
    pwd_after_cd = vfs.pwd()
    print(f"  pwd after cd: {pwd_after_cd}")
    print(f"  ✅ PASS" if pwd_after_cd == "/projects" else "  ❌ FAIL")
    print()
    
    # Test 5: touch (create file)
    print("Test 5: touch (create file)")
    success, msg = vfs.touch("hello.txt")
    print(f"  touch hello.txt: {msg}")
    ls_after_touch = vfs.ls()
    print(f"  ls after touch: {ls_after_touch}")
    print(f"  ✅ PASS" if ('hello.txt', 'file') in ls_after_touch else "  ❌ FAIL")
    print()
    
    # Test 6: echo (write to file)
    print("Test 6: echo (write to file)")
    success, msg = vfs.echo("Hello, Virtual World!", "hello.txt")
    print(f"  echo 'Hello, Virtual World!' > hello.txt: {msg}")
    print(f"  ✅ PASS" if success else "  ❌ FAIL")
    print()
    
    # Test 7: cat (read file)
    print("Test 7: cat (read file)")
    success, content = vfs.cat("hello.txt")
    print(f"  cat hello.txt:")
    print(f"    Content: {content}")
    print(f"  ✅ PASS" if content == "Hello, Virtual World!" else "  ❌ FAIL")
    print()
    
    # Test 8: cp (copy file)
    print("Test 8: cp (copy file)")
    success, msg = vfs.cp("hello.txt", "hello_copy.txt")
    print(f"  cp hello.txt hello_copy.txt: {msg}")
    success2, content2 = vfs.cat("hello_copy.txt")
    print(f"  Copied file content: {content2}")
    print(f"  ✅ PASS" if content2 == "Hello, Virtual World!" else "  ❌ FAIL")
    print()
    
    # Test 9: mv (rename/move file)
    print("Test 9: mv (rename file)")
    success, msg = vfs.mv("hello_copy.txt", "renamed.txt")
    print(f"  mv hello_copy.txt renamed.txt: {msg}")
    ls_after_mv = vfs.ls()
    print(f"  ls after mv: {ls_after_mv}")
    has_renamed = any(name == "renamed.txt" for name, _ in ls_after_mv)
    has_old = any(name == "hello_copy.txt" for name, _ in ls_after_mv)
    print(f"  ✅ PASS" if has_renamed and not has_old else "  ❌ FAIL")
    print()
    
    # Test 10: rm (delete file)
    print("Test 10: rm (delete file)")
    success, msg = vfs.rm("renamed.txt")
    print(f"  rm renamed.txt: {msg}")
    ls_after_rm = vfs.ls()
    has_file = any(name == "renamed.txt" for name, _ in ls_after_rm)
    print(f"  ✅ PASS" if not has_file else "  ❌ FAIL")
    print()
    
    # Test 11: mkdir nested
    print("Test 11: Create nested directories")
    success, msg = vfs.mkdir("subfolder")
    print(f"  mkdir subfolder: {msg}")
    success, msg = vfs.cd("subfolder")
    print(f"  cd subfolder: success={success}")
    pwd_nested = vfs.pwd()
    print(f"  pwd: {pwd_nested}")
    print(f"  ✅ PASS" if pwd_nested == "/projects/subfolder" else "  ❌ FAIL")
    print()
    
    # Test 12: Navigate back with ..
    print("Test 12: Navigate back with ..")
    success, msg = vfs.cd("..")
    pwd_back = vfs.pwd()
    print(f"  cd .. (pwd after): {pwd_back}")
    print(f"  ✅ PASS" if pwd_back == "/projects" else "  ❌ FAIL")
    print()
    
    # Test 13: Navigate to root
    print("Test 13: Navigate to root")
    success, msg = vfs.cd("/")
    pwd_root = vfs.pwd()
    print(f"  cd / (pwd after): {pwd_root}")
    print(f"  ✅ PASS" if pwd_root == "/" else "  ❌ FAIL")
    print()
    
    # Test 14: Error handling - cd non-existent
    print("Test 14: Error handling - cd non-existent directory")
    success, msg = vfs.cd("nonexistent")
    print(f"  cd nonexistent: success={success}")
    print(f"  Error message: {msg}")
    print(f"  ✅ PASS" if not success else "  ❌ FAIL")
    print()
    
    print("=" * 60)
    print("VIRTUAL FILESYSTEM TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_virtual_fs()
