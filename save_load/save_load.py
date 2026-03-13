import base64
import binascii
import json
import os
import shutil

from colorama import Fore, Style
from items.item_base import item_factory

SAVE_DIRECTORY = "saved_games/"

def check_save_directory():
    """Asegura la existencia de la carpeta de guardado."""
    if not os.path.exists(SAVE_DIRECTORY):
        try:
            os.makedirs(SAVE_DIRECTORY)
        except OSError as e:
            print(f"{Fore.RED}No se pudo crear la carpeta de guardado: {e}{Style.RESET_ALL}")

def save_game(player, unlocked_enemies, defeated_enemies):
    """Serializa, crea backup y guarda el estado del juego."""
    check_save_directory()

    file_path = os.path.join(SAVE_DIRECTORY, f"{player.name}.sav")
    backup_path = os.path.join(SAVE_DIRECTORY, f"{player.name}.bak")

    # --- LÓGICA DE BACKUP ---
    # Si ya existe una partida guardada, la renombramos a .bak antes de escribir la nueva
    if os.path.exists(file_path):
        try:
            shutil.copy2(file_path, backup_path)  # copy2 preserva metadatos
        except Exception as e:
            print(f"{Fore.YELLOW}Aviso: No se pudo crear el backup: {e}{Style.RESET_ALL}")

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
            "defense": player.stats.defense
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

        file_path = os.path.join(SAVE_DIRECTORY, f"{player.name}.sav")
        with open(file_path, "wb") as f:
            f.write(encoded_data)
        print(f"{Fore.GREEN}¡Progreso de {player.name} guardado con éxito!{Style.RESET_ALL}")
    except PermissionError:
        print(f"{Fore.RED}Error: No tienes permisos para escribir en {SAVE_DIRECTORY}.{Style.RESET_ALL}")
    except TypeError as e:
        print(f"{Fore.RED}Error de serialización: Algún objeto no se puede convertir a JSON. {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error inesperado al guardar: {e}{Style.RESET_ALL}")

def load_game(player):
    """Carga y reconstruye el estado del jugador desde un archivo. Intenta usar backup si el original falla."""
    file_path = os.path.join(SAVE_DIRECTORY, f"{player.name}.sav")
    backup_path = os.path.join(SAVE_DIRECTORY, f"{player.name}.bak")

    # Si no existe el principal, pero sí el backup, intentamos restaurar el backup
    if not os.path.exists(file_path) and os.path.exists(backup_path):
        print(f"{Fore.YELLOW}Archivo principal no encontrado. Restaurando desde backup...{Style.RESET_ALL}")
        try:
            shutil.copy2(backup_path, file_path)
        except OSError:
            pass

    if not os.path.exists(file_path):
        print(f"{Fore.RED}No se encontró ninguna partida guardada para {player.name}.{Style.RESET_ALL}")
        return None

    try:
        # Intentamos cargar el principal
        return _perform_load(player, file_path)
    except (json.JSONDecodeError, binascii.Error, UnicodeDecodeError):
        print(f"{Fore.RED}El archivo de guardado está corrupto o no es válido.{Style.RESET_ALL}")
        return None
    except KeyError as e:
        print(f"{Fore.RED}Falta un dato esperado en el archivo de guardado: {e}{Style.RESET_ALL}")
    except Exception as e:
        if os.path.exists(backup_path):
            print(f"{Fore.YELLOW}Fallo en el archivo principal. Intentando con el backup...{e}{Style.RESET_ALL}")
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
    player.stats.defense = stats_data["defense"]

    player.inventory.gold = save_data.get("gold", 0)
    items_reconstructed = [item_factory(data) for data in save_data.get("inventory", [])]
    player.inventory.load_saved_inventory(items_reconstructed, save_data.get("inventory_quantities", {}))

    if save_data.get("equipped_weapon"):
        player.equipped_weapon = item_factory(save_data["equipped_weapon"])
    if save_data.get("equipped_armor"):
        player.equipped_armor = item_factory(save_data["equipped_armor"])

    print(f"{Fore.CYAN}Carga exitosa desde: {os.path.basename(path)}{Style.RESET_ALL}")
    return save_data["player_name"], save_data["unlocked_enemies"], save_data["defeated_enemies"]