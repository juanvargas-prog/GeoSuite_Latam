#from cycler import L
import pandas as pd
import re
import json
# pip install psycopg2-binary sqlalchemy (si vas a usar postgres)
from sqlalchemy import create_engine
# pip install google-generativeai
import google.generativeai as genai
import time
import os
import shutil
# pip install google-api-python-client google-auth httplib2 google-auth-httplib2 google-auth-oauthlib
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

def obtener_palabras_conocidas():

    # Configuración de las variables desde el archivo local .env
    ruta_plugin = os.path.dirname(__file__)
    ruta_env = os.path.join(ruta_plugin, ".env")
    load_dotenv(dotenv_path=ruta_env)

    # 2. Leer la variable
    service_account_str = os.getenv("SERVICE_ACCOUNT_INFO")

    if service_account_str:
        SERVICE_ACCOUNT_INFO = json.loads(service_account_str)
        print("Credenciales cargadas correctamente")
    else:
        print("No se encontro la variable de entorno SERVICE_ACCOUNT_INFO") 
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SHEET_ID = '1DwHXQtOtBsAGnrAnDeZRSfxpI7cdRUOR0Ay563X888E'
    # sheet 07 1mExc_Gz1h3eWDya4kZgNRXiKDDwPq01b4VTeXDaK0wo
    # sheet 10 1DwHXQtOtBsAGnrAnDeZRSfxpI7cdRUOR0Ay563X888E

    try:
        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        # Leer columnas A (IN) y B (OUT) de la hoja
        rango = 'Nexa!A:B'
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=rango).execute()
        valores = result.get('values', [])
        
        if not valores:
            print("No se encontraron datos en Google Sheets.")
            return {}, []
            
        palabras_dict = {}
        palabras_out = set()
        
        # Asumiendo que la fila 0 tiene el encabezado IN | OUT
        for fila in valores[1:]:
            if len(fila) >= 2:
                # Ignorando mayúsculas y minúsculas validándolo mediante .upper() y borrando espacios extremos
                val_in = str(fila[0]).strip().upper()
                val_out = str(fila[1]).strip().upper()
                
                if val_in and val_out:
                    # Formateamos regex con límites de palabra para evitar que reemplace letras por dentro
                    palabras_dict[rf'\b{re.escape(val_in)}\b'] = val_out
                    palabras_out.add(val_out)
                    
        #print(f"¡Éxito! Diccionario de retroalimentación cargado con {len(palabras_dict)} registros desde Google Sheets.")
        return palabras_dict, list(palabras_out)
        
    except Exception as e:
        print(f"Error conectando a Google Sheets: {e}")
        return {}, []

