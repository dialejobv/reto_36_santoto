#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import streamlit as st
import base64
import requests
from gtts import gTTS
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import hashlib
from datetime import datetime
import math
import re
import random

try:
    from streamlit_mic_recorder import speech_to_text
    MIC_RECORDER_AVAILABLE = True
except ImportError:
    MIC_RECORDER_AVAILABLE = False
    st.warning("El reconocimiento de voz no está disponible. Instala: pip install streamlit-mic-recorder")

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    st.warning("La calculadora simbólica no está disponible. Instala: pip install sympy")

# -------------------- Configuración de la página -------------------- 
st.set_page_config(
    page_title="Tutor SAPIENS",
    page_icon="∫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- Configuración de DeepSeek -------------------- 
API_KEY = 'sk-53751d5c6f344a5dbc0571de9f51313e'
API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Sistema de expresiones del avatar (de prueba.py)
AVATAR_EXPRESSIONS = {
    "neutral": {"emoji": "😐", "color": "#667eea", "description": "Neutral"},
    "happy": {"emoji": "😊", "color": "#4CAF50", "description": "Contento"},
    "thinking": {"emoji": "🤔", "color": "#FF9800", "description": "Pensando"},
    "surprised": {"emoji": "😲", "color": "#9C27B0", "description": "Sorprendido"},
    "excited": {"emoji": "🌟", "color": "#FFD700", "description": "Entusiasmado"},
    "explaining": {"emoji": "💡", "color": "#2196F3", "description": "Explicando"},
    "concerned": {"emoji": "😟", "color": "#FF5722", "description": "Preocupado"}
}

def get_ejemplo_palabras(expresion):
    """Retorna ejemplos de palabras para cada expresión"""
    ejemplos = {
        "neutral": ["saludos", "inicio", "hola"],
        "happy": ["gracias", "bien", "perfecto", "excelente"],
        "thinking": ["cómo", "qué", "por qué", "explica"],
        "surprised": ["increíble", "wow", "sorpresa", "asombroso"],
        "excited": ["importante", "clave", "fundamental", "esencial"],
        "explaining": ["derivada", "integral", "límite", "función"],
        "concerned": ["difícil", "problema", "error", "complicado"]
    }
    return ejemplos.get(expresion, [])

# -------------------- Función texto_a_voz mejorada (unificada) --------------------
def texto_a_voz(texto, mensaje_hash):
    try:
        texto_simple = texto

        # 🧹 1. Limpiar Markdown
        texto_simple = re.sub(r'\*\*(.*?)\*\*', r'\1', texto_simple)
        texto_simple = re.sub(r'\*(.*?)\*', r'\1', texto_simple)
        texto_simple = re.sub(r'_(.*?)_', r'\1', texto_simple)
        
        # 🔧 2. FUNCIÓN PARA TRADUCIR CUALQUIER ECUACIÓN
        def traducir_ecuacion_completa(ecuacion):
            # Limpiar la ecuación
            ecuacion = ecuacion.replace('\\[', '').replace('\\]', '')
            ecuacion = ecuacion.replace('\\(', '').replace('\\)', '')
            ecuacion = ecuacion.replace('$', '')
            
            # Traducir símbolos matemáticos comunes
            traducciones = {
                '\\int': ' integral ',
                '\\sum': ' suma ',
                '\\lim': ' límite ',
                '\\frac': ' fracción ',
                '\\sqrt': ' raíz ',
                '\\infty': ' infinito ',
                '\\pi': ' pi ',
                '\\alpha': ' alfa ',
                '\\beta': ' beta ',
                '\\theta': ' theta ',
                '\\lambda': ' lambda ',
                '\\to': ' tiende a ',
                '\\partial': ' parcial ',
                '\\cdot': ' por ',
            }
            
            for simbolo, traduccion in traducciones.items():
                ecuacion = ecuacion.replace(simbolo, traduccion)
            
            # Operadores matemáticos
            ecuacion = ecuacion.replace('+', ' más ')
            ecuacion = ecuacion.replace('-', ' menos ')
            ecuacion = ecuacion.replace('*', ' por ')
            ecuacion = ecuacion.replace('/', ' entre ')
            ecuacion = ecuacion.replace('=', ' igual ')
            ecuacion = ecuacion.replace('^', ' elevado a ')
            ecuacion = ecuacion.replace('_', ' sub ')
            ecuacion = ecuacion.replace('<', ' menor que ')
            ecuacion = ecuacion.replace('>', ' mayor que ')
            
            # Símbolos de agrupación (solo espacios, no pronunciarlos)
            ecuacion = ecuacion.replace('(', ' ').replace(')', ' ')
            ecuacion = ecuacion.replace('[', ' ').replace(']', ' ')
            ecuacion = ecuacion.replace('{', ' ').replace('}', ' ')
            
            # Letras y variables comunes (asegurar espacios)
            ecuacion = re.sub(r'(\b[u v w x y z a b c d e f g h i j k l m n o p q r s t]\b)', r' \1 ', ecuacion)
            
            # Diferenciaciones e integrales específicas
            ecuacion = re.sub(r'\bdu\b', 'd u', ecuacion)
            ecuacion = re.sub(r'\bdv\b', 'd v', ecuacion)
            ecuacion = re.sub(r'\bdx\b', 'd x', ecuacion)
            ecuacion = re.sub(r'\bdy\b', 'd y', ecuacion)
            ecuacion = re.sub(r'\bdt\b', 'd t', ecuacion)
            
            # Exponentes comunes
            ecuacion = re.sub(r'x\^2', 'x al cuadrado', ecuacion)
            ecuacion = re.sub(r'x\^3', 'x al cubo', ecuacion)
            ecuacion = re.sub(r'x\^\{2\}', 'x al cuadrado', ecuacion)
            ecuacion = re.sub(r'x\^\{3\}', 'x al cubo', ecuacion)
            ecuacion = re.sub(r'e\^x', 'e elevado a x', ecuacion)
            ecuacion = re.sub(r'e\^\{x\}', 'e elevado a x', ecuacion)
            
            # Limpiar espacios múltiples
            ecuacion = re.sub(r'\s+', ' ', ecuacion).strip()
            
            return ecuacion

        # 🎯 3. PROCESAR DIFERENTES TIPOS DE ECUACIONES
        
        # Primero: ecuaciones entre \[ \] (display)
        def traducir_ecuacion_display(match):
            ecuacion = match.group(1)
            return f' {traducir_ecuacion_completa(ecuacion)} '
        
        texto_simple = re.sub(r'\\\[(.*?)\\\]', traducir_ecuacion_display, texto_simple)
        
        # Segundo: ecuaciones entre \( \) (inline)
        def traducir_ecuacion_inline(match):
            ecuacion = match.group(1)
            return f' {traducir_ecuacion_completa(ecuacion)} '
        
        texto_simple = re.sub(r'\\\((.*?)\\\)', traducir_ecuacion_inline, texto_simple)
        
        # Tercero: ecuaciones entre $$ (display)
        texto_simple = re.sub(r'\$\$(.*?)\$\$', traducir_ecuacion_display, texto_simple)
        
        # Cuarto: ecuaciones entre $ (inline)
        texto_simple = re.sub(r'\$(.*?)\$', traducir_ecuacion_inline, texto_simple)
        
        # ✂️ 4. Eliminar símbolos LaTeX restantes
        texto_simple = re.sub(r'\\[a-zA-Z]+', '', texto_simple)
        texto_simple = texto_simple.replace('{', ' ').replace('}', ' ')
        
        # 🧼 5. Limpieza final y formato natural
        texto_simple = re.sub(r'\s+', ' ', texto_simple).strip()
        
        # ✨ 6. MEJORAR FLUIDEZ Y PUNTUACIÓN
        texto_simple = texto_simple.replace('.', '. ')
        texto_simple = texto_simple.replace(',', ', ')
        texto_simple = texto_simple.replace('!', '! ')
        texto_simple = texto_simple.replace('?', '? ')
        texto_simple = texto_simple.replace(':', ': ')
        texto_simple = texto_simple.replace(';', '; ')
        
        # Corregir espacios alrededor de puntuación
        texto_simple = re.sub(r'\s+\.', '.', texto_simple)
        texto_simple = re.sub(r'\s+,', ',', texto_simple)
        texto_simple = re.sub(r'\s+!', '!', texto_simple)
        texto_simple = re.sub(r'\s+\?', '?', texto_simple)
        
        texto_simple = re.sub(r'\s+', ' ', texto_simple).strip()
        
        # 🔄 7. CORRECCIONES ESPECÍFICAS
        texto_simple = texto_simple.replace('mas ', 'más ')
        texto_simple = texto_simple.replace('integral de u d v igual u v menos integral de v d u', 
                                          'integral de u d v igual u v menos integral de v d u')
        
        # 🔊 8. Generar audio
        filename = f"audio_{mensaje_hash}.mp3"
        tts = gTTS(text=texto_simple, lang='es', slow=False)
        tts.save(filename)

        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        os.remove(filename)
        return audio_base64

    except Exception as e:
        st.error(f"Error al generar audio: {e}")
        return None

# -------------------- Estilos CSS unificados con avatar dinámico -------------------- 
st.markdown("""
<style>
    :root { --sapiens-color: #00BFFF; }
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-header { font-size: 2.2rem; font-weight: 800; color: var(--sapiens-color); text-align: left; margin-bottom: 0.5rem; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main-sub { color: #374151; margin-bottom: 1rem; }
    .chat-container { background: linear-gradient(to bottom, #ffffff, #f8f9fa); border-radius: 20px; padding: 20px; height: 520px; overflow-y: auto; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08); border: 1px solid rgba(0,0,0,0.04); }
    .user-message { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 16px; border-radius: 16px 16px 4px 16px; margin: 12px 0; max-width: 78%; margin-left: auto; box-shadow: 0 4px 10px rgba(102, 126, 234, 0.25); font-size: 0.98rem; line-height: 1.5; word-wrap: break-word; }
    .assistant-message { background: linear-gradient(135deg, #f5f7fa 0%, #eef6ff 100%); color: #0f172a; padding: 12px 16px; border-radius: 16px 16px 16px 4px; margin: 12px 0; max-width: 78%; margin-right: auto; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06); font-size: 0.98rem; line-height: 1.5; word-wrap: break-word; }
    
    /* AVATAR DINÁMICO CON EXPRESIONES (unificado de prueba.py) */
    .avatar-container { background: linear-gradient(180deg,#ffffff 0%, #fbfdff 100%); border-radius: 16px; padding: 22px; height: 520px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06); border: 1px solid rgba(0,0,0,0.03); display: flex; flex-direction: column; align-items: center; justify-content: flex-start; gap: 12px; }
    
    .avatar-circle { 
        width: 140px; 
        height: 140px; 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: white; 
        font-size: 4rem; 
        font-weight: 800; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
        animation: float 3s ease-in-out infinite;
        position: relative;
    }
    
    .expression-indicator {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(255, 255, 255, 0.9);
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .avatar-expression {
        font-size: 4rem;
        animation: expressionChange 0.5s ease;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-10px) scale(1.05); }
    }
    
    @keyframes expressionChange {
        0% { transform: scale(0.8); opacity: 0.5; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .tutor-info {
        text-align: center;
        color: #2c3e50;
    }
    
    .tutor-name { 
        font-size: 1.25rem; 
        font-weight: 800; 
        color: var(--sapiens-color); 
    }
    
    .tutor-specialty { 
        color: #374151; 
        margin-bottom: 15px;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    
    .specialty-list {
        text-align: left;
        margin-top: 15px;
        padding-left: 20px;
    }
    
    .specialty-item { 
        color: #374151; 
        font-size: 0.9rem; 
        font-weight: 500;
        line-height: 1.6;
        margin: 8px 0;
    }
    
    .input-section { background: white; border-radius: 12px; padding: 14px; margin-top: 16px; box-shadow: 0 6px 18px rgba(2,6,23,0.04); }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 18px; padding: 10px 18px; font-weight: 600; font-size: 0.95rem; transition: all 0.2s ease; }
    .stButton > button:hover { transform: translateY(-2px); }
    .graph-container { background: white; border-radius: 12px; padding: 12px; box-shadow: 0 6px 18px rgba(2,6,23,0.03); }
    .chat-container::-webkit-scrollbar { width: 8px; }
    .chat-container::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #667eea, #764ba2); border-radius: 10px; }
    
    /* --- Estilos de la Calculadora (Desktop) --- */
    .calculator-container {
        padding: 10px;
        background-color: #f7f7f7;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    .calculator-container .stTextInput input[disabled] {
        font-size: 2.1rem;
        font-weight: 700;
        text-align: right;
        background: #e0e5ec;
        color: #333;
        border-radius: 10px;
        padding: 15px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    .calculator-container .stButton > button {
        font-size: 1.2rem;
        font-weight: 600;
        height: 65px; 
        border-radius: 12px;
        background: #ffffff;
        color: #485461;
        border: 1px solid #d1d9e6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .calculator-container .stButton > button:hover {
        background: #f0f2f5;
        color: #000;
        transform: translateY(-2px);
    }
    .calculator-container .stButton > button:active {
        background: #e0e5ec;
        transform: translateY(0);
    }
    .calc-op-button .stButton > button {
        background: #ff9f43; /* Naranja */
        color: white;
    }
    .calc-op-button .stButton > button:hover { background: #e68a2e; }
    .calc-eq-button .stButton > button {
        background: #00BFFF; /* Color Sapiens */
        color: white;
    }
    .calc-eq-button .stButton > button:hover { background: #009acc; }
    .calc-clear-button .stButton > button {
        background: #ff6b6b; /* Rojo */
        color: white;
    }
    .calc-clear-button .stButton > button:hover { background: #e05252; }
    
    /* --- REGLAS PARA MÓVIL --- */
    @media (max-width: 768px) {
        .chat-container { height: 420px; padding: 14px; }
        .avatar-circle { 
            width: 110px; 
            height:110px; 
            font-size:3rem; 
        }
        .avatar-container { height: auto; padding: 16px; }
        
        .calculator-container [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            width: 100% !important; 
        }
        .calculator-container [data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] {
            flex-basis: 50% !important;
            min-width: 50% !important;
            max-width: 50% !important; 
            padding: 4px;
        }
        .calculator-container .stButton > button {
            height: 60px; 
            font-size: 1.1rem;
        }
        .calculator-container .stTextInput input[disabled] {
            font-size: 1.9rem; 
            padding: 12px;
        }
    }
    
    /* Estilos para display de calculadora simbólica */
    .symbolic-display {
        background: #1e1e1e; 
        color: #00ff00; 
        font-family: 'Courier New', monospace; 
        font-size: 1.4rem; 
        padding: 20px; 
        border-radius: 10px; 
        margin: 10px 0; 
        border: 2px solid #444; 
        min-height: 80px; 
        display: flex; 
        align-items: center; 
        justify-content: flex-end;
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

# -------------------- Sistema de prompts y Funciones auxiliares -------------------- 

SYSTEM_PROMPT = """Eres el Profesor SAPIENS, un tutor experto en Cálculo Diferencial e Integral con más de 20 años de experiencia docente. Tu misión es guiar a los estudiantes en su aprendizaje, no hacerles las tareas.
**PERSONALIDAD Y ENFOQUE PEDAGÓGICO:**
- Eres paciente, motivador y clarificador
- Usas analogías y ejemplos de la vida real para explicar conceptos abstractos
- Celebras los esfuerzos y progresos del estudiante
- Corriges errores con amabilidad y constructivamente
- Adaptas tu explicación al nivel del estudiante
**REGLAS FUNDAMENTALES:**
1. **NO RESUELVAS PROBLEMAS COMPLETOS**: Guía al estudiante paso a paso, haz preguntas socráticas
2. **ENFATIZA LA COMPRENSIÓN**: Explica el "por qué" detrás de cada concepto, no solo el "cómo"
3. **PROPORCIONA EJERCICIOS SIMILARES**: Si piden resolver un problema, da uno similar para practicar
4. **VERIFICA LA COMPRENSIÓN**: Pregunta "¿Entiendes por qué hicimos esto?" o "¿Quieres que repita algún paso?"
5. **CONEXIONES CON EL MUNDO REAL**: Muestra aplicaciones prácticas de los conceptos matemáticos
**OBJETIVOS DE ENSEÑANZA:**
1. Explicar conceptos de manera clara y paso a paso 
2. Usar ejemplos prácticos y visuales cuando sea posible 
3. Ser paciente y adaptarte al nivel del estudiante 
4. Proporcionar ejercicios de práctica relevantes 
5. Fomentar el pensamiento crítico y la resolución independiente
**FORMATO MATEMÁTICO OBLIGATORIO:**
- **USAR EXCLUSIVAMENTE FORMATO LaTeX PARA FÓRMULAS:**
  - Ecuaciones en línea: $fórmula$
  - Ecuaciones centradas: $$fórmula$$
  - NO usar corchetes [ ] para fórmulas
  - NO usar formato texto plano para matemáticas
**EJEMPLOS DE FORMATO CORRECTO:**
- Integral por partes: $\int u  dv = uv - \int v  du$
- Derivada: $\frac{d}{dx} f(x)$
- Límite: $\lim_{x \to a} f(x)$
- Ecuación centrada: $$\int x e^x dx = x e^x - e^x + C$$
**ESTRATEGIAS DE ENSEÑANZA:**
- Para límites: "Imagina que te acercas a un punto sin llegar a tocarlo..."
- Para derivadas: "Pensemos en la velocidad instantánea de un coche..."
- Para integrales: "Visualicemos el área bajo una curva como la distancia recorrida..."
- Usa metáforas: "La derivada es como una lupa que nos muestra el comportamiento local..."
- Si el estudiante pregunta sobre gráficas o funciones, menciona que puede visualizarlas en la aplicación
**FORMATO DE RESPUESTAS:**
- Comienza con un saludo cálido: "¡Excelente pregunta!" o "Me alegra que preguntes sobre esto..."
- Divide explicaciones complejas en pasos numerados
- Usa **exclusivamente formato LaTeX** para todas las fórmulas matemáticas
- Termina con una pregunta de verificación o un ejercicio de práctica
**EJEMPLOS DE INTERACCIÓN:**
Estudiante: "Resuélveme esta integral: ∫x² dx"
Tú: "¡Perfecto! Vamos a trabajar juntos en esta integral. Primero, ¿recuerdas la regla básica para integrar potencias de x? Te doy una pista: ¿qué función cuando derivas te da x²? La fórmula general es: $$\int x^n dx = \frac{x^{n+1}}{n+1} + C$$ ¿Quieres intentar aplicarla?"
Estudiante: "No entiendo límites"
Tú: "Los límites pueden ser confusos al principio. Imagina que te acercas a una pared: puedes acercarte mucho, mucho, pero sin llegar a tocarla. Eso es un límite. Matemáticamente: $$\lim_{x \to a} f(x) = L$$ ¿Qué parte específica te causa confusión?"
Estudiante: "¿Cómo derivo sen(x)?"
Tú: "¡Buena pregunta! La derivada del seno es uno de esos resultados importantes. ¿Sabías que viene de la definición fundamental de derivada? $$\frac{d}{dx} \sin(x) = \lim_{h \to 0} \frac{\sin(x+h) - \sin(x)}{h}$$ Pero para ahorrar tiempo, te puedo decir que: $$\frac{d}{dx} \sin(x) = \cos(x)$$ ¿Quieres que exploremos por qué esto es cierto?"
**TEMAS PRINCIPALES:**
- Límites y continuidad
- Derivadas y sus aplicaciones
- Integrales definidas e indefinidas  
- Teorema Fundamental del Cálculo
- Series y sucesiones
- Ecuaciones diferenciales básicas
Recuerda: Tu objetivo es que el estudiante desarrolle confianza y comprensión genuina, no solo obtener respuestas. Sé conciso pero completo en tus explicaciones."""

def determinar_expresion(entrada_usuario, respuesta_bot):
    """Determina la expresión del avatar basado en el contenido de la conversación (de prueba.py)"""
    texto = (entrada_usuario + " " + respuesta_bot).lower()
    
    # Palabras clave para cada expresión
    palabras_felices = ['hola', 'gracias', 'genial', 'excelente', 'perfecto', 'bien', 'entendido', 'correcto', 'fácil']
    palabras_pensamiento = ['?', 'cómo', 'qué', 'por qué', 'cuándo', 'dónde', 'explica', 'piensa', 'calcula', 'deriva', 'integra']
    palabras_sorpresa = ['sorpresa', 'increíble', 'wow', 'asombroso', 'impresionante', 'increíblemente', 'sorprendente']
    palabras_entusiasmo = ['importante', 'clave', 'fundamental', 'esencial', 'crucial', 'interesante']
    palabras_preocupacion = ['difícil', 'complicado', 'problema', 'error', 'no entiendo', 'confuso', 'complejo']
    
    # Lógica para determinar expresión
    if any(palabra in texto for palabra in palabras_felices):
        return "happy"
    elif any(palabra in texto for palabra in palabras_pensamiento):
        return "thinking"
    elif any(palabra in texto for palabra in palabras_sorpresa):
        return "surprised"
    elif any(palabra in texto for palabra in palabras_entusiasmo):
        return "excited"
    elif any(palabra in texto for palabra in palabras_preocupacion):
        return "concerned"
    elif "derivada" in texto or "integral" in texto or "límite" in texto:
        return "explaining"
    else:
        return random.choice(["neutral", "thinking", "explaining"])

def enviar_mensaje(mensaje, historial):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": msg["role"], "content": msg["content"]} for msg in historial]
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
        return f"⚠️ Error de conexión: {err}"
    except Exception as e:
        return f"⚠️ Error inesperado: {str(e)}"

def crear_grafica_calculo(tipo, parametros=None):
    """Crea gráficas específicas para cálculo (unificada)"""
    fig = None
    tipo_lower = (tipo or "").lower()
    
    if "derivada" in tipo_lower or "tangente" in tipo_lower:
        x = np.linspace(-3, 3, 200)
        y = x**3 - 3*x
        x0 = 1; y0 = x0**3 - 3*x0; m = 3*x0**2 - 3
        tangente = m * (x - x0) + y0
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x) = x³ - 3x', line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=x, y=tangente, mode='lines', name='Línea tangente', line=dict(color='#764ba2', dash='dash', width=2)))
        fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='markers', name='Punto de tangencia', marker=dict(size=10, color='red')))
        fig.update_layout(title="Derivada como pendiente de la tangente", template='plotly_white')
        return fig
    
    if "integral" in tipo_lower or "área" in tipo_lower:
        x = np.linspace(0, np.pi, 200)
        y = np.sin(x)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x)=sen(x)', line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', name='Área', fillcolor='rgba(102,126,234,0.25)'))
        fig.update_layout(title="Integral definida como área bajo la curva", template='plotly_white')
        return fig
    
    if "límite" in tipo_lower or "continuidad" in tipo_lower:
        x1 = np.linspace(-3, 1, 100); x2 = np.linspace(1.0001, 3, 100)
        y1 = x1**2; y2 = x2 + 1
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x1, y=y1, mode='lines', name='f(x) para x < 1', line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=x2, y=y2, mode='lines', name='f(x) para x > 1', line=dict(color='#764ba2', width=3)))
        fig.add_trace(go.Scatter(x=[1], y=[1], mode='markers', name='Límite por la izquierda', marker=dict(size=10, color='#667eea')))
        fig.add_trace(go.Scatter(x=[1], y=[2], mode='markers', name='Límite por la derecha', marker=dict(size=10, color='#764ba2')))
        fig.update_layout(title="Análisis de límites y continuidad", template='plotly_white')
        return fig
    
    if "función" in tipo_lower or "gráfica" in tipo_lower:
        x = np.linspace(-2*np.pi, 2*np.pi, 300)
        y = np.sin(x)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x) = sen(x)', line=dict(color='#667eea', width=3)))
        fig.update_layout(title="Función trigonométrica: sen(x)", template='plotly_white')
        return fig
    
    # Default gráfica
    x = np.linspace(-4, 4, 200); y = x**2
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x) = x²', line=dict(color='#667eea', width=3)))
    fig.update_layout(title="Gráfica de una función cuadrática", template='plotly_white')
    return fig 

# -------------------- Inicializar el estado de la sesión -------------------- 
if "historial" not in st.session_state:
    st.session_state.historial = []
if "mostrar_grafica" not in st.session_state:
    st.session_state.mostrar_grafica = False
if "tipo_grafica" not in st.session_state:
    st.session_state.tipo_grafica = ""
if "audio_actual" not in st.session_state:
    st.session_state.audio_actual = None
if "audio_generated" not in st.session_state:
    st.session_state.audio_generated = False
if "audio_cleanup_done" not in st.session_state:
    st.session_state.audio_cleanup_done = False
if "contador_mensajes" not in st.session_state:
    st.session_state.contador_mensajes = 0
if "last_voice_processed" not in st.session_state:
    st.session_state.last_voice_processed = None
if "avatar_expression" not in st.session_state:
    st.session_state.avatar_expression = "neutral"

# --- INICIALIZACIÓN DE ESTADO PARA LA CALCULADORA --- 
if 'calc_display' not in st.session_state:
    st.session_state.calc_display = "0"
if 'calc_operand1' not in st.session_state:
    st.session_state.calc_operand1 = 0
if 'calc_operation' not in st.session_state:
    st.session_state.calc_operation = None
if 'calc_new_input' not in st.session_state:
    st.session_state.calc_new_input = True

# Nuevo estado para la calculadora simbólica
if 'calc_mode' not in st.session_state:
    st.session_state.calc_mode = "básica"  # "básica" o "simbólica"
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []
if 'calc_symbolic_input' not in st.session_state:
    st.session_state.calc_symbolic_input = ""

# -------------------- Lógica de la Calculadora Básica -------------------- 
def handle_digit(digit):
    """Añade un dígito a la pantalla"""
    if st.session_state.calc_new_input:
        st.session_state.calc_display = digit
        st.session_state.calc_new_input = False
    elif st.session_state.calc_display == "0":
        st.session_state.calc_display = digit
    else:
        st.session_state.calc_display += digit

def handle_decimal():
    """Añade un punto decimal"""
    if st.session_state.calc_new_input:
        st.session_state.calc_display = "0."
        st.session_state.calc_new_input = False
    elif "." not in st.session_state.calc_display:
        st.session_state.calc_display += "."

def handle_clear():
    """Limpia la calculadora (AC)"""
    st.session_state.calc_display = "0"
    st.session_state.calc_operand1 = 0
    st.session_state.calc_operation = None
    st.session_state.calc_new_input = True
    st.session_state.calc_symbolic_input = ""

def handle_operation(op):
    """Maneja los operadores +, -, ×, ÷"""
    try:
        operand2 = float(st.session_state.calc_display)

        if st.session_state.calc_operation and not st.session_state.calc_new_input:
            handle_equals()

        st.session_state.calc_operand1 = float(st.session_state.calc_display)
        st.session_state.calc_operation = op
        st.session_state.calc_new_input = True

    except ValueError:
        st.session_state.calc_display = "Error"
        st.session_state.calc_new_input = True

def handle_unary_operation(op):
    """Maneja operaciones de un solo número (√, x², 1/x, ±)"""
    try:
        val = float(st.session_state.calc_display)
        if op == '√':
            if val < 0:
                st.session_state.calc_display = "Error"
            else:
                st.session_state.calc_display = str(math.sqrt(val))
        elif op == 'x²':
            st.session_state.calc_display = str(val ** 2)
        elif op == '1/x':
            if val == 0:
                st.session_state.calc_display = "Error"
            else:
                st.session_state.calc_display = str(1 / val)
        elif op == '±':
            st.session_state.calc_display = str(val * -1)

        st.session_state.calc_new_input = True
    except ValueError:
        st.session_state.calc_display = "Error"

    st.session_state.calc_operation = None

def handle_equals():
    """Resuelve la operación (=)"""
    try:
        operand2 = float(st.session_state.calc_display)

        if st.session_state.calc_operation == "÷":
            if operand2 == 0:
                st.session_state.calc_display = "Error"
            else:
                st.session_state.calc_display = str(st.session_state.calc_operand1 / operand2)
        elif st.session_state.calc_operation == "×":
            st.session_state.calc_display = str(st.session_state.calc_operand1 * operand2)
        elif st.session_state.calc_operation == "-":
            st.session_state.calc_display = str(st.session_state.calc_operand1 - operand2)
        elif st.session_state.calc_operation == "+":
            st.session_state.calc_display = str(st.session_state.calc_operand1 + operand2)

    except ValueError:
        st.session_state.calc_display = "Error"
    except Exception:
        st.session_state.calc_display = "Error"

    try:
        val = float(st.session_state.calc_display)
        st.session_state.calc_display = str(round(val, 10))
    except:
        pass

    st.session_state.calc_operation = None
    st.session_state.calc_new_input = True
    try:
        st.session_state.calc_operand1 = float(st.session_state.calc_display)
    except ValueError:
        st.session_state.calc_operand1 = 0

# -------------------- Lógica de la Calculadora Simbólica --------------------
def calcular_operacion_simbolica():
    """Calcular operación usando sympy para cálculos simbólicos"""
    if not SYMPY_AVAILABLE:
        st.session_state.calc_display = "SymPy no disponible"
        return
        
    try:
        import sympy as sp
        from sympy import symbols, integrate, diff, solve, limit, sin, cos, tan, log, exp, sqrt, pi, oo
        
        expr = st.session_state.calc_symbolic_input.strip()
        if not expr:
            st.session_state.calc_display = "Ingrese expresión"
            return
        
        # Definir símbolos comunes
        x, y, z = symbols('x y z')
        
        # Detectar tipo de operación
        if '∫' in expr or 'integral' in expr.lower():
            # Integral
            expr_clean = expr.replace('∫', '').replace('integral', '').replace('dx', '').replace('dy', '').replace('dz', '')
            try:
                func = sp.sympify(expr_clean)
                result = integrate(func, x)
                st.session_state.calc_display = f"∫{expr_clean}dx = {result} + C"
                st.session_state.calc_history.append({'input': expr, 'result': f"∫{expr_clean}dx = {result} + C"})
            except:
                st.session_state.calc_display = "Error en integral"
        
        elif 'd/d' in expr or 'derivada' in expr.lower():
            # Derivada
            expr_clean = expr.replace('d/dx', '').replace('d/dy', '').replace('derivada', '')
            try:
                func = sp.sympify(expr_clean)
                result = diff(func, x)
                st.session_state.calc_display = f"d/dx({expr_clean}) = {result}"
                st.session_state.calc_history.append({'input': expr, 'result': f"d/dx({expr_clean}) = {result}"})
            except:
                st.session_state.calc_display = "Error en derivada"
        
        elif 'lim' in expr.lower() or 'límite' in expr.lower():
            # Límite
            try:
                if '->' in expr:
                    parts = expr.split('->')
                    func = sp.sympify(parts[0].replace('lim', '').replace('límite', ''))
                    point = sp.sympify(parts[1])
                    result = limit(func, x, point)
                    st.session_state.calc_display = f"lim({func}, x->{point}) = {result}"
                else:
                    st.session_state.calc_display = "Usar: lim(f(x), x->a)"
            except:
                st.session_state.calc_display = "Error en límite"
        
        elif 'solve' in expr.lower() or '=' in expr:
            # Ecuación
            try:
                if '=' in expr:
                    equation = expr.replace('=', '-(') + ')'
                    solutions = solve(sp.sympify(equation), x)
                    st.session_state.calc_display = f"Soluciones: {solutions}"
                else:
                    st.session_state.calc_display = "Usar: solve(ecuación=0)"
            except:
                st.session_state.calc_display = "Error resolviendo ecuación"
        
        else:
            # Expresión algebraica simple
            try:
                result = sp.simplify(expr)
                st.session_state.calc_display = f"{expr} = {result}"
                st.session_state.calc_history.append({'input': expr, 'result': f"{expr} = {result}"})
            except:
                st.session_state.calc_display = f"Error: {expr}"
                
    except ImportError:
        st.session_state.calc_display = "Instala sympy: pip install sympy"
    except Exception as e:
        st.session_state.calc_display = f"Error: {str(e)}"

def agregar_simbolo(simbolo):
    """Agregar símbolo a la entrada simbólica"""
    st.session_state.calc_symbolic_input += simbolo
    if st.session_state.calc_mode == "simbólica":
        st.session_state.calc_display = st.session_state.calc_symbolic_input

def cambiar_modo(modo):
    """Cambiar entre modo básico y simbólico"""
    st.session_state.calc_mode = modo
    handle_clear()

# -------------------- Título principal -------------------- 
st.markdown('<div class="main-header">∫ Tutor <span style="color:var(--sapiens-color)">Sapiens</span></div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">Tu asistente de Cálculo con Avatar Dinámico — explica paso a paso y con visualizaciones</div>', unsafe_allow_html=True)

# -------------------- Layout principal -------------------- 
col1, col2 = st.columns([2, 1])

# ===== COLUMNA IZQUIERDA: CHAT ===== 
with col1:
    st.markdown("### 💬 Conversación con tu Tutor")
    
    # Contenedor del chat
    chat_html = '<div class="chat-container">'
    if len(st.session_state.historial) == 0:
        chat_html += '''
        <div style="text-align: center; padding: 50px; color: #777;">
            <h3>👋 ¡Hola! Soy <strong style="color:var(--sapiens-color)">SAPIENS</strong>.</h3>
            <p>Pregúntame sobre derivadas, integrales, límites y más. ¡Usa el micrófono o escribe!</p>
            <p><strong>Comienza haciendo una pregunta.</strong></p>
        </div>
        '''
    else:
        for i, mensaje in enumerate(st.session_state.historial):
            if mensaje["role"] == "user":
                chat_html += f'<div class="user-message"><strong>Tú:</strong><br>{mensaje["content"]}</div>'
            else:
                contenido = mensaje["content"]
                chat_html += f'<div class="assistant-message"><strong>🎓 SAPIENS:</strong><br>{contenido}</div>'
    
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # MATHJAX PARA RENDERIZAR FÓRMULAS
    st.markdown("""
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
    MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']],
            processEscapes: true
        },
        svg: {
            fontCache: 'global'
        }
    };
    </script>
    """, unsafe_allow_html=True)

    # Entrada de mensajes
    input_option = st.radio("Modo de entrada:", ("✍️ Texto", "🎤 Voz"), horizontal=True, key="input_mode")

    user_input = ""
    procesar_mensaje = False

    if input_option == "✍️ Texto":
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            user_input = st.text_input("Escribe aquí:", placeholder="Haz tu pregunta aquí", key=f"text_input_{st.session_state.contador_mensajes}", label_visibility="collapsed")
        with col_btn:
            if st.button("📤 Enviar", use_container_width=True):
                if user_input and user_input.strip():
                    procesar_mensaje = True
    else:
        if not MIC_RECORDER_AVAILABLE:
            st.error("El reconocimiento de voz no está disponible. Instala: pip install streamlit-mic-recorder")
        else:
            st.info("🎙️ Pulsa el botón de grabación y haz tu pregunta.")
            texto_grabado = speech_to_text(language='es', start_prompt="🔴 Grabar", stop_prompt="⏹️ Detener", just_once=True, use_container_width=False, key=f'recorder_{st.session_state.contador_mensajes}')
            if texto_grabado:
                if st.session_state.last_voice_processed != texto_grabado:
                    user_input = texto_grabado
                    procesar_mensaje = True
                    st.session_state.last_voice_processed = texto_grabado
                    st.success(f"✅ Mensaje grabado: {texto_grabado}")

    # Procesamiento de mensajes - VERSIÓN CORREGIDA
    if procesar_mensaje and user_input and user_input.strip():
        # Agregar mensaje del usuario al historial
        st.session_state.historial.append({"role": "user", "content": user_input, "time": datetime.now().strftime("%H:%M")})
        
        # Obtener respuesta del tutor
        with st.spinner("🤔 SAPIENS está procesando tu pregunta..."):
            respuesta = enviar_mensaje(user_input, st.session_state.historial)
        
        # Determinar expresión del avatar (NUEVA FUNCIONALIDAD)
        st.session_state.avatar_expression = determinar_expresion(user_input, respuesta)
        
        # Agregar respuesta al historial
        st.session_state.historial.append({"role": "assistant", "content": respuesta, "time": datetime.now().strftime("%H:%M")})
        
        # Lógica para mostrar gráfica
        palabras_clave_graficas = ["gráfica", "gráfico", "función", "derivada", "integral", "límite", "continuidad", "tangente", "área", "curva", "visualiza", "dibuja", "muestra", "grafica"]
        if any(palabra in user_input.lower() for palabra in palabras_clave_graficas):
            st.session_state.mostrar_grafica = True
            st.session_state.tipo_grafica = user_input
            
        # ✅ GENERAR AUDIO PARA CADA RESPUESTA - ESTO ES CLAVE
        mensaje_hash = hashlib.md5(respuesta.encode()).hexdigest()
        audio_base64 = texto_a_voz(respuesta, mensaje_hash)
        
        if audio_base64:
            st.session_state.audio_actual = audio_base64
            st.session_state.audio_generated = True  # Nueva variable de estado
        else:
            st.session_state.audio_actual = None
            st.session_state.audio_generated = False
        
        st.session_state.contador_mensajes += 1
        st.rerun()

# ✅ REPRODUCIR AUDIO - VERSIÓN MEJORADA
if st.session_state.get('audio_actual') and st.session_state.get('audio_generated', False):
    # Usar un contenedor específico para el audio
    audio_html = f"""
    <div style="display: none;">
        <audio autoplay id="audioPlayer">
            <source src="data:audio/mp3;base64,{st.session_state.audio_actual}" type="audio/mp3">
        </audio>
    </div>
    <script>
        document.getElementById('audioPlayer').play().catch(function(error) {{
            console.log('Error al reproducir audio:', error);
        }});
    </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    
    # Mostrar indicador de que se está reproduciendo audio
    st.markdown("""
    <div style="text-align: center; padding: 5px; background: #e8f5e8; border-radius: 5px; margin: 5px 0;">
        <small>🔊 Reproduciendo respuesta...</small>
    </div>
    """, unsafe_allow_html=True)
    
    #  LIMPIAR SOLO DESPUÉS de confirmar que se mostró
    # Usar un pequeño delay para asegurar la reproducción
    if "audio_cleanup_done" not in st.session_state:
        st.session_state.audio_cleanup_done = False
    
    if not st.session_state.audio_cleanup_done:
        st.session_state.audio_cleanup_done = True
    else:
        # Limpiar el estado de audio para la próxima respuesta
        st.session_state.audio_actual = None
        st.session_state.audio_generated = False
        st.session_state.audio_cleanup_done = False

