import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# Configuración de la página
st.set_page_config(
    page_title="EVALUA - DSB",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# BANNER OFICIAL EN LA PARTE SUPERIOR
# ==========================================
try:
    banner_img = Image.open("banner.jpg")
    st.image(banner_img, use_container_width=True)
except FileNotFoundError:
    st.warning("⚠️ Sube tu archivo 'banner.jpg' al repositorio de GitHub para mostrar el banner oficial.")

# Título y descripción principal
st.title("⚡ EVALUA - DSB — Unidad Educativa Daniel Sánchez Bustamante")
st.markdown("Herramienta docente integral: Exámenes multi-versión, cronómetro de aula y escaneo rápido por cámara.")

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["📝 Generador Multi-Versión", "⏱️ Examen en Línea (Cronómetro)", "📷 Escáner y Calificación Rápida"])

# ==========================================
# PESTAÑA 1: GENERADOR DE EXÁMENES MULTI-VERSIÓN
# ==========================================
with tab1:
    st.header("📝 Generador de Exámenes con Versiones (A y B)")
    st.markdown("Crea evaluaciones personalizadas desde documentos, enlaces o temas, generando versiones distintas para evitar copias.")

    col1, col2 = st.columns(2)
    with col1:
        materia = st.selectbox(
            "Materia:",
            [
                "TTG (Técnica Tecnológica General)", 
                "TTE (Técnica Tecnológica Especializada)", 
                "Educación Musical", 
                "Artes Plásticas y Visuales", 
                "Valores Espirituales y Religiones", 
                "Educación Física y Deportes"
            ]
        )
        nivel = st.selectbox("Nivel / Curso:", ["1ro de Secundaria", "2do de Secundaria", "3ro de Secundaria", "4to de Secundaria", "5to de Secundaria", "6to de Secundaria"])
        tipo_pregunta = st.selectbox("Tipo de Preguntas:", ["Opción Múltiple", "Preguntas Abiertas / Desarrollo", "Mixto"])

    with col2:
        cantidad = st.slider("Número de preguntas:", min_value=3, max_value=15, value=5)
        version_examen = st.selectbox("Versión a generar:", ["Versión A y Versión B (Ambas)", "Solo Versión A", "Solo Versión B"])
        nivel_dificultad = st.select_slider("Dificultad:", options=["Básico", "Intermedio", "Avanzado"])

    st.markdown("---")
    origen_fuente = st.radio("Origen del contenido:", ["Tema Escrito / Texto", "Imagen de Guía / Libro", "Enlace Web o Video"], horizontal=True)

    prompt_contenido = ""
    imagen_subida = None

    if origen_fuente == "Tema Escrito / Texto":
        prompt_contenido = st.text_area("Escribe el contenido o tema base:")
    elif origen_fuente == "Imagen de Guía / Libro":
        imagen_subida = st.file_uploader("Sube foto de referencia:", type=["png", "jpg", "jpeg"])
    elif origen_fuente == "Enlace Web o Video":
        url_input = st.text_input("Pega el enlace web o YouTube:")
        prompt_contenido = f"Extrae la información de este link: {url_input}"

    api_key_input = st.text_input("API Key de Gemini (opcional si está en Secrets):", type="password")

    if st.button("🚀 Generar Exámenes (Versiones)"):
        with st.spinner("Generando versiones del examen con IA..."):
            try:
                if api_key_input:
                    genai.configure(api_key=api_key_input)
                elif "GEMINI_API_KEY" in st.secrets:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                instrucciones = f"""
                Actúa como profesor de {materia} para {nivel}. 
                Genera exámenes formales con el contenido proporcionado. 
                Cantidad: {cantidad} preguntas. Tipo: {tipo_pregunta}. 
                Si el usuario pidió '{version_examen}', redacta las versiones indicadas con preguntas equivalentes pero ordenadas o redactadas de forma distinta para evitar copias. Incluye solucionario para el maestro al final.
                """

                if imagen_subida:
                    res = model.generate_content([instrucciones, Image.open(imagen_subida)])
                else:
                    res = model.generate_content(f"{instrucciones}\n\nFuente: {prompt_contenido}")

                st.success("¡Exámenes generados con éxito!")
                st.markdown("---")
                st.markdown(res.text)
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# PESTAÑA 2: EXAMEN EN LÍNEA CON CRONÓMETRO
# ==========================================
with tab2:
    st.header("⏱️ Examen en Línea con Tiempo Límite")
    st.markdown("Controla el tiempo de evaluación en clase tipo formulario digital.")

    tiempo_minutos = st.number_input("Minutos asignados para la prueba:", min_value=1, max_value=120, value=15)
    
    if "examen_activo" not in st.session_state:
        st.session_state.examen_activo = False

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🏁 Iniciar Cronómetro de Examen"):
            st.session_state.examen_activo = True
            st.session_state.tiempo_limite = time.time() + (tiempo_minutos * 60)
            st.rerun()
    with col_b2:
        if st.button("🔄 Reiniciar"):
            st.session_state.examen_activo = False
            st.rerun()

    placeholder_t = st.empty()

    if st.session_state.get("examen_activo", False):
        restante = int(st.session_state.tiempo_limite - time.time())
        if restante > 0:
            m, s = divmod(restante, 60)
            placeholder_t.markdown(f"### ⏳ Tiempo restante: **{m:02d}:{s:02d}**")
            
            with st.form("form_online"):
                st.write("**Pregunta 1:** Responda de acuerdo al avance de la materia.")
                st.text_input("Respuesta P1:", key="r1")
                if st.form_submit_button("📤 Enviar Examen"):
                    st.success("¡Enviado correctamente!")
                    st.session_state.examen_activo = False
            time.sleep(1)
            st.rerun()
        else:
            placeholder_t.error("⏰ ¡El tiempo ha concluido!")
            st.session_state.examen_activo = False
    else:
        placeholder_t.info(f"Cronómetro listo ({tiempo_minutos} minutos).")

