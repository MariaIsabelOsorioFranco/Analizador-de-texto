import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
from streamlit_lottie import st_lottie
import json

st.set_page_config(
    page_title="Analizador de Texto",
    page_icon="🍊",
    layout="wide"
)

st.markdown("""
<style>
.stApp { 
    background-color: #fff5ec; 
    color: #4e342e !important; 
}

.stApp p, .stApp span, .stApp label, .stApp li, .stApp div {
    color: #4e342e !important;
}

section[data-testid="stSidebar"] { 
    background-color: #ffe0b2 !important; 
}
section[data-testid="stSidebar"] * {
    color: #4e342e !important;
}

h1, h2, h3, h4, h5, h6 { 
    color: #e65100 !important; 
}

div.stButton > button {
    background-color: #ff9800 !important; 
    color: white !important;
    border-radius: 12px;
    padding: 10px 24px;
    border: none;
    font-size: 16px;
    font-weight: bold;
    transition: all 0.3s ease;
}
div.stButton > button * {
    color: white !important;
}
div.stButton > button:hover {
    background-color: #ffe0b2 !important; 
    color: #4e342e !important;
}

.stTextArea textarea, .stTextInput input {
    background-color: #ffffff !important;
    border-color: #ffb74d !important;
    color: #4e342e !important;
}

.streamlit-expanderHeader, .streamlit-expanderContent {
    color: #4e342e !important;
}
</style>
""", unsafe_allow_html=True)

def cargar_lottie(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

try:
    animacion_positiva = cargar_lottie("positivo.json")
    animacion_negativa = cargar_lottie("negativo.json")
    animacion_neutral = cargar_lottie("neutral.json")
except:
    animacion_positiva = None
    animacion_negativa = None
    animacion_neutral = None

st.title("🍊 Analizador de Texto con TextBlob")

st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:

- Análisis de sentimiento y subjetividad
- Extracción de palabras clave
- Análisis de frecuencia de palabras
""")

st.sidebar.title("📙 Opciones")

modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

def contar_palabras(texto):
    stop_words = set([
        "a","al","algo","algunas","algunos","ante","antes","como","con",
        "contra","cual","cuando","de","del","desde","donde","durante",
        "e","el","ella","ellas","ellos","en","entre","era","es","esa",
        "esas","ese","eso","esos","esta","estas","este","esto","estos",
        "ha","han","hasta","he","la","las","le","les","lo","los","me",
        "mi","mis","mucho","muy","nada","ni","no","nos","o","otra",
        "otro","para","pero","poco","por","porque","que","quien","se",
        "si","sin","sobre","somos","son","soy","su","sus","también",
        "te","ti","tiene","todo","tu","tus","un","una","uno","unos",
        "y","ya","yo",
        "the","and","for","that","with","you","your","are","was","were",
        "this","have","from","they","their","would","there","what","when",
        "where","which","while","about","after","before","because","been",
        "being","into","through","during","above","below","between"
    ])

    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [
        palabra for palabra in palabras
        if palabra not in stop_words and len(palabra) > 2
    ]

    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1

    contador_ordenado = dict(
        sorted(contador.items(), key=lambda x: x[1], reverse=True)
    )
    return contador_ordenado

translator = Translator()

def traducir_texto(texto):
    try:
        traduccion = translator.translate(
            texto,
            src='es',
            dest='en'
        )
        return traduccion.text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)

    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity

    frases_originales = [
        frase.strip()
        for frase in re.split(r'[.!?]+', texto_original)
        if frase.strip()
    ]

    frases_traducidas = [
        frase.strip()
        for frase in re.split(r'[.!?]+', texto_ingles)
        if frase.strip()
    ]

    frases_combinadas = []
    for i in range(min(len(frases_originales), len(frases_traducidas))):
        frases_combinadas.append({
            "original": frases_originales[i],
            "traducido": frases_traducidas[i]
        })

    contador_palabras = contar_palabras(texto_ingles)

    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Análisis de Sentimiento y Subjetividad")
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        st.write("**Sentimiento:**")
        st.progress(sentimiento_norm)

        if resultados["sentimiento"] > 0.05:
            st.success(f"🍁 Positivo ({resultados['sentimiento']:.2f})")
            if animacion_positiva:
                st_lottie(animacion_positiva, height=180, key="positivo")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"🍂 Negativo ({resultados['sentimiento']:.2f})")
            if animacion_negativa:
                st_lottie(animacion_negativa, height=180, key="negativo")
        else:
            st.info(f"🍊 Neutral ({resultados['sentimiento']:.2f})")
            if animacion_neutral:
                st_lottie(animacion_neutral, height=180, key="neutral")

        st.write("**Subjetividad:**")
        st.progress(resultados["subjetividad"])

        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})")

    with col2:
        st.subheader("Palabras más frecuentes")
        if resultados["contador_palabras"]:
            palabras_top = dict(list(resultados["contador_palabras"].items())[:10])
            st.bar_chart(palabras_top)

    st.subheader("Texto Traducido")
    with st.expander("Ver traducción completa"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Texto Original (Español):**")
            st.text(resultados["texto_original"])
        with col2:
            st.markdown("**Texto Traducido (Inglés):**")
            st.text(resultados["texto_traducido"])

    st.subheader("Frases detectadas")
    if resultados["frases"]:
        for i, frase_dict in enumerate(resultados["frases"][:10], 1):
            frase_original = frase_dict["original"]
            frase_traducida = frase_dict["traducido"]
            blob_frase = TextBlob(frase_traducida)
            sentimiento = blob_frase.sentiment.polarity

            if sentimiento > 0.05:
                emoji = "😊"
            elif sentimiento < -0.05:
                emoji = "😟"
            else:
                emoji = "😐"

            st.write(f"{i}. {emoji} **Original:** *\"{frase_original}\"*")
            st.write(f"   **Traducción:** *\"{frase_traducida}\"*")
            st.write("---")
    else:
        st.write("No se detectaron frases.")

if modo == "Texto directo":
    st.subheader("Ingresa tu texto para analizar")
    texto = st.text_area(
        "",
        height=200,
        placeholder="Escribe o pega aquí el texto..."
    )

    if st.button("Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando texto..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("Por favor ingresa un texto.")

elif modo == "Archivo de texto":
    st.subheader("Carga un archivo de texto")
    archivo = st.file_uploader(
        "",
        type=["txt", "csv", "md"]
    )

    if archivo is not None:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            with st.expander("Ver contenido del archivo"):
                st.text(contenido[:1000])

            if st.button("Analizar archivo"):
                with st.spinner("Analizando archivo..."):
                    resultados = procesar_texto(contenido)
                    crear_visualizaciones(resultados)
        except Exception as e:
            st.error(f"Error al procesar archivo: {e}")

with st.expander("📚 Información sobre el análisis"):
    st.markdown("""
### Sobre el análisis de texto

- **Sentimiento**: Va de -1 (muy negativo) a 1 (muy positivo)
- **Subjetividad**: Va de 0 (objetivo) a 1 (subjetivo)

### Librerías utilizadas

```txt
streamlit
textblob
pandas
googletrans==4.0.0rc1
streamlit-lottie
""")
