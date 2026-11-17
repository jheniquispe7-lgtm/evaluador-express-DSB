import streamlit as st
import os

st.set_page_config(
    page_title="EVALÚA - DSB | Inicio",
    page_icon="🏫",
    layout="centered"
)

# --- BANNER INSTITUCIONAL (Sello de identidad) ---
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.jpg.jpg"):
    st.image("banner.jpg.jpg", use_container_width=True)

st.title("EVALÚA - DSB")
st.subheader("Plataforma Modular de Apoyo Docente")
st.markdown(
    "Herramienta diseñada para optimizar el tiempo de elaboración de evaluaciones "
    "y garantizar la transparencia académica en la **Unidad Educativa Daniel Sánchez Bustamante**."
)

st.markdown("---")
st.markdown("### Seleccione la herramienta que desea utilizar:")

col1, col2 = st.columns(2)

with col1:
    st.info("🤖 **Generador con IA**\n\nCrea bancos de preguntas desde cero en segundos para ahorrar tiempo de planificación.")
    st.page_link("pages/1_Generador_IA.py", label="Abrir Generador IA", icon="➡️", use_container_width=True)

with col2:
    st.success("🔀 **Exámenes Anti-Copia**\n\nGenera filas aleatorias (A, B, C) para evaluar el conocimiento real del estudiante.")
    st.page_link("pages/2_Examenes_Anticopia.py", label="Abrir Mezclador", icon="➡️", use_container_width=True)

st.markdown("---")
with st.expander("📷 Módulo Experimental: Escáner Óptico por Visión"):
    st.caption("Herramienta complementaria sujeta a condiciones de iluminación y enfoque de cámara.")
    st.page_link("pages/3_Escaner_Optico.py", label="Ir al Escáner Óptico", icon="🔍")
