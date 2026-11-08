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
# BANNER PRINCIPAL (TÍTULO DE LA HERRAMIENTA)
# ==========================================
try:
    banner_img = Image.open("banner.jpg")
    st.image(banner_img, use_container_width=True)
except FileNotFoundError:
    st.title("⚡ EVALUA - DSB")
    st.warning("⚠️ Sube tu archivo 'banner.jpg' al repositorio de GitHub para mostrar el banner oficial.")

st.markdown("**Plataforma de Evaluación Docente — Unidad Educativa Daniel Sánchez Bustamante:** Creación de banco de preguntas, patrones anti-copias por versiones (A, B, C) de 4 opciones (A-D) y escaneo rápido.")

# Pestañas principales de la aplicación
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Banco de Preguntas y Patrones", 
    "📄 Generar Hoja de Respuestas", 
    "⏱️ Examen en Línea", 
    "📷 Escáner de Aciertos (✓/✗)"
])

api_key_input = st.sidebar.text_input("API Key de Gemini:", type="password")

def configurar_ia():
    if api_key_input:
        genai.configure(api_key=api_key_input)
    elif "GEMINI_API_KEY" in st.secrets:
        genai.configure(st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Por favor ingresa tu API Key de Gemini.")
        st.stop()
    return genai.GenerativeModel('models/gemini-1.5-flash')

# ==========================================
# PESTAÑA 1: BANCO DE PREGUNTAS Y PATRONES (A-D)
# ==========================================
with tab1:
    st.header("📝 Banco de Preguntas y Generación de Patrones por Versiones")
    st.markdown("Dicta o escribe tus preguntas con sus 4 opciones (**A, B, C, D**) y define cuál es la respuesta correcta. La IA generará los patrones de respuestas diferentes para cada versión (Fila A, B, C...) evitando copias.")

    st.info("💡 **Consejo:** Usa el micrófono del teclado de tu celular para dictar las preguntas con rapidez.")

    with st.form("form_agregar_pregunta"):
        pregunta_txt = st.text_area("Pregunta:")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            op_a = st.text_input("Opción A:")
            op_b = st.text_input("Opción B:")
        with col_opt2:
            op_c = st.text_input("Opción C:")
            op_d = st.text_input("Opción D:")
            
        correcta = st.selectbox("Indica cuál de estas opciones es la respuesta CORRECTA:", ["A", "B", "C", "D"])
        
        btn_agregar = st.form_submit_button("➕ Añadir Pregunta al Banco")

    if "banco_docente" not in st.session_state:
        st.session_state.banco_docente = []

    if btn_agregar and pregunta_txt and op_a and op_b and op_c and op_d:
        st.session_state.banco_docente.append({
            "pregunta": pregunta_txt,
            "A": op_a, "B": op_b, "C": op_c, "D": op_d,
            "correcta": correcta
        })
        st.success(f"¡Pregunta agregada correctamente! Total en banco: {len(st.session_state.banco_docente)}")

    if st.session_state.banco_docente:
        st.markdown("---")
        st.subheader("📚 Preguntas Registradas")
        for idx, item in enumerate(st.session_state.banco_docente, 1):
            st.markdown(f"**P{idx}. {item['pregunta']}**")
            st.markdown(f"A) {item['A']} | B) {item['B']} | C) {item['C']} | D) {item['D']} — *Correcta: **[{item['correcta']}]***")
        
        if st.button("🗑️ Vaciar Banco de Preguntas"):
            st.session_state.banco_docente = []
            st.rerun()

    st.markdown("---")
    st.subheader("🔀 Generar Exámenes y Patrones Diferentes por Filas (A, B, C...)")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        materia_sel = st.selectbox("Materia:", ["TTG", "TTE", "Educación Musical", "Artes Plásticas", "Valores Espirituales y Religiones", "Educación Física"])
    with col_v2:
        curso_sel = st.selectbox("Curso:", ["1ro Secundaria", "2do Secundaria", "3ro Secundaria", "4to Secundaria", "5to Secundaria", "6to Secundaria"])

    if st.button("🚀 Crear Versiones y Patrones Anti-Copias"):
        if not st.session_state.banco_docente:
            st.warning("Primero debes registrar al menos una pregunta en el banco.")
        else:
            with st.spinner("Creando patrones únicos y recombinando versiones (A, B, C)..."):
                try:
                    model = configurar_ia()
                    prompt_versiones = f"""
                    Actúa como profesor experto de {materia_sel} ({curso_sel}).
                    Tengo el siguiente banco de preguntas con sus respuestas correctas oficiales:
                    {st.session_state.banco_docente}

                    Genera lo siguiente:
                    1. **Fila A**: Examen con el orden original.
                    2. **Fila B**: Versión alterna donde se reordenan las preguntas y se permutan los incisos A, B, C, D de forma inteligente.
                    3. **Fila C**: Otra versión con un patrón diagonal alternativo (inspirado en patrones de hojas ópticas de 4 opciones A-D).
                    4. Las **Claves o Patrones de Respuestas Oficiales** detallados para cada fila (Fila A, Fila B, Fila C) para que el maestro pueda calificar rápidamente con su cámara.
                    """
                    
                    res_Versiones = model.generate_content(prompt_versiones)
                    st.success("¡Exámenes multi-versión y patrones generados con éxito!")
                    st.markdown("---")
                    st.markdown(res_Versiones.text)
                except Exception as err:
                    st.error(f"Error al generar las versiones: {err}")

# ==========================================
# PESTAÑA 2: GENERADOR DE HOJA DE RESPUESTAS
# ==========================================
with tab2:
    st.header("📄 Generador de Plantilla de Hoja de Respuestas (A-D)")
    st.markdown("Visualiza y genera el formato de hoja de respuestas de 4 opciones listo para imprimir y repartir a tus estudiantes.")

    num_p_hoja = st.slider("Número de preguntas para la plantilla:", min_value=5, max_value=30, value=20)
    
    if st.button("🖨️ Mostrar Vista Previa de Hoja de Respuestas"):
        st.info("Plantilla generada basada en el formato estándar con opciones A, B, C y D:")
        
        st.markdown("### 📋 HOJA DE RESPUESTAS — EVALUA DSB")
        st.markdown("**Nombre:** __________________________ | **Curso:** ____________ | **Fila:** ____")
        st.markdown("---")
        
        for p in range(1, num_p_hoja + 1):
            st.markdown(f"**{p:2d}**     ` A `     ` B `     ` C `     ` D `")
        st.markdown("---")
        st.success("¡Listo para imprimir o distribuir digitalmente!")

# ==========================================
# PESTAÑA 3: EXAMEN EN LÍNEA
# ==========================================
with tab3:
    st.header("⏱️ Examen en Línea con Cronómetro (A-D)")
    minutos_Ex = st.number_input("Tiempo límite (minutos):", min_value=1, max_value=120, value=15)
    
    if "online_activo" not in st.session_state:
        st.session_state.online_activo = False

    if st.button("🏁 Iniciar Prueba en Línea"):
        st.session_state.online_activo = True
        st.session_state.fin_tiempo = time.time() + (minutos_Ex * 60)
        st.rerun()

    cron_caja = st.empty()
    if st.session_state.get("online_activo", False):
        restante_t = int(st.session_state.fin_tiempo - time.time())
        if restante_t > 0:
            mm, ss = divmod(restante_t, 60)
            cron_caja.markdown(f"### ⏳ Tiempo restante: **{mm:02d}:{ss:02d}**")
            with st.form("form_online_estudiante"):
                st.write("**Evaluación en curso:**")
                st.text_input("Nombre del Estudiante:")
                st.radio("Pregunta 1:", ["A", "B", "C", "D"])
                if st.form_submit_button("📤 Enviar Examen"):
                    st.success("¡Respuestas enviadas con éxito!")
                    st.session_state.online_activo = False
            time.sleep(1)
            st.rerun()
        else:
            cron_caja.error("⏰ ¡El tiempo ha concluido!")
            st.session_state.online_activo = False
    else:
        cron_caja.info(f"Cronómetro configurado a {minutos_Ex} minutos.")

# ==========================================
# PESTAÑA 4: ESCÁNER DE ACIERTOS (✓ / ✗)
# ==========================================
with tab4:
    st.header("📷 Escáner Óptico de Hoja de Respuestas (A-D)")
    st.markdown("Toma una foto a la hoja marcada por el estudiante. La IA leerá las marcas en las opciones **A, B, C y D**, las contrastará con el patrón de la versión (Fila A, B, C...) y calculará los aciertos automáticamente con marcas verdes ($\checkmark$) y rojas ($\times$).")

    version_fila = st.radio("Selecciona la Fila evaluada:", ["Fila A", "Fila B", "Fila C", "Fila D"], horizontal=True)
    patron_oficial = st.text_input("Ingresa el patrón de respuestas correctas (ej: 1-A, 2-C, 3-B, 4-D...):")

    foto_alumno = st.camera_input("📸 Capturar la hoja de respuestas del estudiante:")

    if foto_alumno and st.button("🔍 Escanear y Calcular Calificación"):
        if not patron_oficial:
            st.warning("Por favor, ingresa el patrón de respuestas correctas antes de escanear.")
        else:
            with st.spinner("Escaneando óvalos y calculando aciertos..."):
                try:
                    vision_ia = configurar_ia()
                    prompt_lector = f"""
                    Actúa como un escáner óptico de corrección de exámenes de 4 opciones (A, B, C, D).
                    Patrón de respuestas correctas oficial para la {version_fila}: {patron_oficial}
                    
                    Analiza la imagen de la hoja de respuestas del alumno y:
                    1. Identifica qué letra (A, B, C o D) marcó el estudiante en cada número.
                    2. Compara cada respuesta del alumno con el patrón oficial y etiqueta rigurosamente:
                       - ✅ si es correcto (Acierto).
                       - ❌ si es incorrecto (Error, mostrando qué marcó vs la respuesta correcta).
                    3. Presenta una tabla resumen final con:
                       - **Total de Aciertos (✓)**: 
                       - **Total de Errores (✗)**: 
                       - **Nota Final (sobre 100 puntos)**:
                    """

                    img_hoja = Image.open(foto_alumno)
                    res_escaneo = vision_ia.generate_content([prompt_lector, img_hoja])

                    st.success("¡Escaneo y corrección completados con éxito!")
                    st.markdown("---")
                    st.markdown(res_escaneo.text)
                except Exception as e:
                    st.error(f"Error al procesar el escaneo: {e}")
