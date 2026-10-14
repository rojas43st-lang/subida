from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
import shutil
import uuid
import mimetypes

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB por archivo
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".zip", ".rar"
}

app = FastAPI(title="SubeFácil")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def listar_archivos():
    items = []
    for path in sorted(UPLOAD_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if path.is_file() and not path.name.startswith("."):
            original_name = path.name.split("__", 1)[-1] if "__" in path.name else path.name
            size = path.stat().st_size
            items.append({
                "stored_name": path.name,
                "name": original_name,
                "size": size,
                "size_label": f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.2f} MB",
                "extension": Path(original_name).suffix.lower().lstrip(".") or "archivo",
            })
    return items


@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"archivos": listar_archivos(), "mensaje": None, "error": None},
    )


@app.post("/subir")
async def subir_archivos(archivos: list[UploadFile] = File(...)):
    if not archivos:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

    for archivo in archivos:
        original = Path(archivo.filename or "archivo").name
        extension = Path(original).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            await archivo.close()
            raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {original}")
        contenido = await archivo.read()
        if len(contenido) > MAX_FILE_SIZE:
            await archivo.close()
            raise HTTPException(status_code=413, detail=f"{original} supera el límite de 20 MB.")
        nombre_guardado = f"{uuid.uuid4().hex}__{original}"
        destino = UPLOAD_DIR / nombre_guardado
        destino.write_bytes(contenido)
        await archivo.close()

    return RedirectResponse(url="/?subido=1", status_code=HTTP_303_SEE_OTHER)


@app.get("/descargar/{nombre_guardado}")
async def descargar(nombre_guardado: str):
    from fastapi.responses import FileResponse
    # Solo permite nombres de archivo simples dentro de uploads.
    if Path(nombre_guardado).name != nombre_guardado:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido.")
    path = UPLOAD_DIR / nombre_guardado
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    nombre_original = nombre_guardado.split("__", 1)[-1]
    return FileResponse(path, filename=nombre_original)


@app.post("/eliminar/{nombre_guardado}")
async def eliminar(nombre_guardado: str):
    if Path(nombre_guardado).name != nombre_guardado:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido.")
    path = UPLOAD_DIR / nombre_guardado
    if path.is_file():
        path.unlink()
    return RedirectResponse(url="/?eliminado=1", status_code=HTTP_303_SEE_OTHER)
