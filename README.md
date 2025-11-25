# 🧠 Proyecto S.A.P.I.E.N.S.

## Sistema de Apoyo Personalizado e Inteligente para Estudiantes de la Santo Tomás

------------

## 🧠 Introducción

S.A.P.I.E.N.S. (Sistema de Apoyo Personalizado e Inteligente para Estudiantes de la Santo Tomás) es un tutor virtual de cálculo impulsado por inteligencia artificial generativa, diseñado para apoyar a estudiantes de ingeniería en asignaturas fundamentales como:

- Cálculo diferencial
- Cálculo integral
- Límites y continuidad
- Ecuaciones diferenciales
- Conceptos matemáticos básicos

El sistema provee:

✨ Explicaciones paso a paso
✨ Conversación en lenguaje natural
✨ Entrada por texto y por voz
✨ Visualizaciones interactivas con Plotly
✨ Generación automática de audio con gTTS
✨ Calculadora básica y simbólica con SymPy
✨ Un avatar animado para una experiencia más humana

Todo integrado en una interfaz construida con Streamlit, conectada a la API de DeepSeek, con un modelo pedagógico diseñado para fomentar comprensión y autonomía.

------------

## 🎯 Objetivo del Proyecto

Desarrollar un tutor inteligente académico para Cálculo, accesible, usable y educativo, alineado con la transformación digital educativa de la Universidad Santo Tomás.

------------

## 🏗️ Arquitectura General

### 🔧 Diagrama de Arquitectura Técnica

    flowchart TD
        User["👤 Estudiante"] --> UI["🖥️ Interfaz Streamlit"]
        UI --> ChatBox["💬 Chat (HTML + CSS personalizado)"]
        UI --> Voice["🎤 speech_to_text (micrófono)"]
        UI --> Calculator["🧮 Calculadora (básica + simbólica)"]
        UI --> Graphs["📊 Gráficas Plotly"]
        
        ChatBox --> Backend["⚙️ Backend Python"]
        Voice --> Backend
        Calculator --> Backend
    
        Backend --> DeepSeek["🧠 DeepSeek API"]
        Backend --> TTS["🔊 gTTS\n(Texto → Voz)"]
    
        DeepSeek --> Backend
        TTS --> UI
        Backend --> UI
    
