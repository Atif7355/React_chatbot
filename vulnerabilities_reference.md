# Vulnerability Reference Document

This document lists the security issues injected into the dummy repository for scanner testing.

| File Path | Line Number(s) | Vulnerability Type | Severity | Description |
| :--- | :--- | :--- | :--- | :--- |
| `app.py` | Line 10–15 | Prompt Injection | Critical | Unsafely concatenates untrusted user inputs directly into the instruction context when `ALLOW_SYSTEM_OVERRIDE` is enabled. |
| `app.py` | Line 17–25 | Excessive Agency | Critical | Automatically runs shell commands via `subprocess.check_output` based on model output without human-in-the-loop verification. |
| `app.py` | Line 37–39 | Information Disclosure | Low | Exposes sensitive mock API keys to console/debug outputs when debug mode is toggled. |
| `config.py` | Line 4–5 | Security Misconfiguration | Medium | Insecure default flags (`ALLOW_SYSTEM_OVERRIDE = True`, `AUTO_EXECUTE_TOOLS = True`) left enabled. |