"""
Unit tests for Punas Power Shell components.
Tests individual modules in isolation.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import unittest
from src.parser import CommandParser
from src.virtual_fs import VirtualFileSystem
from src.filesystem import FileManager
from src.history import CommandHistory
from src.config import Config


class TestCommandParser(unittest.TestCase):
    """Test the CommandParser class."""
    
    def setUp(self):
        self.parser = CommandParser()
    
    def test_parse_simple_command(self):
        """Test parsing a simple command."""
        result = self.parser.parse("pwd")
        self.assertEqual(result.name, "pwd")
        self.assertEqual(result.arguments, [])
    
    def test_parse_command_with_args(self):
        """Test parsing a command with arguments."""
        result = self.parser.parse("mkdir test_dir")
        self.assertEqual(result.name, "mkdir")
        self.assertEqual(result.arguments, ["test_dir"])
    
    def test_parse_quoted_string(self):
        """Test parsing quoted arguments."""
        result = self.parser.parse('echo "hello world"')
        self.assertEqual(result.name, "echo")
        self.assertEqual(result.arguments, ["hello world"])
    
    def test_parse_multiple_arguments(self):
        """Test parsing multiple arguments."""
        result = self.parser.parse("cp -r source dest")
        self.assertEqual(result.name, "cp")
        self.assertEqual(result.arguments, ["-r", "source", "dest"])
    
    def test_parse_empty_input(self):
        """Test parsing empty input."""
        result = self.parser.parse("")
        self.assertIsNone(result)
    
    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only input."""
        result = self.parser.parse("   ")
        self.assertIsNone(result)
    
    def test_parse_redirect_operator(self):
        """Test parsing redirect operator."""
        result = self.parser.parse("echo test > file.txt")
        self.assertEqual(result.name, "echo")
        self.assertIn(">", result.arguments)
        self.assertIn("file.txt", result.arguments)


class TestVirtualFileSystem(unittest.TestCase):
    """Test the VirtualFileSystem class."""
    
    def setUp(self):
        self.vfs = VirtualFileSystem()
    
    def test_initial_pwd(self):
        """Test initial working directory is root."""
        self.assertEqual(self.vfs.pwd(), "/")
    
    def test_mkdir_creates_directory(self):
        """Test mkdir creates a directory."""
        success, msg = self.vfs.mkdir("test")
        self.assertTrue(success)
        self.assertIn("created", msg.lower())
    
    def test_ls_shows_created_directory(self):
        """Test ls shows created directories."""
        self.vfs.mkdir("test")
        items = self.vfs.ls()
        self.assertIn(("test", "dir"), items)
    
    def test_cd_changes_directory(self):
        """Test cd changes current directory."""
        self.vfs.mkdir("subdir")
        success, _ = self.vfs.cd("subdir")
        self.assertTrue(success)
        self.assertEqual(self.vfs.pwd(), "/subdir")
    
    def test_cd_with_dotdot(self):
        """Test cd with .. goes to parent."""
        self.vfs.mkdir("subdir")
        self.vfs.cd("subdir")
        success, _ = self.vfs.cd("..")
        self.assertTrue(success)
        self.assertEqual(self.vfs.pwd(), "/")
    
    def test_cd_to_root(self):
        """Test cd to root."""
        self.vfs.mkdir("test")
        self.vfs.cd("test")
        success, _ = self.vfs.cd("/")
        self.assertTrue(success)
        self.assertEqual(self.vfs.pwd(), "/")
    
    def test_touch_creates_file(self):
        """Test touch creates a file."""
        success, msg = self.vfs.touch("file.txt")
        self.assertTrue(success)
        self.assertIn("created", msg.lower())
    
    def test_ls_shows_created_file(self):
        """Test ls shows created files."""
        self.vfs.touch("file.txt")
        items = self.vfs.ls()
        self.assertIn(("file.txt", "file"), items)
    
    def test_echo_writes_to_file(self):
        """Test echo writes to a file."""
        success, _ = self.vfs.echo("test content", "file.txt")
        self.assertTrue(success)
    
    def test_cat_reads_file(self):
        """Test cat reads file content."""
        self.vfs.echo("hello", "file.txt")
        success, content = self.vfs.cat("file.txt")
        self.assertTrue(success)
        self.assertEqual(content, "hello")
    
    def test_cp_copies_file(self):
        """Test cp copies a file."""
        self.vfs.echo("content", "file.txt")
        success, _ = self.vfs.cp("file.txt", "copy.txt")
        self.assertTrue(success)
        _, content = self.vfs.cat("copy.txt")
        self.assertEqual(content, "content")
    
    def test_mv_renames_file(self):
        """Test mv renames a file."""
        self.vfs.touch("old.txt")
        success, _ = self.vfs.mv("old.txt", "new.txt")
        self.assertTrue(success)
        items = self.vfs.ls()
        names = [name for name, _ in items]
        self.assertNotIn("old.txt", names)
        self.assertIn("new.txt", names)
    
    def test_rm_deletes_file(self):
        """Test rm deletes a file."""
        self.vfs.touch("file.txt")
        success, _ = self.vfs.rm("file.txt")
        self.assertTrue(success)
        items = self.vfs.ls()
        self.assertNotIn(("file.txt", "file"), items)
    
    def test_rm_directory_without_recursive_fails(self):
        """Test rm fails on directory without -r."""
        self.vfs.mkdir("dir")
        success, msg = self.vfs.rm("dir", recursive=False)
        self.assertFalse(success)
        self.assertIn("directory", msg.lower())
    
    def test_rm_directory_recursive(self):
        """Test rm with -r removes directory."""
        self.vfs.mkdir("dir")
        success, _ = self.vfs.rm("dir", recursive=True)
        self.assertTrue(success)
        items = self.vfs.ls()
        self.assertNotIn(("dir", "dir"), items)
    
    def test_ls_sorts_directories_first(self):
        """Test ls shows directories before files."""
        self.vfs.touch("file.txt")
        self.vfs.mkdir("zfolder")
        self.vfs.mkdir("afolder")
        items = self.vfs.ls()
        # All dirs should come before all files
        dir_count = sum(1 for _, t in items if t == "dir")
        first_file_index = next(i for i, (_, t) in enumerate(items) if t == "file")
        self.assertLessEqual(dir_count, first_file_index)


