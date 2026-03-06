# Modrinth Modpack Manager & Changelog Generator

Una aplicación de escritorio profesional construida con Python y PyQt6 diseñada para optimizar la gestión de modpacks de Minecraft. Permite a los creadores comparar automáticamente diferentes versiones de archivos `.mrpack` y generar changelogs limpios en formato Markdown o listas completas de mods en segundos.

![1772814276018](images/readme/1772814276018.avif)

![1772814317296](images/readme/1772814317296.avif)

## Características

- **Métodos de Entrada Dual**: Obtén versiones anteriores directamente desde la API de Modrinth usando la ID de tu proyecto, o carga archivos `.mrpack` localmente.
- **Comparación Inteligente**: Detecta automáticamente los mods añadidos, eliminados y actualizados entre dos versiones del modpack.
- **Formato Automático**: Genera archivos Markdown listos para producción, ideales para las notas de parche de Modrinth o GitHub.
- **Memoria de Sesión**: Recuerda tu ID de Modrinth y rutas locales para un flujo de trabajo más rápido en tu próxima sesión.
- **Salidas Organizadas**: Crea directorios de salida organizados por proyecto y guarda los archivos con el nombre de la versión correspondiente.
- **Interfaz Moderna**: Cuenta con una interfaz limpia en PyQt6 con soporte nativo para Modo Oscuro y Claro.
- **Autoinstalador**: No requiere configuración compleja. Ejecutar el script instalará automáticamente las dependencias faltantes.

## Requisitos

- Python 3.8 o superior.

## Instalación y Uso

1. Clona este repositorio:

   ```bash
   git clone [https://github.com/yourusername/modrinth-changelog-generator.git](https://github.com/yourusername/modrinth-changelog-generator.git)
   ```

2. Navega al directorio del proyecto:

```bash
cd modrinth-changelog-generator

```

3. Ejecuta la aplicación:

```bash
python src/main.py

```

_Nota: Si `PyQt6` o `requests` no están instalados, la aplicación los instalará automáticamente en su primera ejecución._

## Cómo usar

1. **Cargar Versión Base**: En el panel izquierdo, ingresa tu ID de Modrinth para obtener una versión publicada, o selecciona un archivo `.mrpack` antiguo desde tu disco duro.
2. **Cargar Nueva Versión**: Selecciona tu archivo `.mrpack` recién exportado.
3. **Seleccionar Método de Salida**: Elige entre generar un Changelog Comparativo (muestra solo los cambios) o una Lista Completa de Mods.
4. **Generar**: Haz clic en "Generate & Save Markdown". El texto se mostrará en el panel derecho, se copiará al portapapeles y se guardará como un archivo `.md` en la carpeta `outputs/`.

## Licencia

Este proyecto está bajo la Licencia MIT.

```

```
