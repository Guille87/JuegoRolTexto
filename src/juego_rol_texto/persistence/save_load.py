import base64
import binascii
import json
import os
import shutil

from juego_rol_texto.config.paths import SAVE_DIR
from juego_rol_texto.items.factory import item_factory
from juego_rol_texto.ui import console


def check_save_directory() -> None:
    """Asegura la existencia de la carpeta de guardado."""
    if not os.path.exists(SAVE_DIR):
        try:
            os.makedirs(SAVE_DIR)
        except OSError as e:
            console.error(f"No se pudo crear la carpeta de guardado: {e}")


def save_game(player, unlocked_enemies: list, defeated_enemies: list) -> None:
    """Serializa, crea backup y guarda el estado del juego."""
    check_save_directory()

    file_path = os.path.join(SAVE_DIR, f"{player.name}.sav")
    backup_path = os.path.join(SAVE_DIR, f"{player.name}.bak")

    # --- LÓGICA DE BACKUP ---
    # Si ya existe una partida guardada, la renombramos a .bak antes de escribir la nueva
    if os.path.exists(file_path):
        try:
            shutil.copy2(file_path, backup_path)  # copy2 preserva metadatos
        except Exception as e:
            console.warning(f"Aviso: No se pudo crear el backup: {e}")

    # Delegamos la creación del diccionario de stats al objeto stats (Encapsulamiento)
    save_data = {
        "player_name": player.name,
        "unlocked_enemies": unlocked_enemies,
        "defeated_enemies": defeated_enemies,
        "gold": player.inventory.gold,
        "player_stats": {
            "level": player.level,
            "experience": player.experience,
            "health": player.stats.health,
            "max_health": player.stats.max_health,
            "min_atk": player.stats.min_atk,
            "max_atk": player.stats.max_atk,
            "armor": player.stats.armor,
            "magic_resist": player.stats.magic_resist
        },
        # Usamos list comprehension para el inventario
        "inventory": [item.to_dict() for item in player.inventory.items],
        "inventory_quantities": player.inventory.quantities,
        "equipped_weapon": player.equipped_weapon.to_dict() if player.equipped_weapon else None,
        "equipped_armor": player.equipped_armor.to_dict() if player.equipped_armor else None,
    }

    try:
        json_str = json.dumps(save_data)
        encoded_data = base64.b64encode(json_str.encode('utf-8'))

        file_path = os.path.join(SAVE_DIR, f"{player.name}.sav")
        with open(file_path, "wb") as f:
            f.write(encoded_data)
        console.success(f"¡Progreso de {player.name} guardado con éxito!")
    except PermissionError:
        console.error(f"Error: No tienes permisos para escribir en {SAVE_DIR}.")
    except TypeError as e:
        console.error(f"Error de serialización: Algún objeto no se puede convertir a JSON. {e}")
    except Exception as e:
        console.error(f"Error inesperado al guardar: {e}")


def load_game(player):
    """Carga y reconstruye el estado del jugador desde un archivo. Intenta usar backup si el original falla."""
    file_path = os.path.join(SAVE_DIR, f"{player.name}.sav")
    backup_path = os.path.join(SAVE_DIR, f"{player.name}.bak")

    # Si no existe el principal, pero sí el backup, intentamos restaurar el backup
    if not os.path.exists(file_path) and os.path.exists(backup_path):
        console.warning("Archivo principal no encontrado. Restaurando desde backup...")
        try:
            shutil.copy2(backup_path, file_path)
        except OSError:
            pass

    if not os.path.exists(file_path):
        console.error(f"No se encontró ninguna partida guardada para {player.name}.")
        return None

    try:
        # Intentamos cargar el principal
        return _perform_load(player, file_path)
    except (json.JSONDecodeError, binascii.Error, UnicodeDecodeError):
        console.error("El archivo de guardado está corrupto o no es válido.")
        return None
    except KeyError as e:
        console.error(f"Falta un dato esperado en el archivo de guardado: {e}")
    except Exception as e:
        if os.path.exists(backup_path):
            console.warning(f"Fallo en el archivo principal. Intentando con el backup...{e}")
            return _perform_load(player, backup_path)
        return None


def _perform_load(player, path):
    """Función auxiliar para realizar la carga física desde un path determinado."""
    with open(path, "rb") as f:
        encoded_data = f.read()

    decoded_bytes = base64.b64decode(encoded_data)
    save_data = json.loads(decoded_bytes.decode('utf-8'))

    stats_data = save_data["player_stats"]
    player.level = stats_data["level"]
    player.experience = stats_data["experience"]
    player.stats.max_health = stats_data["max_health"]
    player.stats.health = stats_data["health"]
    player.stats.min_atk = stats_data["min_atk"]
    player.stats.max_atk = stats_data["max_atk"]
    # Compatibilidad con partidas guardadas antes de renombrar "defense" a "armor"
    # y de añadir "magic_resist" (que no existía en absoluto).
    player.stats.armor = stats_data.get("armor", stats_data.get("defense", 0))
    player.stats.magic_resist = stats_data.get("magic_resist", 0)

    player.inventory.gold = save_data.get("gold", 0)
    items_reconstructed = [item_factory(data) for data in save_data.get("inventory", [])]
    player.inventory.load_saved_inventory(items_reconstructed, save_data.get("inventory_quantities", {}))

    if save_data.get("equipped_weapon"):
        player.equipped_weapon = item_factory(save_data["equipped_weapon"])
    if save_data.get("equipped_armor"):
        player.equipped_armor = item_factory(save_data["equipped_armor"])

    console.info(f"Carga exitosa desde: {os.path.basename(path)}")
    return save_data["player_name"], save_data["unlocked_enemies"], save_data["defeated_enemies"]
