import streamlit as st
import os
import random
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="EVALÚA - DSB",
    page_icon="📚",
    layout="wide"
)

# --- INICIALIZACIÓN DE ESTADOS EN MEMORIA ---
if "banco_preguntas" not in st.session_state:
    st.session_state.banco_preguntas = [
        {
            "materia": "Técnicas Tecnológicas",
            "tema": "Sistemas Web",
            "pregunta": "¿Qué tecnología web interactiva utiliza EVALÚA - DSB?",
            "opciones": ["A) Flask", "B) Streamlit", "C) Django", "D) PHP"],
            "correcta": "B) Streamlit"
        },
        {
            "materia": "Técnicas Tecnológicas",
            "tema": "Inteligencia Artificial",
            "pregunta": "¿Qué modelo de inteligencia artificial apoya en la generación de preguntas?",
            "opciones": ["A) Google Gemini", "B) ChatGPT", "C) Claude", "D) Llama"],
            "correcta": "A) Google Gemini"
        }
    ]

if "examen_activo" not in st.session_state:
    st.session_state.examen_activo = st.session_state.banco_preguntas.copy()

if "calificaciones" not in st.session_state:
    st.session_state.calificaciones = []

# --- BANNER INSTITUCIONAL ---
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.jpg.jpg"):
    st.image("banner.jpg.jpg", use_container_width=True)
else:
    st.markdown("### 🏫 Unidad Educativa Daniel Sánchez Bustamante - EVALÚA-DSB")

st.title("EVALÚA - DSB: Sistema de Evaluación Digital e Impresa")
st.markdown("---")

# --- MENÚ LATERAL DE ROLES ---
st.sidebar.title("Panel de Control")
rol = st.sidebar.selectbox("Seleccione su Rol:", ["Estudiante", "Docente"])

