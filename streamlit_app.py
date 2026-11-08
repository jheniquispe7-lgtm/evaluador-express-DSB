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
# CONFIGURACIÓN SEGURA DE LA API KEY
# ==========================================
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

def obtener_modelo_activo():
    # Buscamos de forma segura el modelo disponible en el entorno actual
    for nombre_modelo in ['gemini-1.5-flash', 'gemini-1.0-pro', 'gemini-pro']:
        try:
            m = genai.GenerativeModel(nombre_modelo)
            return m
        except Exception:
            continue
    # Si ninguno funciona de forma directa, tomamos el primero disponible de la lista
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except Exception:
        pass
    return genai.GenerativeModel('gemini-1.5-flash')

# ==========================================
# BANNER PRINCIPAL (TÍTULO DE LA HERRAMIENTA)
# ==========================================
try:
    banner_img = Image.open("banner.jpg")
    st.image(banner_img, use_container_width=True)
except FileNotFoundError:
    st.title("⚡ EVALUA - DSB")
    st.warning("⚠️ Sube tu archivo 'banner.jpg' al repositorio de GitHub para mostrar el banner oficial.")

st.markdown("**Plataforma de Evaluación Docente — Unidad Educativa Daniel Sánchez Bustamante:** Banco de preguntas, patrones anti-copias (A-D), examen digital con calificación instantánea y escaneo rápido.")

# Pestañas principales de la aplicación
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Banco de Preguntas y Patrones", 
    "📄 Generar Hoja de Respuestas", 
    "⏱️ Examen en Línea (Instantáneo)", 
    "📷 Escáner de Aciertos (✓/✗)"
])

# ==========================================
# PESTAÑA 1: BANCO DE PREGUNTAS Y PATRONES (A-D)
# ==========================================
with tab1:
    st.header("📝 Banco de Preguntas y Generación de Patrones por Versiones")
    st.markdown("Dicta o escribe tus preguntas con sus 4 opciones (**A, B, C, D**) y define cuál es la respuesta correcta.")

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
    
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        materia_sel = st.text_input("Anota la Materia:", value="Técnicas Tecnológicas")
    with col_v2:
        curso_sel = st.selectbox("Curso:", ["1ro Secundaria", "2do Secundaria", "3ro Secundaria", "4to Secundaria", "5to Secundaria", "6to Secundaria"])
    with col_v3:
        cant_versiones = st.slider("¿Cuántas versiones (filas) deseas crear?:", min_value=2, max_value=6, value=3)

    if st.button("🚀 Crear Versiones y Patrones Anti-Copias"):
        if not st.session_state.banco_docente:
            st.warning("Primero debes registrar al menos una pregunta en el banco.")
        else:
            with st.spinner(f"Creando {cant_versiones} patrones únicos y recombinando versiones..."):
                try:
                    model = obtener_modelo_activo()

                    prompt_versiones = f"""
                    Actúa como profesor experto de {materia_sel} ({curso_sel}).
                    Tengo el siguiente banco de preguntas con sus respuestas correctas oficiales:
                    {st.session_state.banco_docente}

                    Genera exactamente {cant_versiones} versiones/filas distintas de examen (Fila A, Fila B, Fila C...).
                    Para cada versión:
                    1. Reordena las preguntas y permuta de forma inteligente las opciones A, B, C y D.
                    2. Muestra las preguntas listas para imprimir o copiar de cada Fila.
                    3. Al final, incluye las **Claves o Patrones de Respuestas Oficiales** detallados para cada una de las {cant_versiones} filas.
                    """
                    
                    res_Versiones = model.generate_content(prompt_versiones)
                    st.success(f"¡Se generaron las {cant_versiones} versiones y sus patrones con éxito!")
                    st.markdown("---")
                    st.markdown(res_Versiones.text)
                except Exception as err:
                    st.error(f"Error al generar las versiones: {err}")

# ==========================================
# PESTAÑA 2: GENERADOR DE HOJA DE RESPUESTAS (CÍRCULOS)
# ==========================================
with tab2:
    st.header("📄 Generador de Plantilla de Hoja de Respuestas (Círculos)")
    st.markdown("Visualiza el formato para impresión. Los estudiantes deben **pintar completamente el círculo** de su respuesta.")

    num_p_hoja = st.slider("Número de preguntas para la plantilla:", min_value=5, max_value=30, value=20)
    
    if st.button("🖨️ Mostrar Vista Previa de Hoja de Respuestas"):
        st.info("📌 **Instrucción para el estudiante:** Rellene/pinte completamente el círculo correspondiente con bolígrafo negro o azul.")
        
        st.markdown("### 📋 HOJA DE RESPUESTAS — EVALUA DSB")
        st.markdown("**Nombre:** __________________________ | **Curso:** ____________ | **Fila:** [ A ] [ B ] [ C ] [ D ]")
        st.markdown("---")
        
        for p in range(1, num_p_hoja + 1):
            st.markdown(f"**P{p:02d}**      ⚪ **A**      ⚪ **B**      ⚪ **C**      ⚪ **D**")
        st.markdown("---")
        st.success("¡Listo para imprimir y distribuir!")

