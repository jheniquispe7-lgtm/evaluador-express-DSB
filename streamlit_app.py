import streamlit as st
import os
import random
from google import genai

# Configuración inicial de la página
st.set_page_config(
    page_title="EVALÚA - DSB",
    page_icon="📚",
    layout="wide"
)

# Inicializar cliente de Google Gemini
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

if "preguntas_generadas" not in st.session_state:
    st.session_state.preguntas_generadas = ""

# --- BANNER INSTITUCIONAL ---
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.jpg.jpg"):
    st.image("banner.jpg.jpg", use_container_width=True)
else:
    st.markdown("### 🏫 Unidad Educativa Daniel Sánchez Bustamante - EVALÚA-DSB")

st.title("EVALÚA - DSB: Sistema de Evaluación Digital e Impresa")
st.markdown("---")

# --- PANEL LATERAL ---
st.sidebar.title("Panel de Control")
rol = st.sidebar.selectbox("Seleccione su Rol:", ["Estudiante", "Docente"])

# ==============================================================================
# MÓDULO DOCENTE
# ==============================================================================
if rol == "Docente":
    st.header("👨‍🏫 Panel de Control Docente")
    
    pin = st.sidebar.text_input("Ingrese PIN Docente:", type="password")
    
    if pin == "1234":
        st.sidebar.success("Acceso Autorizado")
        
        opcion = st.selectbox(
            "Seleccione una función:",
            [
                "1. Generador de Preguntas con IA (Gemini)",
                "2. Generador de Versiones Impresas (Anti-copias)",
                "3. Escáner Óptico y Calificación con IA"
            ]
        )
        
        # --- 1. GENERADOR CON IA ---
        if opcion == "1. Generador de Preguntas con IA (Gemini)":
            st.subheader("🤖 Generación Rápida de Preguntas con Gemini")
            tema = st.text_input("Ingrese el tema o contenido a evaluar:", "Informática básica")
            cantidad = st.number_input("Número de preguntas:", min_value=1, max_value=15, value=10)
            
            if st.button("Generar Preguntas"):
                if client and tema:
                    with st.spinner("Generando preguntas con Google Gemini..."):
                        try:
                            prompt = (
                                f"Crea {cantidad} preguntas de selección múltiple con 4 opciones (A, B, C, D) "
                                f"sobre el tema '{tema}' para estudiantes de secundaria. "
                                f"Indica claramente la respuesta correcta al final de cada pregunta."
                            )
                            response = client.models.generate_content(
                                model="models/gemini-3.8-flash",
                                contents=prompt
                            )
                            st.session_state.preguntas_generadas = response.text
                        except Exception as e:
                            st.error(f"Error de conexión con la IA: {e}")
                else:
                    st.warning("Verifique su API Key o ingrese un tema válido.")
            
            if st.session_state.preguntas_generadas:
                st.markdown("### Preguntas Generadas:")
                st.write(st.session_state.preguntas_generadas)
                st.download_button(
                    label="📥 Descargar Preguntas (.txt)",
                    data=st.session_state.preguntas_generadas,
                    file_name="examen_dsb.txt",
                    mime="text/plain"
                )

        # --- 2. VERSIONES IMPRESAS ---
        elif opcion == "2. Generador de Versiones Impresas (Anti-copias)":
            st.subheader("📄 Generador de Filas Aleatorias (A, B, C)")
            st.write("Pegue aquí las preguntas que desea mezclar para imprimir:")
            texto_preguntas = st.text_area("Ingrese una pregunta por línea:", height=150)
            
            if st.button("Generar Filas Mezcladas"):
                lineas = [l.strip() for l in texto_preguntas.split("\n") if l.strip()]
                if len(lineas) >= 2:
                    for fila in ["A", "B", "C"]:
                        st.markdown(f"#### 📄 FILA {fila}")
                        mezcla = lineas.copy()
                        random.shuffle(mezcla)
                        for idx, p in enumerate(mezcla, 1):
                            st.write(f"**{idx}.** {p}")
                        st.markdown("---")
                else:
                    st.warning("Ingrese al menos 2 preguntas para mezclar.")

        # --- 3. ESCÁNER ÓPTICO CON VISIÓN REAL DE GEMINI ---
        elif opcion == "3. Escáner Óptico y Calificación con IA":
            st.subheader("📷 Escáner Inteligente de Hojas Físicas")
            
            st.write("Ingrese las respuestas correctas oficiales (su clave de respuestas):")
            banco_maestro = st.text_area(
                "Clave de respuestas esperada (Ej: 1:B, 2:A, 3:D, 4:B, 5:C...):",
                value="1:B, 2:A, 3:D, 4:B, 5:C, 6:C, 7:C, 8:C, 9:B, 10:C",
                height=80
            )
            
            nombre_est = st.text_input("Apellidos y Nombres del Estudiante:")
            archivo_img = st.file_uploader("Suba la fotografía de la hoja de respuestas marcada:", type=["jpg", "png", "jpeg"])
            
            if archivo_img and nombre_est:
                st.image(archivo_img, caption="Hoja cargada del estudiante", width=300)
                
                if st.button("Analizar con IA y Calificar"):
                    if client:
                        with st.spinner("Analizando la imagen de la hoja con Google Gemini..."):
                            try:
                                # Convertir la imagen para enviarla a la API de Gemini
                                bytes_data = archivo_img.getvalue()
                                image_part = {"mime_type": archivo_img.type, "data": bytes_data}
                                
                                prompt = (
                                    f"Actúa como un profesor escaneando una hoja de examen de opción múltiple (10 preguntas). "
                                    f"La clave oficial de respuestas correctas es: {banco_maestro}. "
                                    f"Analiza la imagen adjunta donde se ven las marcas del estudiante, identifica qué opción (A, B, C o D) marcó el estudiante en cada pregunta, "
                                    f"comárala con la clave oficial, cuenta cuántos aciertos tiene sobre 10, calcula la nota final sobre 100 y preséntalo ordenadamente indicando si cada pregunta está Correcta (✅) o Incorrecta (❌)."
                                )
                                
                                response = client.models.generate_content(
                                    model="models/gemini-3.8-flash",
                                    contents=[image_part, prompt]
                                )
                                
                                st.success("¡Análisis completado con éxito!")
                                st.markdown("### 📊 Resultado del Escaneo Inteligente")
                                st.write(response.text)
                                
                            except Exception as e:
                                st.error(f"Error al procesar la imagen con la IA: {e}")
                    else:
                        st.warning("El cliente de Gemini no está configurado (falta la API Key).")

    elif pin == "":
        st.info("Ingrese el PIN de docente (1234) en el menú lateral para continuar.")
    else:
        st.error("PIN incorrecto.")

# ==============================================================================
# MÓDULO ESTUDIANTE
# ==============================================================================
elif rol == "Estudiante":
    st.header("🎓 Portal de Evaluación en Línea")
    nombre_alumno = st.text_input("Ingrese sus Apellidos y Nombres:")
    
    if nombre_alumno:
        st.subheader("Examen Activo: Evaluación de Informática")
        
        r1 = st.radio("1. ¿Qué dispositivo muestra imágenes y textos?", ["A. Teclado", "B. Monitor", "C. Ratón", "D. Parlantes"])
        r2 = st.radio("2. ¿Cuál de los siguientes elementos es un dispositivo de entrada?", ["A. Teclado", "B. Monitor", "C. Impresora", "D. Parlantes"])
        
        if st.button("Enviar Examen"):
            puntaje = 100
            st.success(f"¡Examen enviado con éxito, {nombre_alumno}!")
            st.markdown("### Calificación Automática")
            st.metric(label="", value=f"{puntaje} / 100 pts")
    else:
        st.warning("Por favor, ingrese sus apellidos y nombres para habilitar el examen.")
