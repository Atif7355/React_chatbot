# Vulnerability Analysis Report for AI Repository

This document maps out the security vulnerabilities embedded within this dummy repository for testing static analysis tools (SonarQube, Fortify) and AI red-teaming agents.

| File Name | Line Number | Vulnerability Category | Severity | Description | Detection Tool / Agent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `app.py` | Line 10 | Hardcoded Credentials | Low | Hardcoded API token string exposed directly in source code. | SonarQube / Fortify |
| `app.py` | Line 17 | Prompt Injection / Jailbreak | High | User prompt directly concatenated into the system context without sanitization. | AI Red Teaming Agents |
| `app.py` | Line 25 | Cost / DoS (Resource Exhaustion) | Medium | Unbounded `max_tokens` configuration allows resource drain attacks. | SonarQube / Red Team |
| `agent_tools.py`| Line 8 | Excessive Agency | High | Agent executes destructive commands automatically based on string matching without human confirmation. | AI Red Teaming Agents / Fortify |
| `agent_tools.py`| Line 17 | Data Exfiltration / Data Theft | High | Environment variables and internal data structures are exfiltrated to an external URL. | SonarQube / Fortify |
| `config.py` | Line 4 | Security Misconfiguration | Low | Global `DEBUG_MODE` and unsafe settings enabled by default. | SonarQube |

