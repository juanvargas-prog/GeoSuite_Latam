# ── Celda 1 · Imports y constantes ───────────────────────────────────────────
import mimetypes
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES      = ["https://www.googleapis.com/auth/drive"]
FOLDER_MIME = "application/vnd.google-apps.folder"

# ── Celda 2 · Funciones ───────────────────────────────────────────────────────

def build_service(client_secret_path: str, token_path: str = "token.json"):
    """
    Autentica con OAuth2 y devuelve el cliente de Drive.
    - Primera vez: abre el navegador para que apruebes el acceso.
    - Siguientes veces: reutiliza token.json automáticamente.
    """
    creds = None

    # Reutilizar token guardado si existe
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Si no hay token válido, iniciar flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardar token para la próxima vez
        Path(token_path).write_text(creds.to_json())
        print(f"Token guardado en: {token_path}")

    return build("drive", "v3", credentials=creds)


def find_item(service, name: str, parent_id: str, is_folder: bool):
    """Busca archivo o carpeta por nombre en parent_id. Retorna ID o None."""
    mime_filter = (
        f"mimeType = '{FOLDER_MIME}'" if is_folder
        else f"mimeType != '{FOLDER_MIME}'"
    )
    query = (
        f"name = '{name}' "
        f"and '{parent_id}' in parents "
        f"and {mime_filter} "
        f"and trashed = false"
    )
    result = service.files().list(q=query, fields="files(id)", pageSize=1).execute()
    files  = result.get("files", [])
    return files[0]["id"] if files else None


