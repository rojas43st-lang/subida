
from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    FileResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)


# ==========================================
# 1. CONFIGURACIÓN DEL PROYECTO
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MiB

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx",
    ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv",
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".zip", ".rar",
}


# ==========================================
# 2. CREAR LA APLICACIÓN
# ==========================================

app = FastAPI(title="SubeFácil")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# ==========================================
# 3. LISTAR LOS ARCHIVOS GUARDADOS
# ==========================================

def listar_archivos():
    items = []

    for path in sorted(
        UPLOAD_DIR.iterdir(),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ):
        if not path.is_file() or path.name.startswith("."):
            continue

        original_name = (
            path.name.split("__", 1)[-1]
            if "__" in path.name
            else path.name
        )

        size = path.stat().st_size

        if size < 1024:
            size_label = f"{size} B"
        elif size < 1024 * 1024:
            size_label = f"{size / 1024:.1f} KB"
        else:
            size_label = f"{size / (1024 * 1024):.2f} MB"

        extension = Path(original_name).suffix.upper() or "ARCHIVO"

        items.append({
            "stored_name": path.name,
            "name": original_name,
            "size": size,
            "size_label": size_label,
            "extension": extension,
        })

    return items


# ==========================================
# 4. MOSTRAR LA PÁGINA PRINCIPAL
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "archivos": listar_archivos(),
            "mensaje": None,
            "error": None,
        },
    )


# ==========================================
# 5. SUBIR ARCHIVOS
# ==========================================

@app.post("/subir")
async def subir_archivos(
    archivos: list[UploadFile] = File(...),
):
    try:
        for archivo in archivos:
            original = Path(
                archivo.filename or "archivo"
            ).name

            extension = Path(original).suffix.lower()

            # Validar la extensión
            if extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de archivo no permitido: {original}",
                )

            # Leer el contenido
            contenido = await archivo.read()

            # Validar el tamaño
            if len(contenido) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"{original} supera el límite de 20 MB.",
                )

            # Crear un nombre único
            nombre_guardado = (
                f"{__import__('uuid').uuid4().hex}__{original}"
            )

            destino = UPLOAD_DIR / nombre_guardado

            # Guardar el archivo
            destino.write_bytes(contenido)

    finally:
        for archivo in archivos:
            await archivo.close()

    return RedirectResponse(
        url="/?subido=1",
        status_code=HTTP_303_SEE_OTHER,
    )


# ==========================================
# 6. DESCARGAR ARCHIVOS
# ==========================================

@app.get("/descargar/{nombre_guardado}")
async def descargar(nombre_guardado: str):
    # Evitar nombres que contengan rutas
    if Path(nombre_guardado).name != nombre_guardado:
        raise HTTPException(
            status_code=400,
            detail="Nombre de archivo no válido.",
        )

    path = UPLOAD_DIR / nombre_guardado

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado.",
        )

    # Recuperar el nombre original
    nombre_original = (
        nombre_guardado.split("__", 1)[-1]
        if "__" in nombre_guardado
        else nombre_guardado
    )

    return FileResponse(
        path=path,
        filename=nombre_original,
    )


# ==========================================
# 7. ELIMINAR ARCHIVOS
# ==========================================

@app.post("/eliminar/{nombre_guardado}")
async def eliminar(nombre_guardado: str):
    if Path(nombre_guardado).name != nombre_guardado:
        raise HTTPException(
            status_code=400,
            detail="Nombre de archivo no válido.",
        )

    path = UPLOAD_DIR / nombre_guardado

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado.",
        )

    path.unlink()

    return RedirectResponse(
        url="/?eliminado=1",
        status_code=HTTP_303_SEE_OTHER,
    )


# ==========================================
# 8. GENERAR DOCUMENTOS PDF
# ==========================================

@app.post("/generar-pdf")
async def generar_pdf(
    titulo: str = Form(...),
    contenido: str = Form(...),
):
    titulo = titulo.strip()
    contenido = contenido.strip()

    if not titulo or not contenido:
        raise HTTPException(
            status_code=400,
            detail="Debes ingresar un título y un contenido.",
        )

    # Crear el PDF en memoria
    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title=titulo,
    )

    estilos = getSampleStyleSheet()
    elementos = []

    # Agregar el título
    elementos.append(
        Paragraph(
            escape(titulo),
            estilos["Title"],
        )
    )

    elementos.append(Spacer(1, 20))

    # Agregar cada línea del contenido
    for linea in contenido.splitlines():
        if linea.strip():
            elementos.append(
                Paragraph(
                    escape(linea),
                    estilos["BodyText"],
                )
            )

            elementos.append(Spacer(1, 8))

    # Construir el documento
    documento.build(elementos)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="documento.pdf"'
        },
    )
