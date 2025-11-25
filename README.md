# 🧠 Proyecto S.A.P.I.E.N.S.

## Sistema de Apoyo Personalizado e Inteligente para Estudiantes de la Santo Tomás

------------

##  Introducción

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

![Image](https://github.com/user-attachments/assets/2f8d3671-0ce9-4c14-9b18-33f797690a22)
>- Interfaz Tutor Sapiens


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

![Image](https://github.com/user-attachments/assets/41e666c0-2e5c-4d31-adc7-32963bba07cc)
>- Entrada de texto  Sapiens

### 🧠 Lógica del Tutor (DeepSeek)

El tutor se comporta según el SYSTEM_PROMPT que se creó:

- Explica paso a paso
- Usa preguntas socráticas
- NO resuelve tareas completas
- Usa LaTeX en todas las fórmulas
- Corrige con amabilidad
- Agrega ejemplos
- Verifica la comprensión

------------

### 🎤 2. Entrada por Voz

- Integrada mediante streamlit_mic_recorder
- Convierte voz → texto
- Detecta última grabación procesada
- Previene duplicados

Es decir, el estudiante puede hablar y SAPIENS responde ¡como un profesor real!

![Image](https://github.com/user-attachments/assets/09b8336f-a2a9-4daa-a30d-6678491fcb73)
>- Entrada por voz  Sapiens
------------

### 🔊 3. Generación de Audio (TTS)

Tu función texto_a_voz():

✔️ Limpia Markdown
✔️ Traduce ecuaciones LaTeX a lenguaje natural
✔️ Convierte texto → audio .mp3
✔️ Lo reinyecta en la UI
✔️ Reproduce automáticamente

------------

### 📊 4. Gráficas Automáticas

Si el usuario pide cosas como:

- "muéstrame la gráfica de una derivada"
- "visualiza un límite"
- "enséñame el área bajo la curva"

→ Streamlit genera:

- Derivadas con tangente
- Integrales como área
- Límites laterales
- Funciones básicas

Con Plotly, completamente interactivo.

![Image](https://github.com/user-attachments/assets/6d979f24-b5d1-4253-8ea3-425e7e2f778a)
>- Generación de gráficas  Sapiens
------------

### 🧮 5. Calculadora Doble (Básica + Simbólica)

Incluye:

### ✨ Calculadora Básica

- Suma, resta, multiplicación, división
- Raíz, cuadrado, inverso
- Cambiar signo
- Redondeos y manejo de errores

![Image](https://github.com/user-attachments/assets/b5967476-e59c-4480-a5ae-6e610788a72c)
>- Calculadora básica Sapiens

### ✨ Calculadora Simbólica

- Derivadas
- Integrales
- Límites
- Ecuaciones
- Simplificación
- Funciones trigonométricas
- π, e, raíces, variables, etc.

Todo respaldado por SymPy.

![Image](https://github.com/user-attachments/assets/98733ffa-2b12-424c-9514-3f1db893e08d)
>- Calculadora simbólica Sapiens
------------

### 🧑‍🏫 6. Avatar Animado

Con CSS → animación suave y elegante:

- Hace un "pulso" animado
- Representa al Prof. S.A.P.I.E.N.S
- Da identidad al tutor

------------

## 🧪 Ejemplo de Flujo de Uso

1️⃣ El usuario inicia y ve el avatar animado

2️⃣ Pregunta: “¿Cómo derivo $x^3$?”

3️⃣ SAPIENS responde paso a paso

4️⃣ El usuario pide “Muéstrame la gráfica”

5️⃣ Se genera visualización Plotly

6️⃣ El usuario presiona el micrófono y pregunta por voz

7️⃣ La respuesta se reproduce en audio

------------

## 🔮 Impacto Esperado

- Reducción de deserción estudiantil.
- Mejora en el rendimiento académico.
- Tutorías accesibles 24/7.
- Acompañamiento personalizado según necesidades del estudiante.
- Alineación con los ODS 4, 9 y 16.

------------


### 🚀 Ventaja Competitiva y Especialización

## 🔍 Ventaja Competitiva y Enfoque Especializado (S.A.P.I.E.N.S. vs. IA Genérica)

El mercado de tutores virtuales está dominado por modelos de lenguaje generalistas (LLMs). S.A.P.I.E.N.S. se diferencia radicalmente al ofrecer una solución altamente especializada, funcional y diseñada con ingeniería de sistemas:

| Característica | S.A.P.I.E.N.S. (Enfoque Especializado) | IA Genérica (ChatGPT, Bard, etc.) |
|---|---|---|
| **Dominio** | Tutor Exclusivo de Cálculo Diferencial e Integral. El prompt del sistema y los filtros están ajustados para **precisión matemática, pedagogía universitaria y notación formal (LaTeX)**. | Tutor generalista con enfoque amplio. La precisión puede variar en problemas matemáticos complejos o ambiguos, requiriendo *debugging* por parte del usuario. |
| **Precisión Matemática** | Integración del motor **SymPy (Symbolic Python)** en la calculadora. Esto permite realizar cálculo simbólico exacto (derivadas, integrales, simplificación) y visualizar resultados con el mismo nivel de rigor que WolframAlpha. | Depende únicamente de la red neuronal, lo que puede llevar a errores de **alucinación** o imprecisión en las operaciones. |
| **Experiencia de Usuario (UX)** | Interfaz nativa de **Streamlit** optimizada, complementada con entrada por voz (*speech-to-text*) y salida de respuesta en audio (gTTS). La interacción es **multimodal e inmersiva**. | Principalmente entrada y salida de texto. Las funciones de voz y la UX suelen ser menos integradas o dependen de plataformas externas. |
| **Escalabilidad y Mantenimiento** | Desarrollado con una arquitectura **DevOps (Docker y Kubernetes)**. El proyecto es containerizado, asegurando una implementación rápida, una gestión de dependencias estable y una **escalabilidad horizontal inmediata** para toda la población estudiantil de la universidad. | No ofrecen una solución containerizada lista para despliegue institucional; requieren una infraestructura de integración compleja por parte de la universidad. |
| **Visualización** | Capacidad nativa de generar **gráficas interactivas con Plotly** (ej. líneas tangentes, áreas bajo la curva) en tiempo real, vinculando la teoría con la representación visual para mejorar el aprendizaje. | Se limita a describir cómo debe ser una gráfica o a generar código Plotly que el usuario debe copiar y ejecutar externamente. |

### Conclusión del Valor Único:

S.A.P.I.E.N.S. no es solo un motor de lenguaje, es un **sistema de apoyo educativo diseñado e implementado con rigor de ingeniería**, lo que garantiza **precisión matemática, usabilidad multimodal y escalabilidad institucional**, factores críticos que lo separan de las herramientas de IA de propósito general.

----

## 🏁 Conclusión

S.A.P.I.E.N.S. representa un paso clave hacia la transformación digital del proceso de tutoría académica en la Universidad Santo Tomás. Basado en IA generativa, responde a necesidades reales de los estudiantes, potenciando el aprendizaje autónomo y fortaleciendo la permanencia estudiantil mediante un modelo accesible, escalable e innovador.

------------

## 👥 Equipo del Proyecto

- Profesor Diego Alejandro Barragán
- Estudiante Yojan Arley Contreras
-  Estudiante Cristian David Losada
- Estudiante Alejandro Castañeda
