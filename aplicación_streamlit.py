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

# --- CSS REDISEÑADO: MALL DIGITAL ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

.stApp, [data-testid="stDialog"] { 
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    font-family: 'Poppins', sans-serif !important;
}

/* HEADER MODERNO */
header { 
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    padding: 20px 0 !important;
}

/* DIALOG / MODAL */
div[data-testid="stDialog"] div[role="dialog"] {
    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%) !important;
    border-radius: 24px !important;
    max-width: 950px !important;
    box-shadow: 0 25px 80px rgba(0,0,0,0.15) !important;
    border: 1px solid rgba(255,255,255,0.8) !important;
}

div[data-testid="stDialog"] h2, 
div[data-testid="stDialog"] h3, 
div[data-testid="stDialog"] p, 
div[data-testid="stDialog"] span, 
div[data-testid="stDialog"] label {
    color: #1a1a2e !important;
    font-family: 'Poppins', sans-serif !important;
}

/* TARJETAS DE PRODUCTO */
div[data-testid="stVerticalBlockBorderWrapper"] > div[class*="st-emotion-cache"] {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    border-radius: 20px !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    padding: 0 !important;
    overflow: hidden !important;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.07) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div[class*="st-emotion-cache"]:hover {
    transform: translateY(-12px) scale(1.02) !important;
    box-shadow: 0 20px 60px rgba(15, 52, 96, 0.15) !important;
    border-color: #0f3460 !important;
}

.tarjeta-imagen {
    width: 100% !important;
    height: 240px !important;
    object-fit: cover !important;
    border-radius: 20px 20px 0 0 !important;
}

.product-content {
    padding: 20px !important;
}

.product-title {
    color: #1a1a2e;
    font-weight: 700;
    font-size: 1.15rem;
    line-height: 1.3;
    display: block;
    margin-bottom: 8px !important;
    min-height: 50px !important;
}