class TestFileManager(unittest.TestCase):
    """Test the FileManager wrapper."""
    
    def setUp(self):
        self.fm = FileManager()
    
    def test_pwd_returns_string(self):
        """Test pwd returns a string."""
        pwd = self.fm.pwd()
        self.assertIsInstance(pwd, str)
    
    def test_ls_returns_list(self):
        """Test ls returns a list of tuples."""
        items = self.fm.ls()
        self.assertIsInstance(items, list)
    
    def test_mkdir_raises_on_duplicate(self):
        """Test mkdir raises FileExistsError on duplicate."""
        self.fm.mkdir("test")
        with self.assertRaises(FileExistsError):
            self.fm.mkdir("test")
    
    def test_cd_raises_on_invalid_path(self):
        """Test cd raises FileNotFoundError on invalid path."""
        with self.assertRaises(FileNotFoundError):
            self.fm.cd("nonexistent")


class TestCommandHistory(unittest.TestCase):
    """Test the CommandHistory class."""
    
    def setUp(self):
        self.history = CommandHistory()
    
    def test_add_command(self):
        """Test adding a command to history."""
        self.history.add("pwd")
        self.assertEqual(self.history.size(), 1)
    
    def test_get_recent(self):
        """Test getting recent commands."""
        self.history.add("pwd")
        self.history.add("ls")
        recent = self.history.get_recent(2)
        self.assertEqual(len(recent), 2)
    
    def test_search_history(self):
        """Test searching history."""
        self.history.add("mkdir test")
        self.history.add("ls")
        results = self.history.search("mkdir")
        self.assertEqual(len(results), 1)
    
    def test_clear_history(self):
        """Test clearing history."""
        self.history.add("pwd")
        self.history.clear()
        self.assertEqual(self.history.size(), 0)
    
    def test_max_size_limit(self):
        """Test history size limit."""
        history = CommandHistory(max_size=5)
        for i in range(10):
            history.add(f"cmd{i}")
        self.assertEqual(history.size(), 5)


class TestConfig(unittest.TestCase):
    """Test the Config class."""
    
    def setUp(self):
        import os
        # Use a temporary config file for testing
        self.config = Config("test_config.json")
        # Clean up any previous test file
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        self.config = Config("test_config.json")
    
    def tearDown(self):
        import os
        # Clean up test file
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
    
    def test_get_default_value(self):
        """Test getting default configuration value."""
        value = self.config.get("theme")
        self.assertEqual(value, "default")
    
    def test_set_and_get_value(self):
        """Test setting and getting a value."""
        self.config.set("theme", "dark")
        value = self.config.get("theme")
        self.assertEqual(value, "dark")
    
    def test_get_all_returns_dict(self):
        """Test get_all returns a dictionary."""
        all_config = self.config.get_all()
        self.assertIsInstance(all_config, dict)
    
    def test_dict_like_access(self):
        """Test dict-like access to config."""
        value = self.config["theme"]
        self.assertEqual(value, "default")
    
    def test_contains_operator(self):
        """Test 'in' operator with config."""
        self.assertIn("theme", self.config)
        self.assertNotIn("nonexistent", self.config)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
