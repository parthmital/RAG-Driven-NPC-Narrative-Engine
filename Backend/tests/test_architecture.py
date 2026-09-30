import ast
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]

DISALLOWED_IMPORTS = {
    "schemas": {"api", "core", "game", "graph", "llm", "memory", "session"},
    "core": {"api", "game", "graph", "llm", "memory", "session"},
    "game": {"api", "graph", "llm", "memory", "session"},
    "memory": {"api", "game", "graph", "llm", "session"},
    "llm": {"api", "game", "graph", "session"},
    "graph": {"api", "session"},
    "session": {"api"},
}


def iter_python_files():
    for path in BACKEND_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts or "tests" in path.parts:
            continue
        yield path


def package_for(path: Path) -> str:
    relative = path.relative_to(BACKEND_ROOT)
    return relative.parts[0] if len(relative.parts) > 1 else relative.stem


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


class BackendArchitectureTests(unittest.TestCase):
    def test_dependency_rules_are_respected(self):
        violations = []
        for path in iter_python_files():
            package = package_for(path)
            disallowed = DISALLOWED_IMPORTS.get(package, set())
            bad_imports = imported_roots(path) & disallowed
            for imported in sorted(bad_imports):
                violations.append(
                    f"{path.relative_to(BACKEND_ROOT)} imports forbidden layer {imported}"
                )

        self.assertEqual([], violations)

    def test_graph_does_not_write_global_snapshots(self):
        graph_source = (BACKEND_ROOT / "graph" / "definition.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("config.SNAPSHOT_PATH", graph_source)
        self.assertNotIn("store._connect", graph_source)


if __name__ == "__main__":
    unittest.main()
