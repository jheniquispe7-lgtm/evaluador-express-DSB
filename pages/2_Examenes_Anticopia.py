import streamlit as st
import random

st.set_page_config(page_title="Exámenes Anti-Copia | EVALÚA-DSB", page_icon="🔀", layout="wide")

st.title("🔀 Generador de Exámenes Aleatorios (Anti-Copia)")
st.caption("Mezcla el orden de las preguntas en distintas filas para evaluar el conocimiento real de cada estudiante.")
st.markdown("---")

texto_preguntas = st.text_area(
    "Pegue aquí su lista de preguntas (una pregunta por línea):",
    height=180,
    placeholder="¿Qué es el hardware?\n¿Qué dispositivo muestra imágenes?\n¿Cuál es el cerebro de la computadora?\n¿Qué memoria es temporal?"
)

col_opt1, col_opt2 = st.columns([1, 2])
with col_opt1:
    num_filas = st.radio("Cantidad de versiones (Filas):", [2, 3], horizontal=True)

if st.button("🎲 Mezclar y Generar Filas", type="primary"):
    lineas = [l.strip() for l in texto_preguntas.split("\n") if l.strip()]
    
    if len(lineas) >= 2:
        st.success(f"¡Se generaron {num_filas} versiones diferentes con {len(lineas)} preguntas cada una!")
        letras = ["A", "B", "C"][:num_filas]
        columnas = st.columns(num_filas)
        texto_descarga = ""

        for i, letra in enumerate(letras):
            mezcla = lineas.copy()
            random.shuffle(mezcla)
            texto_descarga += f"=== FILA {letra} ===\n"
            
            with columnas[i]:
                st.markdown(f"### 📄 FILA {letra}")
                for idx, p in enumerate(mezcla, 1):
                    # Limpia numeración vieja si el usuario copió números
                    limpia = p.split(".", 1)[-1].strip() if p[0].isdigit() and "." in p[:4] else p
                    st.write(f"**{idx}.** {limpia}")
                    texto_descarga += f"{idx}. {limpia}\n"
                texto_descarga += "\n"

        st.markdown("---")
        st.download_button(
            label="📥 Descargar Todas las Filas Listas para Imprimir (.txt)",
            data=texto_descarga,
            file_name="examenes_anticopia_dsb.txt",
            mime="text/plain"
        )
    else:
        st.warning("Ingrese al menos 2 preguntas (una debajo de otra) para poder mezclarlas.")

st.markdown("---")
st.page_link("streamlit_app.py", label="⬅️ Volver al Inicio")
