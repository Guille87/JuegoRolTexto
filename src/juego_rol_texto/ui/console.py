"""Capa de presentación: centraliza el uso de colorama en toda la aplicación."""

import re

from colorama import Fore, Style

__all__ = [
    "Fore",
    "Style",
    "success",
    "error",
    "warning",
    "info",
    "title",
    "colorize",
    "ask",
    "say",
    "tint_status",
    "STAT_COLORS",
    "stat_line",
]

# --- Coloreado automático de estados alterados ---------------------------------
# Cualquier texto que mencione un estado se colorea igual en todo el juego:
# veneno -> verde, quemadura -> rojo, parálisis -> amarillo, congelación -> azul.
# `colorize()` lo aplica solo, así que basta con usar los helpers de este módulo.
_STATUS_PATTERNS = (
    (re.compile(r"\b(?:veneno|venenos[oa]s?|envenen\w*)\b", re.IGNORECASE), Fore.GREEN),
    (re.compile(r"\b(?:quemad\w*|quemaduras?|quema)\b", re.IGNORECASE), Fore.RED),
    (re.compile(r"\b(?:par[aá]lisis|paraliz\w*)\b", re.IGNORECASE), Fore.YELLOW),
    (re.compile(r"\b(?:congelaci[oó]n|congelad[oa]s?|congela)\b", re.IGNORECASE), Fore.BLUE),
)


def tint_status(text: str, back_to: str = "") -> str:
    """Colorea las palabras de estados alterados dentro de `text`. `back_to` es
    la secuencia de color a la que volver tras cada palabra (para no romper el
    color de una línea que ya venía coloreada)."""

    def _replace(match: re.Match, color: str) -> str:
        return f"{Style.BRIGHT}{color}{match.group(0)}{Style.RESET_ALL}{back_to}"

    for pattern, color in _STATUS_PATTERNS:
        text = pattern.sub(lambda m, c=color: _replace(m, c), text)
    return text


def colorize(text: str, color: str, bright: bool = False) -> str:
    """Envuelve un fragmento de texto en un color, sin resetear el estilo global.
    De paso resalta cualquier estado alterado que se mencione en el texto."""
    prefix = f"{Style.BRIGHT}{color}" if bright else color
    return f"{prefix}{tint_status(text, prefix)}{Style.RESET_ALL}"


def success(message: str) -> None:
    print(colorize(message, Fore.GREEN))


def error(message: str) -> None:
    print(colorize(message, Fore.RED))


def warning(message: str) -> None:
    print(colorize(message, Fore.YELLOW))


def info(message: str) -> None:
    print(colorize(message, Fore.CYAN))


def title(message: str) -> None:
    print(colorize(message, Fore.YELLOW, bright=True))


def say(message: str) -> None:
    """Imprime texto sin color de fondo, pero resaltando los estados alterados."""
    print(tint_status(message))


def ask(prompt: str) -> str:
    """Wrapper fino de input(), punto único para interceptar/testear entradas."""
    return input(prompt)


# --- Color por estadística ----------------------------------------------------
# Un color fijo por concepto para que las fichas (jugador, enemigo, bestiario)
# sean más fáciles de leer de un vistazo.
STAT_COLORS = {
    "nivel": Fore.CYAN,
    "vida": Fore.GREEN,
    "ataque": Fore.RED,
    "armadura": Fore.BLUE,
    "magica": Fore.LIGHTBLUE_EX,
    "critico": Fore.YELLOW,
    "velocidad": Fore.MAGENTA,
    "precision": Fore.LIGHTCYAN_EX,
    "evasion": Fore.LIGHTGREEN_EX,
    "penetracion": Fore.LIGHTMAGENTA_EX,
    "regen": Fore.GREEN,
    "kills": Fore.LIGHTYELLOW_EX,
    "oro": Fore.YELLOW,
    "xp": Fore.LIGHTBLACK_EX,
    "elemento": Fore.CYAN,
    "equipo": Fore.BLUE,
}


def stat_line(text: str, key: str, bright: bool = True) -> str:
    """Colorea una línea de estadística según su concepto (`STAT_COLORS`)."""
    return colorize(text, STAT_COLORS.get(key, Fore.WHITE), bright=bright)