# ==========================================
# PESTAÑA 3: ESCÁNER Y CALIFICACIÓN RÁPIDA (CÁMARA DIRECTA)
# ==========================================
with tab3:
    st.header("📷 Escáner Rápido de Tareas (Cámara en Directo)")
    st.markdown("Usa la cámara de tu celular para escanear al instante la hoja del estudiante y obtener una revisión detallada con marcas verdes (✓) y rojas (❌).")

    foto_capturada = st.camera_input("📸 Toca para tomar la foto de la hoja del estudiante:")
    
    criterios_revision = st.text_area("Indica las respuestas correctas o pautas para la corrección:")

    if foto_capturada and st.button("🔍 Escanear y Calificar al Instante"):
        if not criterios_revision:
            st.warning("Por favor, ingresa las pautas o respuestas correctas para comparar.")
        else:
            with st.spinner("Escaneando y evaluando con IA..."):
                try:
                    if api_key_input:
                        genai.configure(api_key=api_key_input)
                    elif "GEMINI_API_KEY" in st.secrets:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    vision_model = genai.GenerativeModel('models/gemini-1.5-flash')
                    prompt_escaneo = f"""
                    Actúa como un profesor revisando una tarea o examen físico.
                    Pautas correctas del maestro: {criterios_revision}
                    
                    Analiza la imagen escaneada y presenta la corrección ítem por ítem utilizando estrictamente:
                    - ✅ (Check verde) para aciertos.
                    - ❌ (Cruz roja) para errores.
                    Proporciona retroalimentación breve y una nota final sobre 100 puntos.
                    """

                    imagen_examen = Image.open(foto_capturada)
                    res_vision = vision_model.generate_content([prompt_escaneo, imagen_examen])
                    
                    st.success("¡Escaneo y revisión completados!")
                    st.markdown("---")
                    st.markdown(res_vision.text)
                except Exception as err:
                    st.error(f"Error al procesar el escaneo: {err}")
