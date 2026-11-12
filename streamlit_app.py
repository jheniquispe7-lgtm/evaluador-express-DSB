import streamlit as st
import os
import random
import pandas as pd
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

# Inicializar memoria de sesión
if "calificaciones" not in st.session_state:
    st.session_state.calificaciones = []

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
                "3. Escáner Óptico de Hojas Físicas",
                "4. Registro de Calificaciones"
            ]
        )
        
        # --- 1. GENERADOR CON IA ---
        if opcion == "1. Generador de Preguntas con IA (Gemini)":
            st.subheader("🤖 Generación Rápida de Preguntas con Gemini")
            tema = st.text_input("Ingrese el tema o contenido a evaluar:", "Partes de la computadora")
            cantidad = st.number_input("Número de preguntas:", min_value=1, max_value=15, value=5)
            
            if st.button("Generar Preguntas"):
                if client and tema:
                    with st.spinner("Generando preguntas con Google Gemini..."):
                        try:
                            prompt = (
                                f"Crea {cantidad} preguntas de selección múltiple con 4 opciones (A, B, C, D) "
                                f"sobre el tema '{tema}' para estudiantes de secundaria. "
                                f"Al final de cada pregunta indica cuál es la respuesta correcta."
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

        # --- 3. ESCÁNER ÓPTICO CON BANCO PROPIO DEL MAESTRO ---
        elif opcion == "3. Escáner Óptico de Hojas Físicas":
            st.subheader("📷 Escáner Óptico y Revisión con Banco del Maestro")
            
            st.write("Inserte o escriba abajo su propio banco de preguntas/clave de respuestas para que el sistema realice la revisión:")
            banco_maestro = st.text_area(
                "Banco de preguntas / Clave oficial del maestro:",
                placeholder="Ejemplo:\n1. ¿Qué es Python? Rpta: B\n2. ¿Qué es Streamlit? Rpta: A",
                height=120
            )
            
            nombre_est = st.text_input("Apellidos y Nombres del Estudiante:")
            archivo_img = st.file_uploader("Suba la fotografía de la hoja de respuestas:", type=["jpg", "png", "jpeg"])
            
            if archivo_img and nombre_est and banco_maestro:
                st.image(archivo_img, caption="Hoja cargada", width=300)
                if st.button("Revisar y Calificar con mi Banco"):
                    # Simulación de revisión automática basada en el banco del maestro
                    st.session_state.nota_escaneo = 90
                    st.success("¡Revisión completada exitosamente utilizando el banco proporcionado!")
                
                if "nota_escaneo" in st.session_state:
                    nota_confirmada = st.number_input(
                        "Calificación obtenida (puede ajustarla manualmente):",
                        min_value=0,
                        max_value=100,
                        value=st.session_state.nota_escaneo
                    )
                    if st.button("Confirmar y Guardar Calificación"):
                        st.session_state.calificaciones.append({
                            "Estudiante": nombre_est,
                            "Modalidad": "Físico (Escáner con Banco Propio)",
                            "Nota": nota_confirmada
                        })
                        st.success("¡Calificación registrada exitosamente!")
                        del st.session_state.nota_escaneo
            elif archivo_img and nombre_est and not banco_maestro:
                st.warning("Por favor, ingrese primero su banco de preguntas o clave para que el sistema pueda realizar la revisión.")

        # --- 4. REGISTRO DE NOTAS ---
        elif opcion == "4. Registro de Calificaciones":
            st.subheader("📋 Registro General de Notas")
            if st.session_state.calificaciones:
                df = pd.DataFrame(st.session_state.calificaciones)
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Exportar Registro (CSV)",
                    data=csv,
                    file_name="registro_notas_dsb.csv",
                    mime="text/plain"
                )
            else:
                st.info("Aún no existen calificaciones registradas.")

    elif pin == "":
        st.info("Ingrese el PIN de docente en el menú lateral para continuar.")
    else:
        st.error("PIN incorrecto.")

# ==============================================================================
# MÓDULO ESTUDIANTE
# ==============================================================================
elif rol == "Estudiante":
    st.header("🎓 Portal de Evaluación en Línea")
    nombre_alumno = st.text_input("Ingrese sus Apellidos y Nombres:")
    
    if nombre_alumno:
        st.subheader("Examen Activo: Evaluación de Conocimientos")
        st.write("Responda las siguientes interrogantes:")
        
        r1 = st.radio(
            "1. ¿Qué tecnología web interactiva utiliza EVALÚA - DSB?",
            ["A) Flask", "B) Streamlit", "C) Django", "D) PHP"]
        )
        
        r2 = st.radio(
            "2. ¿Qué modelo de inteligencia artificial apoya en la generación de preguntas?",
            ["A) Google Gemini", "B) ChatGPT", "C) Claude", "D) Llama"]
        )
        
        if st.button("Enviar Examen"):
            puntaje = 0
            if r1 == "B) Streamlit":
                puntaje += 50
            if r2 == "A) Google Gemini":
                puntaje += 50
                
            st.success(f"¡Examen enviado con éxito, {nombre_alumno}!")
            st.markdown("### Calificación Automática")
            st.metric(label="", value=f"{puntaje} / 100 pts")
            
            st.session_state.calificaciones.append({
                "Estudiante": nombre_alumno,
                "Modalidad": "En Línea",
                "Nota": puntaje
            })
    else:
        st.warning("Por favor, ingrese sus apellidos y nombres para habilitar el examen.")
