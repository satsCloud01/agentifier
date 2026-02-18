import os
from agentfier.ingestors.base import BaseIngestor
from agentfier.models.analysis import IngestResult

class LocalIngestor(BaseIngestor):
    def ingest(self, source: str, **kwargs) -> IngestResult:
        """Validate local path exists and build file manifest."""
        source = os.path.expanduser(source)
        if not os.path.isdir(source):
            raise ValueError(f"Directory not found: {source}")

        files, total_size = self._build_manifest(source)
        return IngestResult(
            workspace_path=os.path.abspath(source),
            file_manifest=files,
            total_files=len(files),
            total_size_bytes=total_size,
        )