# ==============================================================================
# MÓDULO DOCENTE
# ==============================================================================
if rol == "Docente":
    st.header("👨‍🏫 Panel de Gestión Docente")
    
    pin_ingresado = st.sidebar.text_input("Ingrese PIN Docente:", type="password")
    PIN_SECRETO = "1234"
    
    if pin_ingresado == PIN_SECRETO:
        st.sidebar.success("Acceso Docente Autorizado")
        
        menu_docente = st.selectbox(
            "Seleccione una herramienta:",
            [
                "1. Gestionar Banco de Preguntas",
                "2. Generador de Versiones Impresas (Anti-copias)",
                "3. Escáner Óptico de Hojas Físicas",
                "4. Registro de Calificaciones"
            ]
        )
        
        # --- 1. BANCO DE PREGUNTAS ---
        if menu_docente == "1. Gestionar Banco de Preguntas":
            st.subheader("📚 Banco de Preguntas Reutilizable")
            
            with st.form("form_nueva_pregunta"):
                st.write("Agregar nueva pregunta al banco:")
                materia_p = st.text_input("Materia", "Técnicas Tecnológicas")
                tema_p = st.text_input("Tema o Unidad", "Hardware")
                pregunta_p = st.text_input("Enunciado de la pregunta")
                op_a = st.text_input("Opción A", "A) ...")
                op_b = st.text_input("Opción B", "B) ...")
                op_c = st.text_input("Opción C", "C) ...")
                op_d = st.text_input("Opción D", "D) ...")
                correcta_p = st.selectbox("Respuesta Correcta", [op for op in [op_a, op_b, op_c, op_d] if op])
                
                submitted = st.form_submit_button("Guardar Pregunta")
                if submitted and pregunta_p:
                    st.session_state.banco_preguntas.append({
                        "materia": materia_p,
                        "tema": tema_p,
                        "pregunta": pregunta_p,
                        "opciones": [op_a, op_b, op_c, op_d],
                        "correcta": correcta_p
                    })
                    st.success("¡Pregunta guardada en el banco con éxito!")
            
            st.markdown("### Preguntas Registradas:")
            for i, p in enumerate(st.session_state.banco_preguntas, 1):
                st.write(f"**{i}. [{p['tema']}] {p['pregunta']}** (Correcta: {p['correcta']})")

        # --- 2. VERSIONES IMPRESAS ---
        elif menu_docente == "2. Generador de Versiones Impresas (Anti-copias)":
            st.subheader("📄 Generación de Exámenes Físicos")
            st.write("Seleccione las preguntas para generar las filas de examen:")
            
            indices_sel = []
            for idx, p in enumerate(st.session_state.banco_preguntas):
                if st.checkbox(f"{p['pregunta']}", value=True, key=f"ch_{idx}"):
                    indices_sel.append(idx)
            
            if st.button("Generar Filas A y B"):
                if indices_sel:
                    preguntas_sel = [st.session_state.banco_preguntas[i] for i in indices_sel]
                    st.markdown("---")
                    st.markdown("### 📄 FILA A")
                    for num, item in enumerate(preguntas_sel, 1):
                        st.write(f"**{num}. {item['pregunta']}**")
                        for op in item['opciones']:
                            st.write(f"   {op}")
                    
                    st.markdown("---")
                    st.markdown("### 📄 FILA B (Mezclada)")
                    mezcla = preguntas_sel.copy()
                    random.shuffle(mezcla)
                    for num, item in enumerate(mezcla, 1):
                        st.write(f"**{num}. {item['pregunta']}**")
                        for op in item['opciones']:
                            st.write(f"   {op}")
                else:
                    st.warning("Seleccione al menos una pregunta.")

        # --- 3. ESCÁNER ÓPTICO ---
        elif menu_docente == "3. Escáner Óptico de Hojas Físicas":
            st.subheader("📷 Escáner Óptico y Corrección")
            nombre_est = st.text_input("Apellidos y Nombres del Estudiante:")
            foto_hoja = st.file_uploader("Subir foto de la hoja marcada", type=["jpg", "png", "jpeg"])
            
            if foto_hoja and nombre_est:
                st.image(foto_hoja, caption="Hoja escaneada", width=300)
                if st.button("Procesar Marcas Ópticas"):
                    st.session_state.temp_nota = {"estudiante": nombre_est, "nota": 85}
                
                if "temp_nota" in st.session_state:
                    nota_f = st.number_input("Nota sugerida por el escáner:", 0, 100, st.session_state.temp_nota["nota"])
                    if st.button("Confirmar y Guardar Nota"):
                        st.session_state.calificaciones.append({
                            "Estudiante": st.session_state.temp_nota["estudiante"],
                            "Tipo": "Examen Físico (Escáner)",
                            "Nota": nota_f
                        })
                        st.success("¡Calificación guardada correctamente!")
                        del st.session_state.temp_nota

        # --- 4. REGISTRO DE NOTAS ---
        elif menu_docente == "4. Registro de Calificaciones":
            st.subheader("📋 Historial de Calificaciones")
            if st.session_state.calificaciones:
                df = pd.DataFrame(st.session_state.calificaciones)
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Descargar CSV", data=csv, file_name="notas_dsb.csv", mime="text/csv")
            else:
                st.info("Aún no hay calificaciones registradas.")

    elif pin_ingresado == "":
        st.info("Ingrese el PIN (1234) en el panel izquierdo.")
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
        
        respuestas_est = {}
        for i, p in enumerate(st.session_state.banco_preguntas):
            respuestas_est[i] = st.radio(f"**{i+1}. {p['pregunta']}**", p["opciones"], key=f"r_{i}")
        
        if st.button("Enviar Examen"):
            correctas = 0
            for i, p in enumerate(st.session_state.banco_preguntas):
                if respuestas_est[i] == p["correcta"]:
                    correctas += 1
            
            nota_final = round((correctas / len(st.session_state.banco_preguntas)) * 100)
            st.success(f"¡Examen enviado con éxito, {nombre_alumno}!")
            st.markdown("### Calificación Automática")
            st.metric(label="", value=f"{nota_final} / 100 pts")
            
            st.session_state.calificaciones.append({
                "Estudiante": nombre_alumno,
                "Tipo": "Examen Digital en Línea",
                "Nota": nota_final
            })
    else:
        st.warning("Ingrese su nombre completo para habilitar el examen.")
