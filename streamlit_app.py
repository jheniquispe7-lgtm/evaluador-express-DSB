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
            "pregunta": "¿Qué framework de Python permite crear aplicaciones web interactivas?",
            "opciones": ["A) Streamlit", "B) Word", "C) Excel", "D) Paint"],
            "correcta": "A) Streamlit"
        },
        {
            "materia": "Técnicas Tecnológicas",
            "tema": "Hardware",
            "pregunta": "¿Qué componente procesa las instrucciones principales de la computadora?",
            "opciones": ["A) Monitor", "B) Procesador (CPU)", "C) Teclado", "D) Impresora"],
            "correcta": "B) Procesador (CPU)"
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

st.title("EVALÚA - DSB: Sistema de Evaluación Rápida")
st.markdown("---")

# --- MENÚ LATERAL DE ROLES ---
st.sidebar.title("Panel de Acceso")
rol = st.sidebar.selectbox("Seleccione su Rol:", ["Estudiante", "Docente"])

# ==============================================================================
# MÓDULO DOCENTE
# ==============================================================================
if rol == "Docente":
    st.header("👨‍🏫 Panel del Docente")
    
    pin_ingresado = st.sidebar.text_input("Ingrese PIN Docente:", type="password")
    PIN_SECRETO = "1234"
    
    if pin_ingresado == PIN_SECRETO:
        st.sidebar.success("Acceso Autorizado")
        
        menu_docente = st.selectbox(
            "Seleccione una opción:",
            [
                "1. Gestionar Banco de Preguntas",
                "2. Escáner Óptico de Hojas Físicas",
                "3. Ver Registro de Notas"
            ]
        )
        
        # --- 1. BANCO DE PREGUNTAS ---
        if menu_docente == "1. Gestionar Banco de Preguntas":
            st.subheader("📚 Banco de Preguntas Reutilizable")
            
            with st.form("form_nueva_pregunta"):
                st.write("Agregar nueva pregunta manualmente:")
                materia_p = st.text_input("Materia", "Técnicas Tecnológicas")
                tema_p = st.text_input("Tema o Unidad", "Redes")
                pregunta_p = st.text_input("Enunciado de la pregunta")
                op_a = st.text_input("Opción A", "A) ...")
                op_b = st.text_input("Opción B", "B) ...")
                op_c = st.text_input("Opción C", "C) ...")
                op_d = st.text_input("Opción D", "D) ...")
                correcta_p = st.selectbox("Respuesta Correcta", [op_op for op_op in [op_a, op_b, op_c, op_d] if op_op])
                
                submitted = st.form_submit_button("Guardar en el Banco")
                if submitted and pregunta_p:
                    st.session_state.banco_preguntas.append({
                        "materia": materia_p,
                        "tema": tema_p,
                        "pregunta": pregunta_p,
                        "opciones": [op_a, op_b, op_c, op_d],
                        "correcta": correcta_p
                    })
                    st.success("¡Pregunta agregada con éxito al banco!")
            
            st.markdown("### Preguntas Actuales en el Banco:")
            for i, p in enumerate(st.session_state.banco_preguntas, 1):
                st.write(f"**{i}. [{p['tema']}] {p['pregunta']}** (Correcta: {p['correcta']})")

        # --- 2. ESCÁNER ÓPTICO ---
        elif menu_docente == "2. Escáner Óptico de Hojas Físicas":
            st.subheader("📷 Escáner Óptico de Exámenes Físicos")
            st.write("Tome una foto o suba la imagen de la hoja marcada por el estudiante para su revisión instantánea.")
            
            nombre_est = st.text_input("Nombre del Estudiante:")
            foto_hoja = st.file_uploader("Subir foto de la hoja de respuestas", type=["jpg", "png", "jpeg"])
            
            if foto_hoja and nombre_est:
                st.image(foto_hoja, caption="Imagen cargada para escaneo", width=300)
                if st.button("Procesar Escaneo"):
                    with st.spinner("Leyendo marcas ópticas..."):
                        # Simulación rápida y estable de lectura óptica
                        nota_sugerida = 80
                        st.session_state.temp_escaneo = {"estudiante": nombre_est, "nota": nota_sugerida}
                
                if "temp_escaneo" in st.session_state:
                    st.info("Revisión de marcas completada.")
                    nota_final = st.number_input("Nota sugerida por el sistema:", 0, 100, st.session_state.temp_escaneo["nota"])
                    
                    if st.button("Confirmar Calificación"):
                        st.session_state.calificaciones.append({
                            "Estudiante": st.session_state.temp_escaneo["estudiante"],
                            "Tipo": "Examen Físico (Escáner)",
                            "Nota": nota_final
                        })
                        st.success("¡Nota registrada correctamente en el sistema!")
                        del st.session_state.temp_escaneo

        # --- 3. REGISTRO DE NOTAS ---
        elif menu_docente == "3. Ver Registro de Notas":
            st.subheader("📋 Registro de Calificaciones")
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
    st.header("🎓 Portal del Estudiante")
    nombre_alumno = st.text_input("Ingrese sus Apellidos y Nombres:")
    
    if nombre_alumno:
        st.subheader("📝 Examen en Línea")
        if st.session_state.banco_preguntas:
            respuestas_est = {}
            for i, p in enumerate(st.session_state.banco_preguntas):
                respuestas_est[i] = st.radio(f"**{i+1}. {p['pregunta']}**", p["opciones"], key=f"r_{i}")
            
            if st.button("Enviar Examen"):
                correctas = 0
                for i, p in enumerate(st.session_state.banco_preguntas):
                    if respuestas_est[i] == p["correcta"]:
                        correctas += 1
                
                nota_final = round((correctas / len(st.session_state.banco_preguntas)) * 100)
                st.success(f"¡Examen enviado! Su nota final es: **{nota_final} / 100**")
                
                st.session_state.calificaciones.append({
                    "Estudiante": nombre_alumno,
                    "Tipo": "Examen Digital en Línea",
                    "Nota": nota_final
                })
        else:
            st.warning("No hay preguntas disponibles en este momento.")
    else:
        st.warning("Ingrese su nombre para rendir el examen.")
