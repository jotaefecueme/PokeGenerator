import os
import streamlit as st
from typing import List
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER")
# Eliminamos la carga fija de temperatura aquí
# TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", 1))

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
    region: str = Field(..., description="Región a la que pertenece el Pokémon")
    color: str = Field(..., description="Color dominante del Pokémon")
    descripcion_pokedex: str = Field(..., description="Descripción breve del Pokémon según la Pokédex")
    descripcion_grafica: str = Field(..., description="Descripción visual del aspecto del Pokémon")
    tipo: List[str] = Field(..., description="Lista de tipos del Pokémon")
    altura_m: float = Field(..., description="Altura del Pokémon en metros")
    peso_kg: float = Field(..., description="Peso del Pokémon en kilogramos")
    habilidad: str = Field(..., description="Habilidad principal del Pokémon")
    descripcion_habilidad: str = Field(..., description="Explicación de lo que hace la habilidad")
    ataques: List[str] = Field(..., description="Lista de ataques característicos del Pokémon")
    stats_base: StatsBase = Field(..., description="Estadísticas base del Pokémon")
    evoluciones: List[str] = Field(..., description="Lista de nombres de Pokémon en su línea evolutiva")

st.set_page_config(page_title="PokeGenerator | jotaefecueme", layout="wide")
st.title("PokeGenerator | jotaefecueme")

idea = st.text_area(
    "Describe la idea para generar un Pokémon:", 
    height=150, 
    value="un pokémon que consuma fentanilo se llame paquito, que sea legendario y al menos uno de sus ataques sea CHOCOLATE PARA TODOS!"
)

# Barra para temperatura, rango típico 0-2, default 1
temperature = st.slider("Temperatura de generación", min_value=0.0, max_value=2.0, value=1.0, step=0.1)

if st.button("Generar Pokémon"):
    if not idea.strip():
        st.error("Introduce una idea para generar el Pokémon.")
    else:
        with st.spinner("Generando Pokémon..."):
            try:
                # Inicializamos el modelo aquí con la temperatura dinámica
                llm = init_chat_model(
                    model=MODEL_NAME,
                    model_provider=MODEL_PROVIDER,
                    api_key=GROQ_API_KEY,
                    temperature=temperature,
                )
                structured_llm = llm.with_structured_output(Pokemon)
                
                resultado = structured_llm.invoke(
                    f"Genera un Pokémon basado en esta idea: {idea}. "
                    "Rellena todos los campos del modelo de forma temática. Sé creativo, "
                    "todos los campos tienen que ser originales, pero a la misma vez realistas para ser un pokémon. "
                    "No seas genérico, intenta ser genuino y creativo."
                )
                pokemon = Pokemon.parse_obj(resultado)
                st.success("Pokémon generado correctamente:")
                st.json(pokemon.dict())
            except ValidationError as ve:
                st.error(f"Error de validación del Pokémon generado:\n{ve}")
            except Exception as e:
                st.error(f"Error generando Pokémon:\n{e}")
