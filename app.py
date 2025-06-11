import os
import streamlit as st
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import requests
import time
import threading
import time
import concurrent.futures

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER")

IMG_API_URL = "https://python-quality-fully.ngrok-free.app/generate"

class StatsBase(BaseModel):
    hp: int = Field(..., description="Puntos de salud del Pokémon")
    attack: int = Field(..., description="Ataque físico base del Pokémon")
    defense: int = Field(..., description="Defensa física base del Pokémon")
    special_attack: int = Field(..., description="Ataque especial base del Pokémon")
    special_defense: int = Field(..., description="Defensa especial base del Pokémon")
    speed: int = Field(..., description="Velocidad base del Pokémon")

class Pokemon(BaseModel):
    nombre: str = Field(..., description="Nombre del Pokémon")
    numero_pokedex: int = Field(..., description="Número oficial del Pokémon en la Pokédex")
    categoria: str = Field(..., description="Categoría del Pokémon")
    legendario: bool = Field(..., description="Indica si es un Pokémon legendario")
    region: str = Field(..., description="Región a la que pertenece el Pokémon, puedes inventarte una nueva región o usar una de las ya existentes.")
    color: str = Field(..., description="Color dominante del Pokémon")
    descripcion_pokedex: str = Field(..., description="Descripción breve del Pokémon según la Pokédex")
    descripcion_grafica: str = Field(..., description="Descripción visual del aspecto del Pokémon")
    tipo: list[str] = Field(..., description="Lista de tipos del Pokémon")
    altura_m: float = Field(..., description="Altura del Pokémon en metros")
    peso_kg: float = Field(..., description="Peso del Pokémon en kilogramos")
    habilidad: str = Field(..., description="Habilidad principal del Pokémon")
    descripcion_habilidad: str = Field(..., description="Explicación de lo que hace la habilidad")
    ataques: list[str] = Field(..., description="Lista de ataques característicos del Pokémon")
    stats_base: StatsBase = Field(..., description="Estadísticas base del Pokémon")
    evoluciones: list[str] = Field(..., description="Lista de nombres de Pokémon en su línea evolutiva")
    prompt_imagen: str = Field(
        ...,
            description=(
            "A single, clear, and concise sentence containing only the most important keywords describing the Pokémon's physical appearance: "
            "color, shape, size, posture, and distinctive features. "
            "Do not include art style, environment, or extra details. "
            "This description will be used to generate the Pokémon image. "
            "Must be written in English."
            )


    )

def generar_pokemon(idea: str, temperature: float, max_retries: int = 3, delay: float = 2.0) -> Pokemon:
    llm = init_chat_model(
        model=MODEL_NAME,
        model_provider=MODEL_PROVIDER,
        api_key=GROQ_API_KEY,
        temperature=temperature,
    )
    structured_llm = llm.with_structured_output(Pokemon)

    prompt = (
        f"Genera un Pokémon basado en esta idea: {idea}. "
        "Devuelve únicamente un objeto JSON que cumpla exactamente con el esquema del modelo `Pokemon`. "
        "Todos los campos deben estar en español, excepto el campo 'prompt_imagen', "
        "que debe contener un texto detallado y optimizado para un modelo de generación de imágenes, "
        "escrito en inglés, que describa con precisión y detalle el aspecto visual del Pokémon incluyendo color, forma, tamaño, textura, postura y cualquier característica distintiva. "
        "No añadas etiquetas, texto decorativo, explicaciones ni formato adicional. "
        "No uses comillas triples ni texto extra. Solo JSON puro."
    )


    last_exception = None
    for _ in range(max_retries):
        try:
            resultado = structured_llm.invoke(prompt)
            pokemon = Pokemon.model_validate(resultado)
            return pokemon
        except ValidationError as ve:
            last_exception = ve
            time.sleep(delay)
        except Exception as e:
            last_exception = e
            time.sleep(delay)
    raise last_exception

def generar_imagen(prompt: str) -> list[str]:
    payload = {"prompt": prompt}
    response = requests.post(IMG_API_URL, json=payload, timeout=60)
    if response.status_code == 200:
        data = response.json()
        return data.get("images", [])
    else:
        raise Exception(f"Error al generar imagen: {response.status_code} {response.text}")

st.set_page_config(page_title="PokeGenerator | jotaefecueme", layout="wide")

