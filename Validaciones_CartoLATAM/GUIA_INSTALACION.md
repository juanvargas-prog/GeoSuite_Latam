# Guía de Instalación y Uso
## Validaciones CartoLatam — Plugin QGIS

---

## ¿Qué es esta herramienta?

Plugin de QGIS que valida la calidad de capas cartográficas (vías, sitios, manzanas, etc.)
contra las reglas de negocio de cada país latinoamericano. Genera reportes HTML y CSV,
detecta errores de atributos, topología y geocódigos, y envía los resultados por correo.

---

## LO QUE NECESITAS ANTES DE EMPEZAR

| Requisito | Descripción |
|-----------|-------------|
| QGIS 3.16 o superior | Instalado en tu equipo |
| Cuenta Gmail | La que usarás para enviar reportes |
| Verificación en 2 pasos activa | Necesaria para generar la contraseña de app |
| El archivo `.zip` del plugin | Te lo envía el administrador (Bryan) |
| Tu archivo `.env` personal | Te lo envía el administrador por WhatsApp/Teams |

---

## PASO 1 — Instalar el plugin en QGIS

1. Abre **QGIS**
2. Ve al menú: `Complementos → Administrar e instalar complementos`
3. Haz clic en la pestaña **"Instalar desde ZIP"**
4. Selecciona el archivo `Validaciones_CartoLATAM.zip` que recibiste
5. Clic en **"Instalar complemento"**
6. QGIS mostrará un mensaje de instalación exitosa

> ✅ El plugin se descargará automáticamente desde GitHub al primer uso.
> Necesitas conexión a internet en este paso.

---

## PASO 2 — Crear tu archivo de configuración (.env)

El archivo `.env` contiene tus credenciales personales.
**Nunca lo compartas ni lo subas a ningún lugar.**

### Opción A — El administrador te lo envía listo (recomendado)

Bryan te envía un mensaje con el contenido de tu `.env`. Solo debes:

1. Abre el Explorador de Windows
2. Ve a la carpeta del plugin instalado:
   ```
   C:\Users\TU_USUARIO\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\Validaciones_CartoLATAM\
   ```
   > 💡 Si no ves la carpeta `AppData`, activa "Mostrar archivos ocultos" en el Explorador
3. Crea un archivo nuevo llamado exactamente `.env` (sin extensión adicional)
4. Pega el contenido que te envió Bryan
5. Guarda el archivo

### Opción B — Crearlo desde la plantilla

1. En la carpeta del plugin, copia el archivo `.env.example` y renómbralo como `.env`
2. Ábrelo con el Bloc de notas y completa los valores:

```
GITHUB_TOKEN=el_token_que_te_dio_bryan
GITHUB_REPO=bryanmora-star/validaciones_cartolatam
CREDENTIALS_KEY=la_clave_que_te_dio_bryan
GMAIL_REMITENTE=tucorreo@tudominio.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
CORREO_REPORTE_COMPLETO=lider@tudominio.com
CORREO_REPORTE_RESUMIDO=equipo@tudominio.com
```

---

## PASO 3 — Obtener tu contraseña de aplicación Gmail

*(Solo si vas a enviar reportes por correo)*

1. Ve a **myaccount.google.com**
2. Clic en **Seguridad** (menú izquierdo)
3. Busca **"Verificación en 2 pasos"** → actívala si no está activa
4. Regresa a Seguridad → busca **"Contraseñas de aplicaciones"**
5. Selecciona: App = `Otra (nombre personalizado)` → escribe `QGIS CartoLatam`
6. Clic en **Generar** → copia los 16 caracteres que aparecen
7. Pégalos en tu `.env` como valor de `GMAIL_APP_PASSWORD`

---

## PASO 4 — Verificar que todo funciona

1. **Cierra y abre QGIS**
2. En la barra de herramientas verás el ícono del plugin (Q con checkmark verde)
3. Haz clic — debe abrir el diálogo principal sin errores
4. Si aparece un aviso de "Nueva versión disponible" → acepta para completar la instalación

---

## PASO 5 — Configurar el correo desde la interfaz (alternativa al .env manual)

Si prefieres no editar el `.env` a mano, puedes configurar el correo desde la interfaz:

1. Abre el plugin
2. En la pantalla de Selección, junto a la sección de correo, haz clic en **⚙ Configurar**
3. Llena tu correo, contraseña de app y destinatarios
4. Clic en **"Probar conexión"** para verificar
5. Clic en **"Guardar configuración"**

---

## CÓMO USAR LA HERRAMIENTA

### Modo VALIDAR (revisión interna)
Para revisar y corregir errores antes de la entrega:
1. Selecciona **🔍 VALIDAR**
2. Escribe el nombre de la tarea (ej: "Revisión vías Colombia semana 3")
3. Selecciona el **País** y las **Capas** a validar
4. Elige qué validar: **Atributos**, **Topología**, **Geocódigos** (o los tres)
5. Clic en **"Validar Atributos + Topología + Geocódigos →"**
6. Espera el proceso — verás el avance en tiempo real
7. Al terminar: revisa el resumen agrupado por tipo de error
8. Opcionalmente envíate el reporte por correo para trabajarlo offline

### Modo VALIDACIÓN FINAL (entrega oficial)
Para generar el reporte oficial que va al líder:
1. Selecciona **📋 VALIDACIÓN FINAL**
2. Escribe el nombre de la tarea
3. Los tres tipos de validación se activan automáticamente
4. Configura el correo del líder en la sección de correo
5. Clic en **"Validar Atributos + Topología + Geocódigos →"**
6. Al terminar: revisa los resultados y clic en **"Enviar entrega al líder"**
   > ⚠️ Si la calidad es menor al 70%, el sistema pedirá confirmación antes de enviar

---

## ACTUALIZACIONES AUTOMÁTICAS

El plugin se actualiza solo cada vez que abres QGIS.
Si hay una versión nueva, aparecerá un mensaje:

```
Nueva versión disponible: v1.1.0 (instalada: v1.0.2)
¿Descargar e instalar ahora?  [Sí] [No]
```

Acepta y reinicia QGIS para aplicar los cambios.

---

## SOLUCIÓN DE PROBLEMAS

| Problema | Solución |
|---------|---------|
| "No se pudo descargar el plugin" | Verifica GITHUB_TOKEN en tu .env y conexión a internet |
| "Error 401 Unauthorized" | El token de GitHub expiró — pídele uno nuevo a Bryan |
| Error al enviar correo | Verifica GMAIL_APP_PASSWORD en tu .env o usa ⚙ Configurar en la interfaz |
| "No se encontró CREDENTIALS_KEY" | Pide la clave al administrador (Bryan) |
| Las capas no cargan | Asegúrate de que las capas estén cargadas en QGIS antes de abrir el plugin |
| Caché de Sheets desactualizado | El caché se renueva automáticamente cada 24 horas |

---

## CONTACTO

**Administrador del plugin:** Bryan Mora  
**Correo:** bryan.mora@servinformacion.com  
**Problemas técnicos:** crear issue en el repositorio de GitHub

---

*Versión del documento: 1.1.0 — Servinformación*
