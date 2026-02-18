"""
Frontend analyzer.

Detects the frontend framework, state management library, routing solution,
component / UI kit, build tooling, and server-side rendering setup.
"""

import json
import logging
import re
from pathlib import Path

from pydantic import BaseModel

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import FrontendResult

logger = logging.getLogger(__name__)


class FrontendAnalyzer(BaseAnalyzer):
    """Dimension 11 -- Frontend."""

    DIMENSION = "frontend"

    PATTERNS: list[str] = [
        # Component files
        "**/*.tsx",
        "**/*.jsx",
        "**/*.vue",
        "**/*.svelte",
        # Conventional directories
        "**/src/components/**/*",
        "**/src/pages/**/*",
        "**/src/views/**/*",
        # State management
        "**/store/**/*.ts",
        "**/store/**/*.js",
        "**/redux/**/*",
        # Routing
        "**/router/**/*.ts",
        "**/router/**/*.js",
        # Framework configs
        "**/next.config*",
        "**/nuxt.config*",
        "**/angular.json",
        # Build tool configs
        "**/vite.config*",
        "**/webpack.config*",
        "**/rollup.config*",
        # TypeScript / Tailwind
        "**/tsconfig.json",
        "**/tailwind.config*",
        # Package manifest (framework detection)
        "**/package.json",
    ]

    # ------------------------------------------------------------------
    # Result model
    # ------------------------------------------------------------------

    def _get_result_model(self) -> type[BaseModel]:
        return FrontendResult

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------

    def _run_heuristics(self, files: list[Path]) -> dict:
        findings: dict = {
            "framework": "",
            "state_management": "",
            "routing_library": "",
            "build_tool": "",
            "has_ssr": False,
            "component_library": "",
            "tsx_count": 0,
            "jsx_count": 0,
            "vue_count": 0,
            "svelte_count": 0,
        }

        # Count component file types
        for f in files:
            ext = f.suffix.lower()
            if ext == ".tsx":
                findings["tsx_count"] += 1
            elif ext == ".jsx":
                findings["jsx_count"] += 1
            elif ext == ".vue":
                findings["vue_count"] += 1
            elif ext == ".svelte":
                findings["svelte_count"] += 1

        # Framework detection by config presence
        file_names = {f.name.lower() for f in files}
        rel_paths = set()
        for f in files:
            try:
                rel_paths.add(str(f.relative_to(self.workspace)).lower())
            except ValueError:
                pass

        if "angular.json" in file_names:
            findings["framework"] = "Angular"
        elif "nuxt.config.ts" in file_names or "nuxt.config.js" in file_names:
            findings["framework"] = "Nuxt"
            findings["has_ssr"] = True
        elif "next.config.js" in file_names or "next.config.mjs" in file_names or "next.config.ts" in file_names:
            findings["framework"] = "Next.js"
            findings["has_ssr"] = True
        elif findings["vue_count"] > 0:
            findings["framework"] = "Vue"
        elif findings["svelte_count"] > 0:
            findings["framework"] = "Svelte"
        elif findings["tsx_count"] > 0 or findings["jsx_count"] > 0:
            findings["framework"] = "React"

        # Build tool detection
        if "vite.config.ts" in file_names or "vite.config.js" in file_names:
            findings["build_tool"] = "Vite"
        elif "webpack.config.js" in file_names or "webpack.config.ts" in file_names:
            findings["build_tool"] = "Webpack"
        elif "rollup.config.js" in file_names or "rollup.config.mjs" in file_names:
            findings["build_tool"] = "Rollup"

        # Parse package.json for state management / routing hints
        package_jsons = [f for f in files if f.name == "package.json"]
        for pj in package_jsons:
            try:
                data = json.loads(pj.read_text(errors="replace"))
                all_deps = {}
                all_deps.update(data.get("dependencies", {}))
                all_deps.update(data.get("devDependencies", {}))

                # State management
                if "redux" in all_deps or "@reduxjs/toolkit" in all_deps:
                    findings["state_management"] = "Redux"
                elif "zustand" in all_deps:
                    findings["state_management"] = "Zustand"
                elif "mobx" in all_deps:
                    findings["state_management"] = "MobX"
                elif "pinia" in all_deps:
                    findings["state_management"] = "Pinia"
                elif "vuex" in all_deps:
                    findings["state_management"] = "Vuex"
                elif "recoil" in all_deps:
                    findings["state_management"] = "Recoil"
                elif "jotai" in all_deps:
                    findings["state_management"] = "Jotai"

                # Routing
                if "react-router-dom" in all_deps or "react-router" in all_deps:
                    findings["routing_library"] = "React Router"
                elif "vue-router" in all_deps:
                    findings["routing_library"] = "Vue Router"
                elif "@angular/router" in all_deps:
                    findings["routing_library"] = "Angular Router"

                # Component libraries
                if "@mui/material" in all_deps or "@material-ui/core" in all_deps:
                    findings["component_library"] = "Material UI"
                elif "antd" in all_deps:
                    findings["component_library"] = "Ant Design"
                elif "@chakra-ui/react" in all_deps:
                    findings["component_library"] = "Chakra UI"
                elif "primevue" in all_deps or "primereact" in all_deps:
                    findings["component_library"] = "PrimeVue/PrimeReact"

                # SSR detection from deps
                if "next" in all_deps:
                    findings["has_ssr"] = True
                if "nuxt" in all_deps:
                    findings["has_ssr"] = True
                if "@sveltejs/kit" in all_deps:
                    findings["has_ssr"] = True
                    findings["framework"] = "SvelteKit"

            except (json.JSONDecodeError, Exception):
                continue

        return findings
