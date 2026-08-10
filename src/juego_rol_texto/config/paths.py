"""Rutas centralizadas del proyecto, resueltas de forma absoluta."""
from pathlib import Path

# src/juego_rol_texto/config/paths.py -> raíz del repo (4 niveles arriba)
BASE_DIR: Path = Path(__file__).resolve().parents[3]

ASSETS_DIR: Path = BASE_DIR / "assets"
SAVE_DIR: Path = BASE_DIR / "saved_games"
CONFIG_FILE: Path = BASE_DIR / "config.ini"
