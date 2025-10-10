import streamlit as st
import base64
import requests
from gtts import gTTS
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import hashlib

# Configuración de la página
st.set_page_config(
    page_title="Tutor IA de Cálculo",
    page_icon="∫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuración de DeepSeek
API_KEY = 'sk-53751d5c6f344a5dbc0571de9f51313e'
API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Estilos CSS mejorados
st.markdown("""
<style>
    /* Estilos generales */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Chat Container */
    .chat-container {
        background: linear-gradient(to bottom, #ffffff, #f8f9fa);
        border-radius: 20px;
        padding: 25px;
        height: 550px;
        overflow-y: auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Mensajes */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 15px 0;
        max-width: 75%;
        margin-left: auto;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.4);
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2c3e50;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 15px 0;
        max-width: 75%;
        margin-right: auto;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Avatar Container */
    .avatar-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        padding: 30px;
        height: 550px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .avatar {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 25px;
        color: white;
        font-size: 5rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
        animation: pulse 3s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .tutor-info {
        text-align: center;
        color: #2c3e50;
    }
    
    .tutor-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 15px;
    }
    
    .tutor-specialty {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 20px;
        font-weight: 500;
    }
    
    .specialty-list {
        text-align: left;
        margin-top: 15px;
        padding-left: 20px;
    }
    
    .specialty-item {
        color: #666;
        margin: 8px 0;
        font-size: 0.95rem;
    }
    
    /* Input Container */
    .input-section {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Gráficas */
    .graph-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Scrollbar personalizado */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Radio buttons */
    .stRadio > div {
        flex-direction: row;
        gap: 20px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: white;
        font-size: 0.9rem;
        margin-top: 30px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sistema de prompts para cálculo
SYSTEM_PROMPT = """Eres un tutor experto en Cálculo Diferencial e Integral. Tu objetivo es:

1. Explicar conceptos de manera clara y paso a paso
2. Usar ejemplos prácticos y visuales cuando sea posible
3. Ser paciente y adaptarte al nivel del estudiante
4. Proporcionar ejercicios de práctica relevantes
5. Usar notación matemática apropiada

Temas principales:
- Límites y continuidad
- Derivadas y aplicaciones
- Integrales definidas e indefinidas
- Teoremas fundamentales del cálculo
- Series y sucesiones
- Ecuaciones diferenciales básicas

Sé conciso pero completo. Si el estudiante pregunta sobre gráficas o funciones, menciona que puede visualizarlas."""

def enviar_mensaje(mensaje, historial):
    """Envía mensaje a la API de DeepSeek"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for msg in historial:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": mensaje})
    
    data = {
        'model': 'deepseek-chat',
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 1000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as err:
        return f"⚠️ Error de conexión: {err}\n\nPor favor, verifica tu conexión a internet e intenta de nuevo."
    except Exception as e:
        return f"⚠️ Error inesperado: {str(e)}"

def texto_a_voz(texto, mensaje_hash):
    """Convierte texto a voz y retorna el audio en base64"""
    try:
        filename = f"audio_{mensaje_hash}.mp3"
        tts = gTTS(texto, lang='es', slow=False)
        tts.save(filename)
        
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        os.remove(filename)
        return audio_base64
    except Exception as e:
        st.error(f"Error al generar audio: {e}")
        return None

def crear_grafica_calculo(tipo, parametros=None):
    """Crea gráficas específicas para cálculo"""
    fig = None
    
    tipo_lower = tipo.lower()
    
    if "derivada" in tipo_lower or "tangente" in tipo_lower:
        x = np.linspace(-3, 3, 200)
        y = x**3 - 3*x
        dy = 3*x**2 - 3
        
        x0 = 1
        y0 = x0**3 - 3*x0
        m = 3*x0**2 - 3
        tangente = m * (x - x0) + y0
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x) = x³ - 3x', line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=x, y=tangente, mode='lines', name='Línea tangente', line=dict(color='#764ba2', dash='dash', width=2)))
        fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='markers', name='Punto de tangencia', marker=dict(size=12, color='red')))
        fig.update_layout(
            title="Derivada como pendiente de la tangente",
            xaxis_title="x",
            yaxis_title="y",
            hovermode='x unified',
            template='plotly_white'
        )
    
    elif "integral" in tipo_lower or "área" in tipo_lower:
        x = np.linspace(0, np.pi, 100)
        y = np.sin(x)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x) = sen(x)', line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', name='Área bajo la curva', fillcolor='rgba(102, 126, 234, 0.3)'))
        fig.update_layout(
            title="Integral definida como área bajo la curva",
            xaxis_title="x",
            yaxis_title="y",
            hovermode='x unified',
            template='plotly_white'
        )
    
    elif "límite" in tipo_lower or "continuidad" in tipo_lower:
        x1 = np.linspace(-3, 1, 100)
        x2 = np.linspace(1, 3, 100)
        y1 = x1**2
        y2 = x2 + 1
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x1, y=y1, mode='lines', name='f(x) para x < 1', line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=x2, y=y2, mode='lines', name='f(x) para x ≥ 1', line=dict(color='#764ba2', width=3)))
        fig.add_trace(go.Scatter(x=[1], y=[1], mode='markers', name='Discontinuidad', marker=dict(size=12, color='red', symbol='circle-open')))
        fig.update_layout(
            title="Análisis de límites y continuidad",
            xaxis_title="x",
            yaxis_title="y",
            hovermode='x unified',
            template='plotly_white'
        )
    
    elif "función" in tipo_lower or "gráfica" in tipo_lower:
        x = np.linspace(-2*np.pi, 2*np.pi, 300)
        y = np.sin(x)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x) = sen(x)', line=dict(color='#667eea', width=3)))
        fig.update_layout(
            title="Función trigonométrica: sen(x)",
            xaxis_title="x",
            yaxis_title="y",
            hovermode='x unified',
            template='plotly_white'
        )
    
    else:
        x = np.linspace(-5, 5, 200)
        y = 1 / (1 + np.exp(-x))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x) = 1/(1+e⁻ˣ)', line=dict(color='#667eea', width=3)))
        fig.update_layout(
            title="Función sigmoide",
            xaxis_title="x",
            yaxis_title="y",
            hovermode='x unified',
            template='plotly_white'
        )
    
    return fig

