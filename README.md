# 🧠 Proyecto S.A.P.I.E.N.S.

## Sistema de Apoyo Personalizado e Inteligente para Estudiantes de la Santo Tomás

------------

## 🧠 Introducción

S.A.P.I.E.N.S. (Sistema de Apoyo Personalizado e Inteligente para Estudiantes de la Santo Tomás) es un prototipo funcional de tutor académico basado en inteligencia artificial generativa, diseñado para apoyar el aprendizaje autónomo, mejorar el desempeño académico y reducir la deserción estudiantil en la Facultad de Ingeniería Electrónica.

El sistema integra técnicas modernas de IA, análisis de necesidades académicas y una arquitectura digital basada en Python, Streamlit y modelos de lenguaje, permitiendo ofrecer acompañamiento inmediato, adaptativo y contextualizado. Diseñado para apoyar a estudiantes de ingeniería en asignaturas fundamentales como:

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

## 🎯 Problema Identificado

Los modelos de tutoría tradicionales presentan limitaciones como:

- Baja disponibilidad de docentes.
- Escasez de acompañamiento personalizado.
- Sobrecarga de asignaturas con alta dificultad.
- Dificultades de los estudiantes para mantener hábitos de estudio efectivos.
- Desmotivación y falta de herramientas de apoyo digital.

Estas situaciones contribuyen al bajo rendimiento y a la deserción estudiantil, especialmente en programas de ingeniería.

------------

## ❓ Pregunta Problema

¿Cómo transformar los modelos de tutoría académica tradicionales mediante IA, para garantizar procesos de aprendizaje más eficaces y adaptados a estudiantes de la Universidad Santo Tomás?


------------


## 🎯 Objetivo del Proyecto

Potenciar el rendimiento académico y la autonomía de los estudiantes mediante la implementación de S.A.P.I.E.N.S., posicionando a la universidad como referente en innovación educativa.

------------

## 🎯 Objetivos Específicos

- Identificar necesidades académicas y factores asociados a la deserción.
- Formular el modelo conceptual del tutor inteligente.
- Desarrollar un Producto Mínimo Viable (PMV) para pruebas piloto.
- Validar usabilidad, pertinencia y adopción por estudiantes reales.
- Integrar recursos académicos institucionales como fuente de conocimiento.

------------

## 🧩 Alcance del Proyecto

Incluye:

- Diseño y desarrollo de un prototipo funcional de tutor IA.
- Personalización basada en perfil y necesidades del estudiante.
- Entorno de interacción inmediato: texto y voz.
- Pruebas piloto con estudiantes tomasinos.
- Integración de explicaciones, ejemplos y recursos educativos.
- Bases para escalabilidad futura a más asignaturas.

Delimitaciones:

- Se construye un PMV (no versión comercial).
- Cubre un número limitado de materias iniciales.
- La calidad depende de la base de conocimientos disponible.
- No reemplaza al tutor humano.
- Sujeto a restricciones éticas y legales (Ley 1581 de 2012).

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
    

------------

## ⚡ Tecnologías Utilizadas

| Tecnología                       | Uso                             |
| -------------------------------- | ------------------------------- |
| **Python 3.x**                   | Lógica principal                |
| **Streamlit**                    | Interfaz de usuario             |
| **DeepSeek API**                 | Motor de IA para tutoría        |
| **gTTS (Google Text-to-Speech)** | Audio de respuestas             |
| **Plotly**                       | Gráficas interactivas           |
| **SymPy**                        | Cálculo simbólico               |
| **NumPy / Math**                 | Operaciones matemáticas         |
| **HTML + CSS**                   | Diseño custom del chat y avatar |

------------

## 🎛️ Componentes Funcionales del Sistema

### 💬 1. Módulo de Conversación (Chat)

Incluye:

- Chat visual con estilos personalizados
- Mensajes usuario/asistente
- Renderizado de fórmulas matemáticas con MathJax
- Sistema de prompts pedagógicos
- Control de historial
- Re-renderización automática

### 🧠 Lógica del Tutor (DeepSeek)

El tutor se comporta según el SYSTEM_PROMPT que creaste:

- Explica paso a paso
- Usa preguntas socráticas
- NO resuelve tareas completas
- Usa LaTeX en todas las fórmulas
- Corrige con amabilidad
- Agrega ejemplos
- Verifica la comprensión
