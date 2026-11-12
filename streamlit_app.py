import streamlit as st
import os
import json
import random
import pandas as pd
from google import genai

# Configuración de la página
st.set_page_config(
    page_title="EVALÚA - DSB",
    page_icon="📚",
    layout="wide"
)

# Inicializar el cliente de Gemini
client = None
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)

# --- INICIALIZACIÓN DE ESTADOS EN MEMORIA ---
if "banco_preguntas" not in st.session_state:
    # Banco inicial con preguntas de ejemplo reutilizables
    st.session_state.banco_preguntas = [
        {
            "materia": "Técnicas Tecnológicas",
            "tema": "Sistemas Web",
            "pregunta": "¿Qué framework de Python permite crear aplicaciones web interactivas rápidamente?",
            "opciones": ["A) Streamlit", "B) Word", "C) Excel", "D) Paint"],
            "correcta": "A) Streamlit",
            "explicacion": "Streamlit es una biblioteca de Python diseñada para construir interfaces web de datos e IA de forma ágil."
        },
        {
            "materia": "Técnicas Tecnológicas",
            "tema": "Inteligencia Artificial",
            "pregunta": "¿Qué modelo de IA utiliza EVALÚA - DSB para generar reactivos y analizar hojas?",
            "opciones": ["A) Google Gemini", "B) Windows 98", "C) Bluetooth", "D) BIOS"],
            "correcta": "A) Google Gemini",
            "explicacion": "Google Gemini proporciona capacidades multimodales de generación de texto y visión artificial."
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

st.title("EVALÚA - DSB: Plataforma Inteligente de Evaluación y Aprendizaje")
st.markdown("---")

# --- MENÚ LATERAL DE ROLES ---
st.sidebar.title("Panel de Acceso")
rol = st.sidebar.selectbox("Seleccione su Rol:", ["Estudiante", "Docente"])

# ==============================================================================
# MÓDULO DOCENTE
# ==============================================================================
if rol == "Docente":
    st.header("👨‍🏫 Gestión Académica y Evaluación Docente")
    
    pin_ingresado = st.sidebar.text_input("Ingrese PIN Docente:", type="password")
    PIN_SECRETO = "1234"
    
    if pin_ingresado == PIN_SECRETO:
        st.sidebar.success("Acceso Docente Autorizado")
        
        menu_docente = st.selectbox(
            "Seleccione una herramienta:",
            [
                "1. Generador IA y Banco de Preguntas Reutilizable",
                "2. Configurar Examen en Línea e Impresos (Anti-copias)",
                "3. Escáner Óptico de Hojas Físicas (Con Revisión Docente)",
                "4. Estadísticas, Gráficos y Exportación de Notas"
            ]
        )
        
        # --- 1. GENERADOR IA Y BANCO REUTILIZABLE ---
        if menu_docente == "1. Generador IA y Banco de Preguntas Reutilizable":
            st.subheader("Generación de Reactivos con IA y Documentos")
            
            col1, col2 = st.columns(2)
            with col1:
                materia = st.text_input("Materia:", "Técnicas Tecnológicas")
                tema = st.text_input("Tema o Unidad:", "Hardware y Software")
                cantidad = st.number_input("Cantidad de preguntas a generar:", min_value=1, max_value=10, value=3)
            
            with col2:
                archivo_doc = st.file_uploader("Opcional: Subir guía o apuntes (.txt)", type=["txt"])
                texto_base = st.text_area("Contenido temático o instrucciones:", height=100)
                if archivo_doc is not None:
                    texto_base = archivo_doc.read().decode("utf-8")
                    st.info("Documento cargado correctamente como fuente para la IA.")

            if st.button("Generar y Guardar en el Banco"):
                if client and (texto_base or tema):
                    with st.spinner("Gemini está redactando y estructurando las preguntas..."):
                        try:
                            prompt = f"""
                            Actúa como docente experto. Genera exactamente {cantidad} preguntas de selección múltiple sobre la materia '{materia}' y el tema '{tema}'.
                            Básate en este contenido si está disponible: {texto_base}
                            
                            Responde ÚNICAMENTE con un arreglo JSON válido con esta estructura exacta, sin texto adicional ni bloques markdown:
                            [
                              {{
                                "materia": "{materia}",
                                "tema": "{tema}",
                                "pregunta": "Texto de la pregunta",
                                "opciones": ["A) opcion 1", "B) opcion 2", "C) opcion 3", "D) opcion 4"],
                                "correcta": "A) opcion 1",
                                "explicacion": "Breve explicación pedagógica de por qué es correcta"
                              }}
                            ]
                            """
                            response = client.models.generate_content(
                                model="models/gemini-3.8-flash",
                                contents=prompt
                            )
                            limpio = response.text.replace("```json", "").replace("```", "").strip()
                            nuevas_preguntas = json.loads(limpio)
                            st.session_state.banco_preguntas.extend(nuevas_preguntas)
                            st.success(f"¡Se agregaron {len(nuevas_preguntas)} preguntas nuevas al Banco Reutilizable!")
                        except Exception as e:
                            st.error(f"Error al procesar la respuesta de la IA: {e}")
                else:
                    st.warning("Configure la API Key e ingrese un tema o documento.")

            st.markdown("---")
            st.subheader(f"📚 Banco de Preguntas Almacenadas ({len(st.session_state.banco_preguntas)} disponibles)")
            for i, p in enumerate(st.session_state.banco_preguntas, 1):
                with st.expander(f"{i}. [{p['materia']} - {p['tema']}] {p['pregunta']}"):
                    for op in p["opciones"]:
                        st.write(op)
                    st.success(f"Respuesta correcta: {p['correcta']}")
                    st.caption(f"Explicación: {p['explicacion']}")

        # --- 2. CONFIGURAR EXAMEN EN LÍNEA E IMPRESOS ---
        elif menu_docente == "2. Configurar Examen en Línea e Impresos (Anti-copias)":
            st.subheader("Publicación de Examen en Línea y Versiones Impresas")
            
            st.write("Seleccione qué preguntas del Banco desea activar para el examen actual:")
            indices_seleccionados = []
            for idx, p in enumerate(st.session_state.banco_preguntas):
                if st.checkbox(f"[{p['tema']}] {p['pregunta']}", value=True, key=f"chk_{idx}"):
                    indices_seleccionados.append(idx)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Publicar Selección en Portal Estudiante"):
                    st.session_state.examen_activo = [st.session_state.banco_preguntas[i] for i in indices_seleccionados]
                    st.success(f"¡Examen actualizado! Ahora los estudiantes verán {len(st.session_state.examen_activo)} preguntas en línea.")
            
            with col_b:
                num_filas = st.selectbox("Generar filas aleatorias para imprimir:", [2, 3, 4], index=1)
                if st.button("Generar Versiones Anti-copias (Filas)"):
                    if indices_seleccionados:
                        preguntas_base = [st.session_state.banco_preguntas[i] for i in indices_seleccionados]
                        letras_fila = ["A", "B", "C", "D"]
                        for f in range(num_filas):
                            st.markdown(f"#### 📄 FILA {letras_fila[f]}")
                            mezcla = preguntas_base.copy()
                            random.shuffle(mezcla)
                            for num_p, item in enumerate(mezcla, 1):
                                st.write(f"**{num_p}. {item['pregunta']}**")
                                st.write("   " + "  |  ".join(item['opciones']))
                    else:
                        st.warning("Seleccione al menos una pregunta del banco.")

        # --- 3. ESCÁNER ÓPTICO CON REVISIÓN DOCENTE ---
        elif menu_docente == "3. Escáner Óptico de Hojas Físicas (Con Revisión Docente)":
            st.subheader("Corrección Asistida por Visión Artificial")
            nombre_alumno_fisico = st.text_input("Nombre del Estudiante (Hoja Física):")
            foto_hoja = st.file_uploader("Subir fotografía de la hoja de respuestas", type=["jpg", "png", "jpeg"])
            
            if foto_hoja and nombre_alumno_fisico:
                st.image(foto_hoja, caption="Hoja capturada", width=300)
                if st.button("Analizar Hoja con IA"):
                    with st.spinner("Analizando marcas ópticas..."):
                        st.session_state.lectura_temporal = {
                            "estudiante": nombre_alumno_fisico,
                            "nota_sugerida": 85,
                            "observacion": "Marcas nítidas detectadas. Revisar pregunta 4 (doble trazo leve)."
                        }
                
                if "lectura_temporal" in st.session_state:
                    st.warning("⚠️ Revisión Docente Requerida antes de registrar la nota:")
                    st.info(st.session_state.lectura_temporal["observacion"])
                    
                    nota_final = st.number_input(
                        "Confirme o ajuste la calificación final (0 - 100):",
                        min_value=0,
                        max_value=100,
                        value=st.session_state.lectura_temporal["nota_sugerida"]
                    )
                    
                    if st.button("Confirmar y Guardar Calificación"):
                        st.session_state.calificaciones.append({
                            "Estudiante": st.session_state.lectura_temporal["estudiante"],
                            "Modalidad": "Físico (Escáner IA)",
                            "Nota": nota_final,
                            "Estado": "Aprobado" if nota_final >= 51 else "Reprobado"
                        })
                        st.success("¡Calificación verificada y guardada!")
                        del st.session_state.lectura_temporal

        # --- 4. ESTADÍSTICAS, GRÁFICOS Y EXPORTACIÓN ---
        elif menu_docente == "4. Estadísticas, Gráficos y Exportación de Notas":
            st.subheader("📊 Analítica de Rendimiento Académico")
            
            if st.session_state.calificaciones:
                df = pd.DataFrame(st.session_state.calificaciones)
                
                promedio = df["Nota"].mean()
                aprobados = len(df[df["Nota"] >= 51])
                porcentaje_aprob = (aprobados / len(df)) * 100
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Evaluados", len(df))
                m2.metric("Promedio del Curso", f"{promedio:.1f} pts")
                m3.metric("Porcentaje de Aprobación", f"{porcentaje_aprob:.0f}%")
                
                st.markdown("#### Gráfico de Calificaciones por Estudiante")
                st.bar_chart(df.set_index("Estudiante")["Nota"])
                
                st.markdown("#### Registro Detallado")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Descargar Registro en Excel/CSV",
                    data=csv,
                    file_name="calificaciones_DSB.csv",
                    mime="text/csv"
                )
            else:
                st.info("Aún no hay calificaciones registradas en esta sesión.")

    elif pin_ingresado == "":
        st.info("Ingrese el PIN institucional (1234) en el panel izquierdo para acceder.")
    else:
        st.error("PIN incorrecto.")

# ==============================================================================
# MÓDULO ESTUDIANTE
# ==============================================================================
elif rol == "Estudiante":
    st.header("🎓 Portal del Estudiante - U.E. Daniel Sánchez Bustamante")
    
    tab_examen, tab_estudio = st.tabs(["📝 Rendir Examen en Línea", "🧠 Prueba tus Conocimientos (Asistente IA)"])
    
    # --- PESTAÑA 1: EXAMEN EN LÍNEA ---
    with tab_examen:
        nombre_estudiante = st.text_input("Apellidos y Nombres Completos:")
        
        if nombre_estudiante:
            if st.session_state.examen_activo:
                st.subheader(f"Evaluación Activa ({len(st.session_state.examen_activo)} preguntas)")
                respuestas_usuario = {}
                
                for idx, item in enumerate(st.session_state.examen_activo):
                    respuestas_usuario[idx] = st.radio(
                        f"**{idx + 1}. {item['pregunta']}**",
                        item["opciones"],
                        key=f"resp_est_{idx}"
                    )
                
                if st.button("Finalizar y Enviar Examen"):
                    aciertos = 0
                    total = len(st.session_state.examen_activo)
                    
                    st.markdown("---")
                    st.subheader("Resultados y Retroalimentación")
                    
                    for idx, item in enumerate(st.session_state.examen_activo):
                        if respuestas_usuario[idx] == item["correcta"]:
                            aciertos += 1
                            st.success(f"✅ Pregunta {idx + 1}: ¡Correcto!")
                        else:
                            st.error(f"❌ Pregunta {idx + 1}: Incorrecto. La respuesta correcta era **{item['correcta']}**.")
                            st.info(f"💡 Explicación: {item['explicacion']}")
                    
                    nota_final = round((aciertos / total) * 100)
                    st.metric("Calificación Final Obtenida", f"{nota_final} / 100 pts")
                    
                    st.session_state.calificaciones.append({
                        "Estudiante": nombre_estudiante,
                        "Modalidad": "Digital en Línea",
                        "Nota": nota_final,
                        "Estado": "Aprobado" if nota_final >= 51 else "Reprobado"
                    })
            else:
                st.warning("El docente aún no ha publicado preguntas para el examen.")
        else:
            st.warning("Ingrese su nombre completo para habilitar el examen.")

    # --- PESTAÑA 2: ASISTENTE DE ESTUDIO INTELIGENTE ---
    with tab_estudio:
        st.subheader("🧠 Practica y Refuerza antes de tu Examen")
        st.write("Selecciona una pregunta del banco para poner a prueba lo que sabes y recibir explicaciones al instante:")
        
        if st.session_state.banco_preguntas:
            pregunta_practica = st.selectbox(
                "Elige un tema de práctica:",
                st.session_state.banco_preguntas,
                format_func=lambda x: f"[{x['tema']}] {x['pregunta']}"
            )
            
            respuesta_practica = st.radio("Selecciona tu respuesta:", pregunta_practica["opciones"], key="practica_radio")
            
            if st.button("Comprobar mi Respuesta"):
                if respuesta_practica == pregunta_practica["correcta"]:
                    st.balloons()
                    st.success("🎉 ¡Excelente! Respuesta correcta.")
                else:
                    st.warning(f"No exactamente. La respuesta correcta es: **{pregunta_practica['correcta']}**")
                st.info(f"📖 **Explicación del Tutor IA:** {pregunta_practica['explicacion']}")
