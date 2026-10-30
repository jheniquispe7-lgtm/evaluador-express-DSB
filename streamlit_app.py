import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# Configuración de la página
st.set_page_config(
    page_title="Evaluador Express - DSB",
    page_icon="⚡",
    layout="wide"
)

# Título principal de la aplicación
st.title("⚡ Evaluador Express - Unidad Educativa Daniel Sánchez Bustamante")
st.markdown("Herramienta integral de apoyo docente: Generación de exámenes con IA, cronómetro de aula y evaluación visual.")

# Pestañas principales de la aplicación
tab1, tab2, tab3 = st.tabs(["📝 Generador de Exámenes", "⏱️ Cronómetro de Aula", "📷 Evaluador por Imágenes"])

# ==========================================
# PESTAÑA 1: GENERADOR DE EXÁMENES CON IA
# ==========================================
with tab1:
    st.header("Generador Automático de Exámenes")
    st.markdown("Utiliza Inteligencia Artificial para crear evaluaciones personalizadas adaptadas a tus materias.")

    col1, col2 = st.columns(2)
    with col1:
        materia = st.selectbox(
            "Selecciona la Materia:",
            [
                "TTG (Técnica Tecnológica General)", 
                "TTE (Técnica Tecnológica Especializada)", 
                "Educación Musical", 
                "Artes Plásticas y Visuales", 
                "Valores Espirituales y Religiones", 
                "Educación Física y Deportes"
            ]
        )
        tipo_pregunta = st.selectbox(
            "Tipo de Preguntas:",
            ["Opción Múltiple", "Preguntas Abiertas / Desarrollo", "Mixto (Ambos)"]
        )

    with col2:
        nivel = st.selectbox("Curso / Nivel:", ["1iro de Secundaria", "2ndo de Secundaria", "3ero de Secundaria", "4to de Secundaria", "5to de Secundaria", "6to de Secundaria"])
        cantidad = st.slider("Número de preguntas:", min_value=3, max_value=15, value=5)

    tema_especifico = st.text_input("Tema específico o contenido a evaluar (Ej: Redes inalámbricas, Acordes musicales, Anatomía artística...):")

    # Configuración opcional de API Key de Gemini
    api_key_input = st.text_input("Ingresa tu API Key de Gemini (opcional si está configurada en secretos):", type="password")

    if st.button("🚀 Generar Examen"):
        if not tema_especifico:
            st.warning("Por favor, ingresa un tema específico para el examen.")
        else:
            with st.spinner("Generando evaluación con Inteligencia Artificial..."):
                try:
                    # Configurar API Key
                    if api_key_input:
                        genai.configure(api_key=api_key_input)
                    else:
                        # Intenta buscar en los secretos de Streamlit si están configurados
                        if "GEMINI_API_KEY" in st.secrets:
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        else:
                            # Fallback para pruebas locales o requerimiento explícito
                            st.error("Falta configurar la API Key de Gemini. Inrésala arriba o configúrala en Streamlit Secrets.")
                            st.stop()

                    prompt = f"""
                    Eres un asistente docente experto en el sistema educativo de Bolivia. 
                    Genera una evaluación formal y pedagógica para la materia de {materia}, nivel {nivel}.
                    Tema: {tema_especifico}.
                    Tipo de preguntas: {tipo_pregunta}.
                    Cantidad de preguntas: {cantidad}.
                    
                    Incluye al final una sección con las respuestas correctas o pautas de evaluación detalladas.
                    Formatea la salida de manera limpia utilizando Markdown.
                    """

                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)

                    st.success("¡Examen generado con éxito!")
                    st.markdown("---")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Ocurrió un error al generar el examen: {e}")

# ==========================================
# PESTAÑA 2: CRONÓMETRO DE AULA
# ==========================================
with tab2:
    st.header("⏱️ Cronómetro y Temporizador para Exámenes")
    st.markdown("Controla el tiempo disponible para tus estudiantes durante la prueba en clase.")

    tiempo_minutos = st.number_input("Configurar tiempo de examen (en minutos):", min_value=1, max_value=180, value=30)
    
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("▶️ Iniciar Cronómetro"):
            st.session_state.timer_running = True
            st.session_state.target_time = time.time() + (tiempo_minutos * 60)

    with col_t2:
        if st.button("⏹️ Reiniciar / Detener"):
            st.session_state.timer_running = False

    # Visualizador dinámico del tiempo
    timer_placeholder = st.empty()

    if st.session_state.get("timer_running", False):
        tiempo_restante = int(st.session_state.target_time - time.time())
        if tiempo_restante > 0:
            mins, secs = divmod(tiempo_restante, 60)
            timer_placeholder.metric("Tiempo Restante", f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            st.rerun()
        else:
            timer_placeholder.error("⏰ ¡El tiempo del examen ha terminado!")
            st.session_state.timer_running = False
    else:
        timer_placeholder.metric("Tiempo Configurado", f"{tiempo_minutos:02d}:00")

# ==========================================
# PESTAÑA 3: EVALUADOR POR IMÁGENES
# ==========================================
with tab3:
    st.header("📷 Evaluación de Tareas y Trabajos por Imagen")
    st.markdown("Sube una foto del examen físico o tarea del estudiante para recibir una revisión y sugerencia de calificación mediante IA.")

    uploaded_file = st.file_uploader("Sube la imagen del trabajo o examen (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])
    criterio_eval = st.text_area("Criterios de evaluación o rúbrica esperada (Ej: Coherencia, ortografía, resolución correcta de ejercicios...):")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Trabajo subido por el estudiante", use_container_width=True)

        if st.button("🔍 Analizar y Calificar Trabajo"):
            if not criterio_eval:
                st.warning("Por favor, ingresa los criterios de evaluación para que la IA pueda calificar con precisión.")
            else:
                with st.spinner("Analizando la imagen con Visión Artificial..."):
                    try:
                        if "GEMINI_API_KEY" in st.secrets:
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        
                        vision_model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt_vision = f"""
                        Actúa como un profesor exigente pero justo. Analiza esta imagen correspondiente a un trabajo escolar.
                        Criterios de evaluación del profesor: {criterio_eval}
                        
                        Proporciona:
                        1. Observaciones detalladas del contenido visualizado.
                        2. Puntos fuertes y errores encontrados.
                        3. Una nota sugerida (sobre 100 puntos).
                        """

                        response_vision = vision_model.generate_content([prompt_vision, image])
                        
                        st.success("¡Análisis completado!")
                        st.markdown("---")
                        st.markdown(response_vision.text)

                    except Exception as e:
                        st.error(f"Error al procesar la imagen: {e}")
