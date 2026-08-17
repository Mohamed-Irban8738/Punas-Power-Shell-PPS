"""
Extra command handlers and bulk registration for commands listed in commands.txt.
Provides implemented helpers for several useful commands (rmdir, tree, find, stat, head, tail, nl, grep)
and a safe simulation stub for others so they are recognized in the shell but cannot affect the real system.
"""
from typing import Callable
import os


def _safe_stub(name: str) -> Callable[[list[str]], None]:
    def handler(arguments: list[str]):
        print(f"{name}: not supported in Punas Power Shell (simulated stub). Use host system for real behavior.")
    return handler


def _rmdir_handler_factory(shell):
    def handler(arguments: list[str]):
        if len(arguments) != 1:
            print("rmdir: expected exactly one directory name")
            return
        name = arguments[0]
        try:
            # Attempt to remove directory without recursive
            shell.file_manager.rm(name, recursive=False)
            print(f"Directory removed: {name}")
        except IsADirectoryError as err:
            print(err)
        except FileNotFoundError as err:
            print(err)
    return handler


def _tree_handler_factory(shell):
    def walk_dir(vdir, prefix=""):
        items = vdir.children
        dirs = [c for c in items.values() if hasattr(c, 'children')]
        files = [c for c in items.values() if not hasattr(c, 'children')]
        for d in sorted(dirs, key=lambda x: x.name.lower()):
            print(f"{prefix}{d.name}/")
            walk_dir(d, prefix + "  ")
        for f in sorted(files, key=lambda x: x.name.lower()):
            print(f"{prefix}{f.name}")

    def handler(arguments: list[str]):
        # Only supports current directory or a single path
        target = "."
        if len(arguments) == 1:
            target = arguments[0]
        elif len(arguments) > 1:
            print("tree: usage: tree [path]")
            return

        # Resolve path in vfs
        if target in (".", "/"):
            start = shell.file_manager.vfs.current_directory if target == "." else shell.file_manager.vfs.root
        else:
            start_dir, parts = shell.file_manager.vfs.resolve_path(target)
            node, error = shell.file_manager.vfs.navigate_to(start_dir, parts)
            if error:
                print(f"tree: cannot access '{target}': No such file or directory")
                return
            start = node

        print(".")
        walk_dir(start, prefix="")

    return handler


def _stat_handler_factory(shell):
    def handler(arguments: list[str]):
        if len(arguments) != 1:
            print("stat: usage: stat <file>")
            return
        name = arguments[0]
        vfs = shell.file_manager.vfs
        start_dir, parts = vfs.resolve_path(name)
        node, error = vfs.navigate_to(start_dir, parts)
        if error:
            # last part might be the file
            # try to get child in node
            parts2 = parts[-1:]
            child = node.get_child(parts2[0]) if node else None
            if child is None:
                print(f"stat: cannot stat '{name}': No such file or directory")
                return
            target = child
        else:
            target = node

        if hasattr(target, 'content'):
            # file
            size = len(target.content)
            print(f"  File: {target.name}")
            print(f"  Size: {size} bytes")
        else:
            print(f"  Directory: {target.name or '/'}")
            print(f"  Entries: {len(target.children)}")
    return handler


def _basename_handler_factory(shell):
    def handler(arguments: list[str]):
        if len(arguments) != 1:
            print("basename: usage: basename <path>")
            return
        print(os.path.basename(arguments[0]))
    return handler


def _dirname_handler_factory(shell):
    def handler(arguments: list[str]):
        if len(arguments) != 1:
            print("dirname: usage: dirname <path>")
            return
        print(os.path.dirname(arguments[0]) or "/")
    return handler


def _realpath_handler_factory(shell):
    def handler(arguments: list[str]):
        if len(arguments) != 1:
            print("realpath: usage: realpath <path>")
            return
        # Emulate resolving using vfs pwd and parts
        path = arguments[0]
        vfs = shell.file_manager.vfs
        if path.startswith("/"):
            print(path.rstrip("/") or "/")
            return
        # relative
        cwd = vfs.pwd()
        combined = os.path.normpath((cwd + "/" + path).replace("//", "/"))
        print(combined)
    return handler