def Fun_Estandarizador_Alfanumerico(api_key,df,nombre_columna):
        
    # Diccionarios de reemplazo simple.
    d_unidades = {'UNO': '1', 'DOS': '2', 'TRES': '3', 'CUATRO': '4', 'CINCO': '5', 'SEIS': '6', 'SIETE': '7', 'OCHO': '8', 'NUEVE': '9'}
    d_decenas = {'DIEZ': '10', 'VEINTE': '20', 'TREINTA': '30', 'CUARENTA': '40', 'CINCUENTA': '50', 'SESENTA': '60', 'SETENTA': '70', 'OCHENTA': '80', 'NOVENTA': '90'}
    d_especiales = {'ONCE': '11', 'DOCE': '12', 'TRECE': '13', 'CATORCE': '14', 'QUINCE': '15', 'DIECISEIS': '16', 'DIECISIETE': '17', 'DIECIOCHO': '18', 'DIECINUEVE': '19', 'VEINTIUNO': '21', 'VEINTIDOS': '22', 'VEINTITRES': '23', 'VEINTICUATRO': '24', 'VEINTICINCO': '25', 'VEINTISEIS': '26', 'VEINTISIETE': '27', 'VEINTIOCHO': '28', 'VEINTINUEVE': '29'}

    MAPEO_NUMEROS_TEXTO_DICT = {}

    # Compuestos tipo 'TREINTA Y TRES'
    for dec_k, dec_v in d_decenas.items():
        for uni_k, uni_v in d_unidades.items():
            palabra = f"{dec_k} Y {uni_k}"
            numero = str(int(dec_v) + int(uni_v))
            MAPEO_NUMEROS_TEXTO_DICT[rf'\b{palabra}\b'] = numero

    # Agregar especiales, decenas y unidades
    for k, v in d_especiales.items():
        MAPEO_NUMEROS_TEXTO_DICT[rf'\b{k}\b'] = v
    for k, v in d_decenas.items():
        MAPEO_NUMEROS_TEXTO_DICT[rf'\b{k}\b'] = v
    for k, v in d_unidades.items():
        MAPEO_NUMEROS_TEXTO_DICT[rf'\b{k}\b'] = v

    # Ordenar por longitud descendente para reemplazar compuestos primero (TREINTA Y TRES antes que TRES)
    MAPEO_NUMEROS_TEXTO = {k: v for k, v in sorted(MAPEO_NUMEROS_TEXTO_DICT.items(), key=lambda item: len(item[0]), reverse=True)}
    
    # Instanciamos las variables globales para inyectarlas directamente en el flujo
    PALABRAS_CONOCIDAS_DICT, PALABRAS_OUT_IGNORAR = obtener_palabras_conocidas()
    # Ordenar por longitud descendente para compuestos primero (ej. DECIMA TERCERA antes de DECIMA)
    MAPEO_PALABRAS_CONOCIDAS = {k: v for k, v in sorted(PALABRAS_CONOCIDAS_DICT.items(), key=lambda item: len(item[0]), reverse=True)}
    
    # 1. Vectorizar la normalización para máxima velocidad usando pd.Series.replace() de RegEx en todo el bloque
    df['address_qa'] = df[nombre_columna].astype(str).str.upper()

    # CASO 0: Sufijos numéricos directos (muy óptimo para 6TA, 13AVA, 22AVA, 1ER)
    df['address_qa'] = df['address_qa'].str.replace(r'\b(\d+)(AVA|AVO|TA|TO|MA|MO|VA|VO|RA|RO|ER|DA|DO)\b', r'\1', regex=True)
    
    # CASO 1: NÚMERO DESPEGADO DE LETRA (ej. 2A -> 2 A, 3BIS -> 3 BIS)
    df['address_qa'] = df['address_qa'].str.replace(r'(\d)([A-Z]+)', r'\1 \2', regex=True)

    # CASO 2: LETRA DESPEGADA DE NÚMERO (ej. A3 -> A 3)
    df['address_qa'] = df['address_qa'].str.replace(r'([A-Z]+)(\d)', r'\1 \2', regex=True)

    # CASO 3: NÚMEROS ALFABÉTICOS A NATURALES (ej. CARRERA UNO -> CARRERA 1)
    df['address_qa'] = df['address_qa'].replace(MAPEO_NUMEROS_TEXTO, regex=True)
    
    # CASO 4: CORRECCION DE PALABRAS CONOCIDAS POR RETROALIMENTACION
    df['address_qa'] = df['address_qa'].replace(MAPEO_PALABRAS_CONOCIDAS, regex=True)

    # Limpiamos dobles espacios y strip final
    df['address_qa'] = df['address_qa'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Restauramos vacíos iniciales si los hay
    df.loc[df[nombre_columna].isna(), 'address_qa'] = df[nombre_columna]

    # 2. Comparamos la original con la QA para ver si hubo un cambio
    df['original_limpia'] = df[nombre_columna].str.upper().str.replace(r'\s+', ' ', regex=True).str.strip()

    # 3. Asignamos la marca 'Directo' si hubo cambios
    df['ia_qa'] = None
    df.loc[df['original_limpia'] != df['address_qa'], 'ia_qa'] = 'Directo'

    # Eliminamos la columna temporal
    df = df.drop(columns=['original_limpia'])

    #print(df.loc[df['ia_qa'] == 'Directo', [nombre_columna,'address_qa','ia_qa']])
    
    #print(f"1. RES METODO 1: {df}")
    
    # ==========================================
    # INICIO DEL SEGUNDO METODO POR IA
    # ==========================================

    # ==========================================
    # EJECUCIÓN DEL METODO 2
    # ==========================================

    if 'address_qa' not in df.columns:
        df['address_qa'] = df['direccion']
        
    #df['ia_qa'] = None

    # 3. Llamada masiva y filtrada a Gemini
    diccionario_ia = obtener_diccionario_correcciones_gemini(api_key, df,PALABRAS_OUT_IGNORAR, columna='address_qa')

    if diccionario_ia:
        # 4. Clonamos la columna address_qa a temp para comparar los cambios hechos solo por IA
        df['address_temp'] = df['address_qa']
        
        # 5. Aplicamos los reemplazos de la IA iterando sobre los hallazgos
        #for mala_palabra, correccion in diccionario_ia.items():
            # Usamos \b para que coincida con la palabra exacta y no un fragmento
            #patron = r'\b' + re.escape(mala_palabra) + r'\b'
            #df['address_qa'] = df['address_qa'].str.replace(patron, str(correccion), regex=True)
            
        # Creamos un diccionario de regex para que solo reemplace palabras completas
        dict_regex = {rf'\b{re.escape(k)}\b': v for k, v in diccionario_ia.items()}
        
        # Aplicamos TODO el diccionario de una sola vez
        df['address_qa'] = df['address_qa'].replace(dict_regex, regex=True)
        
        # Limpiamos posibles espacios dobles
        df['address_qa'] = df['address_qa'].str.replace(r'\s+', ' ', regex=True).str.strip()
        
        # 6. Asignamos la marca 'Gemini' en ia_qa donde haya diferencias
        condicion_cambio_ia = df['address_temp'] != df['address_qa']
        df.loc[condicion_cambio_ia, 'ia_qa'] = 'Gemini'
        
        # Eliminamos la columna temporal de soporte
        df = df.drop(columns=['address_temp'])

    #print(f"3. RES METODO 2: {df}")
    # Revisamos el resultado final
    #print("PROCESO GENERADO EXITOSAMENTE...")
    
    return df
        
def obtener_diccionario_correcciones_gemini(api_key, df, PALABRAS_OUT_IGNORAR, columna):

    genai.configure(api_key=api_key, transport="rest")
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    #print("Extrayendo vocabulario único del DataFrame...")
    
    tipos_via_correctos = {
        'CALLE', 'CARRERA', 'DIAGONAL', 'TRANSVERSAL', 'AVENIDA', 'CIRCULAR',
        'SUR', 'NORTE', 'ESTE', 'OESTE', 
        'BIS', 
        'VIA', 'AUTOPISTA',
        'MANZANA', 'LOTE', 'CASA'
    }
    
    conectores = {'DE', 'LA', 'LAS', 'EL', 'LOS', 'EN', 'CON', 'DEL', 'AL', 'Y', 'POR'}
    palabras_ignoradas = tipos_via_correctos.union(conectores)
    
    # Sumamos las palabras que ya mapeamos manualmente como correctas en Google Sheets (Columna OUT)
    palabras_ignoradas = palabras_ignoradas.union(set(PALABRAS_OUT_IGNORAR))
        
    todas_las_direcciones = " ".join(df[columna].dropna().astype(str).str.upper().tolist())
    palabras_encontradas = set(re.findall(r'\b[A-Z]{4,}\b', todas_las_direcciones))
    
    palabras_sospechosas = list(palabras_encontradas - palabras_ignoradas)
    #print(f'Las palabras sospechos son: {palabras_sospechosas}')
    
    if not palabras_sospechosas:
        print("No se encontraron palabras para analizar.")
        return {}
        
    print(f"Se encontraron {len(palabras_sospechosas)} palabras únicas a evaluar. Consultando a Gemini...")
    
    tamano_lote = 150 
    diccionario_final_ia = {}
    
    for i in range(0, len(palabras_sospechosas), tamano_lote):
        lote_actual = palabras_sospechosas[i:i + tamano_lote]
        print(f"Procesando lote {i//tamano_lote + 1} ({len(lote_actual)} palabras)...")
        
        prompt = f"""
        Eres un corrector ortográfico estricto de direcciones de Latinoamérica.
        A continuación tienes una lista de palabras extraídas de direcciones (cada palabra es un string).
        
        Tu tarea es identificar ÚNICAMENTE:
        1. ERRORES DE ORTOGRAFÍA CLAROS en palabras comunes de vías (ej: CALLLE -> CALLE, ARRROYO -> ARROYO, DIAGOONAL -> DIAGONAL, TRASVERSAL -> TRANSVERSAL).
        2. Números equivocados a texto que deban ser dígitos y no se hayan corregido antes (ej: SEG -> 2, TERC -> 3).

        REGLAS ESTRICTAS QUE DEBES OBEDECER SIN EXCEPCIÓN:
        - NO conviertas ni expandas siglas o abreviaturas. Ignóralas por completo (ej: STA debe seguir como STA, PTE como PTE, AVE como AVE, AV como AV, CRA como CRA). NO INTENTES ADIVINAR.
        - NO conviertas números romanos. Ignóralos por completo (ej: IV, V, X, XX, II deben permanecer igual).
        - IGNORA nombres propios (de barrios, calles, conjuntos, personas, animales, apellidos).
        - IGNORA errores que solo sea por tildes, NO agregues palabras que su unico error sea la tilde.
        - SI TIENES DUDAS sobre si una palabra es un error, una sigla, nombre propio o número romano, IGNÓRALA.
        
        Devuélveme ÚNICAMENTE un objeto JSON válido donde:
        - Key: Palabra con ERROR ORTOGRÁFICO EVIDENTE.
        - Value: Corrección sugerida (la palabra completa o el dígito).
        Ejemplo del JSON esperado: {{"CALLLE": "CALLE", "ARRROYO": "ARROYO", "PRI": "1"}}
        Si ninguna palabra cumple o si todo parece sigla/nombre propio/romano, devuelve un JSON vacío: {{}}
        
        Lista de palabras a evaluar:
        {lote_actual}
        """
        
        intentos = 3
        for intento in range(intentos):
            try:
                respuesta = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                diccionario_lote = json.loads(respuesta.text)
                diccionario_final_ia.update(diccionario_lote)
                break
            except Exception as e:
                print(f"  > Advertencia: Intento {intento + 1} falló en el lote {i//tamano_lote + 1}: {str(e)}")
                if intento < intentos - 1:
                    print("  > Reintentando en 3 segundos...")
                    time.sleep(3)
                else:
                    print(f"Error definitivo procesando el lote {i//tamano_lote + 1}. Saltando este lote.")

    #print("Diccionario final generado por Gemini:")
    #print(json.dumps(diccionario_final_ia, indent=2, ensure_ascii=False))
    
    directorio_actual = os.path.dirname(__file__)
    ruta_json = os.path.join(directorio_actual, 'diccionario_ia_direcciones.json')
    
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(diccionario_final_ia, f, ensure_ascii=False, indent=4)
        
    carpeta_destino = r"C:\Nexa"
    ruta_destino = os.path.join(carpeta_destino, 'diccionario_ia_direcciones.json')
    # Ejecutar la función
    descargar_json(ruta_json, ruta_destino)    
    return diccionario_final_ia
    
    
def descargar_json(ruta_origen, ruta_destino):

    carpeta_destino = r"C:\Nexa"
    
    try:
        # 2. Verificar si la carpeta existe, si no, crearla
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
            #print(f"📁 Carpeta creada: {carpeta_destino}")
        
        # 3. Verificar que el archivo de origen exista antes de copiar
        if not os.path.exists(ruta_origen):
            print(f"❌ Error: El archivo origen no existe en {ruta_origen}")
            return

        # 4. Copiar y reemplazar (shutil.copy2 sobreescribe por defecto)
        shutil.copy2(ruta_origen, ruta_destino)
        #print(f"✅ Archivo copiado exitosamente a: {ruta_destino}")

    except PermissionError:
        print("❌ Error de Permisos: QGIS no tiene permiso para escribir en C:/. Prueba ejecutar QGIS como administrador.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

