"""
Security analyzer.

Detects encryption configuration, CORS setup, input validation, audit
logging, compliance indicators, and security headers.
"""

import logging
import re
from pathlib import Path

from pydantic import BaseModel

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import SecurityResult

logger = logging.getLogger(__name__)


class SecurityAnalyzer(BaseAnalyzer):
    """Dimension 10 -- Security."""

    DIMENSION = "security"

    PATTERNS: list[str] = [
        # Security modules
        "**/*security*.py",
        "**/*security*.java",
        "**/*security*.ts",
        # CORS
        "**/*cors*.py",
        "**/*cors*.java",
        "**/*cors*.ts",
        # Encryption / crypto
        "**/*encrypt*.py",
        "**/*encrypt*.java",
        "**/*crypto*.py",
        # Audit
        "**/*audit*.py",
        "**/*audit*.java",
        # Sanitization / validation
        "**/*sanitiz*.py",
        "**/*sanitiz*.ts",
        "**/*validat*.py",
        # Node.js security headers
        "**/helmet*.js",
        # Application config (may contain security settings)
        "**/application*.yml",
        "**/application*.properties",
        # Nginx config
        "**/nginx*.conf",
    ]

    # ------------------------------------------------------------------
    # Result model
    # ------------------------------------------------------------------

    def _get_result_model(self) -> type[BaseModel]:
        return SecurityResult

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------

    def _run_heuristics(self, files: list[Path]) -> dict:
        findings: dict = {
            "tls_ssl_detected": False,
            "cors_detected": False,
            "encryption_imports": [],
            "audit_logging_detected": False,
            "security_headers_detected": [],
            "input_sanitization_detected": False,
            "security_frameworks": [],
        }

        encryption_keywords = [
            ("AES", re.compile(r"\bAES\b")),
            ("RSA", re.compile(r"\bRSA\b")),
            ("bcrypt", re.compile(r"\bbcrypt\b")),
            ("hashlib", re.compile(r"\bhashlib\b")),
            ("cryptography", re.compile(r"from cryptography")),
            ("Fernet", re.compile(r"\bFernet\b")),
            ("argon2", re.compile(r"\bargon2\b")),
            ("scrypt", re.compile(r"\bscrypt\b")),
        ]

        tls_patterns = [
            re.compile(r"ssl_certificate|ssl_cert", re.IGNORECASE),
            re.compile(r"https://|TLS|SECURE_SSL_REDIRECT", re.IGNORECASE),
            re.compile(r"ssl:\s*true", re.IGNORECASE),
        ]

        cors_patterns = [
            re.compile(r"CORS|cors|Access-Control-Allow-Origin", re.IGNORECASE),
            re.compile(r"CorsMiddleware|cors_allowed_origins", re.IGNORECASE),
        ]

        header_keywords = {
            "helmet": re.compile(r"\bhelmet\b", re.IGNORECASE),
            "CSP": re.compile(r"Content-Security-Policy", re.IGNORECASE),
            "HSTS": re.compile(r"Strict-Transport-Security", re.IGNORECASE),
            "X-Frame-Options": re.compile(r"X-Frame-Options", re.IGNORECASE),
            "X-Content-Type-Options": re.compile(r"X-Content-Type-Options", re.IGNORECASE),
        }

        sanitization_patterns = [
            re.compile(r"sanitize|bleach|escape|DOMPurify", re.IGNORECASE),
            re.compile(r"XSS|xss_clean|html\.escape", re.IGNORECASE),
        ]

        security_frameworks: set[str] = set()
        encryption_found: set[str] = set()
        headers_found: set[str] = set()

        for f in files:
            try:
                content = f.read_text(errors="replace")
            except Exception:
                continue

            # TLS / SSL
            for pat in tls_patterns:
                if pat.search(content):
                    findings["tls_ssl_detected"] = True
                    break

            # CORS
            for pat in cors_patterns:
                if pat.search(content):
                    findings["cors_detected"] = True
                    break

            # Encryption imports
            for name, pat in encryption_keywords:
                if pat.search(content):
                    encryption_found.add(name)

            # Audit logging
            if re.search(r"audit|AuditLog|audit_log", content, re.IGNORECASE):
                findings["audit_logging_detected"] = True

            # Security headers
            for name, pat in header_keywords.items():
                if pat.search(content):
                    headers_found.add(name)

            # Input sanitization
            for pat in sanitization_patterns:
                if pat.search(content):
                    findings["input_sanitization_detected"] = True
                    break

            # Security framework detection
            if "Spring Security" in content or "spring-security" in content:
                security_frameworks.add("Spring Security")
            if "django.contrib.auth" in content:
                security_frameworks.add("Django Auth")
            if "passport" in content.lower():
                security_frameworks.add("Passport.js")

        findings["encryption_imports"] = sorted(encryption_found)
        findings["security_headers_detected"] = sorted(headers_found)
        findings["security_frameworks"] = sorted(security_frameworks)

        return findings
