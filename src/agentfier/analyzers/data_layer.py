"""
Data Layer analyzer -- Dimension 3.

Inspects model definitions, migration scripts, ORM configurations, and
infrastructure files to identify databases, caches, and message queues.
"""

import re
from pathlib import Path

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import DataLayerResult

DB_PATTERNS: dict[str, list[str]] = {
    "postgres": [r"postgres", r"psycopg", r"pg_", r"postgresql"],
    "mysql": [r"mysql", r"mariadb"],
    "mongodb": [r"mongo", r"pymongo", r"mongoose"],
    "redis": [r"redis", r"jedis", r"lettuce"],
    "elasticsearch": [r"elasticsearch", r"elastic"],
    "sqlite": [r"sqlite"],
    "dynamodb": [r"dynamodb", r"dynamo"],
    "cassandra": [r"cassandra"],
}


class DataLayerAnalyzer(BaseAnalyzer):
    DIMENSION = "data_layer"
    PATTERNS = [
        "**/models/**/*.py",
        "**/models/**/*.java",
        "**/models/**/*.ts",
        "**/entities/**/*.java",
        "**/entity/**/*.java",
        "**/*schema*.sql",
        "**/*migration*",
        "**/migrations/**/*",
        "**/alembic/**/*",
        "**/flyway/**/*",
        "**/docker-compose*.yml",
        "**/docker-compose*.yaml",
        "**/application*.yml",
        "**/application*.yaml",
        "**/application*.properties",
        "**/database*.py",
        "**/database*.java",
        "**/database*.ts",
        "**/orm*.py",
        "**/db/**/*.py",
        "**/db/**/*.java",
    ]

    def _get_result_model(self) -> type[DataLayerResult]:
        return DataLayerResult

    def _run_heuristics(self, files: list[Path]) -> dict:
        detected_dbs: set[str] = set()
        has_migrations = False
        has_orm = False
        cache_hints: set[str] = set()
        queue_hints: set[str] = set()

        for f in files:
            fpath = str(f).lower()

            if "migration" in fpath or "alembic" in fpath or "flyway" in fpath:
                has_migrations = True

            try:
                content = f.read_text(errors="replace").lower()
                for db_type, patterns in DB_PATTERNS.items():
                    for pat in patterns:
                        if re.search(pat, content):
                            detected_dbs.add(db_type)
                            break

                if any(
                    kw in content
                    for kw in [
                        "@entity",
                        "base.metadata",
                        "declarative_base",
                        "orm",
                        "sequelize",
                        "typeorm",
                        "prisma",
                    ]
                ):
                    has_orm = True
                if any(kw in content for kw in ["redis", "memcached", "cache"]):
                    cache_hints.add("redis" if "redis" in content else "cache")
                if any(
                    kw in content
                    for kw in ["kafka", "rabbitmq", "celery", "sqs", "amqp"]
                ):
                    for q in ["kafka", "rabbitmq", "celery", "sqs"]:
                        if q in content:
                            queue_hints.add(q)
            except Exception:
                pass

        return {
            "detected_databases": list(detected_dbs),
            "has_migrations": has_migrations,
            "has_orm": has_orm,
            "cache_hints": list(cache_hints),
            "queue_hints": list(queue_hints),
        }
