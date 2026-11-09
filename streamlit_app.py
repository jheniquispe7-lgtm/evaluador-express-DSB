import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# ==========================================
# CONFIGURACIÓN GENERAL Y ESTILO (FASE 4)
# ==========================================
st.set_page_config(
    page_title="EVALUA - DSB",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CONFIGURACIÓN DE LA API KEY Y MODELO
# ==========================================
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

def obtener_modelo_oficial():
    """Instancia el modelo recomendado oficial por la API de Google."""
    try:
        return genai.GenerativeModel("gemini-3.8-flash")
    except Exception:
        try:
            return genai.GenerativeModel("gemini-1.5-flash")
        except Exception:
            return genai.GenerativeModel("gemini-pro")

# ==========================================
# ESTRUCTURA DE ALMACENAMIENTO (FASE 1 Y 5)
# ==========================================
if "banco_docente" not in st.session_state:
    st.session_state.banco_docente = []

if "historial_notas" not in st.session_state:
    st.session_state.historial_notas = []

# ==========================================
# BARRA LATERAL: CONTROL DE ACCESO Y ROLES (FASE 3)
# ==========================================
st.sidebar.title("🔐 Control de Acceso")
rol_usuario = st.sidebar.radio(
    "Selecciona tu perfil de usuario:",
    ["👨‍🏫 Modo Docente", "👨‍🎓 Modo Estudiante"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**EVALÚA - DSB**\n\n"
    "Unidad Educativa Daniel Sánchez Bustamante\n"
    "Caranavi - La Paz, Bolivia"
)

# ==========================================
# ENCABEZADO E INSTITUCIONAL
# ==========================================
try:
    banner_img = Image.open("banner.jpg")
    st.image(banner_img, use_container_width=True)
except FileNotFoundError:
    st.title("⚡ EVALUA - DSB")
    st.caption("Sistema Integrado de Evaluación Digital e Impresa")

st.markdown("**Plataforma de Evaluación Docente — U.E. Daniel Sánchez Bustamante**")

# ==========================================
# VISTA: MODO DOCENTE
# ==========================================
if rol_usuario == "👨‍🏫 Modo Docente":
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Banco y Patrones (A-D / V-F)", 
        "📄 Generar Hoja Físicas", 
        "📊 Registro de Calificaciones", 
        "📷 Escáner Óptico de Aciertos"
    ])

    # --------------------------------------
    # PESTAÑA 1: BANCO DE PREGUNTAS (FASE 2 Y 5)
    # --------------------------------------
    with tab1:
        st.header("📝 Banco de Preguntas y Generador de Patrones")
        st.markdown("Registra preguntas y crea exámenes en diferentes versiones (Filas A, B, C...) para evitar copias.")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            materia_act = st.text_input("Asignatura / Materia:", value="Técnicas Tecnológicas")
        with col_m2:
            curso_act = st.selectbox("Curso:", ["1ro Secundaria", "2do Secundaria", "3ro Secundaria", "4to Secundaria", "5to Secundaria", "6to Secundaria"])

        st.markdown("---")
        st.subheader("➕ Agregar Nueva Pregunta")
        
        tipo_pregunta = st.selectbox("Selecciona el tipo de evaluación (Fase 2):", ["Selección Múltiple (A-D)", "Verdadero / Falso"])

        with st.form("form_agregar_pregunta"):
            pregunta_txt = st.text_area("Enunciado de la pregunta:")
            
            if tipo_pregunta == "Selección Múltiple (A-D)":
                col_a, col_b = st.columns(2)
                with col_a:
                    op_a = st.text_input("Opción A:")
                    op_b = st.text_input("Opción B:")
                with col_b:
                    op_c = st.text_input("Opción C:")
                    op_d = st.text_input("Opción D:")
                correcta = st.selectbox("Respuesta Correcta:", ["A", "B", "C", "D"])
            else:
                op_a, op_b, op_c, op_d = "Verdadero", "Falso", "-", "-"
                correcta = st.selectbox("Respuesta Correcta:", ["A (Verdadero)", "B (Falso)"])[0]

            btn_agregar = st.form_submit_button("💾 Guardar en el Banco")

        if btn_agregar and pregunta_txt:
            st.session_state.banco_docente.append({
                "materia": materia_act,
                "curso": curso_act,
                "tipo": tipo_pregunta,
                "pregunta": pregunta_txt,
                "A": op_a, "B": op_b, "C": op_c, "D": op_d,
                "correcta": correcta
            })
            st.success(f"¡Pregunta agregada! Total en banco: {len(st.session_state.banco_docente)}")

        if st.session_state.banco_docente:
            st.markdown("---")
            st.subheader("📚 Preguntas Registradas en el Banco")
            for idx, item in enumerate(st.session_state.banco_docente, 1):
                st.markdown(f"**P{idx} [{item['tipo']}] [{item['materia']}]: {item['pregunta']}**")
                st.markdown(f"A) {item['A']} | B) {item['B']} | C) {item['C']} | D) {item['D']} — *Correcta: **[{item['correcta']}]***")
            
            if st.button("🗑️ Vaciar Banco de Preguntas"):
                st.session_state.banco_docente = []
                st.rerun()

        st.markdown("---")
        st.subheader("🔀 Generar Exámenes Anti-Copias con IA")
        cant_versiones = st.slider("Número de versiones / filas a generar:", min_value=2, max_value=6, value=3)

        if st.button("🚀 Crear Versiones y Claves de Respuestas"):
            if not st.session_state.banco_docente:
                st.warning("Debe registrar al menos una pregunta antes de generar el examen.")
            else:
                with st.spinner("La IA está permutando las preguntas y opciones para cada fila..."):
                    try:
                        model = obtener_modelo_oficial()
                        prompt = f"""
                        Actúa como un docente evaluador de {materia_act} ({curso_act}).
                        Genera {cant_versiones} versiones distintas (Fila A, Fila B, Fila C...) para imprimir.
                        Banco de preguntas oficial: {st.session_state.banco_docente}

                        Para cada versión:
                        1. Reordena las preguntas y permuta las opciones de respuesta.
                        2. Muestra las preguntas listas para ser impresas.
                        3. Al final, entrega la clave/patrón de respuestas oficial para cada fila.
                        """
                        res = model.generate_content(prompt)
                        st.success("¡Versiones generadas exitosamente!")
                        st.markdown(res.text)
                    except Exception as err:
                        st.error(f"Error en la generación: {err}")

    # --------------------------------------
    # PESTAÑA 2: HOJAS IMPRESAS
    # --------------------------------------
    with tab2:
        st.header("📄 Plantillas de Respuestas Físicas")
        st.markdown("Genera e imprime hojas de respuestas con formato de alvéolos (círculos) rellenables.")

        num_p_hoja = st.slider("Número de preguntas para la plantilla:", min_value=5, max_value=30, value=20)
        if st.button("🖨️ Generar Vista Previa de Imputación"):
            st.markdown("### 📋 U.E. DANIEL SÁNCHEZ BUSTAMANTE — HOJA DE RESPUESTAS")
            st.markdown("**Estudiante:** _______________________ | **Curso:** _________ | **Fila:** [ A ] [ B ] [ C ] [ D ]")
            st.markdown("---")
            for p in range(1, num_p_hoja + 1):
                st.markdown(f"**P{p:02d}**      ⚪ **A**      ⚪ **B**      ⚪ **C**      ⚪ **D**")
            st.markdown("---")

    # --------------------------------------
    # PESTAÑA 3: REGISTRO DE NOTAS (FASE 1 Y 4)
    # --------------------------------------
    with tab3:
        st.header("📊 Registro y Planilla de Calificaciones")
        st.markdown("Consulta en tiempo real la lista de estudiantes y las calificaciones obtenidas.")

        if st.session_state.historial_notas:
            st.dataframe(st.session_state.historial_notas, use_container_width=True)
            if st.button("🗑️ Borrar Historial de Notas"):
                st.session_state.historial_notas = []
                st.rerun()
        else:
            st.info("Aún no hay exámenes enviados en esta sesión.")

    # --------------------------------------
    # PESTAÑA 4: ESCÁNER CON IA
    # --------------------------------------
    with tab4:
        st.header("📷 Escáner Óptico por IA")
        st.markdown("Fotografía la hoja física de un alumno para calificar automáticamente mediante visión artificial.")

        version_fila = st.selectbox("Fila a calificar:", ["Fila A", "Fila B", "Fila C", "Fila D"])
        patron_oficial = st.text_input("Patrón de respuestas correctas (Ej: 1-A, 2-C, 3-B...):")
        foto_alumno = st.camera_input("Capturar la hoja de respuestas:")

        if foto_alumno and st.button("🔍 Escanear y Evaluar"):
            if not patron_oficial:
                st.warning("Debe ingresar la clave de respuestas correctas.")
            else:
                with st.spinner("Analizando círculos marcados con visión artificial..."):
                    try:
                        vision_ia = obtener_modelo_oficial()
                        prompt_escaneo = f"""
                        Analiza la hoja de respuestas física capturada.
                        Patrón oficial para la {version_fila}: {patron_oficial}
                        Identifica los círculos marcados y entrega:
                        1. Lista detallada de aciertos (✅) y errores (❌).
                        2. Desglose de puntuación.
                        3. Nota Final sobre 100 puntos.
                        """
                        img = Image.open(foto_alumno)
                        res_scan = vision_ia.generate_content([prompt_escaneo, img])
                        st.markdown(res_scan.text)
                    except Exception as err:
                        st.error(f"Error al escanear: {err}")

