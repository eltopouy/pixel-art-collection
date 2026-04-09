# 🛠️ Guía de Mantenimiento: Pixel Universe

Sigue estos pasos para subir nuevos archivos a medida que los obtengas. Esta guía asegura que la web siempre esté sincronizada y organizada.

---

## 1. Generar Nuevas Imágenes
Usa tu script de IA para generar los archivos `.png`. 
Asegúrate de que los archivos caigan en la raíz de `pixel_art_final/` o que el metadato coincida con el nombre del archivo generado.

## 2. Organizar Automáticamente
Cada vez que tengas archivos nuevos sueltos en la carpeta raíz, ejecuta el script de organización:

```powershell
# Desde la terminal
py scripts/organize.py
```

**¿Qué hace este script?**
- Lee el archivo `meta.json`.
- Mueve los archivos PNG sueltos a sus respectivas subcarpetas dentro de `images/` (por categoría).
- Actualiza las rutas en `meta.json` para que la web pueda mostrarlos.

## 3. Subir a la Web (Despliegue)
Para que los cambios sean públicos en GitHub Pages, usa estos comandos:

```powershell
# 1. Agrega todos los cambios (fotos nuevas + metadatos)
git add .

# 2. Crea el punto de restauración/subida
git commit -m "Add new assets and update metadata"

# 3. Sube a la nube
git push
```

---

## 💡 Tips de Oro
- **Metadatos:** Si el archivo no existe físicamente, el script saltará al siguiente. Asegúrate de que el nombre del `.png` coincida exactamente con el campo `file_name` en tu generador de JSON.
- **Categorías:** Si agregas categorías nuevas en el JSON, el script creará las carpetas automáticamente.
- **Imágenes:** No borres la carpeta `images/`, allí es donde vive el 100% de la colección organizada.

---
*Mantenimiento realizado por Antigravity AI*
