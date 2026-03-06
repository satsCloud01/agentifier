"""
Tests for all ingestors: LocalIngestor, GitHubIngestor, JarIngestor, and BaseIngestor._build_manifest.
"""

import os
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from agentfier.ingestors.base import BaseIngestor
from agentfier.ingestors.local_ingestor import LocalIngestor
from agentfier.ingestors.github_ingestor import GitHubIngestor
from agentfier.ingestors.jar_ingestor import JarIngestor
from agentfier.models.analysis import IngestResult


# ===========================================================================
# BaseIngestor._build_manifest
# ===========================================================================


class _ConcreteIngestor(BaseIngestor):
    """Minimal concrete implementation for testing the base."""
    def ingest(self, source, **kwargs):
        return IngestResult(workspace_path=str(source))


class TestBuildManifest:
    def test_counts_files(self, tmp_workspace: Path):
        ing = _ConcreteIngestor()
        files, total = ing._build_manifest(str(tmp_workspace))
        assert len(files) > 0
        assert total > 0

    def test_skips_git_dir(self, tmp_path: Path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("[core]")
        (tmp_path / "main.py").write_text("pass")
        ing = _ConcreteIngestor()
        files, _ = ing._build_manifest(str(tmp_path))
        paths = [f.path for f in files]
        assert not any(".git" in p for p in paths)

    def test_skips_node_modules(self, tmp_path: Path):
        nm = tmp_path / "node_modules"
        nm.mkdir()
        (nm / "lodash.js").write_text("module.exports = {}")
        (tmp_path / "index.js").write_text("const _ = require('lodash')")
        ing = _ConcreteIngestor()
        files, _ = ing._build_manifest(str(tmp_path))
        paths = [f.path for f in files]
        assert not any("node_modules" in p for p in paths)

    def test_extension_captured(self, tmp_path: Path):
        (tmp_path / "app.py").write_text("pass")
        ing = _ConcreteIngestor()
        files, _ = ing._build_manifest(str(tmp_path))
        exts = {f.extension for f in files}
        assert ".py" in exts

    def test_empty_directory(self, tmp_path: Path):
        ing = _ConcreteIngestor()
        files, total = ing._build_manifest(str(tmp_path))
        assert files == []
        assert total == 0

    def test_relative_paths(self, tmp_path: Path):
        sub = tmp_path / "src"
        sub.mkdir()
        (sub / "module.py").write_text("pass")
        ing = _ConcreteIngestor()
        files, _ = ing._build_manifest(str(tmp_path))
        paths = [f.path for f in files]
        # Should be relative to workspace (no absolute prefix)
        assert all(not os.path.isabs(p) for p in paths)


# ===========================================================================
# LocalIngestor
# ===========================================================================


class TestLocalIngestor:
    def test_valid_directory(self, tmp_workspace: Path):
        ing = LocalIngestor()
        result = ing.ingest(str(tmp_workspace))
        assert isinstance(result, IngestResult)
        assert result.total_files > 0
        assert os.path.isabs(result.workspace_path)

    def test_nonexistent_directory_raises(self):
        ing = LocalIngestor()
        with pytest.raises(ValueError, match="Directory not found"):
            ing.ingest("/tmp/definitely_does_not_exist_xyz")

    def test_file_path_raises(self, tmp_path: Path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        ing = LocalIngestor()
        with pytest.raises(ValueError):
            ing.ingest(str(f))

    def test_tilde_expansion(self, monkeypatch, tmp_path: Path):
        monkeypatch.setenv("HOME", str(tmp_path))
        (tmp_path / "app.py").write_text("pass")
        ing = LocalIngestor()
        result = ing.ingest("~")
        assert result.total_files >= 1

    def test_size_bytes_nonzero(self, tmp_workspace: Path):
        ing = LocalIngestor()
        result = ing.ingest(str(tmp_workspace))
        assert result.total_size_bytes > 0

    def test_workspace_path_absolute(self, tmp_workspace: Path):
        ing = LocalIngestor()
        result = ing.ingest(str(tmp_workspace))
        assert os.path.isabs(result.workspace_path)


# ===========================================================================
# GitHubIngestor
# ===========================================================================


class TestGitHubIngestor:
    def _make_ingestor(self, tmp_path: Path) -> GitHubIngestor:
        ws = str(tmp_path / "workspaces")
        return GitHubIngestor(workspace_dir=ws)

    def test_creates_workspace_dir(self, tmp_path: Path):
        ws = str(tmp_path / "ws")
        GitHubIngestor(workspace_dir=ws)
        assert os.path.isdir(ws)

    def test_clones_repo(self, tmp_path: Path):
        """Fresh clone path: Repo.clone_from is called once."""
        ing = self._make_ingestor(tmp_path)
        mock_repo = MagicMock()

        def fake_clone(url, clone_dir, depth=1):
            # Create a fake .git and some files
            Path(clone_dir).mkdir(parents=True, exist_ok=True)
            (Path(clone_dir) / ".git").mkdir()
            (Path(clone_dir) / "README.md").write_text("# Repo")
            return mock_repo

        with patch("agentfier.ingestors.github_ingestor.Repo") as MockRepo:
            MockRepo.clone_from.side_effect = fake_clone
            result = ing.ingest("https://github.com/example/myrepo")

        MockRepo.clone_from.assert_called_once()
        assert result.total_files >= 1

    def test_pulls_if_already_cloned(self, tmp_path: Path):
        ing = self._make_ingestor(tmp_path)
        clone_dir = tmp_path / "workspaces" / "myrepo"
        clone_dir.mkdir(parents=True)
        (clone_dir / ".git").mkdir()
        (clone_dir / "app.py").write_text("pass")

        mock_repo = MagicMock()
        mock_repo.remotes.origin.pull = MagicMock()

        with patch("agentfier.ingestors.github_ingestor.Repo") as MockRepo:
            MockRepo.return_value = mock_repo
            result = ing.ingest("https://github.com/example/myrepo")

        mock_repo.remotes.origin.pull.assert_called_once()
        assert result.total_files >= 1

    def test_repo_name_extracted_from_url(self, tmp_path: Path):
        ing = self._make_ingestor(tmp_path)

        def fake_clone(url, clone_dir, depth=1):
            Path(clone_dir).mkdir(parents=True, exist_ok=True)
            (Path(clone_dir) / ".git").mkdir()
            (Path(clone_dir) / "file.py").write_text("pass")
            return MagicMock()

        with patch("agentfier.ingestors.github_ingestor.Repo") as MockRepo:
            MockRepo.clone_from.side_effect = fake_clone
            result = ing.ingest("https://github.com/org/awesome-project.git")

        assert "awesome-project" in result.workspace_path

    def test_ingest_result_type(self, tmp_path: Path):
        ing = self._make_ingestor(tmp_path)
        clone_dir = tmp_path / "workspaces" / "repo"
        clone_dir.mkdir(parents=True)
        (clone_dir / ".git").mkdir()
        (clone_dir / "main.py").write_text("pass")

        with patch("agentfier.ingestors.github_ingestor.Repo") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo
            result = ing.ingest("https://github.com/x/repo")

        assert isinstance(result, IngestResult)


# ===========================================================================
# JarIngestor
# ===========================================================================


def _make_jar(path: Path) -> Path:
    """Create a minimal valid JAR (zip) with MANIFEST.MF and a .class stub."""
    jar_path = path / "sample.jar"
    with zipfile.ZipFile(jar_path, "w") as zf:
        zf.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\nMain-Class: com.example.App\n")
        zf.writestr("com/example/App.class", b"\xca\xfe\xba\xbe".decode("latin-1"))
        zf.writestr("application.properties", "server.port=8080\n")
    return jar_path


class TestJarIngestor:
    def _make_ingestor(self, tmp_path: Path) -> JarIngestor:
        ws = str(tmp_path / "workspaces")
        return JarIngestor(workspace_dir=ws, cfr_jar_path="tools/cfr.jar")

    def test_ingest_bytes(self, tmp_path: Path):
        ing = self._make_ingestor(tmp_path)
        jar_path = _make_jar(tmp_path)
        jar_bytes = jar_path.read_bytes()

        # Skip actual decompilation
        with patch.object(ing, "_decompile", return_value=None):
            result = ing.ingest(jar_bytes, filename="sample.jar")

        assert isinstance(result, IngestResult)
        assert result.total_files > 0

    def test_ingest_file_path(self, tmp_path: Path):
        ing = self._make_ingestor(tmp_path)
        jar_path = _make_jar(tmp_path)

        with patch.object(ing, "_decompile", return_value=None):
            result = ing.ingest(str(jar_path), filename="sample.jar")

        assert isinstance(result, IngestResult)

    def test_invalid_source_raises(self, tmp_path: Path):
        ing = self._make_ingestor(tmp_path)
        with pytest.raises(ValueError, match="Invalid source"):
            with patch.object(ing, "_decompile", return_value=None):
                ing.ingest("not_a_file_path", filename="bad.jar")

    def test_workspace_created(self, tmp_path: Path):
        ws = str(tmp_path / "workspaces")
        JarIngestor(workspace_dir=ws)
        assert os.path.isdir(ws)

    def test_decompile_skips_when_no_java(self, tmp_path: Path):
        ing = self._make_ingestor(tmp_path)
        import subprocess
        with patch("subprocess.run", side_effect=FileNotFoundError):
            # Should log warning but not raise
            ing._decompile("fake.jar", str(tmp_path / "decompiled"))

    def test_ensure_cfr_downloads_if_missing(self, tmp_path: Path):
        ws = str(tmp_path / "ws")
        cfr = str(tmp_path / "tools" / "cfr.jar")
        ing = JarIngestor(workspace_dir=ws, cfr_jar_path=cfr)

        mock_response = MagicMock()
        mock_response.content = b"fake-jar-bytes"
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__.return_value.get.return_value = mock_response
            ing._ensure_cfr()

        assert os.path.isfile(cfr)
        assert Path(cfr).read_bytes() == b"fake-jar-bytes"

    def test_ensure_cfr_skips_if_exists(self, tmp_path: Path):
        cfr = tmp_path / "cfr.jar"
        cfr.write_bytes(b"existing")
        ing = JarIngestor(workspace_dir=str(tmp_path), cfr_jar_path=str(cfr))

        with patch("httpx.Client") as MockClient:
            ing._ensure_cfr()
            MockClient.assert_not_called()

    def test_ingest_creates_extracted_and_decompiled_dirs(self, tmp_path: Path):
        ing = self._make_ingestor(tmp_path)
        jar_path = _make_jar(tmp_path)
        jar_bytes = jar_path.read_bytes()

        with patch.object(ing, "_decompile", return_value=None):
            result = ing.ingest(jar_bytes, filename="sample.jar")

        ws_base = Path(ing.workspace_dir) / "sample"
        assert (ws_base / "extracted").is_dir()
        assert (ws_base / "decompiled").is_dir()
