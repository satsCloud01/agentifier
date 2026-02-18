import os
import zipfile
import subprocess
import logging
import tempfile
from pathlib import Path
from agentfier.ingestors.base import BaseIngestor
from agentfier.models.analysis import IngestResult

logger = logging.getLogger(__name__)

class JarIngestor(BaseIngestor):
    def __init__(self, workspace_dir: str = "data/workspaces", cfr_jar_path: str = "tools/cfr.jar"):
        self.workspace_dir = workspace_dir
        self.cfr_jar_path = cfr_jar_path
        os.makedirs(workspace_dir, exist_ok=True)

    def ingest(self, source: str | bytes, **kwargs) -> IngestResult:
        """Ingest a JAR/WAR file.
        source: can be file path (str) or file bytes
        kwargs: filename (str) - original filename for naming
        """
        filename = kwargs.get("filename", "uploaded.jar")
        base_name = os.path.splitext(filename)[0]
        work_dir = os.path.join(self.workspace_dir, base_name)
        os.makedirs(work_dir, exist_ok=True)

        # Save the file
        jar_path = os.path.join(work_dir, filename)
        if isinstance(source, bytes):
            with open(jar_path, 'wb') as f:
                f.write(source)
        elif isinstance(source, str) and os.path.isfile(source):
            import shutil
            shutil.copy2(source, jar_path)
        else:
            raise ValueError(f"Invalid source: expected file path or bytes")

        # Extract the archive
        extract_dir = os.path.join(work_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        logger.info(f"Extracting {filename}...")
        with zipfile.ZipFile(jar_path, 'r') as zf:
            zf.extractall(extract_dir)

        # Decompile .class files with CFR
        decompiled_dir = os.path.join(work_dir, "decompiled")
        os.makedirs(decompiled_dir, exist_ok=True)
        self._decompile(jar_path, decompiled_dir)

        # Build manifest from both extracted (for configs) and decompiled (for source)
        files, total_size = self._build_manifest(work_dir)

        return IngestResult(
            workspace_path=os.path.abspath(work_dir),
            file_manifest=files,
            total_files=len(files),
            total_size_bytes=total_size,
        )

    def _decompile(self, jar_path: str, output_dir: str):
        """Run CFR decompiler on the JAR file."""
        self._ensure_cfr()

        # Check Java is available
        try:
            subprocess.run(["java", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Java not found. Skipping decompilation. Install JDK 17+ for full analysis.")
            return

        logger.info(f"Decompiling with CFR...")
        try:
            result = subprocess.run(
                ["java", "-jar", self.cfr_jar_path, jar_path, "--outputdir", output_dir],
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout
            )
            if result.returncode != 0:
                logger.warning(f"CFR decompilation had warnings: {result.stderr[:500]}")
            else:
                logger.info("Decompilation completed successfully.")
        except subprocess.TimeoutExpired:
            logger.warning("CFR decompilation timed out after 5 minutes.")
        except Exception as e:
            logger.warning(f"Decompilation failed: {e}")

    def _ensure_cfr(self):
        """Download CFR decompiler if not present."""
        if os.path.isfile(self.cfr_jar_path):
            return

        logger.info("CFR decompiler not found. Downloading...")
        os.makedirs(os.path.dirname(self.cfr_jar_path) or ".", exist_ok=True)

        import httpx
        # CFR releases on GitHub
        cfr_url = "https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar"
        try:
            with httpx.Client(follow_redirects=True, timeout=60) as client:
                response = client.get(cfr_url)
                response.raise_for_status()
                with open(self.cfr_jar_path, 'wb') as f:
                    f.write(response.content)
            logger.info(f"CFR downloaded to {self.cfr_jar_path}")
        except Exception as e:
            logger.error(f"Failed to download CFR: {e}")
            raise RuntimeError(
                f"Could not download CFR decompiler. Please manually download from "
                f"{cfr_url} and place at {self.cfr_jar_path}"
            ) from e