def _head_handler_factory(shell):
    def handler(arguments: list[str]):
        n = 10
        if len(arguments) == 0:
            print("head: usage: head [-n lines] file")
            return
        if arguments[0] == "-n":
            if len(arguments) < 3:
                print("head: usage: head [-n lines] file")
                return
            try:
                n = int(arguments[1])
            except ValueError:
                print("head: invalid number of lines")
                return
            filename = arguments[2]
        else:
            filename = arguments[0]
        try:
            content = shell.file_manager.cat(filename)
            lines = content.splitlines()
            for line in lines[:n]:
                print(line)
        except Exception as e:
            print(e)
    return handler


def _tail_handler_factory(shell):
    def handler(arguments: list[str]):
        n = 10
        if len(arguments) == 0:
            print("tail: usage: tail [-n lines] file")
            return
        if arguments[0] == "-n":
            if len(arguments) < 3:
                print("tail: usage: tail [-n lines] file")
                return
            try:
                n = int(arguments[1])
            except ValueError:
                print("tail: invalid number of lines")
                return
            filename = arguments[2]
        else:
            filename = arguments[0]
        try:
            content = shell.file_manager.cat(filename)
            lines = content.splitlines()
            for line in lines[-n:]:
                print(line)
        except Exception as e:
            print(e)
    return handler


def _nl_handler_factory(shell):
    def handler(arguments: list[str]):
        if len(arguments) != 1:
            print("nl: usage: nl file")
            return
        try:
            content = shell.file_manager.cat(arguments[0])
            for i, line in enumerate(content.splitlines(), 1):
                print(f"{i}\t{line}")
        except Exception as e:
            print(e)
    return handler


def _grep_handler_factory(shell):
    def handler(arguments: list[str]):
        if len(arguments) < 1:
            print("grep: usage: grep pattern [file ...]")
            return
        pattern = arguments[0]
        files = arguments[1:] if len(arguments) > 1 else [f for f, t in shell.file_manager.ls() if t == 'file']
        for fname in files:
            try:
                content = shell.file_manager.cat(fname)
                for line in content.splitlines():
                    if pattern in line:
                        print(f"{fname}: {line}")
            except Exception:
                continue
    return handler


def _find_handler_factory(shell):
    def handler(arguments: list[str]):
        # simple find: find [path] -name pattern
        path = "."
        name_pattern = None
        if not arguments:
            path = "."
        else:
            path = arguments[0]
            if len(arguments) >= 3 and arguments[1] == "-name":
                name_pattern = arguments[2]
        # resolve start
        vfs = shell.file_manager.vfs
        start_dir, parts = vfs.resolve_path(path)
        node, error = vfs.navigate_to(start_dir, parts)
        if error:
            print(f"find: '{path}': No such file or directory")
            return

        def recurse(dirnode, prefix=""):
            for name, child in dirnode.children.items():
                full = (prefix + "/" + name).lstrip("/")
                if name_pattern is None or name_pattern == name:
                    print(f"/{full}")
                if hasattr(child, 'children'):
                    recurse(child, prefix + "/" + name)
        recurse(node, prefix="" if path.startswith("/") else vfs.pwd())
    return handler


def register_all(dispatcher, shell):
    """Read commands.txt and register handlers: implemented ones get full handlers, others get safe stubs."""
    base = os.path.join(os.path.dirname(__file__), '..')
    commands_file = os.path.join(os.path.dirname(__file__), '..', 'commands.txt')
    try:
        with open(commands_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except Exception:
        lines = []

    implemented = {
        'rmdir': _rmdir_handler_factory(shell),
        'tree': _tree_handler_factory(shell),
        'stat': _stat_handler_factory(shell),
        'basename': _basename_handler_factory(shell),
        'dirname': _dirname_handler_factory(shell),
        'realpath': _realpath_handler_factory(shell),
        'head': _head_handler_factory(shell),
        'tail': _tail_handler_factory(shell),
        'nl': _nl_handler_factory(shell),
        'grep': _grep_handler_factory(shell),
        'find': _find_handler_factory(shell),
    }

    # Register everything read from file
    existing = set()
    try:
        existing = set(dispatcher.get_commands())
    except Exception:
        existing = set()

    for cmd in lines:
        name = cmd.split()[0]
        # Skip headings or lines with uppercase letters (we only want command names)
        if name.lower() != name:
            continue
        # Do not overwrite commands already registered by the shell
        if name in existing:
            continue
        if name in implemented:
            dispatcher.register(name, implemented[name])
        else:
            dispatcher.register(name, _safe_stub(name))
