# Security Policy

<p align="center"><a href="SECURITY.md">English</a> · <a href="docs/SECURITY_es.md">Español</a></p>

## Supported versions

This is a small hobby project. Only the latest release and `main` receive fixes.

## Reporting a vulnerability

Please **do not open a public issue** for security problems.

Email **guillermo_amado@hotmail.es** with:

- a description of the problem and its impact,
- steps to reproduce,
- the version or commit affected.

You can expect an acknowledgement within a few days. Once a fix is ready it will
be released and the report credited, unless you prefer to stay anonymous.

## Scope notes

- The optional Discord crash report (`config/crash_reporting.py`) scrubs the OS
  username and home paths before sending, and is opt-in and off by default.
- The admin/debug panel is a single-player cheat gated by a password hash in the
  git-ignored `config/secrets.py`; it is not a security boundary.
