# HouseKeeping para Android (proyecto APK)

Este proyecto es una **aplicación Kivy para Android**, no Streamlit. Utiliza la plantilla XLSX original, incluidos logotipos, celdas combinadas, estilos y hojas. Incluye las preguntas de la inspección, los hallazgos y 9 pares de fotos antes/después.

## Para producir el APK con GitHub Actions

1. Crea un repositorio **privado** en GitHub y sube todos los archivos del contenido de esta carpeta, incluida `assets/plantilla_housekeeping.xlsx` y `.github/workflows/android-apk.yml`.
2. En GitHub entra en **Actions → Compilar APK Android → Run workflow**.
3. Cuando finalice, descarga el artefacto **HouseKeeping-Android-APK**. Dentro estará el `.apk` que podrás instalar en tu Android.

También puedes compilarlo en un sistema con Buildozer instalado, con `buildozer -v android debug`.

## Advertencias

- Es **código fuente para compilar**, no un APK terminado. La compilación y las funciones Android aún no han sido probadas en un teléfono.
- La selección de imágenes usa el selector de archivos Android; la cámara puede aparecer entre las fuentes disponibles según el teléfono.
- Solo exporta XLSX en esta primera versión; la exportación PDF está pendiente.
- El archivo se guarda primero en la carpeta privada de la app. Se intenta copiarlo a Documentos mediante androidstorage4kivy.
- La interfaz sigue las **preguntas y estructura de la plantilla**, pero no reproduce la cuadrícula de Excel como interfaz de pantalla.
- La plantilla incluye logos corporativos; usa el repositorio privado y verifica las políticas de manejo de información de tu empresa.
