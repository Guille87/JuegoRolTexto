# Roadmap

<p align="center"><a href="../ROADMAP.md">English</a> · <a href="ROADMAP_es.md">Español</a></p>

Documento vivo de lo que hay y lo que está planeado. Para el historial detallado
de versiones, mira el [CHANGELOG](CHANGELOG_es.md); para el registro de balance,
[TODO.md](../TODO.md).

## Hecho

- Combate ATB (Active Time Battle), 1 contra 1, con críticos, daño físico y
  mágico, penetración, debilidades elementales y efectos de estado.
- 14 enemigos con mecánicas propias y una cadena de desbloqueo fija.
- 11 huecos de equipo estilo Diablo; herrería (12 recetas), tienda, bestiario.
- Panel de administración/debug protegido con contraseña.
- Música de fondo por «mood».
- Guardado/carga en JSON con copia de seguridad; reconocimiento del jugador por
  nombre sin distinguir mayúsculas/minúsculas.
- Registro de errores en disco e informe opcional (opt-in) a Discord.
- CI (Ruff + tests en Python 3.10–3.13), badge de cobertura, workflow de release.

## Próximo / en estudio

- **Recalibrar la cadena de 14 enemigos** tras cambiar `BASE_HIT_CHANCE` de 90 a
  100 — hasta ahora solo se ha reverificado el Goblin.
- **Bonus de conjunto de armadura** (2/4/6 piezas de un mismo set).
- **Combate contra varios enemigos de verdad** — hoy varios lo fingen con un
  «golpe extra» en vez de un segundo combatiente con su propio medidor de turno.
- **Auto-batalla multiplataforma** — hoy solo Windows por `msvcrt`.
- Ampliar el conjunto de reglas de Ruff (`UP`, `B`, …) y subir la cobertura de la capa de UI.
- Separación MVC más limpia en la capa de presentación.

## Ideas (sin compromiso)

- Canal de feedback dentro del juego (una opción de menú que publique en Discord,
  como el informe de errores).
- Localización / soporte multi-idioma en el propio juego.