# ==========================================
# VISTA: MODO ESTUDIANTE (FASE 3 Y 4)
# ==========================================
else:
    st.header("✍️ Portal de Evaluación Estudiantil")
    st.markdown("Completa los datos requeridos y responde a la prueba asignada.")

    preguntas_activas = st.session_state.banco_docente

    if not preguntas_activas:
        st.info("📌 **Nota:** Actualmente no hay un examen activo publicado por el docente.")
    else:
        st.success(f"📋 Examen disponible con {len(preguntas_activas)} preguntas.")

        with st.form("form_estudiante_online"):
            nombre_alumno = st.text_input("Nombre Completo del Estudiante:", placeholder="Ej. Ana Mamani Calle")
            st.markdown("---")
            
            respuestas = {}
            for idx, p in enumerate(preguntas_activas, 1):
                st.markdown(f"**P{idx}. {p['pregunta']}**")
                
                if p["tipo"] == "Verdadero / Falso":
                    opciones_display = ["A", "B"]
                    labels = {"A": "A) Verdadero", "B": "B) Falso"}
                else:
                    opciones_display = ["A", "B", "C", "D"]
                    labels = {"A": f"A) {p['A']}", "B": f"B) {p['B']}", "C": f"C) {p['C']}", "D": f"D) {p['D']}"}

                respuestas[idx] = st.radio(
                    f"Selección para P{idx}:",
                    opciones_display,
                    format_func=lambda x: labels[x],
                    key=f"est_p_{idx}"
                )
                st.markdown("---")

            btn_enviar = st.form_submit_button("📤 Finalizar y Enviar Examen")

        if btn_enviar:
            if not nombre_alumno.strip():
                st.error("Por favor, ingresa tu Nombre Completo antes de enviar.")
            else:
                aciertos = 0
                total = len(preguntas_activas)

                for idx, p in enumerate(preguntas_activas, 1):
                    if respuestas[idx] == p.get("correcta", "A"):
                        aciertos += 1

                nota_final = round((aciertos / total) * 100, 1)
                hora_envio = datetime.now().strftime("%H:%M:%S")

                # Guardar resultado en el panel docente
                st.session_state.historial_notas.append({
                    "Estudiante": nombre_alumno,
                    "Nota (/100)": nota_final,
                    "Aciertos": f"{aciertos}/{total}",
                    "Hora": hora_envio
                })

                st.balloons()
                st.success(f"¡Examen enviado con éxito, {nombre_alumno}!")
                st.metric(label="Tu Calificación", value=f"{nota_final} / 100 pts", delta=f"{aciertos} de {total} aciertos")
