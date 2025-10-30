import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# ------------------- FUNCIONES AUXILIARES -------------------

def limpiar_audios_antiguos(dias):
    """Elimina archivos .mp3 más antiguos que 'dias' días en la carpeta temp."""
    mp3_files = glob.glob("temp/*.mp3")
    if mp3_files:
        ahora = time.time()
        limite = dias * 86400
        for archivo in mp3_files:
            if os.stat(archivo).st_mtime < ahora - limite:
                os.remove(archivo)
                print("🧹 Archivo eliminado:", archivo)


def texto_a_audio(idioma_entrada, idioma_salida, texto, dominio_tld):
    """Traduce el texto y lo convierte a audio con gTTS."""
    traduccion = traductor.translate(texto, src=idioma_entrada, dest=idioma_salida)
    texto_traducido = traduccion.text
    try:
        nombre_archivo = texto[:20].strip().replace(" ", "_")
    except:
        nombre_archivo = "audio"
    ruta = f"temp/{nombre_archivo}.mp3"
    gTTS(texto_traducido, lang=idioma_salida, tld=dominio_tld, slow=False).save(ruta)
    return nombre_archivo, texto_traducido


# ------------------- CONFIGURACIÓN DE LA APP -------------------

st.set_page_config(page_title="Traductor OCR con Voz", page_icon="🈹")

st.title("🈹 Traductor con Reconocimiento Óptico y Voz")
st.markdown("Sube una imagen o toma una foto, extrae el texto, tradúcelo y escúchalo al instante 🎧")

# Crear carpeta temporal si no existe
os.makedirs("temp", exist_ok=True)
limpiar_audios_antiguos(7)

# ------------------- FUENTE DE IMAGEN -------------------

st.subheader("📸 Fuente de la imagen")
usar_camara = st.checkbox("Usar cámara en lugar de cargar archivo")

if usar_camara:
    imagen_capturada = st.camera_input("Toma una foto para analizar")
else:
    imagen_capturada = None

# Filtro solo para cámara
with st.sidebar:
    st.header("⚙️ Configuración de imagen")
    filtro_camara = st.radio("¿Aplicar filtro de inversión?", ("Sí", "No"))

# ------------------- CARGA DE IMAGEN -------------------

imagen_cargada = st.file_uploader("O carga una imagen (PNG/JPG):", type=["png", "jpg"])

texto_extraido = ""

if imagen_cargada is not None:
    st.image(imagen_cargada, caption="Imagen cargada correctamente ✅", use_container_width=True)
    
    # Guardar y procesar
    with open(imagen_cargada.name, 'wb') as f:
        f.write(imagen_cargada.read())

    img_cv = cv2.imread(imagen_cargada.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    texto_extraido = pytesseract.image_to_string(img_rgb)
    st.success("Texto detectado desde imagen cargada:")
    st.write(texto_extraido)

elif imagen_capturada is not None:
    bytes_imagen = imagen_capturada.getvalue()
    img_cv = cv2.imdecode(np.frombuffer(bytes_imagen, np.uint8), cv2.IMREAD_COLOR)
    
    if filtro_camara == "Sí":
        img_cv = cv2.bitwise_not(img_cv)

    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    texto_extraido = pytesseract.image_to_string(img_rgb)
    st.success("Texto detectado desde cámara:")
    st.write(texto_extraido)

# ------------------- CONFIGURACIÓN DE TRADUCCIÓN -------------------

with st.sidebar:
    st.header("🌍 Parámetros de traducción y voz")
    traductor = Translator()

    idioma_entrada = st.selectbox("Lenguaje de entrada", ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés"))
    idioma_salida = st.selectbox("Lenguaje de salida", ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés"))

    # Mapeo de idiomas
    codigos_idioma = {
        "Inglés": "en",
        "Español": "es",
        "Bengalí": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
    }

    input_lang = codigos_idioma[idioma_entrada]
    output_lang = codigos_idioma[idioma_salida]

    acento = st.selectbox(
        "Acento del inglés (si aplica):",
        ("Por defecto", "India", "Reino Unido", "EE.UU.", "Canadá", "Australia", "Irlanda", "Sudáfrica")
    )

    acentos_tld = {
        "Por defecto": "com",
        "India": "co.in",
        "Reino Unido": "co.uk",
        "EE.UU.": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
    }
    dominio_tld = acentos_tld[acento]

    mostrar_texto = st.checkbox("Mostrar texto traducido")
    traducir_y_voz = st.button("🔊 Traducir y reproducir audio")

# ------------------- GENERACIÓN DE AUDIO -------------------

if traducir_y_voz and texto_extraido.strip():
    archivo, texto_traducido = texto_a_audio(input_lang, output_lang, texto_extraido, dominio_tld)

    # Mostrar resultado
    st.subheader("🎧 Resultado del audio:")
    with open(f"temp/{archivo}.mp3", "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3")

    if mostrar_texto:
        st.subheader("📜 Texto traducido:")
        st.write(texto_traducido)

    
