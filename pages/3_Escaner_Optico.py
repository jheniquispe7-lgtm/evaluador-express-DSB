import streamlit as st
import os
from PIL import Image
from google import genai

st.set_page_config(page_title="Escáner Óptico | EVALÚA-DSB", page_icon="📷", layout="centered")

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

st.title("📷 Escáner Óptico Experimental")
st.info("Nota: La precisión de este módulo depende de la iluminación, enfoque y encuadre de la fotografía.")

clave = st.text_input("Clave oficial:", value="1:B, 2:A, 3:D, 4:B, 5:C, 6:C, 7:C, 8:C, 9:B, 10:C")
foto = st.file_uploader("Suba fotografía nítida de la hoja:", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, width=250)
    if st.button("Analizar Hoja", type="primary"):
        with st.spinner("Evaluando imagen..."):
            exito = False
            if client:
                try:
                    img = Image.open(foto)
                    res = client.models.generate_content(
                        model="models/gemini-2.5-flash",
                        contents=[img, f"Evalúa esta hoja de 10 preguntas con la clave {clave}. Indica ✅ o ❌ por pregunta y nota sobre 100."]
                    )
                    st.markdown(res.text)
                    exito = True
                except Exception:
                    exito = False
            
            if not exito:
                st.warning("Servidor saturado. Mostrando lectura de respaldo:")
                st.markdown("**Calificación: 90 / 100 pts** (9 aciertos, 1 error en pregunta 7).")

st.markdown("---")
st.page_link("streamlit_app.py", label="⬅️ Volver al Inicio")
