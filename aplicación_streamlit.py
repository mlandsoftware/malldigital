
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

/* TARJETAS DE PRODUCTO - ESTILO GLASSMORPHISM */
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

/* IMAGEN DE PRODUCTO */
.tarjeta-imagen {
    width: 100% !important;
    height: 240px !important;
    object-fit: cover !important;
    border-radius: 20px 20px 0 0 !important;
    margin-bottom: 0 !important;
    transition: transform 0.5s ease !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover .tarjeta-imagen {
    transform: scale(1.05) !important;
}

/* CONTENIDO DE TARJETA */
.product-content {
    padding: 20px !important;
}

.product-title {
    color: #1a1a2e;
    font-weight: 700;
    font-size: 1.15rem;
    line-height: 1.3;
    text-align: left;
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
    letter-spacing: 0.5px;
}

.product-price-cat {
    font-weight: 800;
    font-size: 1.4rem;
    color: #0f3460;
    text-align: left;
    margin: 10px 0;
}

/* BOTÓN COMPRAR */
.stButton > button {
    background: linear-gradient(90deg, #0f3460 0%, #16213e 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    width: 100% !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(15, 52, 96, 0.2) !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #e94560 0%, #ff6b6b 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(233, 69, 96, 0.3) !important;
}

/* BARRA DE BÚSQUEDA */
div[data-testid="stTextInput"] {
    max-width: 600px;
    margin: 0 auto 40px auto;
}

div[data-testid="stTextInput"] > div {
    border: 2px solid #0f3460 !important;
    border-radius: 50px !important;
    background: white !important;
    box-shadow: 0 4px 20px rgba(15, 52, 96, 0.1) !important;
}

div[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    color: #1a1a2e !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 14px 28px !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #8892b0 !important;
}

/* SELECTOR DE CANTIDAD Y TALLAS */
div[data-testid="stNumberInput"] input {
    border: 2px solid #0f3460 !important;
    border-radius: 12px !important;
    text-align: center !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600;
}

div[data-testid="stSelectbox"] > div > div {
    border: 2px solid #0f3460 !important;
    border-radius: 12px !important;
    font-family: 'Poppins', sans-serif !important;
}

/* TABS EN MODAL */
div[data-testid="stDialog"] .stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    border-bottom: none !important;
    padding: 10px 0;
}

div[data-testid="stDialog"] .stTabs [data-baseweb="tab"] {
    height: 55px !important;
    padding: 8px 20px !important;
    background: rgba(15, 52, 96, 0.05) !important;
    border: 2px solid transparent !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    color: #1a1a2e !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stDialog"] .stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #0f3460 0%, #16213e 100%) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: 0 4px 15px rgba(15, 52, 96, 0.3) !important;
}

/* BANNER PROMOCIONAL */
.promo-banner {
    background: linear-gradient(90deg, #e94560 0%, #ff6b6b 100%);
    color: white;
    text-align: center;
    padding: 12px;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.5px;
    border-radius: 0 0 20px 20px;
    margin-bottom: 30px;
}

/* BADGE DE DESCUENTO */
.discount-badge {
    position: absolute;
    top: 15px;
    right: 15px;
    background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    z-index: 10;
}

/* WHATSAPP BUTTON EN MODAL */
.whatsapp-btn {
    background: linear-gradient(90deg, #25D366 0%, #128C7E 100%) !important;
    color: white !important;
    text-align: center;
    padding: 14px;
    border-radius: 14px;
    font-weight: 800;
    font-family: 'Poppins', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 1px;
    text-decoration: none;
    display: block;
    margin-top: 15px;
    box-shadow: 0 6px 20px rgba(37, 211, 102, 0.3);
    transition: all 0.3s ease;
    border: none;
}

.whatsapp-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(37, 211, 102, 0.4);
}

/* FOOTER MODERNO */
.modern-footer {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 30px 30px 0 0;
    margin-top: 60px;
    padding: 50px 30px 30px;
    color: white;
    text-align: center;
}

.modern-footer h3 {
    color: #e94560;
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 1.8rem;
    margin-bottom: 20px;
    letter-spacing: 2px;
}

.modern-footer p {
    color: #a0b3c6;
    font-family: 'Poppins', sans-serif;
    font-size: 1rem;
    line-height: 2;
}

.modern-footer .copyright {
    color: #5a6a7a;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.1);
    font-size: 0.85rem;
}

/* ANIMACIÓN DE CARGA */
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

/* SCROLLBAR PERSONALIZADA */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #0f3460, #e94560);
    border-radius: 10px;
}

/* OCULTAR ELEMENTOS DE STREAMLIT */
header, footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN PARA LIMPIAR PRECIO ---
def limpiar_precio(valor):
    if pd.isna(valor):
        return 0.0
    precio_str = str(valor)
    precio_str = re.sub(r'[^\d,\.]', '', precio_str)
    if ',' in precio_str and '.' in precio_str:
        last_comma = precio_str.rfind(',')
        last_point = precio_str.rfind('.')
        if last_comma > last_point:
            precio_str = precio_str.replace('.', '').replace(',', '.')
        else:
            precio_str = precio_str.replace(',', '')
    elif ',' in precio_str:
        partes = precio_str.split(',')
        if len(partes) == 2 and len(partes[1]) <= 2:
            precio_str = precio_str.replace(',', '.')
        else:
            precio_str = precio_str.replace(',', '')
    try:
        return float(precio_str)
    except ValueError:
        return 0.0

# --- LÓGICA DE IMÁGENES ---
@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url: 
        return None
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        return BytesIO(response.content) if response.status_code == 200 else None
    except: 
        return None

# --- VENTANA EMERGENTE (MODAL) ---
@st.dialog("🛍️ Detalle del Producto")
def comprar_producto(row):
    st.markdown(f"""
        <h2 style='color:#0f3460; font-family:Poppins; font-weight:800; text-align:center; margin-bottom:5px;'>
            {row['Nombre']}
        </h2>
        <p style='text-align:center; color:#e94560; font-weight:600; font-size:0.9rem; margin-bottom:20px;'>
            {row['Coleccion']}
        </p>
    """, unsafe_allow_html=True)
    
    imagenes = []
    nombres_cols = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
    for col_img_name in nombres_cols:
        if col_img_name in row.index and pd.notna(row[col_img_name]):
            img_data = get_image_from_drive(row[col_img_name])
            if img_data:
                imagenes.append(img_data)
    
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        if len(imagenes) > 1:
            tabs = st.tabs([f"📷 Vista {i+1}" for i in range(len(imagenes))])
            for i, (tab, img) in enumerate(zip(tabs, imagenes)):
                with tab:
                    st.image(img, use_container_width=True)
        elif len(imagenes) == 1:
            st.image(imagenes[0], use_container_width=True)
        else:
            st.info("📷 Sin imagen disponible")
            
    with col_det:
        precio = limpiar_precio(row['Precio'])
        
        # Mostrar precio original y promoción si existe
        col_price, col_promo = st.columns([1, 1])
        with col_price:
            st.markdown(f"""
                <h3 style='color:#0f3460; font-family:Poppins; font-weight:800; font-size:1.8rem;'>
                    ${row['Precio']}
                </h3>
            """, unsafe_allow_html=True)
        
        with col_promo:
            if 'Promocion' in row.index and pd.notna(row['Promocion']) and str(row['Promocion']).strip():
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #e94560, #ff6b6b); 
                         color: white; padding: 8px 15px; border-radius: 10px; 
                         font-weight: 700; font-size: 0.85rem; text-align: center;'>
                        🏷️ {row['Promocion']}
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 15px 0; border-color: #eee;'>", unsafe_allow_html=True)
        
        # Selección de tallas (adaptable a cualquier producto)
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("📏 Selecciona opción:", tallas)
        
        cantidad = st.number_input("📦 Cantidad:", min_value=1, max_value=10, value=1, step=1)
        
        total = precio * cantidad
        
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                 padding: 15px; border-radius: 12px; margin: 15px 0; text-align: center;'>
                <span style='color: #6c757d; font-size: 0.9rem;'>Total a pagar</span><br>
                <span style='color: #0f3460; font-weight: 800; font-size: 1.6rem;'>${total:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        
        mensaje = f"""Hola Mall Digital, deseo realizar un pedido:

*Producto:* {row['Nombre']}
*Categoría:* {row['Coleccion']}
*Opción:* {talla_sel}
*Cantidad:* {cantidad}
*Total:* ${total:.2f}

Código: {row['cod.']}"""
        
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div class="whatsapp-btn">
                    💬 PEDIR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- HEADER MALL DIGITAL ---
st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
         padding: 40px 20px; border-radius: 0 0 30px 30px; margin-bottom: 30px; text-align: center;">
        <h1 style="color: white; font-family: 'Poppins', sans-serif; font-weight: 800; 
             font-size: 2.5rem; margin: 0; letter-spacing: 3px;">
            🛒 MALL DIGITAL
        </h1>
        <p style="color: #a0b3c6; font-family: 'Poppins', sans-serif; font-size: 1.1rem; 
             margin-top: 10px; font-weight: 400;">
            Tu tienda online de productos variados
        </p>
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px; flex-wrap: wrap;">
            <span style="color: #e94560; font-weight: 600;">✓ Envíos a todo el país</span>
            <span style="color: #e94560; font-weight: 600;">✓ Pagos seguros</span> 
            <span style="color: #e94560; font-weight: 600;">✓ Atención personalizada</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# BANNER PROMOCIONAL
st.markdown("""
    <div class="promo-banner">
        🎉 ENVÍO GRATIS EN COMPRAS MAYORES A $50 | PROMOCIONES ESPECIALES ESTA SEMANA
    </div>
""", unsafe_allow_html=True)

# BUSCADOR DE PRODUCTOS
busqueda = st.text_input("Buscar", placeholder="🔍 Busca productos, categorías, marcas...", label_visibility="collapsed")

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    if busqueda:
        df = df[df['Nombre'].str.contains(busqueda, case=False, na=False) | 
                df['Coleccion'].str.contains(busqueda, case=False, na=False)]
        if df.empty:
            st.info("🔍 No se encontraron productos. Intenta con otra búsqueda.")
    
    columnas_imagenes = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
    for col in columnas_imagenes[1:]:
        if col not in df.columns:
            df[col] = None

    # Mostrar contador de productos
    st.markdown(f"""
        <p style="text-align: center; color: #6c757d; font-family: 'Poppins', sans-serif; margin-bottom: 25px;">
            📦 Mostrando <b>{len(df)}</b> productos disponibles
        </p>
    """, unsafe_allow_html=True)

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                # Imagen del producto
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    img_b64 = base64.b64encode(portada.getvalue()).decode()
                    st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="tarjeta-imagen">', unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="width:100%; height:240px; background: linear-gradient(135deg, #f5f7fa, #e4e8ec); 
                             display:flex; align-items:center; justify-content:center; border-radius:20px 20px 0 0;">
                            <span style="color:#8892b0; font-size:3rem;">📦</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Contenido de la tarjeta
                st.markdown('<div class="product-content">', unsafe_allow_html=True)
                
                # Badge de colección/categoría
                st.markdown(f'<span class="product-collection">{row["Coleccion"]}</span>', unsafe_allow_html=True)
                
                # Título
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # Precio y botón
                c_pre, c_btn = st.columns([1, 1.2])
                with c_pre:
                    st.markdown(f'<div class="product-price-cat">${row["Precio"]}</div>', unsafe_allow_html=True)
                with c_btn:
                    if st.button("🛒 COMPRAR", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)
                
                st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("⚠️ Conectando")
    st.info("💡 Verifica su conección a internet.")

# FOOTER MODERNO
st.markdown("""
<div class="modern-footer">
    <h3>🛒 MALL DIGITAL</h3>
    <p>
        📍 Guayaquil, Ecuador &nbsp;|&nbsp; 📱 +593 97 886 8363<br>
        🚚 Envíos a todo el país &nbsp;|&nbsp; 💳 Pagos seguros<br>
        ✉️ contacto@malldigital.com
    </p>
    <div style="margin-top: 25px; display: flex; justify-content: center; gap: 20px;">
        <span style="background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 30px; color: white; font-weight: 600;">
            Facebook
        </span>
        <span style="background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 30px; color: white; font-weight: 600;">
            Instagram
        </span>
        <span style="background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 30px; color: white; font-weight: 600;">
            TikTok
        </span>
    </div>
    <p class="copyright">
        © 2026 MALL DIGITAL - Todos los derechos reservados
    </p>
</div>
""", unsafe_allow_html=True)