st.markdown(
    """
    <style>
    /* Fondo degradado suave */
    .main {
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: #f0f0f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 1.5rem 2rem;
    }

    /* Encabezado principal */
    .css-1v3fvcr h1 {
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: 0.1rem;
        color: #ffde59;
        text-shadow: 2px 2px 4px #000000cc;
        margin-bottom: 1rem;
    }

    /* Área de texto para idea */
    textarea {
        background-color: #121212;
        border: 2px solid #ffde59;
        border-radius: 12px;
        color: #fff;
        font-size: 1.1rem;
        padding: 0.8rem 1rem;
        resize: vertical;
        box-shadow: 0 0 12px #ffde5988;
        transition: border-color 0.3s ease;
    }
    textarea:focus {
        border-color: #ffd700;
        outline: none;
        box-shadow: 0 0 15px #ffd700cc;
    }

    /* Botones */
    button[kind="primary"] {
        background-color: #ffde59 !important;
        color: #121212 !important;
        font-weight: 700 !important;
        padding: 0.75rem 2rem !important;
        border-radius: 20px !important;
        box-shadow: 0 5px 15px #ffde5999 !important;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    button[kind="primary"]:hover {
        background-color: #ffc700 !important;
        color: #111 !important;
    }

    /* Slider */
    .stSlider > div {
        color: #ffde59;
        font-weight: 700;
    }

    /* JSON viewer box */
    .stJson {
        background: rgba(255, 222, 89, 0.15);
        border-radius: 15px;
        padding: 1rem;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 0.95rem;
        color: #f5f5f5;
        overflow-x: auto;
        box-shadow: inset 0 0 10px #ffde59aa;
    }

    /* Imagenes */
    .stImage > img {
        border-radius: 20px;
        box-shadow: 0 8px 15px rgba(255, 222, 89, 0.7);
        transition: transform 0.3s ease;
        margin-bottom: 1rem;
    }
    .stImage > img:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 25px rgba(255, 222, 89, 0.9);
    }

    /* Warning y Error */
    .stAlert {
        border-radius: 15px;
        padding: 1rem;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .stAlertWarning {
        background-color: #ffce45cc !important;
        color: #4b3500 !important;
    }
    .stAlertError {
        background-color: #ff5c5ccc !important;
        color: #5a0000 !important;
        white-space: pre-wrap;
    }

    /* Columnas más amplias */
    [data-testid="stColumns"] > div {
        padding: 0 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("PokeGenerator | jotaefecueme")

idea = st.text_area(
    "Describe el Pokémon que quieres generar, puedes dar todos los detalles que quieras.",
    height=68,
    value="un pokémon que consuma fentanilo se llame Paquito, que sea legendario y al menos uno de sus ataques sea CHOCOLATE PARA TODOS! y su region sea Españita"
)

if "pokemon" not in st.session_state:
    st.session_state.pokemon = None
if "error" not in st.session_state:
    st.session_state.error = None
if "last_idea" not in st.session_state:
    st.session_state.last_idea = ""
if "last_temp" not in st.session_state:
    st.session_state.last_temp = 0.6
if "imagenes" not in st.session_state:
    st.session_state.imagenes = []

if not idea.strip():
    st.warning("Introduce una idea para generar el Pokémon.")
    disabled = True
else:
    disabled = False

    if st.button("Generar Pokémon", disabled=False):
        with st.spinner("Generando Pokémon..."):
            try:
                pokemon = generar_pokemon(idea, st.session_state.last_temp)
                st.session_state.pokemon = pokemon.model_dump()
                st.session_state.error = None
                st.session_state.imagenes = []
                st.session_state.last_idea = idea
            except ValidationError as ve:
                st.session_state.error = f"Error de validación del Pokémon generado:\n{ve}"
                st.session_state.pokemon = None
            except Exception as e:
                st.session_state.error = f"Error generando Pokémon:\n{e}"
                st.session_state.pokemon = None

if st.session_state.pokemon is not None:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Datos generados del Pokémon:")
        st.markdown("**Nivel de fantasía:**")
        col_slider, _ = st.columns([2, 1])  
        with col_slider:
            nivel_fantasia = st.slider(
                label="slider_nivel_fantasia",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.last_temp,
                step=0.01,
                label_visibility="collapsed",
            )

        st.session_state.last_temp = nivel_fantasia

        st.json(st.session_state.pokemon)

    with col2:
        st.subheader("Imágenes generadas del Pokémon:")

        if st.button("Generar imagenes", disabled=(not st.session_state.pokemon)):
            try:
                descripcion_visual = st.session_state.pokemon['prompt_imagen']
                st.session_state.imagenes = []
                st.session_state.error = None

                progress_bar = st.progress(0)

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(generar_imagen, descripcion_visual)

                    for i in range(140):  
                        time.sleep(0.1)
                        progress_bar.progress((i + 1) / 140)
                        if future.done():
                            break

                    progress_bar.progress(1.0)

                    imagenes = future.result()
                    st.session_state.imagenes = imagenes

            except Exception as e:
                mensaje = (
                    "AH! AH! AH!\n"
                    "¡NO HAS DICHO LA PALABRA MÁGICA!\n\n"
                    "El servicio de generación de imágenes está desactivado -> avisa a jotaefecueme\n\n"
                ) * 10
                st.session_state.error = mensaje

        if st.session_state.get("error"):
            st.error(st.session_state.error)

        if st.session_state.imagenes:
            for i in range(0, len(st.session_state.imagenes), 2):
                cols = st.columns(2)
                for j, img_b64 in enumerate(st.session_state.imagenes[i:i+2]):
                    img_data_url = f"data:image/png;base64,{img_b64}"
                    cols[j].image(img_data_url, use_container_width=True)