def get_or_create_folder(service, name: str, parent_id: str) -> str:
    """Devuelve el ID de la carpeta en Drive; la crea si no existe."""
    existing_id = find_item(service, name, parent_id, is_folder=True)
    if existing_id:
        print(f"  [carpeta existente] {name}  →  {existing_id}")
        return existing_id

    folder = service.files().create(
        body={"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]},
        fields="id"
    ).execute()
    print(f"  [carpeta creada]    {name}  →  {folder['id']}")
    return folder["id"]


def upload_or_update_file(service, local_file: Path, drive_folder_id: str) -> str:
    """Sube un archivo; si ya existe en Drive lo sobreescribe."""
    mime_type = mimetypes.guess_type(local_file.name)[0] or "application/octet-stream"
    media     = MediaFileUpload(str(local_file), mimetype=mime_type, resumable=True)

    existing_id = find_item(service, local_file.name, drive_folder_id, is_folder=False)
    if existing_id:
        service.files().update(fileId=existing_id, media_body=media).execute()
        print(f"  [actualizado] {local_file.name}")
        return existing_id
    else:
        file = service.files().create(
            body={"name": local_file.name, "parents": [drive_folder_id]},
            media_body=media,
            fields="id"
        ).execute()
        print(f"  [subido]      {local_file.name}")
        return file["id"]


def upload_directory(service, local_dir: Path, drive_folder_id: str):
    """Recorre local_dir y sube cada archivo/subcarpeta a Drive."""
    for item in sorted(local_dir.iterdir()):
        if item.is_dir():
            sub_id = get_or_create_folder(service, item.name, drive_folder_id)
            upload_directory(service, item, sub_id)
        elif item.is_file():
            upload_or_update_file(service, item, drive_folder_id)
def upload_directory(service, local_dir: Path, drive_folder_id: str):
    """Recorre local_dir y sube cada archivo/subcarpeta a Drive."""
    for item in sorted(local_dir.iterdir()):
        if item.is_dir():
            sub_id = get_or_create_folder(service, item.name, drive_folder_id)
            upload_directory(service, item, sub_id)
        elif item.is_file():
            upload_or_update_file(service, item, drive_folder_id)

def generar_nombre_carpeta(service, drive_parent_folder_id: str, bd: str) -> str:
    """
    Genera el nombre de la carpeta con el formato:
    {consecutivo}_Entrega_{DD}_{MM}_{YYYY}_{SIGLAS}
    El consecutivo es el número de carpetas existentes en drive_parent_folder_id + 1.
    """
    from datetime import datetime as _dt
 
    _DICT_PAISES = {
        "Brasil": "BRA", "Chile": "CHI", "Peru": "PER", "Argentina": "ARG",
        "Guatemala": "GTM", "Mexico": "MEX", "Salvador": "SALV",
        "Ecuador": "ECU", "Panama": "PAN", "Honduras": "HOND",
        "Dominicana": "RD", "Paraguay": "PRY", "Uruguay": "URY",
        "Puerto_Rico": "PR", "Costa_Rica": "CR", "Jamaica": "JM",
        "Trinidad": "TT"
    }
 
    # Siglas del país
    SIGLAS = next(
        (cod for pais, cod in _DICT_PAISES.items() if pais.lower() in bd.lower()),
        "UNK"
    )
 
    # Contar carpetas existentes en el destino
    query = (
        f"'{drive_parent_folder_id}' in parents "
        f"and mimeType = '{FOLDER_MIME}' "
        f"and trashed = false"
    )
    total = 0
    token = None
    while True:
        resp  = service.files().list(
            q=query, fields="nextPageToken, files(id)",
            pageSize=1000, pageToken=token
        ).execute()
        total += len(resp.get("files", []))
        token  = resp.get("nextPageToken")
        if not token:
            break
 
    consecutivo = total + 1
 
    # Fecha
    ahora = _dt.now()
    nombre = (
        f"{consecutivo}_Entrega_"
        f"{ahora.strftime('%d')}_{ahora.strftime('%m')}_{ahora.strftime('%Y')}"
        f"_{SIGLAS}"
    )
    print(f"  [nombre generado] {nombre}")
    return nombre

def upload_folder(service, local_folder: str, drive_parent_folder_id: str, bd: str) -> str:
    """
    Sube local_folder a drive_parent_folder_id.
    El nombre con el que se crea en Drive lo genera generar_nombre_carpeta(),
    por lo que puede diferir del nombre local.
    Retorna el ID de Drive de la carpeta creada.
    """
    local_path = Path(local_folder)
    if not local_path.is_dir():
        raise ValueError(f"La ruta '{local_folder}' no es una carpeta válida.")
 
    drive_folder_name = generar_nombre_carpeta(service, drive_parent_folder_id, bd)
 
    print(f"\n📂 Carpeta local  : {local_path}")
    print(f"☁️  Nombre en Drive: {drive_folder_name}")
    print(f"☁️  Destino Drive  : {drive_parent_folder_id}\n")
 
    root_id = get_or_create_folder(service, drive_folder_name, drive_parent_folder_id)
    upload_directory(service, local_path, root_id)
 
    print(f"\n✅ Listo. ID en Drive: {root_id}")
    return root_id
# ── Celda 3 · Punto de entrada para el plugin QGIS ───────────────────────────

import os

def subir_carpeta_exportada(ruta_carpeta_local: str,
                             drive_parent_folder_id: str,
                             client_secret_path: str = None,
                             token_path: str = None) -> str:
    """
    Sube ruta_carpeta_local a Google Drive dentro de drive_parent_folder_id.

    Parámetros
    ----------
    ruta_carpeta_local      : Ruta absoluta de la carpeta generada por exportar_gdf
                              (ej. 'C:/export_latam/Latam_Peru_20250528')
    drive_parent_folder_id  : ID de la carpeta destino en Google Drive
    client_secret_path      : Ruta al JSON de credenciales OAuth2.
                              Si es None usa 'client_secret.json' junto al plugin.
    token_path              : Ruta donde guardar/leer el token OAuth2.
                              Si es None usa 'token.json' junto al plugin.

    Retorna
    -------
    str : ID de Drive de la carpeta subida.
    """
    # Resolver rutas por defecto relativas al directorio de este archivo
    _plugin_dir = os.path.dirname(os.path.abspath(__file__))

    if client_secret_path is None:
        client_secret_path = os.path.join(_plugin_dir, "client_secret.json")
    if token_path is None:
        token_path = os.path.join(_plugin_dir, "token.json")

    if not os.path.exists(client_secret_path):
        raise FileNotFoundError(
            f"No se encontró el archivo de credenciales OAuth2: {client_secret_path}\n"
            "Descárgalo desde Google Cloud Console y colócalo en la carpeta del plugin."
        )

    service = build_service(client_secret_path, token_path)
    folder_id = upload_folder(service, ruta_carpeta_local, drive_parent_folder_id)
    return folder_id