# Inicializar el estado de la sesión
if "historial" not in st.session_state:
    st.session_state.historial = []
if "mostrar_grafica" not in st.session_state:
    st.session_state.mostrar_grafica = False
if "tipo_grafica" not in st.session_state:
    st.session_state.tipo_grafica = ""
if "audio_actual" not in st.session_state:
    st.session_state.audio_actual = None
if "contador_mensajes" not in st.session_state:
    st.session_state.contador_mensajes = 0

# Título principal
st.markdown('<h1 class="main-header">∫ Tutor IA de Cálculo ∂</h1>', unsafe_allow_html=True)

# Layout principal
col1, col2 = st.columns([2, 1])

# ===== COLUMNA IZQUIERDA: CHAT =====
with col1:
    st.markdown("### 💬 Conversación con tu Tutor")
    
    # Contenedor del chat
    chat_html = '<div class="chat-container">'
    
    if len(st.session_state.historial) == 0:
        chat_html += '''
        <div style="text-align: center; padding: 50px; color: #999;">
            <h3>👋 ¡Hola! Soy tu tutor de Cálculo</h3>
            <p>Puedes preguntarme sobre:</p>
            <ul style="list-style: none; padding: 0;">
                <li>📈 Derivadas e integrales</li>
                <li>📊 Límites y continuidad</li>
                <li>📐 Aplicaciones del cálculo</li>
                <li>🎯 Ejercicios y problemas</li>
            </ul>
            <p><strong>¡Comienza haciendo una pregunta!</strong></p>
        </div>
        '''
    else:
        for i, mensaje in enumerate(st.session_state.historial):
            if mensaje["role"] == "user":
                chat_html += f'<div class="user-message"><strong>Tú:</strong><br>{mensaje["content"]}</div>'
            else:
                chat_html += f'<div class="assistant-message"><strong>🎓 Tutor:</strong><br>{mensaje["content"]}</div>'
    
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    
    # Sección de input
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 Haz tu pregunta")
    
    input_option = st.radio(
        "Modo de entrada:",
        ("✍️ Texto", "🎤 Voz"),
        horizontal=True,
        key="input_mode"
    )
    
    user_input = ""
    procesar_mensaje = False
    
    if input_option == "✍️ Texto":
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            user_input = st.text_input(
                "Escribe aquí:",
                placeholder="Ej: ¿Cómo se calcula la derivada de x²?",
                key=f"text_input_{st.session_state.contador_mensajes}",
                label_visibility="collapsed"
            )
        with col_btn:
            if st.button("📤 Enviar", use_container_width=True):
                if user_input and user_input.strip():
                    procesar_mensaje = True
    else:
        st.info("🎙️ Haz clic para grabar tu pregunta")
        texto_grabado = speech_to_text(
            language='es',
            start_prompt="🔴 Grabar",
            stop_prompt="⏹️ Detener",
            just_once=True,
            use_container_width=False,
            key=f'recorder_{st.session_state.contador_mensajes}'
        )
        
        if texto_grabado:
            user_input = texto_grabado
            procesar_mensaje = True
            st.success(f"✅ Mensaje grabado: {texto_grabado}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Procesar mensaje
    if procesar_mensaje and user_input and user_input.strip():
        # Agregar mensaje del usuario
        st.session_state.historial.append({"role": "user", "content": user_input})
        
        # Obtener respuesta
        with st.spinner("🤔 Procesando tu pregunta..."):
            respuesta = enviar_mensaje(user_input, st.session_state.historial)
        
        # Agregar respuesta al historial
        st.session_state.historial.append({"role": "assistant", "content": respuesta})
        
        # Verificar si se debe mostrar gráfica
        palabras_clave_graficas = [
            "gráfica", "gráfico", "función", "derivada", "integral",
            "límite", "continuidad", "tangente", "área", "curva",
            "visualiza", "dibuja", "muestra", "grafica"
        ]
        
        if any(palabra in user_input.lower() for palabra in palabras_clave_graficas):
            st.session_state.mostrar_grafica = True
            st.session_state.tipo_grafica = user_input
        
        # Generar audio
        mensaje_hash = hashlib.md5(respuesta.encode()).hexdigest()
        audio_base64 = texto_a_voz(respuesta, mensaje_hash)
        st.session_state.audio_actual = audio_base64
        
        # Incrementar contador para forzar recreación de widgets
        st.session_state.contador_mensajes += 1
        
        st.rerun()

# Reproducir audio si existe
if st.session_state.audio_actual:
    st.markdown(f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{st.session_state.audio_actual}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)
    st.session_state.audio_actual = None

# ===== COLUMNA DERECHA: AVATAR Y HERRAMIENTAS =====
with col2:
    st.markdown("### 👨‍🏫 Tu Profesor Virtual")
    
    # Avatar del tutor
    st.markdown("""
    <div class="avatar-container">
        <div class="avatar">∫</div>
        <div class="tutor-info">
            <div class="tutor-name">Dr. Cálculo</div>
            <div class="tutor-specialty">Especialista en Cálculo</div>
            <div class="specialty-list">
                <div class="specialty-item">• Cálculo Diferencial</div>
                <div class="specialty-item">• Cálculo Integral</div>
                <div class="specialty-item">• Límites y Continuidad</div>
                <div class="specialty-item">• Ecuaciones Diferenciales</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs para gráficas y herramientas
    tab1, tab2, tab3 = st.tabs(["📊 Gráficas", "🧮 Calculadora", "📚 Fórmulas"])
    
    with tab1:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        
        if st.session_state.mostrar_grafica:
            fig = crear_grafica_calculo(st.session_state.tipo_grafica)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            if st.button("❌ Ocultar gráfica"):
                st.session_state.mostrar_grafica = False
                st.rerun()
        else:
            st.info("💡 **Pregunta sobre funciones, derivadas o integrales para ver visualizaciones**")
            
            st.markdown("**Ejemplos:**")
            ejemplos = [
                "Muestra la gráfica de una derivada",
                "Visualiza una integral definida",
                "Explica límites con una gráfica"
            ]
            for ej in ejemplos:
                if st.button(f"'{ej}'", use_container_width=True, key=f"ejemplo_{ej}"):
                    st.session_state.historial.append({"role": "user", "content": ej})
                    with st.spinner("Procesando..."):
                        respuesta = enviar_mensaje(ej, st.session_state.historial)
                    st.session_state.historial.append({"role": "assistant", "content": respuesta})
                    st.session_state.mostrar_grafica = True
                    st.session_state.tipo_grafica = ej
                    st.session_state.contador_mensajes += 1
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🧮 Calculadora")
        
        calc_tipo = st.selectbox(
            "Tipo de cálculo:",
            ["Básico", "Derivada", "Integral"]
        )
        
        if calc_tipo == "Básico":
            col_a, col_op, col_b = st.columns([2, 1, 2])
            with col_a:
                num1 = st.number_input("Número 1", value=0.0, format="%.4f")
            with col_op:
                operacion = st.selectbox("Op", ["+", "-", "×", "÷", "^"])
            with col_b:
                num2 = st.number_input("Número 2", value=0.0, format="%.4f")
            
            if st.button("Calcular", use_container_width=True):
                try:
                    if operacion == "+":
                        resultado = num1 + num2
                    elif operacion == "-":
                        resultado = num1 - num2
                    elif operacion == "×":
                        resultado = num1 * num2
                    elif operacion == "÷":
                        resultado = num1 / num2 if num2 != 0 else "Error"
                    elif operacion == "^":
                        resultado = num1 ** num2
                    st.success(f"**Resultado:** {resultado}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif calc_tipo == "Derivada":
            st.info("💡 Pregunta al tutor: '¿Cuál es la derivada de...?'")
        
        else:
            st.info("💡 Pregunta al tutor: '¿Cómo integro...?'")
    
    with tab3:
        st.markdown("### 📚 Fórmulas de Cálculo")
        
        formulas = {
            "Derivadas básicas": [
                "d/dx(xⁿ) = nxⁿ⁻¹",
                "d/dx(eˣ) = eˣ",
                "d/dx(ln x) = 1/x",
                "d/dx(sen x) = cos x",
                "d/dx(cos x) = -sen x"
            ],
            "Integrales básicas": [
                "∫ xⁿ dx = xⁿ⁺¹/(n+1) + C",
                "∫ eˣ dx = eˣ + C",
                "∫ 1/x dx = ln|x| + C",
                "∫ sen x dx = -cos x + C",
                "∫ cos x dx = sen x + C"
            ],
            "Reglas de derivación": [
                "(f+g)' = f' + g'",
                "(fg)' = f'g + fg'",
                "(f/g)' = (f'g - fg')/g²",
                "(f∘g)' = f'(g)·g'"
            ]
        }
        
        categoria = st.selectbox("Categoría:", list(formulas.keys()))
        
        for formula in formulas[categoria]:
            st.markdown(f"• `{formula}`")

# Footer
st.markdown('<div class="footer">Tutor IA de Cálculo • Powered by DeepSeek API • Desarrollado con ❤️ y Streamlit</div>', unsafe_allow_html=True)

# Botón para limpiar historial (en sidebar oculto)
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.historial = []
        st.session_state.mostrar_grafica = False
        st.session_state.tipo_grafica = ""
        st.session_state.audio_actual = None
        st.session_state.contador_mensajes = 0
        st.rerun()
    
    st.markdown("---")
    st.markdown(f"**Mensajes:** {len(st.session_state.historial)}")
    
    if len(st.session_state.historial) > 0:
        st.download_button(
            label="📥 Descargar conversación",
            data="\n\n".join([f"**{m['role'].upper()}:** {m['content']}" for m in st.session_state.historial]),
            file_name="conversacion_calculo.txt",
            mime="text/plain"
        )