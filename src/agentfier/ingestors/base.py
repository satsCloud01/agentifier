from abc import ABC, abstractmethod
from agentfier.models.analysis import IngestResult

class BaseIngestor(ABC):
    @abstractmethod
    def ingest(self, source: str | bytes, **kwargs) -> IngestResult:
        """Ingest a source and return an IngestResult with workspace path and file manifest."""
        ...

    def _build_manifest(self, workspace_path: str) -> tuple[list, int]:
        """Walk workspace directory and build file manifest.
        Returns (file_list, total_size_bytes).
        Skips: .git, __pycache__, node_modules, .class files in non-decompiled dirs,
        target/, build/, dist/, .idea/, .vscode/
        """
        import os
        from agentfier.models.analysis import FileInfo

        skip_dirs = {'.git', '__pycache__', 'node_modules', '.idea', '.vscode', '.gradle'}
        files = []
        total_size = 0
        for root, dirs, filenames in os.walk(workspace_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fname in filenames:
                fpath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(fpath)
                except OSError:
                    continue
                ext = os.path.splitext(fname)[1]
                rel_path = os.path.relpath(fpath, workspace_path)
                files.append(FileInfo(path=rel_path, size=size, extension=ext))
                total_size += size
        return files, total_size
