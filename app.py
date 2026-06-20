import re
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FraudAlert ML",
    page_icon="🛡️",
    layout="wide"
)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.markdown("""
<style>
/* ── Base ── */
.stApp { background-color: #f0f4f8; }

/* ── Watermark ── */
.stApp::before {
    content: "FRAUD DETECTION";
    position: fixed; top: 50%; left: 50%;
    transform: translate(-50%, -50%) rotate(-25deg);
    font-size: 130px; font-weight: 900; letter-spacing: 8px;
    color: rgba(0,0,0,0.025);
    z-index: 0; pointer-events: none; white-space: nowrap;
}

/* ── Header ── */
.fraud-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.fraud-header::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #e94560, #ff6b35, #ffd700);
}
.fraud-header h1 {
    font-size: 2.8rem; font-weight: 800;
    color: #ffffff;
    margin: 0.5rem 0 0.3rem;
    letter-spacing: 1px;
}
.fraud-header .subtitle {
    color: #e94560; font-size: 0.9rem;
    font-weight: 600; letter-spacing: 4px;
    text-transform: uppercase; margin-bottom: 0.5rem;
}
.fraud-header p { color: #a8b2d8; font-size: 0.95rem; margin: 0; }

/* ── Cards de datos ── */
.dato-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.dato-card .label {
    font-size: 0.72rem; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 1px;
    margin-bottom: 0.3rem;
}
.dato-card .value { font-size: 1rem; font-weight: 600; color: #1e293b; }

/* ── Badge de clasificación ── */
.badge-segura {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border: 2px solid #22c55e;
    border-radius: 12px; padding: 1.5rem;
    text-align: center; margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(34,197,94,0.15);
}
.badge-sospechosa {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border: 2px solid #f59e0b;
    border-radius: 12px; padding: 1.5rem;
    text-align: center; margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(245,158,11,0.15);
}
.badge-peligrosa {
    background: linear-gradient(135deg, #fff1f2, #ffe4e6);
    border: 2px solid #e94560;
    border-radius: 12px; padding: 1.5rem;
    text-align: center; margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(233,69,96,0.15);
}
.badge-insuficiente {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border: 2px solid #cbd5e1;
    border-radius: 12px; padding: 1.5rem;
    text-align: center; margin: 1rem 0;
}
.badge-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.badge-title { font-size: 1.6rem; font-weight: 800; margin: 0.3rem 0; }
.badge-score { font-size: 2.5rem; font-weight: 900; }
.badge-score-label { font-size: 0.8rem; color: #64748b; letter-spacing: 2px; text-transform: uppercase; }

/* ── Análisis box ── */
.analisis-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
    line-height: 1.7;
    color: #334155;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    font-size: 0.92rem;
}

/* ── Step cards ── */
.step-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.4rem 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
}
.step-card:hover {
    box-shadow: 0 4px 16px rgba(233,69,96,0.12);
    transform: translateY(-2px);
}
.step-number { font-size: 1.8rem; margin-bottom: 0.5rem; }
.step-title { font-weight: 700; color: #1e293b; font-size: 0.95rem; margin-bottom: 0.4rem; }
.step-desc { font-size: 0.82rem; color: #64748b; line-height: 1.5; }

/* ── Historial cards ── */
.hist-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
}
.hist-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

/* ── Botón principal ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #e94560, #c73652) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.75rem 2rem !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 15px rgba(233,69,96,0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(233,69,96,0.4) !important;
}

/* ── Section titles ── */
.section-title {
    font-size: 1.1rem; font-weight: 700;
    color: #1e293b; margin: 1.5rem 0 1rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.section-title::after {
    content: ""; flex: 1;
    height: 1px; background: #e2e8f0;
    margin-left: 0.5rem;
}

/* ── Métricas ── */
[data-testid="stMetric"] {
    background-color: white !important;
    padding: 15px !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    border: 1px solid #e2e8f0 !important;
}

/* ── Footer ── */
.fraud-footer {
    text-align: center; color: #94a3b8;
    font-size: 0.78rem; padding: 1.5rem;
    border-top: 1px solid #e2e8f0;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "chat_mensajes" not in st.session_state:
    st.session_state.chat_mensajes = []
if "contexto_publicacion" not in st.session_state:
    st.session_state.contexto_publicacion = None
if "historial_analisis" not in st.session_state:
    st.session_state.historial_analisis = []

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("FraudAlertML_logo_512.png", width=140)
    except Exception:
        pass

st.markdown("""
<div class="fraud-header">
    <div class="subtitle">AI · Risk · Scanner</div>
    <h1>FraudAlert ML</h1>
    <p>Evaluación inteligente de riesgo para publicaciones de Mercado Libre Argentina</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CÓMO FUNCIONA
# ─────────────────────────────────────────────
with st.expander("ℹ️ ¿Cómo funciona FraudAlert ML?", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    pasos = [
        ("🔗", "Pegá la URL", "Copiá el link de cualquier publicación de Mercado Libre Argentina"),
        ("📋", "Datos opcionales", "Agregá precio, reputación y ventas para un análisis más preciso"),
        ("🤖", "Gemini analiza", "La IA evalúa señales de riesgo y patrones de fraude conocidos"),
        ("🛡️", "Tu veredicto", "SEGURA, SOSPECHOSA o PELIGROSA con score y explicación detallada"),
    ]
    for col, (icon, titulo, desc) in zip([c1, c2, c3, c4], pasos):
        with col:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-number">{icon}</div>
                <div class="step-title">{titulo}</div>
                <div class="step-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("""
    <br>
    <div style='background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:0.8rem 1.2rem;
                font-size:0.85rem;color:#9a3412;'>
        ⚠️ FraudAlert ML es una herramienta de apoyo. El análisis con IA es orientativo 
        y no reemplaza la verificación manual antes de comprar.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FUNCIONES
# ─────────────────────────────────────────────
def extraer_item_id(texto: str) -> str | None:
    resultado = re.search(r"MLA[-]?\d+", texto.strip().upper())
    return resultado.group(0).replace("-", "") if resultado else None


def extraer_nombre_url(url: str, item_id: str) -> str:
    try:
        id_con_guion = item_id[:3] + "-" + item_id[3:]
        parte = url.split(id_con_guion)[-1] if id_con_guion in url else ""
        parte = parte.split("_JM")[0].split("#")[0].strip("-").strip()
        nombre = parte.replace("-", " ").strip()
        palabras = [p for p in nombre.split() if len(p) > 1]
        return " ".join(palabras[:8]).title() if palabras else ""
    except Exception:
        return ""


def extraer_score(texto: str) -> int:
    """Extrae el score numérico del análisis."""
    match = re.search(r"Score de riesgo:\s*(\d+)", texto)
    return int(match.group(1)) if match else 50


def analizar_con_gemini(item_id: str, url: str, datos_usuario: dict) -> str:
    if not GEMINI_API_KEY:
        return "⚠️ Configurá la GEMINI_API_KEY en el archivo .env"

    client = genai.Client(api_key=GEMINI_API_KEY)
    nombre_url = extraer_nombre_url(url, item_id)
    tiene_datos = any(v.strip() for v in datos_usuario.values() if v)

    if tiene_datos:
        bloque = f"""
DATOS DE LA PUBLICACIÓN:
- URL: {url}
- ID: {item_id}
- Nombre inferido de la URL: {nombre_url or 'no disponible'}
- Precio: {datos_usuario.get('precio') or 'no informado'}
- Reputación del vendedor: {datos_usuario.get('reputacion') or 'no informada'}
- Cantidad de ventas: {datos_usuario.get('ventas') or 'no informada'}
- Condición: {datos_usuario.get('condicion') or 'no informada'}
- Observaciones: {datos_usuario.get('observaciones') or 'ninguna'}
"""
        nivel = "datos proporcionados por el usuario + URL"
    else:
        bloque = f"""
DATOS DE LA PUBLICACIÓN:
- URL: {url}
- ID: {item_id}
- Nombre inferido de la URL: {nombre_url or 'no disponible'}

Nota: No se proporcionaron datos adicionales. Analizá basándote en la URL y tu conocimiento
de patrones de fraude en Mercado Libre Argentina.
"""
        nivel = "URL e ID únicamente"

    prompt = f"""Actuá como especialista en detección de fraude y análisis de riesgo en e-commerce,
con experiencia específica en Mercado Libre Argentina.

Analizá esta publicación. Información disponible ({nivel}):

{bloque}

CRITERIOS DE EVALUACIÓN:
- Precio >40% menor al mercado → riesgo ALTO
- Vendedor nuevo sin reputación → riesgo ALTO
- Vendedor MercadoLíder con muchas ventas → señal de CONFIANZA fuerte
- Keyword stuffing en el título → riesgo MEDIO
- Solicitar pago fuera de ML/Mercado Pago → riesgo MUY ALTO
- Precio acorde al mercado → señal de CONFIANZA

INSTRUCCIONES:
- Usá SOLO los datos disponibles, no inventes información
- Si los datos son insuficientes, usá INFORMACIÓN INSUFICIENTE
- No seas alarmista sin evidencia concreta
- Sé específico y útil para el comprador argentino

Respondé EXACTAMENTE con este formato:

Clasificación: [SEGURA / SOSPECHOSA / PELIGROSA / INFORMACIÓN INSUFICIENTE]
Score de riesgo: XX/100

Motivos:
1. 
2. 
3. 

Qué verificar antes de comprar:
- 
- 
- 

Nivel de confianza del análisis: [Alto / Medio / Bajo]
Justificación:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return response.text or ""


def chat_con_gemini(pregunta: str) -> str:
    if not GEMINI_API_KEY:
        return "⚠️ Configurá la GEMINI_API_KEY en el archivo .env"

    client = genai.Client(api_key=GEMINI_API_KEY)
    contexto = st.session_state.contexto_publicacion or "No hay publicación analizada aún."

    system_msg = f"""Sos FraudBot, asistente especializado en detección de fraude en Mercado Libre Argentina.
Respondés preguntas sobre compras seguras, señales de alerta y fraudes en e-commerce.
Sos claro, conciso y usás lenguaje simple para el comprador argentino.

Contexto de la publicación analizada:
{contexto}

Si preguntan sobre esta publicación, usá ese contexto.
Si no hay publicación analizada, respondé de forma general."""

    mensajes = [
        types.Content(role="user", parts=[types.Part(text=system_msg)]),
        types.Content(role="model", parts=[types.Part(text="Entendido, listo para ayudarte.")]),
    ]
    for msg in st.session_state.chat_mensajes:
        role = "user" if msg["role"] == "user" else "model"
        mensajes.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    mensajes.append(types.Content(role="user", parts=[types.Part(text=pregunta)]))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=mensajes,
        config=types.GenerateContentConfig(temperature=0.3),
    )
    return response.text or ""


def mostrar_badge(analisis: str):
    """Muestra el badge visual grande con clasificación y score."""
    score = extraer_score(analisis)

    if "PELIGROSA" in analisis:
        css = "badge-peligrosa"
        icon = "🚨"
        label = "PELIGROSA"
        color = "#e94560"
    elif "SOSPECHOSA" in analisis:
        css = "badge-sospechosa"
        icon = "⚠️"
        label = "SOSPECHOSA"
        color = "#d29922"
    elif "SEGURA" in analisis and "INFORMACIÓN" not in analisis:
        css = "badge-segura"
        icon = "✅"
        label = "SEGURA"
        color = "#2ea043"
    else:
        css = "badge-insuficiente"
        icon = "ℹ️"
        label = "INFORMACIÓN INSUFICIENTE"
        color = "#7d8590"

    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        st.markdown(f"""
        <div class="{css}">
            <div class="badge-icon">{icon}</div>
            <div class="badge-title" style="color:{color}">{label}</div>
            <div style="margin-top:0.8rem">
                <div class="badge-score" style="color:{color}">{score}<span style="font-size:1.2rem;color:#7d8590">/100</span></div>
                <div class="badge-score-label">Score de Riesgo</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Barra de progreso de riesgo
    color_bar = color
    st.markdown(f"""
    <div style='margin:0.5rem 0 1.5rem'>
        <div style='display:flex;justify-content:space-between;font-size:0.72rem;
                    color:#7d8590;margin-bottom:0.3rem'>
            <span>🟢 Sin riesgo</span>
            <span>🔴 Riesgo máximo</span>
        </div>
        <div style='background:#21262d;border-radius:6px;height:8px;overflow:hidden'>
            <div style='width:{score}%;height:100%;
                        background:linear-gradient(90deg,#2ea043,{color_bar});
                        border-radius:6px;transition:width 0.5s ease'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# VALIDACIÓN API KEY
# ─────────────────────────────────────────────
if not GEMINI_API_KEY:
    st.error("⚠️ No se encontró la GEMINI_API_KEY. Verificá tu archivo .env")
    st.code('GEMINI_API_KEY="tu-api-key-aqui"', language="bash")
    st.stop()

# ─────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 Analizá una publicación</div>', unsafe_allow_html=True)

entrada = st.text_input(
    "URL o ID",
    placeholder="https://articulo.mercadolibre.com.ar/MLA-1518988129-...",
    label_visibility="collapsed",
)

# ─────────────────────────────────────────────
# DATOS OPCIONALES
# ─────────────────────────────────────────────
with st.expander("➕ Datos de la publicación (opcional · mejora la precisión)", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        precio_input    = st.text_input("💰 Precio", placeholder="Ej: $64.990")
        ventas_input    = st.text_input("📦 Ventas", placeholder="Ej: +1000 vendidos")
    with col_b:
        reputacion_input = st.selectbox(
            "🏆 Reputación del vendedor",
            ["No informada", "MercadoLíder Platinum", "MercadoLíder Gold",
             "MercadoLíder", "Verde (buena)", "Amarilla (regular)",
             "Naranja (mala)", "Roja (muy mala)", "Sin reputación (nuevo)"]
        )
        condicion_input = st.selectbox("🔧 Condición", ["No informada", "Nuevo", "Usado"])
    observaciones_input = st.text_area(
        "📝 Observaciones",
        placeholder="Ej: precio muy bajo, fotos genéricas, pide contacto por WhatsApp...",
        height=70
    )

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    analizar = st.button("🛡️ Analizar Riesgo", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# ANÁLISIS PRINCIPAL
# ─────────────────────────────────────────────
if analizar:
    if not entrada:
        st.warning("Ingresá una URL o ID de Mercado Libre.")
    else:
        item_id = extraer_item_id(entrada)
        if not item_id:
            st.error("No se detectó un ID válido de Mercado Libre en la URL.")
            st.stop()

        nombre_url = extraer_nombre_url(entrada, item_id)

        # Info detectada
        col_id1, col_id2 = st.columns(2)
        with col_id1:
            st.markdown(f"""
            <div class="dato-card">
                <div class="label">ID detectado</div>
                <div class="value">🔖 {item_id}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_id2:
            if nombre_url:
                st.markdown(f"""
                <div class="dato-card">
                    <div class="label">Producto inferido</div>
                    <div class="value">📦 {nombre_url}</div>
                </div>
                """, unsafe_allow_html=True)

        datos_usuario = {
            "precio":        precio_input if precio_input else "",
            "ventas":        ventas_input if ventas_input else "",
            "reputacion":    reputacion_input if reputacion_input != "No informada" else "",
            "condicion":     condicion_input if condicion_input != "No informada" else "",
            "observaciones": observaciones_input if observaciones_input else "",
        }

        # Mostrar datos ingresados si los hay
        tiene_datos = any(v.strip() for v in datos_usuario.values())
        if tiene_datos:
            cols_datos = st.columns(4)
            campos = [
                ("💰", "Precio", datos_usuario.get("precio")),
                ("📦", "Ventas", datos_usuario.get("ventas")),
                ("🏆", "Reputación", datos_usuario.get("reputacion")),
                ("🔧", "Condición", datos_usuario.get("condicion")),
            ]
            for i, (icon, label, val) in enumerate(campos):
                if val:
                    with cols_datos[i % 4]:
                        st.markdown(f"""
                        <div class="dato-card">
                            <div class="label">{icon} {label}</div>
                            <div class="value">{val}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # Análisis
        st.markdown('<div class="section-title">🤖 Análisis con Gemini</div>', unsafe_allow_html=True)

        with st.spinner("Analizando publicación..."):
            analisis = analizar_con_gemini(item_id, entrada, datos_usuario)

        # Badge grande
        mostrar_badge(analisis)

        # Texto del análisis en caja oscura
        st.markdown(f"""
        <div class="analisis-box">
            {analisis.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        # Guardar estado
        clasificacion = "INFORMACIÓN INSUFICIENTE"
        for c in ["PELIGROSA", "SOSPECHOSA", "SEGURA"]:
            if c in analisis:
                clasificacion = c
                break

        st.session_state.historial_analisis.append({
            "id": item_id,
            "titulo": nombre_url or item_id,
            "clasificacion": clasificacion,
            "score": extraer_score(analisis),
        })

        st.session_state.contexto_publicacion = f"""
ID: {item_id}
Producto: {nombre_url or 'no disponible'}
Precio: {datos_usuario.get('precio') or 'no informado'}
Reputación: {datos_usuario.get('reputacion') or 'no informada'}
Ventas: {datos_usuario.get('ventas') or 'no informadas'}
Condición: {datos_usuario.get('condicion') or 'no informada'}
Resultado:
{analisis}
"""
        st.session_state.chat_mensajes = []

# ─────────────────────────────────────────────
# HISTORIAL
# ─────────────────────────────────────────────
if st.session_state.historial_analisis:
    st.markdown('<div class="section-title">📋 Historial de esta sesión</div>', unsafe_allow_html=True)
    emojis  = {"SEGURA": "✅", "SOSPECHOSA": "⚠️", "PELIGROSA": "🚨", "INFORMACIÓN INSUFICIENTE": "ℹ️"}
    colores = {"SEGURA": "#2ea043", "SOSPECHOSA": "#d29922", "PELIGROSA": "#e94560", "INFORMACIÓN INSUFICIENTE": "#7d8590"}
    cols    = st.columns(min(len(st.session_state.historial_analisis), 4))
    for i, item in enumerate(st.session_state.historial_analisis[-4:]):
        emoji  = emojis.get(item["clasificacion"], "ℹ️")
        color  = colores.get(item["clasificacion"], "#7d8590")
        score  = item.get("score", 0)
        with cols[i % 4]:
            st.markdown(f"""
            <div class="hist-card">
                <div style='font-size:1.8rem'>{emoji}</div>
                <div style='font-size:0.75rem;font-weight:700;color:#e6edf3;
                            margin:0.3rem 0;line-height:1.3'>{item['titulo'][:30]}</div>
                <div style='font-size:0.7rem;color:{color};font-weight:600'>{item['clasificacion']}</div>
                <div style='font-size:0.85rem;color:#7d8590;margin-top:0.2rem'>{score}/100</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">💬 FraudBot</div>', unsafe_allow_html=True)

if st.session_state.contexto_publicacion:
    st.markdown("""
    <div style='background:#f0fdf4;border:1px solid #22c55e;border-radius:8px;
                padding:0.6rem 1rem;font-size:0.85rem;color:#16a34a;margin-bottom:1rem'>
        🟢 FraudBot tiene el contexto de la publicación analizada
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='background:#f8fafc;border:1px solid #cbd5e1;border-radius:8px;
                padding:0.6rem 1rem;font-size:0.85rem;color:#64748b;margin-bottom:1rem'>
        💬 Analizá una publicación o hacé preguntas generales sobre compras seguras en ML
    </div>
    """, unsafe_allow_html=True)

for mensaje in st.session_state.chat_mensajes:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])

pregunta = st.chat_input("Preguntale a FraudBot...")

if pregunta:
    with st.chat_message("user"):
        st.write(pregunta)
    st.session_state.chat_mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("assistant"):
        with st.spinner(""):
            respuesta = chat_con_gemini(pregunta)
        st.write(respuesta)
    st.session_state.chat_mensajes.append({"role": "assistant", "content": respuesta})

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="fraud-footer">
    🛡️ <strong>FraudAlert ML</strong> · Proyecto Final · Prompt Engineering para Programadores · 2026<br>
    El análisis generado por IA es orientativo y no reemplaza la verificación manual antes de comprar.
</div>
""", unsafe_allow_html=True)