.product-collection {
    display: inline-block;
    background: linear-gradient(90deg, #e94560 0%, #ff6b6b 100%);
    color: white !important;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.product-price-cat {
    font-weight: 800;
    font-size: 1.4rem;
    color: #0f3460;
    margin: 10px 0;
}

/* BOTONES */
.stButton > button {
    background: linear-gradient(90deg, #0f3460 0%, #16213e 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    width: 100% !important;
    padding: 12px !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #e94560 0%, #ff6b6b 100%) !important;
    transform: translateY(-2px) !important;
}

.whatsapp-btn {
    background: linear-gradient(90deg, #25D366 0%, #128C7E 100%) !important;
    color: white !important;
    text-align: center;
    padding: 14px;
    border-radius: 14px;
    font-weight: 800;
    text-decoration: none;
    display: block;
    margin-top: 15px;
}

/* FOOTER */
.modern-footer {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 30px 30px 0 0;
    margin-top: 60px;
    padding: 50px 30px 30px;
    color: white;
    text-align: center;
}

header, footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE SOPORTE ---
def limpiar_precio(valor):
    if pd.isna(valor): return 0.0
    precio_str = str(valor)
    precio_str = re.sub(r'[^\d,\.]', '', precio_str)
    if ',' in precio_str and '.' in precio_str:
        precio_str = precio_str.replace('.', '').replace(',', '.')
    elif ',' in precio_str:
        partes = precio_str.split(',')
        if len(partes) == 2 and len(partes[1]) <= 2:
            precio_str = precio_str.replace(',', '.')
        else:
            precio_str = precio_str.replace(',', '')
    try: return float(precio_str)
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

# --- MODAL DE PRODUCTO ---
@st.dialog("🛍️ Detalle del Producto")
def comprar_producto(row):
    st.markdown(f"""
        <h2 style='color:#0f3460; font-family:Poppins; font-weight:800; text-align:center; margin-bottom:5px;'>
            {row['Nombre']}
        </h2>
        <p style='text-align:center; color:#e94560; font-weight:600; font-size:0.9rem; margin-bottom:20px;'>
            {row['Categoria']}
        </p>
    """, unsafe_allow_html=True)
    
    # Carga de imágenes
    imagenes = []
    nombres_cols = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
    for col_img_name in nombres_cols:
        if col_img_name in row.index and pd.notna(row[col_img_name]):
            img_data = get_image_from_drive(row[col_img_name])
            if img_data: imagenes.append(img_data)
    
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        if len(imagenes) > 1:
            tabs = st.tabs([f"📷 Vista {i+1}" for i in range(len(imagenes))])
            for tab, img in zip(tabs, imagenes):
                with tab: st.image(img, use_container_width=True)
        elif len(imagenes) == 1:
            st.image(imagenes[0], use_container_width=True)
        else:
            st.info("📷 Sin imagen disponible")
            
    with col_det:
        precio = limpiar_precio(row['Precio'])
        
        # Precio y Promoción
        col_price, col_promo = st.columns([1, 1])
        with col_price:
            st.markdown(f"<h3 style='color:#0f3460; font-weight:800; font-size:1.8rem;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        
        with col_promo:
            if 'Promocion' in row.index and pd.notna(row['Promocion']) and str(row['Promocion']).strip():
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #e94560, #ff6b6b); color: white; padding: 8px 15px; border-radius: 10px; font-weight: 700; font-size: 0.85rem; text-align: center;'>
                        🏷️ {row['Promocion']}
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 15px 0; border-color: #eee;'>", unsafe_allow_html=True)
        
        # --- NUEVA SECCIÓN: DESCRIPCIÓN (CAMBIO 2) ---
        if 'Descripcion' in row.index and pd.notna(row['Descripcion']) and str(row['Descripcion']).strip():
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 15px; border-radius: 12px; margin: 15px 0;'>
                    <span style='color: #6c757d; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>Descripcion</span><br>
                    <span style='color: #1a1a2e; font-size: 1rem; line-height: 1.5;'>{row['Descripcion']}</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 15px; border-radius: 12px; margin: 15px 0;'>
                    <span style='color: #6c757d; font-size: 0.9rem;'>Sin descripcion disponible</span>
                </div>
            """, unsafe_allow_html=True)
        
        cantidad = st.number_input("Cantidad:", min_value=1, max_value=10, value=1, step=1)
        total = precio * cantidad
        
        st.markdown(f"""
            <div style='background: #f8f9fa; padding: 15px; border-radius: 12px; margin: 15px 0; text-align: center;'>
                <span style='color: #6c757d; font-size: 0.9rem;'>Total a pagar</span><br>
                <span style='color: #0f3460; font-weight: 800; font-size: 1.6rem;'>${total:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # --- WHATSAPP (CAMBIO 3) ---
        mensaje = f"""Hola Mall Digital, deseo realizar un pedido:

*Producto:* {row['Nombre']}
*Categoria:* {row['Categoria']}
*Cantidad:* {cantidad}
*Total:* ${total:.2f}

Codigo: {row['cod.']}"""
        
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div class="whatsapp-btn">💬 PEDIR POR WHATSAPP</div></a>', unsafe_allow_html=True)

# --- INTERFAZ PRINCIPAL ---
st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 40px 20px; border-radius: 0 0 30px 30px; text-align: center;">
        <h1 style="color: white; font-weight: 800; font-size: 2.5rem; margin: 0; letter-spacing: 3px;">🛒 MALL DIGITAL</h1>
        <p style="color: #a0b3c6; font-size: 1.1rem; margin-top: 10px;">Tu tienda online de productos variados</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="promo-banner" style="background: #e94560; color: white; text-align: center; padding: 10px; font-weight: 600;">🎉 ENVÍO GRATIS EN COMPRAS MAYORES A $50</div>', unsafe_allow_html=True)

busqueda = st.text_input("Buscar", placeholder="🔍 Busca por nombre o categoría...", label_visibility="collapsed")

# --- CARGA DE DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # --- BUSQUEDA (CAMBIO 4) ---
    if busqueda:
        df = df[df['Nombre'].str.contains(busqueda, case=False, na=False) | 
                df['Categoria'].str.contains(busqueda, case=False, na=False)]
    
    st.markdown(f'<p style="text-align: center; color: #6c757d; margin-bottom: 25px;">📦 Mostrando <b>{len(df)}</b> productos</p>', unsafe_allow_html=True)

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                # --- PORTADA (CAMBIO 1) ---
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    img_b64 = base64.b64encode(portada.getvalue()).decode()
                    st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="tarjeta-imagen">', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="width:100%; height:240px; background: #eee; display:flex; align-items:center; justify-content:center;">📦</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="product-content">', unsafe_allow_html=True)
                # --- BADGE (CAMBIO 5) ---
                st.markdown(f'<span class="product-collection">{row["Categoria"]}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                c_pre, c_btn = st.columns([1, 1.2])
                with c_pre:
                    st.markdown(f'<div class="product-price-cat">${row["Precio"]}</div>', unsafe_allow_html=True)
                with c_btn:
                    if st.button("🛒 COMPRAR", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)
                st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- FOOTER ---
st.markdown("""
<div class="modern-footer">
    <h3>🛒 MALL DIGITAL</h3>
    <p>📍 Guayaquil, Ecuador | 📱 +593 97 886 8363<br>© 2026 MALL DIGITAL - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
