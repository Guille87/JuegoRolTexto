# Política de seguridad

<p align="center"><a href="../SECURITY.md">English</a> · <a href="SECURITY_es.md">Español</a></p>

## Versiones con soporte

Es un proyecto pequeño y personal. Solo la última versión publicada y `main`
reciben correcciones.

## Cómo informar de una vulnerabilidad

Por favor, **no abras un issue público** para problemas de seguridad.

Escribe a **guillermo_amado@hotmail.es** con:

- una descripción del problema y su impacto,
- los pasos para reproducirlo,
- la versión o el commit afectado.

Recibirás un acuse de recibo en unos días. Cuando haya una corrección lista se
publicará y se dará crédito a quien lo reportó, salvo que prefieras el anonimato.

## Notas de alcance

- El informe opcional de errores a Discord (`config/crash_reporting.py`) censura
  el nombre de usuario del sistema y las rutas del perfil antes de enviar nada, y
  está desactivado por defecto (opt-in).
- El panel de administración/debug es un cheat de un jugador protegido por un
  hash de contraseña en el `config/secrets.py` no versionado; no es una frontera
  de seguridad.
