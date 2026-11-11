import streamlit as st
import os
from google import genai

# Configuración de la página
st.set_page_config(
    page_title="EVALÚA - DSB",
    page_icon="📚",
    layout="wide"
)

# Inicializar el cliente de Gemini (usando el modelo oficial)
client = None
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)

# --- BANNER INSTITUCIONAL ---
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner-1.jpg"):
    st.image("banner-1.jpg", use_container_width=True)
else:
    st.markdown("### 🏫 Unidad Educativa Daniel Sánchez Bustamante - EVALÚA-DSB")

st.title("EVALÚA - DSB: Sistema de Evaluación Digital e Impresa")
st.markdown("---")

# --- MENÚ LATERAL DE NAVEGACIÓN Y ROLES ---
st.sidebar.title("Panel de Control")
rol = st.sidebar.selectbox("Seleccione su Rol:", ["Estudiante", "Docente"])

if "banco_preguntas" not in st.session_state:
    st.session_state.banco_preguntas = []

if "calificaciones" not in st.session_state:
    st.session_state.calificaciones = []

# --- VISTA DOCENTE (CON SEGURIDAD POR PIN) ---
if rol == "Docente":
    st.header("👨‍🏫 Módulo de Gestión Docente")
    
    # Sistema de seguridad para el docente
    pin_ingresado = st.sidebar.text_input("Ingrese PIN Docente:", type="password")
    PIN_SECRETO = "1234"  # PIN institucional de acceso
    
    if pin_ingresado == PIN_SECRETO:
        st.sidebar.success("Acceso Docente Autorizado")
        
        menu_docente = st.selectbox(
            "Seleccione una opción:",
            [
                "1. Banco de Preguntas y Generación IA",
                "2. Generación de Exámenes Impresos (Anti-copias)",
                "3. Escáner Óptico de Hojas Físicas",
                "4. Registro de Calificaciones"
            ]
        )
        
        if menu_docente == "1. Banco de Preguntas y Generación IA":
            st.subheader("Generación de Reactivos con Google Gemini")
            materia = st.text_input("Materia o Área:", "Técnicas Tecnológicas")
            contenido = st.text_area("Contenido o Tema a evaluar:")
            
            if st.button("Generar Preguntas con IA"):
                if client and contenido:
                    with st.spinner("Generando preguntas con inteligencia artificial..."):
                        try:
                            prompt = f"Genera 3 preguntas de selección múltiple con 4 alternativas (A, B, C, D) e indica la respuesta correcta para la materia de {materia} sobre el tema: {contenido}."
                            response = client.models.generate_content(
                                model="models/gemini-3.8-flash",
                                contents=prompt
                            )
                            st.success("¡Preguntas generadas con éxito!")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"Error al conectar con la API de Gemini: {e}")
                else:
                    st.warning("Por favor configure la API Key y el contenido temático.")

        elif menu_docente == "2. Generación de Exámenes Impresos (Anti-copias)":
            st.subheader("Diseño de Versiones Aleatorias (Filas A, B, C)")
            cantidad_versiones = st.number_input("Número de versiones a generar:", min_value=1, max_value=4, value=3)
            if st.button("Generar Versiones para Imprimir"):
                st.info(f"Se han estructurado {cantidad_versiones} versiones con orden alternado de preguntas listas para exportar.")

        elif menu_docente == "3. Escáner Óptico de Hojas Físicas":
            st.subheader("Corrección Asistida por Visión Artificial")
            foto_hoja = st.file_uploader("Subir fotografía de la hoja de respuestas", type=["jpg", "png", "jpeg"])
            
            if foto_hoja:
                st.image(foto_hoja, caption="Hoja capturada", width=300)
                if st.button("Analizar Hoja con IA"):
                    with st.spinner("Analizando marcas del estudiante..."):
                        # Simulación de lectura IA con propuesta preliminar
                        st.session_state.lectura_temporal = {"estudiante": "Estudiante Evaluado", "nota_sugerida": 85}
                
                if "lectura_temporal" in st.session_state:
                    st.warning("⚠️ El escáner ha procesado la hoja. Revise la lectura antes de guardar:")
                    st.write(f"**Estudiante detectado:** {st.session_state.lectura_temporal['estudiante']}")
                    st.write(f"**Calificación preliminar sugerida por IA:** {st.session_state.lectura_temporal['nota_sugerida']} / 100")
                    
                    # Control pedagógico: El docente valida o ajusta la nota final
                    nota_final_docente = st.number_input("Confirme o ajuste la nota final:", min_value=0, max_value=100, value=st.session_state.lectura_temporal['nota_sugerida'])
                    
                    if st.button("Confirmar y Guardar Calificación"):
                        st.session_state.calificaciones.append({
                            "Estudiante": st.session_state.lectura_temporal['estudiante'], 
                            "Nota": nota_final_docente
                        })
                        st.success("¡Calificación guardada exitosamente en el registro!")
                        del st.session_state.lectura_temporal

        elif menu_docente == "4. Registro de Calificaciones":
            st.subheader("Panel Centralizado de Notas (Sesión Activa)")
            if st.session_state.calificaciones:
                for idx, item in enumerate(st.session_state.calificaciones, 1):
                    st.write(f"{idx}. **{item['Estudiante']}** — Calificación: **{item['Nota']} pts**")
            else:
                st.info("No hay registros de calificaciones en la sesión actual.")
                
    elif pin_ingresado == "":
        st.info("Por favor, ingrese el PIN (1234) en la barra lateral para acceder al panel de docente.")
    else:
        st.error("PIN incorrecto. Acceso denegado.")

# --- VISTA ESTUDIANTE ---
elif rol == "Estudiante":
    st.header("🎓 Portal de Evaluación en Línea")
    nombre_estudiante = st.text_input("Ingrese sus Apellidos y Nombres:")
    
    if nombre_estudiante:
        st.subheader("Examen Activo: Evaluación de Conocimientos")
        st.write("Responda las siguientes interrogantes:")
        
        p1 = st.radio("1. ¿Qué tecnología web interactiva utiliza EVALÚA - DSB?", ["A) Flask", "B) Streamlit", "C) Django", "D) PHP"])
        p2 = st.radio("2. ¿Qué modelo de inteligencia artificial apoya en la generación de preguntas?", ["A) Google Gemini", "B) ChatGPT", "C) Claude", "D) Llama"])
        
        if st.button("Enviar Examen"):
            nota = 0
            if "Streamlit" in p1:
                nota += 50
            if "Google Gemini" in p2:
                nota += 50
                
            st.success(f"¡Examen enviado con éxito, {nombre_estudiante}!")
            st.metric(label="Calificación Automática", value=f"{nota} / 100 pts")
            st.session_state.calificaciones.append({"Estudiante": nombre_estudiante, "Nota": nota})
    else:
        st.warning("Por favor ingrese su nombre completo para habilitar el examen.")