# ===== COLUMNA DERECHA: AVATAR DINÁMICO Y HERRAMIENTAS ===== 
with col2:
    st.markdown("### 👨‍🏫 Tu Profesor Virtual")
    
    # AVATAR DINÁMICO CON EXPRESIONES (unificado de prueba.py)
    # Obtener configuración de la expresión actual
    expresion_actual = AVATAR_EXPRESSIONS[st.session_state.avatar_expression]
    
    st.markdown(f"""
    <div class="avatar-container">
        <div class="expression-indicator" style="color: {expresion_actual['color']};">
            {expresion_actual['description']}
        </div>
        <div class="avatar-circle" style="background: linear-gradient(135deg, {expresion_actual['color']} 0%, {expresion_actual['color']}80 100%);">
            <div class="avatar-expression">{expresion_actual['emoji']}</div>
        </div>
        <div class="tutor-info">
            <div class="tutor-name">Dr. SAPIENS</div>
            <div class="tutor-specialty">
                <span class="status-dot" style="background-color: {expresion_actual['color']};"></span>
                Estado: {expresion_actual['description']}
            </div>
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
    tab1, tab2, tab3 = st.tabs(["📊 Gráficas", "🧮 Calculadora", "🎭 Expresiones"])

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
            st.markdown("**Ejemplos de temas:**")
            ejemplos = ["Muestra la gráfica de una derivada", "Visualiza una integral definida", "Explica límites con una gráfica"]
            for ej in ejemplos:
                if st.button(f"'{ej}'", use_container_width=True, key=f"ejemplo_{ej}"):
                    st.session_state.historial.append({"role": "user", "content": ej})
                    with st.spinner("Procesando..."):
                        respuesta = enviar_mensaje(ej, st.session_state.historial)
                    st.session_state.historial.append({"role": "assistant", "content": respuesta})
                    st.session_state.mostrar_grafica = True
                    st.session_state.tipo_grafica = ej
                    # Actualizar expresión del avatar
                    st.session_state.avatar_expression = determinar_expresion(ej, respuesta)
                    st.session_state.contador_mensajes += 1
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PESTAÑA DE CALCULADORA MEJORADA ---
    with tab2:
        st.markdown("### 🧮 Calculadora Científica")
        
        # Selector de modo
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔢 Modo Básico", use_container_width=True, 
                        type="primary" if st.session_state.get('calc_mode', 'básica') == "básica" else "secondary"):
                st.session_state.calc_mode = "básica"
                handle_clear()
        with col2:
            if st.button("∫ Modo Simbólico", use_container_width=True,
                        type="primary" if st.session_state.get('calc_mode', 'básica') == "simbólica" else "secondary"):
                st.session_state.calc_mode = "simbólica"
                handle_clear()
        
        # Display principal
        st.markdown(f"""
        <div class="symbolic-display">
            {st.session_state.calc_display}
        </div>
        """, unsafe_allow_html=True)
        
        # Diferentes interfaces según el modo
        if st.session_state.get('calc_mode', 'básica') == "básica":
            # 🧮 INTERFAZ CALCULADORA BÁSICA
            st.markdown("#### Calculadora Básica")
            
            # Fila 1: Operaciones científicas y Clear
            cols = st.columns([1, 1, 1, 1])
            with cols[0]:
                st.button("√", on_click=handle_unary_operation, args=("√",), use_container_width=True)
            with cols[1]:
                st.button("x²", on_click=handle_unary_operation, args=("x²",), use_container_width=True)
            with cols[2]:
                st.button("1/x", on_click=handle_unary_operation, args=("1/x",), use_container_width=True)
            with cols[3]:
                st.button("C", on_click=handle_clear, use_container_width=True, type="secondary")

            # Filas de números y operaciones
            cols = st.columns(4)
            cols[0].button("7", on_click=handle_digit, args=("7",), use_container_width=True)
            cols[1].button("8", on_click=handle_digit, args=("8",), use_container_width=True)
            cols[2].button("9", on_click=handle_digit, args=("9",), use_container_width=True)
            cols[3].button("÷", on_click=handle_operation, args=("÷",), use_container_width=True)

            cols = st.columns(4)
            cols[0].button("4", on_click=handle_digit, args=("4",), use_container_width=True)
            cols[1].button("5", on_click=handle_digit, args=("5",), use_container_width=True)
            cols[2].button("6", on_click=handle_digit, args=("6",), use_container_width=True)
            cols[3].button("×", on_click=handle_operation, args=("×",), use_container_width=True)

            cols = st.columns(4)
            cols[0].button("1", on_click=handle_digit, args=("1",), use_container_width=True)
            cols[1].button("2", on_click=handle_digit, args=("2",), use_container_width=True)
            cols[2].button("3", on_click=handle_digit, args=("3",), use_container_width=True)
            cols[3].button("−", on_click=handle_operation, args=("-",), use_container_width=True)

            cols = st.columns(4)
            cols[0].button("±", on_click=handle_unary_operation, args=("±",), use_container_width=True)
            cols[1].button("0", on_click=handle_digit, args=("0",), use_container_width=True)
            cols[2].button(".", on_click=handle_decimal, use_container_width=True)
            cols[3].button("+", on_click=handle_operation, args=("+",), use_container_width=True)

            st.button("=", on_click=handle_equals, use_container_width=True)
            
        else:
            # ∫ INTERFAZ CALCULADORA SIMBÓLICA
            st.markdown("#### Calculadora Simbólica")
            
            # Input para expresiones
            col_input, col_calc = st.columns([3, 1])
            with col_input:
                user_input = st.text_input(
                    "Expresión matemática:",
                    value=st.session_state.get('calc_symbolic_input', ''),
                    placeholder="Ej: x^2 + 3x - 5, d/dx(sin(x)), ∫x^2 dx",
                    key="symbolic_input",
                    label_visibility="collapsed"
                )
                if user_input != st.session_state.get('calc_symbolic_input', ''):
                    st.session_state.calc_symbolic_input = user_input
                    st.session_state.calc_display = user_input
            
            with col_calc:
                st.button("Calcular", on_click=calcular_operacion_simbolica, use_container_width=True)
                st.button("Limpiar", on_click=handle_clear, use_container_width=True, type="secondary")
            
            # Teclado matemático para modo simbólico
            st.markdown("##### Teclado Matemático")
            
            # Fila 1: Operadores básicos
            cols = st.columns(6)
            operadores = [("+", "+"), ("-", "-"), ("×", "*"), ("/", "/"), ("^", "^"), ("=", "=")]
            for i, (display, valor) in enumerate(operadores):
                with cols[i]:
                    st.button(display, on_click=agregar_simbolo, args=(valor,), use_container_width=True)
            
            # Fila 2: Símbolos y funciones
            cols = st.columns(6)
            simbolos = [("π", "pi"), ("θ", "theta"), ("√", "sqrt("), ("(", "("), (")", ")"), ("x", "x")]
            for i, (display, valor) in enumerate(simbolos):
                with cols[i]:
                    st.button(display, on_click=agregar_simbolo, args=(valor,), use_container_width=True)
            
            # Fila 3: Cálculo
            cols = st.columns(6)
            calculo = [("d/dx", "d/dx("), ("∫", "∫"), ("lim", "lim("), ("sin", "sin("), ("cos", "cos("), ("log", "log(")]
            for i, (display, valor) in enumerate(calculo):
                with cols[i]:
                    st.button(display, on_click=agregar_simbolo, args=(valor,), use_container_width=True)
            
            # Ejemplos rápidos
            st.markdown("##### Ejemplos Rápidos")
            ej_cols = st.columns(4)
            ejemplos = [
                ("Derivar x²", "d/dx(x^2)"),
                ("Integral x²", "∫x^2"),
                ("Resolver x²=4", "x^2-4=0"),
                ("Simplificar", "x^2 + 2x^2")
            ]
            
            for i, (nombre, ejemplo) in enumerate(ejemplos):
                with ej_cols[i]:
                    if st.button(nombre, use_container_width=True):
                        st.session_state.calc_symbolic_input = ejemplo
                        st.session_state.calc_display = ejemplo
                        calcular_operacion_simbolica()
        
        # Historial (compartido entre ambos modos)
        if st.session_state.get('calc_history', []):
            st.markdown("##### Historial")
            for i, calc in enumerate(reversed(st.session_state.calc_history[-3:])):
                st.text(f"{len(st.session_state.calc_history)-i}. {calc['input']} → {calc['result']}")
        
        st.markdown("---")
        st.info("💡 **Modo Básico:** Operaciones numéricas • **Modo Simbólico:** Cálculo con variables")

    # --- PESTAÑA DE EXPRESIONES DEL AVATAR ---
    with tab3:
        st.markdown("### 🎭 Expresiones del Avatar")
        
        st.markdown("**El avatar cambia automáticamente según la conversación:**")
        
        for expr_key, expr_info in AVATAR_EXPRESSIONS.items():
            col_expr, col_desc = st.columns([1, 3])
            with col_expr:
                st.markdown(f"<div style='font-size: 2rem; text-align: center;'>{expr_info['emoji']}</div>", unsafe_allow_html=True)
            with col_desc:
                st.markdown(f"**{expr_info['description']}**")
                st.markdown(f"*Aparece con palabras como: {', '.join(get_ejemplo_palabras(expr_key))}*")
        
        st.markdown("---")
        st.markdown("💡 **Consejo:** El avatar reacciona automáticamente a tu conversación")
        
        st.markdown("---")
        st.markdown(f"**Expresión actual:** {expresion_actual['description']}")
        if st.session_state.avatar_expression in ["happy", "excited"]:
            st.balloons()  # Celebración visual cuando está feliz

# -------------------- Footer y sidebar -------------------- 
st.markdown('<div class="footer">Tutor IA de Cálculo con Avatar Dinámico • Powered by DeepSeek API • Desarrollado con Streamlit</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.historial = []
        st.session_state.mostrar_grafica = False
        st.session_state.tipo_grafica = ""
        st.session_state.audio_actual = None
        st.session_state.contador_mensajes = 0
        st.session_state.last_voice_processed = None
        st.session_state.avatar_expression = "neutral"  # Reset avatar expression
        handle_clear() # Limpiar la calculadora también
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Mensajes en Historial:** {len(st.session_state.historial)}")
    st.markdown(f"**Expresión actual:** {AVATAR_EXPRESSIONS[st.session_state.avatar_expression]['description']}")
    
    if len(st.session_state.historial) > 0:
        st.download_button(
            label="📥 Descargar conversación",
            data="\n\n".join([f"**{m['role'].upper()}:** {m['content']}" for m in st.session_state.historial]),
            file_name="conversacion_calculo.txt",
            mime="text/plain"
        )