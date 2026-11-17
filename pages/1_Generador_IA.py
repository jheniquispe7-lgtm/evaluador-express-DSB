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

tema = st.text_input("Tema o contenido a evaluar:", placeholder="Ej: La Célula, Segunda Guerra Mundial, Hardware...")
cantidad = st.slider("Cantidad de preguntas:", min_value=3, max_value=15, value=5)

if st.button("✨ Generar Examen con IA", type="primary", use_container_width=True):
    if tema:
        with st.spinner(f"Redactando preguntas sobre '{tema}'..."):
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

            # Respaldo dinámico instantáneo (0 peso, adaptado al tema ingresado)
            if not exito:
                plantillas = [
                    f"1. ¿Cuál es la definición principal o concepto fundamental de {tema}?\nA) Un proceso aislado sin aplicación práctica\nB) El conjunto de principios y elementos que estructuran {tema}\nC) Una herramienta exclusivamente decorativa\nD) Ninguna de las anteriores\nRespuesta correcta: B",
                    f"2. ¿Cuál de los siguientes factores es indispensable para comprender {tema}?\nA) El análisis de sus componentes básicos y su función\nB) Ignorar su contexto histórico o técnico\nC) Aplicar únicamente criterios subjetivos\nD) Suprimir sus etapas principales\nRespuesta correcta: A",
                    f"3. ¿Qué impacto o utilidad principal tiene el estudio de {tema} en la actualidad?\nA) Carece de relevancia en el ámbito académico\nB) Solo se aplica en teorías antiguas\nC) Permite resolver problemas y optimizar procesos relacionados con {tema}\nD) Limita el desarrollo del conocimiento\nRespuesta correcta: C",
                    f"4. Dentro de la clasificación o estructura de {tema}, ¿qué elemento cumple un rol central?\nA) La desorganización de sus partes\nB) La interacción ordenada entre sus elementos fundamentales\nC) La ausencia de reglas o principios\nD) El aislamiento total del entorno\nRespuesta correcta: B",
                    f"5. ¿Cómo se evalúa correctamente la aplicación práctica de {tema}?\nA) Mediante la memorización sin comprensión\nB) Evitando cualquier tipo de comprobación\nC) Identificando sus características clave y resultados esperados\nD) Descartando sus fundamentos teóricos\nRespuesta correcta: C"
                ]
                # Si piden más de 5 preguntas en modo respaldo, completa numerando correlativamente
                extra = [
                    f"{i}. Pregunta de análisis complementario sobre {tema} (Nivel Secundario):\nA) Opción de concepto A\nB) Opción de concepto B\nC) Opción correcta fundamentada en {tema}\nD) Opción de concepto D\nRespuesta correcta: C"
                    for i in range(6, cantidad + 1)
                ]
                todas = (plantillas + extra)[:cantidad]
                st.session_state.preguntas_ia = f"EVALUACIÓN ACADÉMICA - TEMA: {tema.upper()}\n\n" + "\n\n".join(todas)
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
