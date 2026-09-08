"""Catálogo de textos en español. Es el idioma de referencia: cualquier clave
que exista debe estar aquí. Otros catálogos (`catalog_en.py`, ...) pueden estar
incompletos y caen a este.

Convención de claves: `area.subarea.detalle` en minúsculas.
"""

CATALOG: dict[str, str] = {
    # --- Nombres legibles de estados alterados ---
    "status.quemado": "quemadura",
    "status.veneno": "veneno",
    "status.paralizado": "parálisis",
    "status.congelado": "congelación",
    "status.consagrado": "consagración",
    "status.marchito": "marchitamiento",
    "status.fractura_magica": "fractura mágica",
    # --- Nombres legibles de elementos ---
    "element.fuego": "fuego",
    "element.veneno": "veneno",
    "element.rayo": "rayo",
    "element.hielo": "hielo",
    "element.sagrado": "sagrado",
    "element.oscuridad": "oscuridad",
    "element.arcano": "arcano",
    # --- Combate: afinidades elementales ---
    "combat.super_effective": "¡Es supereficaz! El {element} causa estragos en {name}.",
    "combat.immune_hit": "{name} es inmune al {element}: el ataque no le hace nada.",
    "combat.resisted_hit": "{name} resiste el {element}.",
    "combat.status_inflicted": "¡{name} sufre {status}!",
    # --- Combate: estados en el enemigo ---
    "combat.enemy_burn": "🔥 La quemadura le quita {amount} HP a {name}.",
    "combat.enemy_poison": "☣️ El veneno le quita {amount} HP a {name}.",
    "combat.enemy_frozen": "❄️  {name} está congelado y no puede moverse.",
    "combat.enemy_thaws": "El hielo que envuelve a {name} se resquebraja.",
    "combat.enemy_paralysed": "⚡ ¡{name} está paralizado y pierde el turno!",
    "combat.enemy_regen": "💚 {name} regenera {amount} HP.",
    "combat.status_faded_enemy": "✨ El efecto de {status} sobre {name} ha desaparecido.",
    "combat.enemy_succumbs": "{name} sucumbe a sus heridas.",
}
