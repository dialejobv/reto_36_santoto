# app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from datetime import datetime
import base64
import io

# --------- Compatibilidad iframe ---------
try:
    # Streamlit >= 1.40
    iframe = st.iframe
except AttributeError:
    # Streamlit < 1.40
    import streamlit.components.v1 as components
    iframe = components.iframe

# --------- Intentos de import para segmentación ---------
try:
    import mediapipe as mp
    MP_AVAILABLE = True
except Exception:
    MP_AVAILABLE = False

try:
    from rembg import remove as rembg_remove
    REMBG_AVAILABLE = True
except Exception:
    REMBG_AVAILABLE = False

# ---------------- CONFIG PÁGINA ----------------
st.set_page_config(
    page_title="SOFA 2025 - Universidad Santo Tomas",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Carpeta de fotos
os.makedirs("fotos_stand", exist_ok=True)
os.makedirs("assets", exist_ok=True)  # assets/fondo.png debe existir

FONDO_PATH = "assets/fondo.png"

# ---------------- SEGMENTACIÓN ----------------
def _resize_for_seg(img_pil, max_side=512):
    w, h = img_pil.size
    scale = min(max_side / max(w, h), 1.0)
    if scale < 1.0:
        new_size = (int(w * scale), int(h * scale))
        small = img_pil.resize(new_size, Image.LANCZOS)
    else:
        small = img_pil.copy()
        scale = 1.0
    return small, scale

def _segment_mediapipe(pil_img):
    if not MP_AVAILABLE:
        raise RuntimeError("MediaPipe no disponible")
    small, scale = _resize_for_seg(pil_img, max_side=512)
    img_np = np.array(small.convert("RGB"))
    mp_selfie = mp.solutions.selfie_segmentation
    with mp_selfie.SelfieSegmentation(model_selection=1) as seg:
        results = seg.process(img_np)
        if results.segmentation_mask is None:
            return None, scale
        mask_small = results.segmentation_mask.astype(np.float32)
    mask_full = cv2.resize(mask_small, pil_img.size, interpolation=cv2.INTER_LINEAR)
    return mask_full, scale

def _segment_rembg(pil_img):
    if not REMBG_AVAILABLE:
        raise RuntimeError("rembg no disponible")
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    out_bytes = rembg_remove(buf.getvalue())
    out_img = Image.open(io.BytesIO(out_bytes)).convert("RGBA")
    alpha = np.array(out_img.split()[-1]).astype(np.float32) / 255.0
    return alpha, 1.0

def _segment_grabcut(pil_img):
    img_rgb = np.array(pil_img.convert("RGB"))
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    H, W = img_bgr.shape[:2]
    rect = (int(W*0.1), int(H*0.1), int(W*0.8), int(H*0.8))
    mask_gc = np.zeros((H, W), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(img_bgr, mask_gc, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    except Exception:
        return np.ones((H, W), dtype=np.float32), 1.0
    mask2 = np.where((mask_gc == 2) | (mask_gc == 0), 0, 1).astype('uint8')
    mask_float = cv2.GaussianBlur(mask2.astype(np.float32), (21,21), 0)
    if mask_float.max() > 0:
        mask_float /= mask_float.max()
    return mask_float.astype(np.float32), 1.0

def aplicar_fondo_mejorado(pil_img, fondo_path=FONDO_PATH, method="auto"):
    if not os.path.exists(fondo_path):
        st.warning("No se encontró el fondo.")
        return pil_img.convert("RGB")

    mask = None
    used = None
    if method in ("auto", "mediapipe") and MP_AVAILABLE and mask is None:
        try:
            mask, _ = _segment_mediapipe(pil_img)
            used = "mediapipe"
        except Exception:
            mask = None
    if method in ("auto", "rembg") and REMBG_AVAILABLE and mask is None:
        try:
            mask, _ = _segment_rembg(pil_img)
            used = "rembg"
        except Exception:
            mask = None
    if mask is None:
        try:
            mask, _ = _segment_grabcut(pil_img)
            used = "grabcut"
        except Exception:
            W,H = pil_img.size
            mask = np.ones((H, W), dtype=np.float32)
            used = "none"

    mask = cv2.GaussianBlur(mask, (15,15), 0)
    mask = np.clip(mask, 0.0, 1.0)

    fondo = Image.open(fondo_path).convert("RGB").resize(pil_img.size, Image.LANCZOS)
    fg = np.array(pil_img.convert("RGB")).astype(np.float32)
    bg = np.array(fondo).astype(np.float32)

    alpha = mask[..., None]
    comp = (fg * alpha + bg * (1.0 - alpha)).astype(np.uint8)
    final = Image.fromarray(comp)

    st.info(f"Fondo aplicado con: {used}")
    return final

# ---------------- DESCARGA ----------------
def crear_boton_descarga(image, nombre):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:file/jpg;base64,{b64}" download="{nombre}.jpg" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-align:center; text-decoration:none; border-radius:5px; display:inline-block;">📸 Descargar tu foto</a>'
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
    st.info("Por favor completa este breve formulario antes de descargar tu foto")

    form_url = "https://share.hsforms.com/13wfiKA-rRAmNJwH2ZxH10g3a8ur"  # tu link
    iframe(form_url, height=600, scrolling=True)  # 👈 alias dinámico

    if st.checkbox("✅ He completado el formulario"):
        st.session_state.etapa = "fondo"
        st.rerun()

def pagina_fondo():
    st.title("🎉 Tu foto está lista")

    if "foto_path" in st.session_state and os.path.exists(st.session_state.foto_path):
        foto = Image.open(st.session_state.foto_path)
        final_img = aplicar_fondo_mejorado(foto, fondo_path=FONDO_PATH, method="auto")
        st.image(final_img, caption="Tu foto con el fondo del stand", use_container_width=True)

        boton_descarga = crear_boton_descarga(final_img, "foto_sofa2025")
        st.markdown(boton_descarga, unsafe_allow_html=True)

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
    elif st.session_state.etapa == "fondo":
        pagina_fondo()

if __name__ == "__main__":
    main()
