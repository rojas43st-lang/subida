# SubeFácil — página para subir archivos

Proyecto educativo hecho con **FastAPI**, **Jinja2**, **HTML**, **CSS**, **JavaScript** y **Bootstrap 5.3.8**.

## Funciones
- Subir varios archivos a la vez.
- Arrastrar y soltar archivos.
- Listar los archivos que están en la carpeta `uploads/`.
- Descargar o eliminar archivos.
- Buscar por nombre.
- Diseño adaptable a celular y escritorio.
- Tema claro/oscuro con preferencia guardada en el navegador.
- Límite de 20 MB por archivo y lista de extensiones permitidas.

## Requisitos
Python 3.10 o superior y conexión a internet para cargar Bootstrap desde CDN.

## Ejecutar en Windows (VS Code)
1. Abre esta carpeta en VS Code.
2. Abre la terminal en la carpeta del proyecto.
3. Crea un entorno virtual:

   ```powershell
   py -m venv .venv
   ```

4. Actívalo en PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, usa CMD y ejecuta:

   ```bat
   .venv\Scripts\activate.bat
   ```

5. Instala las dependencias:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Inicia el servidor:

   ```bash
   uvicorn main:app --reload
   ```

7. Abre en el navegador: http://127.0.0.1:8000

## Estructura

```text
subearchivos/
├── main.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── css/estilos.css
│   └── js/app.js
└── uploads/
```

## Importante
Los archivos se guardan en la carpeta `uploads/` del equipo que ejecuta el servidor. Esta versión es para uso local y aprendizaje; no tiene usuarios ni inicio de sesión. Antes de publicarla en internet, agrega autenticación, protección contra abuso, límites de almacenamiento y almacenamiento persistente. En algunos servicios de alojamiento, el disco local es temporal, por lo que no se deben guardar archivos importantes allí.
