import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from datetime import datetime
import base64
import io
from ultralytics import YOLO

# ---------------- CONFIG PÁGINA ----------------
st.set_page_config(
    page_title="SOFA 2025 - Universidad Santo Tomas",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- DIRECTORIOS ----------------
os.makedirs("fotos_stand", exist_ok=True)

# ---------------- CARGAR MODELO YOLO ----------------
MODEL_PATH = "best1.pt"  # Ruta relativa para Hugging Face
ICON_PATH = "icons"       # Carpeta de íconos (relativa)

try:
    model = YOLO(MODEL_PATH)
    st.session_state.yolo_cargado = True
except Exception as e:
    st.error(f"❌ Error al cargar el modelo YOLO: {e}")
    st.session_state.yolo_cargado = False


# ---------------- CARGAR ICONOS ----------------
def cargar_iconos(icon_dir):
    """Carga los íconos PNG de cada clase."""
    icons = {}
    if not os.path.exists(icon_dir):
        return icons

    for cls in model.names.values():
        icon_path = os.path.join(icon_dir, f"{cls}.png")
        if os.path.exists(icon_path):
            icon = Image.open(icon_path).convert("RGBA")
            icons[cls] = icon
    return icons


icons = cargar_iconos(ICON_PATH)


# ---------------- DETECCIÓN YOLO ----------------
def detectar_yolo(pil_img):
    """Detecta objetos con YOLO, dibuja cajas de colores e íconos por clase."""
    img_rgb = np.array(pil_img.convert("RGB"))
    results = model(img_rgb)
    annotated = img_rgb.copy()

    # 🎨 Colores fijos por clase
    colores_clase = {
        "Pepper": (128, 0, 128),        # Morado
        "Protagonista": (0, 255, 0),    # Verde
        "Drogon": (255, 0, 0),          # Rojo
    }

    default_color = (0, 255, 255)

    if hasattr(results[0], "boxes"):
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label_name = model.names.get(cls, f"cls_{cls}")
            label = f"{label_name} {conf:.2f}"

            color = colores_clase.get(label_name, default_color)

            # 🟩 Dibujar caja
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Fondo del texto
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x1, y1 - th - 6), (x1 + tw, y1), color, -1)
            cv2.putText(
                annotated, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2
            )

            # 🧩 Dibujar ícono si existe
            if label_name in icons:
                icon = icons[label_name]
                icon_size = int(0.4 * (y2 - y1))  # Tamaño relativo
                icon = icon.resize((icon_size, icon_size))
                icon_np = np.array(icon)

                # Posición del ícono
                if label_name == "Pepper":
                    x_offset = x2 - icon_size - 10  # arriba a la derecha
                    y_offset = max(y1 - icon_size - 10, 0)
                elif label_name == "Drogon":
                    x_offset = x1
                    y_offset = max(y1 - icon_size - 40, 0)  # más arriba
                else:
                    x_offset = x1
                    y_offset = max(y1 - icon_size - 10, 0)

                y2_icon = min(y_offset + icon_size, annotated.shape[0])
                x2_icon = min(x_offset + icon_size, annotated.shape[1])
                icon_h, icon_w = y2_icon - y_offset, x2_icon - x_offset
                icon_np = icon_np[:icon_h, :icon_w]

                # Mezclar transparencia
                if icon_np.shape[2] == 4:
                    alpha = icon_np[:, :, 3] / 255.0
                    for c in range(3):
                        annotated[y_offset:y2_icon, x_offset:x2_icon, c] = (
                            alpha * icon_np[:, :, c] +
                            (1 - alpha) * annotated[y_offset:y2_icon, x_offset:x2_icon, c]
                        )

    return Image.fromarray(annotated)


# ---------------- DESCARGA ----------------
def crear_boton_descarga(image, nombre):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'''
    <a href="data:file/jpg;base64,{b64}" download="{nombre}.jpg"
    style="background-color:#4CAF50;color:white;padding:10px 20px;
    text-align:center;text-decoration:none;border-radius:5px;display:inline-block;">
    📸 Descargar tu foto</a>
    '''
    return href


# ---------------- PÁGINAS ----------------
def pagina_tomar_foto():
    st.title("🎓 SOFA 2025 - Universidad Santo Tomas")
    st.subheader("📸 Tómate tu foto en el stand")

    img_file_buffer = st.camera_input("Sonríe y toma tu foto 👇", key="camera_widget")
    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)
        nombre_archivo = f"fotos_stand/foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        image.save(nombre_archivo, quality=95)

        st.session_state.foto_path = nombre_archivo
        st.session_state.etapa = "formulario"
        st.rerun()


def pagina_formulario():
    st.title("📝 Completa el formulario")
    st.info("Por favor completa este breve formulario antes de continuar")

    form_url = "https://share.hsforms.com/13wfiKA-rRAmNJwH2ZxH10g3a8ur"
    st.components.v1.iframe(form_url, height=600, scrolling=True)

    if st.checkbox("✅ He completado el formulario"):
        st.session_state.etapa = "deteccion"
        st.rerun()


def pagina_deteccion():
    st.title("🤖 Procesando tu foto con YOLO")

    if "foto_path" in st.session_state and os.path.exists(st.session_state.foto_path):
        foto = Image.open(st.session_state.foto_path)

        if st.session_state.yolo_cargado:
            resultado = detectar_yolo(foto)
            st.image(resultado, caption="Tu foto con detección YOLO", use_container_width=True)

            boton_descarga = crear_boton_descarga(resultado, "foto_yolo_sofa2025")
            st.markdown(boton_descarga, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No se pudo cargar el modelo YOLO.")

        if st.button("🔄 Tomar otra foto"):
            os.remove(st.session_state.foto_path)
            st.session_state.foto_path = None
            st.session_state.etapa = "foto"
            st.rerun()
    else:
        st.warning("No se encontró la foto. Vuelve a tomar una.")
        if st.button("📸 Volver a cámara"):
            st.session_state.etapa = "foto"
            st.rerun()


# ---------------- MAIN ----------------
def main():
    if "etapa" not in st.session_state:
        st.session_state.etapa = "foto"
    if "foto_path" not in st.session_state:
        st.session_state.foto_path = None

    if st.session_state.etapa == "foto":
        pagina_tomar_foto()
    elif st.session_state.etapa == "formulario":
        pagina_formulario()
    elif st.session_state.etapa == "deteccion":
        pagina_deteccion()


if __name__ == "__main__":
    main()
    
