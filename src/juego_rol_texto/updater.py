"""Auto-actualización de la build de Windows.

El juego se reparte como un paquete PyInstaller `--onedir`. Este módulo detecta
si hay una versión más nueva publicada en el GitHub Release, avisa en el menú y
—si el jugador lo pide (PR B)— la descarga, la verifica por SHA-256 y la aplica
reiniciándose, sin tocar `saved_games/` / `config.ini`.

Solo hace algo en la build empaquetada (`sys.frozen`). Ejecutando desde el código
fuente (`python main.py`) todo es no-op: ahí se actualiza con `git`.

Seguridad (v1): HTTPS a la API de GitHub + verificación del SHA-256 publicado en
el mismo Release + protección anti-downgrade. No protege ante una cuenta de
GitHub comprometida; eso lo daría una firma (ver SECURITY.md), que se puede
añadir después en `verify()`.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
import urllib.request
from dataclasses import dataclass

logger = logging.getLogger("juego_rol_texto.updater")

GITHUB_REPO = "Guille87/JuegoRolTexto"
_API_LATEST = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
_USER_AGENT = "JuegoRolTexto-updater (https://github.com/Guille87/JuegoRolTexto)"
_TIMEOUT_S = 10


@dataclass(frozen=True)
class UpdateInfo:
    version: str  # "0.4.0"
    tag: str  # "v0.4.0"
    zip_url: str  # browser_download_url del asset "...-windows.zip"
    sha256: str | None  # de SHA256SUMS, o None si el Release no lo trae
    notes: str  # cuerpo del Release, recortado


def is_active() -> bool:
    """Solo en la build empaquetada, y nunca dentro de CI."""
    return bool(getattr(sys, "frozen", False)) and not os.environ.get("CI")


def _version_tuple(text: str) -> tuple[int, ...]:
    """`"v1.2.3"` / `"1.2.3-rc1"` -> `(1, 2, 3)`. Toma los dígitos iniciales de
    cada parte (los tags del proyecto son siempre `vX.Y.Z`, sin pre-releases)."""
    parts = []
    for chunk in text.strip().lstrip("vV").split("."):
        leading = ""
        for c in chunk:
            if not c.isdigit():
                break
            leading += c
        parts.append(int(leading) if leading else 0)
    return tuple(parts) or (0,)


def _current_version() -> str:
    from juego_rol_texto import __version__

    return __version__


def _get_json(url: str) -> dict | list:  # pragma: no cover - I/O de red, se mockea en tests
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_text(url: str) -> str:  # pragma: no cover - I/O de red, se mockea en tests
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _sha_for(zip_name: str, sha_sums_url: str | None) -> str | None:
    """Descarga SHA256SUMS y devuelve el hash de la línea del zip, o None."""
    if not sha_sums_url:
        return None
    try:
        for line in _get_text(sha_sums_url).splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].lstrip("*") == zip_name:
                return parts[0].lower()
    except Exception as exc:  # noqa: BLE001 - el updater nunca debe lanzar
        logger.warning("No se pudo leer SHA256SUMS: %s", exc)
    return None


def _do_check() -> UpdateInfo | None:
    try:
        data = _get_json(_API_LATEST)
        assert isinstance(data, dict)
        tag = data["tag_name"]
        if _version_tuple(tag) <= _version_tuple(_current_version()):
            return None

        assets = {a["name"]: a["browser_download_url"] for a in data.get("assets", [])}
        zip_name = next((n for n in assets if n.endswith("-windows.zip")), None)
        if not zip_name:
            logger.warning("El Release %s no tiene un asset -windows.zip", tag)
            return None

        return UpdateInfo(
            version=tag.lstrip("vV"),
            tag=tag,
            zip_url=assets[zip_name],
            sha256=_sha_for(zip_name, assets.get("SHA256SUMS")),
            notes=(data.get("body") or "").strip()[:1500],
        )
    except Exception as exc:  # noqa: BLE001 - el updater nunca debe tumbar el juego
        logger.warning("Fallo comprobando actualizaciones: %s", exc)
        return None


# --- Comprobación en segundo plano (mismo patrón que el watchdog de música) ---

_available: UpdateInfo | None = None
_stop = threading.Event()
_thread: threading.Thread | None = None


def check() -> UpdateInfo | None:
    """Consulta el último Release y guarda el resultado en `available()`. Devuelve
    `UpdateInfo` solo si su versión es estrictamente mayor que la instalada y trae
    un `.zip` de Windows; `None` en cualquier otro caso (igual/menor versión, sin
    asset, error de red...). Un fallo de red no borra un aviso ya encontrado."""
    global _available
    info = _do_check()
    if info is not None:
        _available = info
        logger.info("Actualización disponible: %s", info.tag)
    return info


def _worker() -> None:
    cleanup_staging()
    if not _stop.is_set():
        check()


def start_background_check() -> None:
    global _thread
    _stop.clear()
    _thread = threading.Thread(target=_worker, name="updater-check", daemon=True)
    _thread.start()


def stop_background_check() -> None:
    _stop.set()
    if _thread is not None:
        _thread.join(timeout=3)


def available() -> UpdateInfo | None:
    """Lo que consultan los bucles de menú. `None` hasta que el hilo termine."""
    return _available


def cleanup_staging() -> None:
    """Borra `BASE_DIR/.update/` (carpeta de trabajo de una actualización previa).
    Se llama al arrancar. En PR A todavía no existe; queda listo para PR B."""
    import shutil

    from juego_rol_texto.config.paths import BASE_DIR

    shutil.rmtree(BASE_DIR / ".update", ignore_errors=True)
