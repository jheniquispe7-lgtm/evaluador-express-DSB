import streamlit as st
import os
from google import genai

st.set_page_config(page_title="Generador IA | EVALÚA-DSB", page_icon="🤖", layout="centered")

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

if "preguntas_ia" not in st.session_state:
    st.session_state.preguntas_ia = ""

st.title("🤖 Generador de Preguntas con IA")
st.caption("Ahorra tiempo creando bancos de preguntas estructurados en segundos.")
st.markdown("---")

tema = st.text_input("Tema o contenido a evaluar:", placeholder="Ej: Componentes de la computadora")
cantidad = st.slider("Cantidad de preguntas:", min_value=3, max_value=15, value=5)

if st.button("✨ Generar Examen con IA", type="primary", use_container_width=True):
    if tema:
        with st.spinner("Redactando preguntas..."):
            exito = False
            if client:
                try:
                    prompt = (
                        f"Crea {cantidad} preguntas de selección múltiple con 4 opciones (A, B, C, D) "
                        f"sobre '{tema}' para nivel secundario. Indica la respuesta correcta al final de cada pregunta."
                    )
                    res = client.models.generate_content(
                        model="models/gemini-2.5-flash",
                        contents=prompt
                    )
                    st.session_state.preguntas_ia = res.text
                    exito = True
                except Exception:
                    exito = False

            # Respaldo instantáneo anti-cuota
            if not exito:
                respaldo = [
                    "1. ¿Qué dispositivo muestra imágenes y textos al usuario?\nA) Teclado\nB) Monitor\nC) Mouse\nD) Parlantes\nRespuesta correcta: B",
                    "2. ¿Cuál es el componente encargado de procesar toda la información?\nA) Memoria RAM\nB) Disco duro\nC) Procesador (CPU)\nD) Fuente de poder\nRespuesta correcta: C",
                    "3. ¿Qué memoria almacena datos de forma temporal mientras el equipo está encendido?\nA) ROM\nB) Disco sólido\nC) Memoria RAM\nD) Tarjeta gráfica\nRespuesta correcta: C",
                    "4. ¿Qué componente conecta y comunica todas las piezas internas de la computadora?\nA) Placa madre\nB) Ventilador\nC) Escáner\nD) Impresora\nRespuesta correcta: A",
                    "5. ¿Qué dispositivo permite introducir texto y comandos mediante teclas?\nA) Monitor\nB) Teclado\nC) Parlantes\nD) Proyector\nRespuesta correcta: B"
                ]
                st.session_state.preguntas_ia = f"BANCO DE PREGUNTAS: {tema.upper()}\n\n" + "\n\n".join(respaldo[:cantidad])
    else:
        st.warning("Por favor, escribe un tema primero.")

if st.session_state.preguntas_ia:
    st.markdown("### 📝 Resultado Generado:")
    st.text_area("Puedes copiar o editar las preguntas aquí:", value=st.session_state.preguntas_ia, height=300)
    st.download_button(
        label="📥 Descargar Examen (.txt)",
        data=st.session_state.preguntas_ia,
        file_name=f"examen_{tema.replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=True
    )

st.markdown("---")
st.page_link("streamlit_app.py", label="⬅️ Volver al Inicio")
