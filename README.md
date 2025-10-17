# github-webhooks

Un proyecto para probar webhooks de Github + Discord.

## Automatización de búsqueda de tareas

El repositorio incluye el script `automation_task.py`, que automatiza la
consulta del "Listado de Tareas de Configuración" en el Configurador de
Recursos de Red. El script inicia sesión con las credenciales provistas,
aplica filtros (equipo, rango de fechas) y revisa el histórico de cada tarea
para localizar coincidencias con una cadena objetivo.

### Requisitos previos

- Python 3.9 o superior.
- Google Chrome instalado.
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/)
  compatible con la versión de tu navegador y disponible en el `PATH`.
- Dependencias de Python:

  ```bash
  pip install selenium
  ```

### Configuración

Los parámetros (URL, credenciales, filtros y cadena de búsqueda) están
encapsulados en la clase `TaskSearchConfig`. Puedes modificarlos editando el
archivo `automation_task.py` o creando una instancia personalizada:

```python
from automation_task import TaskSearchConfig, NetworkConfiguratorScraper

config = TaskSearchConfig(
    equipo_filter="[OLT]",
    date_from="01/01/2024",
    date_to="31/01/2024",
    search_string="[CADENA]",
)
```

### Ejecución del script

Ejecuta el script directamente con Python:

```bash
python automation_task.py
```

Durante la ejecución se abrirá una ventana de Chrome que recorrerá la interfaz
web de manera automatizada. Al finalizar, el script imprimirá por consola los
IDs de tarea que contienen la cadena buscada o el mensaje
`Sin coincidencias encontradas` si no se detectaron coincidencias.
