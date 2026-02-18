"""
Auth analyzer -- Dimension 5.

Examines authentication middleware, security configurations, and token
handling to identify authentication methods, authorization patterns, and
identity provider integrations.
"""

import re
from pathlib import Path

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import AuthResult

AUTH_PATTERNS: dict[str, list[str]] = {
    "jwt": [r"jwt", r"jsonwebtoken", r"jose", r"JwtToken", r"Bearer"],
    "oauth": [r"oauth", r"OAuth2", r"authorization_code", r"client_credentials"],
    "session": [
        r"session",
        r"express-session",
        r"HttpSession",
        r"SessionMiddleware",
    ],
    "api_key": [r"api[_-]?key", r"X-API-Key", r"ApiKeyAuth"],
    "saml": [r"saml", r"SAML"],
    "oidc": [r"openid", r"oidc", r"OpenIdConnect"],
}

AUTHZ_PATTERNS: dict[str, list[str]] = {
    "rbac": [r"role", r"@RolesAllowed", r"hasRole", r"user_role", r"ROLE_"],
    "abac": [r"attribute", r"policy", r"abac"],
    "acl": [r"acl", r"access_control", r"permission"],
}


class AuthAnalyzer(BaseAnalyzer):
    DIMENSION = "auth"
    PATTERNS = [
        "**/*auth*.py",
        "**/*auth*.java",
        "**/*auth*.ts",
        "**/*auth*.js",
        "**/*security*.py",
        "**/*security*.java",
        "**/*security*.ts",
        "**/*permission*.py",
        "**/*permission*.java",
        "**/*permission*.ts",
        "**/*login*.py",
        "**/*login*.java",
        "**/*login*.ts",
        "**/*token*.py",
        "**/*token*.java",
        "**/*token*.ts",
        "**/*middleware*.py",
        "**/*middleware*.java",
        "**/*middleware*.ts",
        "**/SecurityConfig*.java",
        "**/WebSecurityConfig*.java",
        "**/settings.py",
        "**/application*.yml",
        "**/application*.properties",
    ]

    def _get_result_model(self) -> type[AuthResult]:
        return AuthResult

    def _run_heuristics(self, files: list[Path]) -> dict:
        auth_methods: set[str] = set()
        authz_patterns: set[str] = set()
        identity_hints: list[str] = []

        for f in files:
            try:
                content = f.read_text(errors="replace")

                for method, patterns in AUTH_PATTERNS.items():
                    for pat in patterns:
                        if re.search(pat, content, re.IGNORECASE):
                            auth_methods.add(method)
                            break

                for pattern_name, patterns in AUTHZ_PATTERNS.items():
                    for pat in patterns:
                        if re.search(pat, content, re.IGNORECASE):
                            authz_patterns.add(pattern_name)
                            break

                # Identity provider hints
                for idp in ["auth0", "okta", "cognito", "keycloak", "firebase"]:
                    if idp in content.lower():
                        identity_hints.append(idp)
            except Exception:
                pass

        return {
            "auth_methods_detected": list(auth_methods),
            "authorization_patterns": list(authz_patterns),
            "identity_provider_hints": list(set(identity_hints)),
        }
