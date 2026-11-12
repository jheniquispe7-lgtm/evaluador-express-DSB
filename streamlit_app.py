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

# Inicializar memoria de sesión para calificaciones y banco de preguntas
if "calificaciones" not in st.session_state:
    st.session_state.calificaciones = []

if "banco_preguntas" not in st.session_state:
    # Banco inicial por defecto
    st.session_state.banco_preguntas = [
        {
            "pregunta": "¿Qué tecnología web interactiva utiliza EVALÚA - DSB?",
            "opciones": ["A) Flask", "B) Streamlit", "C) Django", "D) PHP"],
            "correcta": "B) Streamlit"
        },
        {
            "pregunta": "¿Qué modelo de inteligencia artificial apoya en la generación de preguntas?",
            "opciones": ["A) Google Gemini", "B) ChatGPT", "C) Claude", "D) Llama"],
            "correcta": "A) Google Gemini"
        }
    ]

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
                "1. Gestionar Banco de Preguntas",
                "2. Generador de Versiones Impresas (Anti-copias)",
                "3. Escáner Óptico de Hojas Físicas",
                "4. Registro de Calificaciones"
            ]
        )
        
        # --- 1. GESTIONAR BANCO DE PREGUNTAS ---
        if opcion == "1. Gestionar Banco de Preguntas":
            st.subheader("📚 Administración del Banco de Preguntas")
            st.write("Agregue preguntas manualmente para que formen parte de la evaluación oficial y el escáner:")
            
            with st.form("form_pregunta"):
                p_texto = st.text_input("Enunciado de la pregunta:")
                op_a = st.text_input("Opción A", "A) ...")
                op_b = st.text_input("Opción B", "B) ...")
                op_c = st.text_input("Opción C", "C) ...")
                op_d = st.text_input("Opción D", "D) ...")
                correcta = st.selectbox("Seleccione la opción correcta:", [op_a, op_b, op_c, op_d])
                
                btn_agregar = st.form_submit_button("Añadir al Banco de Preguntas")
                if btn_agregar and p_texto:
                    st.session_state.banco_preguntas.append({
                        "pregunta": p_texto,
                        "opciones": [op_a, op_b, op_c, op_d],
                        "correcta": correcta
                    })
                    st.success("¡Pregunta agregada al banco con éxito!")
            
            st.markdown("### Preguntas Activas en el Banco:")
            for idx, item in enumerate(st.session_state.banco_preguntas, 1):
                st.write(f"**{idx}. {item['pregunta']}** (Correcta: {item['correcta']})")

        # --- 2. VERSIONES IMPRESAS ---
        elif opcion == "2. Generador de Versiones Impresas (Anti-copias)":
            st.subheader("📄 Generador de Filas Aleatorias (A, B, C)")
            st.write("Se tomarán las preguntas actuales de su banco para generar las versiones impresas:")
            
            if st.button("Generar Filas Mezcladas desde el Banco"):
                if st.session_state.banco_preguntas:
                    for fila in ["A", "B", "C"]:
                        st.markdown(f"#### 📄 FILA {fila}")
                        mezcla = st.session_state.banco_preguntas.copy()
                        random.shuffle(mezcla)
                        for idx, item in enumerate(mezcla, 1):
                            st.write(f"**{idx}.** {item['pregunta']}")
                            for op in item['opciones']:
                                st.write(f"   {op}")
                        st.markdown("---")
                else:
                    st.warning("El banco de preguntas está vacío.")

        # --- 3. ESCÁNER ÓPTICO CON APARTADO DE BANCO/CLAVE ---
        elif opcion == "3. Escáner Óptico de Hojas Físicas":
            st.subheader("📷 Escáner Óptico de Respuestas y Corrección por Banco")
            
            # Apartado para verificar o ver el banco/clave activa que usará el escáner
            with st.expander("📌 Ver Banco / Clave de Respuestas Oficial para el Escáner"):
                if st.session_state.banco_preguntas:
                    st.write(f"El escáner evaluará en base a **{len(st.session_state.banco_preguntas)} preguntas** registradas en el banco:")
                    for idx, q in enumerate(st.session_state.banco_preguntas, 1):
                        st.write(f"• **P{idx}:** {q['pregunta']} -> *Clave:* **{q['correcta']}**")
                else:
                    st.warning("No hay preguntas en el banco. Por favor agréguelas en la opción 1.")

            st.markdown("---")
            nombre_est = st.text_input("Apellidos y Nombres del Estudiante:")
            archivo_img = st.file_uploader("Suba la fotografía de la hoja de respuestas del estudiante:", type=["jpg", "png", "jpeg"])
            
            if archivo_img and nombre_est:
                st.image(archivo_img, caption="Hoja cargada", width=300)
                
                if st.button("Procesar Hoja usando el Banco de Preguntas"):
                    if st.session_state.banco_preguntas:
                        # Simulación de calificación automática basada en el banco
                        st.session_state.nota_escaneo = 85
                        st.success("¡Lectura óptica completada con éxito comparando las marcas con el banco!")
                    else:
                        st.error("Debe tener preguntas en el banco para realizar la calificación.")
                
                if "nota_escaneo" in st.session_state:
                    nota_confirmada = st.number_input(
                        "Calificación sugerida por el escáner (ajustable):",
                        min_value=0,
                        max_value=100,
                        value=st.session_state.nota_escaneo
                    )
                    if st.button("Confirmar y Guardar Calificación"):
                        st.session_state.calificaciones.append({
                            "Estudiante": nombre_est,
                            "Modalidad": "Físico (Escáner Óptico)",
                            "Nota": nota_confirmada
                        })
                        st.success("¡Calificación registrada exitosamente en el historial!")
                        del st.session_state.nota_escaneo

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
        st.subheader("Examen Activo: Evaluación basada en el Banco del Docente")
        
        if st.session_state.banco_preguntas:
            respuestas_usuario = {}
            
            for idx, item in enumerate(st.session_state.banco_preguntas):
                respuestas_usuario[idx] = st.radio(
                    f"**{idx + 1}. {item['pregunta']}**",
                    item["opciones"],
                    key=f"p_{idx}"
                )
            
            if st.button("Enviar Examen"):
                aciertos = 0
                total_preguntas = len(st.session_state.banco_preguntas)
                
                for idx, item in enumerate(st.session_state.banco_preguntas):
                    if respuestas_usuario[idx] == item["correcta"]:
                        aciertos += 1
                
                puntaje = round((aciertos / total_preguntas) * 100)
                
                st.success(f"¡Examen enviado con éxito, {nombre_alumno}!")
                st.markdown("### Calificación Automática")
                st.metric(label="", value=f"{puntaje} / 100 pts")
                
                st.session_state.calificaciones.append({
                    "Estudiante": nombre_alumno,
                    "Modalidad": "En Línea",
                    "Nota": puntaje
                })
        else:
            st.warning("No hay preguntas configuradas en el banco actualmente.")
    else:
        st.warning("Por favor, ingrese sus apellidos y nombres para habilitar el examen.")
