import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO
import base64
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mall Digital | Tienda Online", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS MEJORADO Y RESPONSIVO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

/* BASES */
.stApp { 
    background: #fdfdfd;
    font-family: 'Poppins', sans-serif !important;
}

/* HACK RESPONSIVO PARA COLUMNAS */
@media (max-width: 768px) {
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
        margin-bottom: 20px;
    }
}

/* HEADER Y BANNER */
.main-header {
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
    padding: 40px 20px;
    border-radius: 0 0 30px 30px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}

/* TARJETAS DE PRODUCTO */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: white !important;
    border-radius: 20px !important;
    border: 1px solid #f0f0f0 !important;
    transition: all 0.3s ease !important;
    overflow: hidden !important;
    padding: 0 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 30px rgba(0,0,0,0.08) !important;
    border-color: #0f3460 !important;
}

.tarjeta-imagen {
    width: 100%;
    height: 250px;
    object-fit: cover;
    border-bottom: 1px solid #f8f8f8;
}

.product-content {
    padding: 18px;
}

.product-category {
    background: #e94560;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 50px;
    text-transform: uppercase;
}

.product-title {
    color: #1a1a2e;
    font-weight: 600;
    font-size: 1.1rem;
    margin-top: 10px;
    height: 2.8rem;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.product-price {
    font-weight: 800;
    font-size: 1.4rem;
    color: #0f3460;
    margin: 10px 0;
}

/* BOTONES */
.stButton > button {
    background: #0f3460 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: 0.3s;
}

.stButton > button:hover {
    background: #e94560 !important;
    box-shadow: 0 5px 15px rgba(233, 69, 96, 0.3) !important;
}

/* DIALOGS / MODALES */
div[data-testid="stDialog"] div[role="dialog"] {
    border-radius: 25px !important;
    padding: 20px !important;
}

.whatsapp-btn {
    background: #25D366;
    color: white !important;
    text-align: center;
    padding: 15px;
    border-radius: 12px;
    font-weight: 700;
    text-decoration: none;
    display: block;
    margin-top: 10px;
}

/* OCULTAR ELEMENTOS STREAMLIT */
header, footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES TÉCNICAS ---
def limpiar_precio(valor):
    if pd.isna(valor): return 0.0
    precio_str = str(valor)
    precio_str = re.sub(r'[^\d,\.]', '', precio_str)
    try:
        # Manejo simple de comas/puntos decimales
        if ',' in precio_str and '.' in precio_str:
            precio_str = precio_str.replace(',', '')
        elif ',' in precio_str:
            precio_str = precio_str.replace(',', '.')
        return float(precio_str)
    except: return 0.0

@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url: return None
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        return BytesIO(response.content) if response.status_code == 200 else None
    except: return None

# --- VENTANA DE COMPRA (MODAL) ---
@st.dialog("🛍️ Detalle del Producto")
def comprar_producto(row):
    st.markdown(f"""
        <div style='text-align:center;'>
            <h2 style='color:#0f3460; margin-bottom:0;'>{row['Nombre']}</h2>
            <span style='color:#e94560; font-weight:600;'>{row['Categoria']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Imágenes del Modal
    imagenes = []
    nombres_cols = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
    for col in nombres_cols:
        if col in row.index and pd.notna(row[col]):
            img = get_image_from_drive(row[col])
            if img: imagenes.append(img)
    
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        if imagenes:
            if len(imagenes) > 1:
                tabs = st.tabs([f"Vista {i+1}" for i in range(len(imagenes))])
                for t, im in zip(tabs, imagenes):
                    with t: st.image(im, use_container_width=True)
            else:
                st.image(imagenes[0], use_container_width=True)
        else:
            st.info("No hay imágenes disponibles")

    with col_det:
        precio = limpiar_precio(row['Precio'])
        st.markdown(f"<h1 style='color:#0f3460;'>${row['Precio']}</h1>", unsafe_allow_html=True)
        
        if 'Promocion' in row.index and pd.notna(row['Promocion']) and str(row['Promocion']).strip():
            st.warning(f"🏷️ {row['Promocion']}")
        
        # CAMBIO 2: Descripción en lugar de tallas
        st.markdown("---")
        if 'Descripcion' in row.index and pd.notna(row['Descripcion']) and str(row['Descripcion']).strip():
            st.markdown(f"""
                <div style='background:#f8f9fa; padding:15px; border-radius:12px; border-left:4px solid #e94560;'>
                    <small style='color:#6c757d; font-weight:700;'>DESCRIPCIÓN</small><br>
                    <div style='color:#1a1a2e; font-size:0.95rem;'>{row['Descripcion']}</div>
                </div>
            """, unsafe_allow_html=True)
        
        cantidad = st.number_input("Cantidad:", min_value=1, max_value=10, value=1)
        total = precio * cantidad
        
        st.markdown(f"**Total: ${total:.2f}**")
        
        # CAMBIO 3: Mensaje WhatsApp
        mensaje = f"""Hola Mall Digital, deseo realizar un pedido:
*Producto:* {row['Nombre']}
*Categoria:* {row['Categoria']}
*Cantidad:* {cantidad}
*Total:* ${total:.2f}
*Codigo:* {row['cod.']}"""
        
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">💬 PEDIR POR WHATSAPP</a>', unsafe_allow_html=True)

# --- CUERPO PRINCIPAL ---
st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; letter-spacing:2px;">🛒 MALL DIGITAL</h1>
        <p style="opacity:0.8;">Calidad y confianza en cada compra</p>
    </div>
""", unsafe_allow_html=True)

busqueda = st.text_input("Buscar", placeholder="🔍 ¿Qué estás buscando hoy?", label_visibility="collapsed")

# --- CARGA Y RENDERIZADO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # CAMBIO 4: Filtro por Categoria
    if busqueda:
        df = df[df['Nombre'].str.contains(busqueda, case=False, na=False) | 
                df['Categoria'].str.contains(busqueda, case=False, na=False)]

    if df.empty:
        st.warning("No se encontraron productos.")
    else:
        # Grid de productos (3 columnas en PC, 1 en móvil vía CSS)
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    # CAMBIO 1: Portada
                    portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                    if portada:
                        img_b64 = base64.b64encode(portada.getvalue()).decode()
                        st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="tarjeta-imagen">', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="height:250px; background:#f0f2f6; display:flex; align-items:center; justify-content:center;">📦</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class="product-content">
                            <span class="product-category">{row['Categoria']}</span>
                            <div class="product-title">{row['Nombre']}</div>
                            <div class="product-price">${row['Precio']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📦 VER DETALLES", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Error al conectar con el catálogo. Revisa tu conexión.")

# FOOTER
st.markdown("""
<div style="text-align:center; padding:40px; color:#6c757d; font-size:0.8rem;">
    © 2026 MALL DIGITAL - Envíos a todo el país 🇪🇨
</div>
""", unsafe_allow_html=True)
