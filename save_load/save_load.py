import base64
import json
import os

from colorama import Fore, Style

from items.item import Item, Potion, Weapon, Armor

# Directorio para los archivos de guardado
SAVE_DIRECTORY = "saved_games/"


def check_save_directory():
    # Comprueba si el directorio de guardado existe, si no, lo crea
    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)


def save_game(player, unlocked_enemies, defeated_enemies):
    check_save_directory()  # Comprueba y crea el directorio de guardado si es necesario

    equipped_weapon_data = player.equipped_weapon.to_dict() if player.equipped_weapon else None
    equipped_armor_data = player.equipped_armor.to_dict() if player.equipped_armor else None

    # Obtener las estadísticas actualizadas del jugador
    player_stats = player.stats()

    # Convertir los datos del juego a formato JSON
    save_data = {
        "player_name": player.name,
        "unlocked_enemies": unlocked_enemies,
        "defeated_enemies": defeated_enemies,
        "inventory": [item.to_dict() for item in player.inventory.items],  # Convertir los objetos a diccionarios
        "equipped_weapon": equipped_weapon_data,
        "equipped_armor": equipped_armor_data,
        "gold": player.inventory.gold,  # Guardar la cantidad de oro del jugador
        "player_stats": player_stats  # Guardar las estadísticas del jugador
    }
    save_file = SAVE_DIRECTORY + player.name + ".json"

    # Convertir los datos del juego a formato JSON
    json_str = json.dumps(save_data)

    # Codificar la cadena JSON utilizando Base64
    encoded_data = base64.b64encode(json_str.encode('utf-8'))

    # Guardar la representación codificada en un archivo
    with open(save_file, "wb") as f:
        f.write(encoded_data)


def load_game(player):
    save_file = SAVE_DIRECTORY + player.name + ".json"

    try:
        with open(save_file, "rb") as f:
            # Leer la representación codificada desde el archivo
            encoded_data = f.read()

        # Decodificar la representación codificada
        decoded_data = base64.b64decode(encoded_data)

        # Convertir la cadena decodificada de nuevo a un objeto JSON
        json_str = decoded_data.decode('utf-8')
        save_data = json.loads(json_str)

        # Imprimir los datos cargados del archivo JSON
        # print("Datos cargados del archivo JSON:")
        # print(save_data)

        # Extraer los datos del juego
        player_name = save_data["player_name"]
        unlocked_enemies = save_data["unlocked_enemies"]
        defeated_enemies = save_data.get("defeated_enemies", [])
        inventory_data = save_data.get("inventory", [])
        equipped_weapon_data = save_data.get("equipped_weapon")
        equipped_armor_data = save_data.get("equipped_armor")
        gold = save_data.get("gold")  # Cargar la cantidad de oro del jugador
        player_stats = save_data.get("player_stats", {})  # Cargar las estadísticas del jugador

        # Restaurar las estadísticas del jugador
        player.level = player_stats.get("level", player.level)
        player.experience = player_stats.get("experience", player.experience)
        player.max_health = player_stats.get("max_health", player.max_health)
        player.health = player_stats.get("health", player.health)
        player.min_attack = player_stats.get("min_attack", player.min_attack)
        player.max_attack = player_stats.get("max_attack", player.max_attack)
        player.defense = player_stats.get("defense", player.defense)

        # Cargar el arma equipada del jugador, si existe
        if equipped_weapon_data:
            player.equipped_weapon = Weapon.from_dict(equipped_weapon_data)

        # Cargar la armadura equipada del jugador, si existe
        if equipped_armor_data:
            player.equipped_armor = Armor.from_dict(equipped_armor_data)

        # Cargar los objetos del inventario del jugador
        if inventory_data:
            inventory_items = []
            for item_data in inventory_data:
                if "healing_amount" in item_data:  # Verificar si es una poción
                    item = Potion.from_dict(item_data)
                elif "damage" in item_data:  # Verificar si es un arma
                    item = Weapon.from_dict(item_data)
                elif "defense" in item_data:  # Verificar si es una armadura
                    item = Armor.from_dict(item_data)
                else:
                    # Agregar manejo para otros tipos de objetos aquí si es necesario
                    item = Item.from_dict(item_data)
                inventory_items.append(item)
        else:
            inventory_items = []  # Inicializar como lista vacía si no hay objetos en el inventario

        # Actualizar el inventario del jugador con los objetos cargados
        player.inventory.items = inventory_items
        # Actualizar la cantidad de oro del jugador
        player.inventory.gold = gold

        return player_name, unlocked_enemies, defeated_enemies
    except FileNotFoundError:
        print(f"{Fore.RED}No se encontró un archivo de guardado con ese nombre.{Style.RESET_ALL}")
        return
