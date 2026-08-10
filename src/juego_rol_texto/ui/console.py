"""Capa de presentación: centraliza el uso de colorama en toda la aplicación."""
from colorama import Fore, Style

__all__ = ["Fore", "Style", "success", "error", "warning", "info", "title", "colorize", "ask"]


def colorize(text: str, color: str, bright: bool = False) -> str:
    """Envuelve un fragmento de texto en un color, sin resetear el estilo global."""
    prefix = f"{Style.BRIGHT}{color}" if bright else color
    return f"{prefix}{text}{Style.RESET_ALL}"


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


def ask(prompt: str) -> str:
    """Wrapper fino de input(), punto único para interceptar/testear entradas."""
    return input(prompt)