# ==========================================
# PESTAÑA 3: EXAMEN EN LÍNEA CON AUTOCALIFICACIÓN INSTANTÁNEA
# ==========================================
with tab3:
    st.header("⏱️ Examen en Línea con Calificación Instantánea")
    st.markdown("Los estudiantes rinden su examen en tiempo real y obtienen su nota e informe de aciertos al momento de enviar.")

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
                nombre_est = st.text_input("Nombre Completo del Estudiante:")
                respuestas_est = {}
                
                preguntas_evaluar = st.session_state.banco_docente if st.session_state.banco_docente else [
                    {"pregunta": "¿Cuál es la respuesta correcta para la P1?", "A": "Opción 1", "B": "Opción 2", "C": "Opción 3", "D": "Opción 4", "correcta": "A"},
                    {"pregunta": "¿Cuál es la respuesta correcta para la P2?", "A": "Opción A", "B": "Opción B", "C": "Opción C", "D": "Opción D", "correcta": "C"}
                ]

                for idx, q in enumerate(preguntas_evaluar, 1):
                    st.write(f"**P{idx}. {q['pregunta']}**")
                    respuestas_est[idx] = st.radio(
                        f"Selecciona la opción para la P{idx}:",
                        ["A", "B", "C", "D"],
                        format_func=lambda opt, item=q: f"{opt}) {item[opt]}",
                        key=f"q_{idx}"
                    )
                    st.markdown("---")

                enviado = st.form_submit_button("📤 Enviar Examen y Ver Nota")

                if enviado:
                    if not nombre_est:
                        st.warning("Por favor escribe tu nombre completo antes de enviar.")
                    else:
                        aciertos = 0
                        total_q = len(preguntas_evaluar)
                        
                        st.markdown(f"### 📊 Resultado para: **{nombre_est}**")
                        
                        for idx, q in enumerate(preguntas_evaluar, 1):
                            resp_al = respuestas_est[idx]
                            resp_cor = q.get('correcta', q.get('correct', 'A'))
                            
                            if resp_al == resp_cor:
                                aciertos += 1
                                st.success(f"**P{idx}:** ✅ Correcto (Marcaste **{resp_al}**)")
                            else:
                                st.error(f"**P{idx}:** ❌ Incorrecto (Marcaste **{resp_al}** | Correcta: **{resp_cor}**)")

                        nota_final = round((aciertos / total_q) * 100, 1)
                        st.markdown("---")
                        st.metric(label="Calificación Final", value=f"{nota_final} / 100 pts", delta=f"{aciertos} de {total_q} aciertos")
                        st.session_state.online_activo = False
            
            time.sleep(1)
            st.rerun()
        else:
            cron_caja.error("⏰ ¡El tiempo del examen ha concluido!")
            st.session_state.online_activo = False
    else:
        cron_caja.info(f"Cronómetro configurado a {minutos_Ex} minutos. Presiona 'Iniciar Prueba en Línea' para comenzar.")

# ==========================================
# PESTAÑA 4: ESCÁNER DE ACIERTOS (✓ / ✗)
# ==========================================
with tab4:
    st.header("📷 Escáner Óptico de Hoja de Respuestas (A-D)")
    st.markdown("Toma una foto a la hoja marcada por el estudiante. La IA leerá las marcas entre **A, B, C y D** y calculará la nota.")

    version_fila = st.radio("Selecciona la Fila evaluada:", ["Fila A", "Fila B", "Fila C", "Fila D"], horizontal=True)
    patron_oficial = st.text_input("Ingresa el patrón de respuestas correctas (ej: 1-A, 2-C, 3-B, 4-D...):")

    foto_alumno = st.camera_input("📸 Capturar la hoja de respuestas del estudiante:")

    if foto_alumno and st.button("🔍 Escanear y Calcular Calificación"):
        if not patron_oficial:
            st.warning("Por favor, ingresa el patrón de respuestas correctas antes de escanear.")
        else:
            with st.spinner("Escaneando círculos rellenados y calculando aciertos..."):
                try:
                    vision_ia = obtener_modelo_activo()

                    prompt_lector = (
                        f"Actúa como un escáner óptico de corrección de exámenes de 4 opciones (A, B, C, D).\n"
                        f"Patrón de respuestas correctas oficial para la {version_fila}: {patron_oficial}\n\n"
                        "Analiza la imagen de la hoja de respuestas del alumno (donde pintó los círculos) y:\n"
                        "1. Identifica qué círculo (A, B, C o D) fue pintado/oscurecido completamente por el estudiante en cada número.\n"
                        "2. Compara cada respuesta del alumno con el patrón oficial y etiqueta rigurosamente:\n"
                        "   - ✅ si es correcto (Acierto).\n"
                        "   - ❌ si es incorrecto (Error, mostrando qué marco vs la respuesta correcta).\n"
                        "3. Presenta una tabla resumen final con:\n"
                        "   - **Total de Aciertos (✓)**: \n"
                        "   - **Total de Errores (✗)**: \n"
                        "   - **Nota Final (sobre 100 puntos)**:"
                    )

                    img_hoja = Image.open(foto_alumno)
                    res_escaneo = vision_ia.generate_content([prompt_lector, img_hoja])

                    st.success("¡Escaneo y corrección completados con éxito!")
                    st.markdown("---")
                    st.markdown(res_escaneo.text)
                except Exception as e:
                    st.error(f"Error al procesar el escaneo: {e}")
