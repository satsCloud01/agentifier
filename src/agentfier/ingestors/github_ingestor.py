import os
import re
import logging
from git import Repo
from agentfier.ingestors.base import BaseIngestor
from agentfier.models.analysis import IngestResult

logger = logging.getLogger(__name__)

class GitHubIngestor(BaseIngestor):
    def __init__(self, workspace_dir: str = "data/workspaces"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)

    def ingest(self, source: str, **kwargs) -> IngestResult:
        """Clone a GitHub repository and build file manifest.
        source: GitHub URL (https://github.com/user/repo or similar)
        """
        url = source.strip()
        # Extract repo name for folder naming
        match = re.search(r'/([^/]+?)(?:\.git)?$', url)
        repo_name = match.group(1) if match else "repo"

        clone_dir = os.path.join(self.workspace_dir, repo_name)

        # If already cloned, pull latest; otherwise clone fresh
        if os.path.isdir(clone_dir) and os.path.isdir(os.path.join(clone_dir, '.git')):
            logger.info(f"Repository already exists at {clone_dir}, pulling latest...")
            repo = Repo(clone_dir)
            repo.remotes.origin.pull()
        else:
            logger.info(f"Cloning {url} to {clone_dir}...")
            Repo.clone_from(url, clone_dir, depth=1)  # shallow clone for speed

        files, total_size = self._build_manifest(clone_dir)
        return IngestResult(
            workspace_path=os.path.abspath(clone_dir),
            file_manifest=files,
            total_files=len(files),
            total_size_bytes=total_size,
        )
