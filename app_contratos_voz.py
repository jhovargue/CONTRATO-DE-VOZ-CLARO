import io
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, Rect, String

st.set_page_config(
    page_title="Formato de Contrato y Validación de Voz Claro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Evitar conflicto con el traductor automático
st.markdown(
    """
    <script>document.documentElement.setAttribute('translate', 'no');</script>
    <meta name="google" content="notranslate">
    """,
    unsafe_allow_html=True
)

# RUTA ABSOLUTA LOCAL EN DISCO C:\ (EVITA EL ERROR DE GOOGLE DRIVE H:)
DIR_LOCAL = Path.home() / ".claro_contratos"
try:
    DIR_LOCAL.mkdir(parents=True, exist_ok=True)
    DB_FILE_PATH = str(DIR_LOCAL / "registros_contratos.json")
except Exception:
    DB_FILE_PATH = os.path.join(tempfile.gettempdir(), "registros_contratos.json")

def cargar_registros():
    try:
        if os.path.exists(DB_FILE_PATH):
            with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def guardar_registros(registros):
    try:
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

if "db_clientes" not in st.session_state:
    st.session_state.db_clientes = cargar_registros()

# Valores actuales en memoria
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "asesor": "JHONNIER VARELA",
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "hora": datetime.now().strftime("%I:%M %p"),
        "ruc": "",
        "razon_social": "",
        "titular": "",
        "num_doc": "",
        "lugar_fecha_nac": "",
        "padres": "",
        "contacto": "",
        "direccion": "",
        "correo": "",
        "indicar": "SI ACEPTO",
        "tipo_solicitud": "Línea Nueva (Alta)",
        "num_portar": "",
        "operador": "MOVISTAR",
        "modalidad_porta": "POSTPAGO",
        "servicio_sel": "2 PLAY I+T",
        "tec_elegida": "FTTH",
        "internet_val": "400",
        "cant_mesh": 1,
        "cant_decos": 0
    }

# --- LOGO OFICIAL VECTORIAL CLARO EMPRESAS ---
SVG_CLARO_EMPRESAS = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 65" style="height: 38px; width: auto; display: block;">
  <text x="5" y="48" font-family="'Segoe UI', Arial, sans-serif" font-size="46" font-weight="900" fill="#DA291C" letter-spacing="-1.5">Claro</text>
  <rect x="108" y="11" width="4.5" height="13" rx="2.25" fill="#DA291C" />
  <rect x="119" y="21" width="4.5" height="13" rx="2.25" transform="rotate(45 121.25 27.5)" fill="#DA291C" />
  <rect x="123" y="38" width="13" height="4.5" rx="2.25" fill="#DA291C" />
  <text x="144" y="48" font-family="'Segoe UI', Arial, sans-serif" font-size="42" font-weight="900" fill="#000000" letter-spacing="-1">empresas</text>
</svg>
"""

def dibujar_logo_claro_empresas_pdf():
    d = Drawing(145, 30)
    d.add(String(2, 6, "Claro", fontName="Helvetica-Bold", fontSize=18, fillColor=colors.HexColor("#DA291C")))
    d.add(Rect(44, 18, 2, 5.5, rx=1, ry=1, fillColor=colors.HexColor("#DA291C"), strokeColor=None))
    d.add(Rect(48, 14, 5.5, 2, rx=1, ry=1, fillColor=colors.HexColor("#DA291C"), strokeColor=None))
    d.add(String(58, 6, "empresas", fontName="Helvetica-Bold", fontSize=16, fillColor=colors.black))
    return d

CATALOGO_PRECIOS = {
    "1 PLAY": {
        "200": {"reg": 69.0, "promo": 69.0, "bono": "400", "meses_promo": 0, "cloud_count": 2},
        "300": {"reg": 79.0, "promo": 79.0, "bono": "600", "meses_promo": 0, "cloud_count": 4},
        "400": {"reg": 89.0, "promo": 69.0, "bono": "1000", "meses_promo": 6, "cloud_count": 5},
        "800": {"reg": 100.0, "promo": 100.0, "bono": "1000", "meses_promo": 0, "cloud_count": 6},
        "1000": {"reg": 145.0, "promo": 119.0, "bono": "1000", "meses_promo": 6, "cloud_count": 6}
    },
    "1 PLAY TELF": {
        "NO APLICA": {"reg": 49.0, "promo": 49.0, "bono": "-", "meses_promo": 0, "cloud_count": 0}
    },
    "2 PLAY I+T": {
        "200": {"reg": 74.0, "promo": 74.0, "bono": "400", "meses_promo": 0, "cloud_count": 2},
        "300": {"reg": 84.0, "promo": 84.0, "bono": "600", "meses_promo": 0, "cloud_count": 4},
        "400": {"reg": 94.0, "promo": 74.0, "bono": "1000", "meses_promo": 6, "cloud_count": 5},
        "800": {"reg": 105.0, "promo": 105.0, "bono": "1000", "meses_promo": 0, "cloud_count": 6},
        "1000": {"reg": 150.0, "promo": 150.0, "bono": "1000", "meses_promo": 0, "cloud_count": 6}
    },
    "2 PLAY I+C": {
        "200": {"reg": 150.0, "promo": 89.0, "bono": "400", "meses_promo": 6, "cloud_count": 2},
        "300": {"reg": 160.0, "promo": 99.0, "bono": "600", "meses_promo": 6, "cloud_count": 4},
        "400": {"reg": 170.0, "promo": 109.0, "bono": "1000", "meses_promo": 6, "cloud_count": 5},
        "800": {"reg": 185.0, "promo": 185.0, "bono": "1000", "meses_promo": 0, "cloud_count": 6},
        "1000": {"reg": 230.0, "promo": 230.0, "bono": "1000", "meses_promo": 0, "cloud_count": 6}
    },
    "3 PLAY": {
        "200": {"reg": 155.0, "promo": 94.0, "bono": "400", "meses_promo": 6, "cloud_count": 2},
        "300": {"reg": 165.0, "promo": 104.0, "bono": "600", "meses_promo": 6, "cloud_count": 4},
        "400": {"reg": 175.0, "promo": 114.0, "bono": "1000", "meses_promo": 6, "cloud_count": 5},
        "800": {"reg": 190.0, "promo": 190.0, "bono": "1000", "meses_promo": 0, "cloud_count": 6},
        "1000": {"reg": 235.0, "promo": 164.0, "bono": "1000", "meses_promo": 6, "cloud_count": 6}
    }
}

def obtener_servicios_cloud(cantidad):
    lista = [
        "1. Claro Drive Negocio: 100 GB",
        "2. Claro Back Up: 15 GB para un equipo",
        "3. Seguridad Empresas: 1 Licencia Antivirus",
        "4. Email Empresas: 2 cuentas",
        "5. Tienda Virtual: Plan Comienza",
        "6. Microsoft 365: 1 Licencia Business Basic"
    ]
    return lista[:cantidad]

# --- GENERADOR DEL PDF NATIVO ---
def generar_pdf_contratos_completo(datos, plan_info):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm
    )
    story = []
    styles = getSampleStyleSheet()

    t_centro1 = ParagraphStyle("TC1", fontName="Helvetica-Bold", fontSize=11, leading=14, alignment=1, textColor=colors.black)
    p_body = ParagraphStyle("PBody", fontName="Helvetica", fontSize=8.5, leading=12.5, textColor=colors.black)
    p_bold = ParagraphStyle("PBold", fontName="Helvetica-Bold", fontSize=8.5, leading=12.5, textColor=colors.black)
    p_legal = ParagraphStyle("PLegal", fontName="Helvetica", fontSize=7.0, leading=9.5, textColor=colors.HexColor("#333333"), alignment=4)

    logo_izq = dibujar_logo_claro_empresas_pdf()
    col_cen = Paragraph("CONTRATO DE VOZ<br/>PLANES FIJOS CLARO EMPRESAS", t_centro1)

    t_header = Table([[logo_izq, col_cen]], colWidths=[6.0 * cm, 12.0 * cm])
    t_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)
    ]))
    story.append(t_header)
    story.append(Spacer(1, 0.3 * cm))

    texto_intro = f"Yo <b>{datos['asesor'] or '________________'}</b> Asesor (a) de Claro, voy a grabar su solicitud, hoy {datos['fecha']} a las {datos['hora']}. Por favor indique lo siguiente."
    story.append(Paragraph(texto_intro, p_body))
    story.append(Spacer(1, 0.25 * cm))

    lineas = [
        f"<b>1) Numero de RUC:</b> {datos['ruc'] or ''}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>2) Razón Social:</b> {datos['razon_social'] or ''}",
        f"<b>1) Su nombre y apellidos completos:</b> {datos['titular'] or ''}",
        f"<b>2) Tipo y número de documento de identidad:</b> {datos['num_doc'] or ''}",
        f"<b>3) Lugar de Nacimiento Y Fecha de Nacimiento:</b> {datos['lugar_fecha_nac'] or ''}",
        f"<b>4) Nombres de sus padres:</b> {datos['padres'] or ''}",
        f"<b>5) Número de contacto:</b> {datos['contacto'] or ''}",
        f"<b>6) Dirección de instalacion y facturación:</b> {datos['direccion'] or ''}",
        f"<b>7) Correo electrónico, ya que por ese medio se enviarán las condiciones de su plan y recibo del servicio:</b><br/>{datos['correo'] or ''}"
    ]

    for l in lineas:
        story.append(Paragraph(l, p_body))
        story.append(Spacer(1, 0.12 * cm))

    if plan_info["es_portabilidad"]:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph("<b>Por favor indique lo siguiente:</b>", p_body))
        story.append(Paragraph(f"• Número que desea portar: <b>{plan_info['num_portar']}</b>", p_body))
        story.append(Paragraph(f"• Empresa operadora actual: <b>{plan_info['operador']}</b>", p_body))
        story.append(Paragraph(f"Modalidad de servicio: <b>{plan_info['modalidad_porta']}</b>", p_body))
        story.append(Paragraph("La portabilidad es gratuita y demora 24 horas desde la solicitud.", p_body))
        story.append(Spacer(1, 0.2 * cm))
    else:
        story.append(Spacer(1, 0.2 * cm))

    nom_tec = "Fibra Óptica" if plan_info["tecnologia"] == "FTTH" else "Fibra Coaxial"
    p1 = f"Ud, solicitó el paquete <b>{plan_info['servicio']} {nom_tec}</b> con costo mensual de <b>S/{plan_info['tarifa_reg']:.2f}</b>. La contratación y activación del paquete está sujeta a la verificación de facilidades técnicas en el domicilio indicado. Para lo cual, CLARO se contactará con Ud. al número brindado para coordinar la fecha de la visita de instalación."
    story.append(Paragraph(p1, p_body))
    story.append(Spacer(1, 0.12 * cm))

    p_inst = "La tarifa de instalación es de <b>S/0</b>. El cual se pagará en 6 cuotas mensuales de <b>S/0</b> durante 6 meses, a partir del primer recibo. Si cancela el servicio antes de los 6 meses, deberá pagar el monto restante."
    story.append(Paragraph(p_inst, p_body))
    story.append(Spacer(1, 0.18 * cm))

    story.append(Paragraph("<b>El paquete incluye:</b>", p_bold))
    if plan_info["tiene_net"]:
        p_net = f"• Internet fijo con velocidad de <b>{plan_info['internet']} Mbps</b>. CLARO garantiza el 70% de la velocidad contratada."
        story.append(Paragraph(p_net, p_body))

    clouds = obtener_servicios_cloud(plan_info["cloud_count"])
    if clouds:
        p_cloud_tit = f"• Servicios Cloud: Recibirá {len(clouds)} herramientas digitales (servicios cloud), las cuales son:"
        story.append(Paragraph(p_cloud_tit, p_body))
        for c in clouds:
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{c}", p_body))
        story.append(Paragraph("Se comunicarán con usted para efectuar la activación del beneficio si lo requiere.", p_body))

    if plan_info["tiene_telf"]:
        p_telf = "• Telefonía fija con 5000 minutos para llamar a destinos nacionales fijo y móvil; 100 minutos para fijos de: EE.UU. (incluido Alaska y Hawái), México, Puerto Rico y Canadá."
        story.append(Paragraph(p_telf, p_body))

    cant_mesh = plan_info["cant_mesh"]
    if cant_mesh > 0:
        p_wifi = f"• Recibirá un servicio WIFI 360 sin costo que incluye {cant_mesh} equipo(s) repetidor(es) en préstamo."
        story.append(Paragraph(p_wifi, p_body))

    cant_decos = plan_info["cant_decos"]
    if plan_info["tiene_tv"] and cant_decos > 0:
        p_deco_txt = f"• Incluye {cant_decos} decodificador(es) adicional(es) para el servicio Claro TV."
        story.append(Paragraph(p_deco_txt, p_body))

    if plan_info["bono"] != "-":
        p_bono = f"• Por promoción los 12 primeros meses navegará a una velocidad de <b>{plan_info['bono']} Megabits por segundo</b>."
        story.append(Paragraph(p_bono, p_body))

    if plan_info["meses_promo"] > 0 and plan_info["tarifa_promo"] < plan_info["tarifa_reg"]:
        p_promo = f"• Además, por los {plan_info['meses_promo']} primeros meses <b>DEBERÁ PAGAR S/ {plan_info['tarifa_promo']:.2f} al mes</b>. Luego se le cobrará la tarifa regular. Los servicios adicionales no están incluidos en la promoción."
        story.append(Paragraph(p_promo, p_body))

    story.append(Paragraph("Perderá la promoción si solicita la baja de uno o más de los servicios contratados, realice un cambio a un plan inferior, cambio de titularidad o cambio de número.", p_body))
    story.append(Spacer(1, 0.18 * cm))

    # EQUIPOS EN PRÉSTAMO CON ONT O EMTA SEGÚN LA TECNOLOGÍA
    story.append(Paragraph("<b>Ud. obtendrá equipos que serán entregados en préstamo y que deberá devolver en su totalidad al término de su contrato:</b>", p_bold))
    if plan_info["tiene_telf"]:
        story.append(Paragraph("• 1 equipo telefónico con pantalla", p_body))
    if plan_info["tiene_net"]:
        tipo_router_pdf = "ONT" if plan_info["tecnologia"] == "FTTH" else "EMTA"
        story.append(Paragraph(f"• 1 equipo router {tipo_router_pdf} Incluye 4 puertos Ethernet y conexión Wifi", p_body))
    if cant_mesh > 0:
        story.append(Paragraph(f"• {cant_mesh} equipo(s) repetidor(es) Wifi 360", p_body))
    if plan_info["tiene_tv"]:
        total_decos = 1 + cant_decos
        story.append(Paragraph(f"• {total_decos} equipo(s) decodificador(es) Claro TV", p_body))
    story.append(Paragraph("De no devolverlos, deberá pagar una penalidad.", p_body))
    story.append(Spacer(1, 0.18 * cm))

    if clouds:
        p_reglas_cloud = (
            "Para activar el servicio Cloud es obligatorio brindar: Nombre, número, correo de la persona de contacto y correo empresarial.<br/>"
            "• Para velocidades desde 400 Mbps, si el cliente tiene Email Empresas y Microsoft 365, debe contar con un dominio propio para cada servicio; de lo contrario, solo practicale elegir uno (son excluyentes).<br/>"
            "• Para Email Empresas, Microsoft 365 y Tienda Virtual, el cliente debe contar con dominio propio. Si no tiene uno, Claro entregará un dominio .com gratis por 12 meses.<br/>"
            "<b>Más información sobre Servicios Cloud: https://www.claro.com.pe/negocios/soluciones/cloud/</b>"
        )
        story.append(Paragraph(p_reglas_cloud, p_legal))
        story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph(f'<b>"PARA COMPLETAR EL REGISTRO DE SU SOLICITUD, POR FAVOR, DIGA: \'{datos["indicar"]}\'".</b>', p_bold))
    story.append(Spacer(1, 0.15 * cm))

    # Cláusula de Protección de Datos Personales
    p_datos_personales = (
        "Le informo que CLARO, ubicado en Av. Nicolás Arriola N° 480, Santa Catalina, La Victoria, Lima, es el responsable del tratamiento "
        "de sus datos, los cuales se registran en el banco de datos de 'Clientes' para gestionar la contratación de los servicios solicitados. "
        "CLARO podrá compartirlos con proveedores que realizan servicios por encargo, los cuales podrá conocer en la Política de Privacidad "
        "publicada en Claro.pe. Los datos brindados son necesarios para atender su solicitud, de lo contrario no podría ser atendida. "
        "Podrá ejercer sus derechos de Acceso, Rectificación, Cancelación y Oposición al correo electrónico proteccióndedatos@claro.com.pe."
    )
    story.append(Paragraph(p_datos_personales, p_legal))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("<b>Su código de solicitud es su número de documento de identidad</b>", p_bold))
    story.append(Paragraph("<b>¡Te damos la bienvenida A LA FAMILIA CLARO!</b>", ParagraphStyle("Bienvenida", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#DA291C"))))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Encabezado visual
st.markdown(
    """
    <div style="background-color: #0d0d0e; padding: 12px 20px; border-radius: 8px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #DA291C;">CLARO EMPRESAS <span style="color: white; font-size: 16px;">| Formato Completo de Contrato de Voz Oficial</span></h3>
        <span style="font-size: 12px; color: #bbb;">Conforme a Plantilla Legal y Locución</span>
    </div>
    """,
    unsafe_allow_html=True
)

# GESTIÓN Y PERSISTENCIA DE REGISTROS
st.markdown("### 🗂️ Registro y Consulta de Clientes Guardados")
col_reg1, col_reg2, col_reg3 = st.columns([2.5, 1, 1])

opciones_clientes = ["-- Nuevo Cliente (Formulario Vacío) --"] + [
    f"{k} · {v.get('razon_social', '')}" for k, v in st.session_state.db_clientes.items()
]

with col_reg1:
    cliente_seleccionado = st.selectbox("Seleccionar Cliente Guardado para Cargar / Modificar:", opciones_clientes)

if cliente_seleccionado != "-- Nuevo Cliente (Formulario Vacío) --":
    ruc_elegido = cliente_seleccionado.split(" · ")[0].strip()
    if st.session_state.get("last_loaded_ruc") != ruc_elegido:
        datos_guardados = st.session_state.db_clientes[ruc_elegido]
        st.session_state.form_data.update(datos_guardados)
        st.session_state.last_loaded_ruc = ruc_elegido
        st.rerun()

with col_reg2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🗑️ Eliminar Registro", use_container_width=True):
        if cliente_seleccionado != "-- Nuevo Cliente (Formulario Vacío) --":
            ruc_a_borrar = cliente_seleccionado.split(" · ")[0].strip()
            if ruc_a_borrar in st.session_state.db_clientes:
                del st.session_state.db_clientes[ruc_a_borrar]
                guardar_registros(st.session_state.db_clientes)
                st.session_state.last_loaded_ruc = None
                st.success("Cliente eliminado del registro.")
                st.rerun()

with col_reg3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("✨ Formulario Nuevo", use_container_width=True):
        st.session_state.form_data = {
            "asesor": "JHONNIER VARELA",
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "hora": datetime.now().strftime("%I:%M %p"),
            "ruc": "", "razon_social": "", "titular": "", "num_doc": "",
            "lugar_fecha_nac": "", "padres": "", "contacto": "", "direccion": "",
            "correo": "", "indicar": "SI ACEPTO", "tipo_solicitud": "Línea Nueva (Alta)",
            "num_portar": "", "operador": "MOVISTAR", "modalidad_porta": "POSTPAGO",
            "servicio_sel": "2 PLAY I+T", "tec_elegida": "FTTH", "internet_val": "400",
            "cant_mesh": 1, "cant_decos": 0
        }
        st.session_state.last_loaded_ruc = None
        st.rerun()

st.markdown("---")

col_form, col_preview = st.columns([1.05, 1.35], gap="medium")
fd = st.session_state.form_data

# --- COLUMNA 1: FORMULARIO ---
with col_form:
    st.markdown("#### 📝 Llenar / Modificar Datos")

    with st.expander("🎙️ 1. Datos del Asesor y Grabación", expanded=True):
        fd["asesor"] = st.text_input("Nombre del Asesor (a):", value=fd["asesor"])
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            fd["fecha"] = st.text_input("Fecha:", value=fd["fecha"])
        with c_f2:
            fd["hora"] = st.text_input("Hora:", value=fd["hora"])

    with st.expander("🏢 2. Datos de la Empresa y RUC", expanded=True):
        fd["ruc"] = st.text_input("Número de RUC:", value=fd["ruc"], placeholder="Ej. 20601816254", max_chars=11)
        fd["razon_social"] = st.text_input("Razón Social:", value=fd["razon_social"], placeholder="Ej. RINCONCITO PUNTO Y SABOR S.A.C.")

    with st.expander("👤 3. Datos del Titular y Preguntas de Seguridad", expanded=True):
        fd["titular"] = st.text_input("Su nombre y apellidos completos:", value=fd["titular"], placeholder="Ej. WADNER MATEO FLORES CANTARO")
        fd["num_doc"] = st.text_input("Tipo y número de documento de identidad:", value=fd["num_doc"], placeholder="Ej. 09353910")
        lfn_val = fd.get("lugar_fecha_nac", "").replace('"', '')
        fd["lugar_fecha_nac"] = st.text_input("Lugar y Fecha de Nacimiento:", value=lfn_val, placeholder="Ej. JUNIN - HUANCAYO 18/05/1967")
        fd["padres"] = st.text_input("Nombres de sus padres:", value=fd["padres"], placeholder="Ej. JUSTINA y BONIFACIO")
        fd["contacto"] = st.text_input("Número de contacto:", value=fd["contacto"], placeholder="Ej. 993083718", max_chars=9)

    with st.expander("📍 4. Dirección, Facturación y Conformidad", expanded=True):
        fd["direccion"] = st.text_area("Dirección de instalación y facturación:", value=fd["direccion"], placeholder="Ej. CALLE FRANCISCO LAZO NRO. 2055 LINCE", height=60)
        fd["correo"] = st.text_input("Correo electrónico:", value=fd["correo"], placeholder="Ej. contacto@empresa.com")
        idx_ind = 0 if fd["indicar"] == "SI ACEPTO" else 1
        fd["indicar"] = st.selectbox("INDICAR CONFORMIDAD:", ["SI ACEPTO", "NO ACEPTO"], index=idx_ind)

    with st.expander("📞 5. Modalidad de Instalación (Alta o Portabilidad)", expanded=True):
        idx_tsol = 0 if fd["tipo_solicitud"] == "Línea Nueva (Alta)" else 1
        fd["tipo_solicitud"] = st.radio("Tipo de Solicitud:", ["Línea Nueva (Alta)", "Portabilidad"], index=idx_tsol, horizontal=True)

        if fd["tipo_solicitud"] == "Portabilidad":
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                fd["num_portar"] = st.text_input("Número que desea portar:", value=fd["num_portar"], placeholder="Ej. 12350253", max_chars=9)
                lista_op = ["MOVISTAR", "ENTEL", "BITEL"]
                idx_op = lista_op.index(fd["operador"]) if fd["operador"] in lista_op else 0
                fd["operador"] = st.selectbox("Empresa operadora actual:", lista_op, index=idx_op)
            with col_p2:
                lista_mod = ["POSTPAGO", "CONTROL", "PREPAGO"]
                idx_mod = lista_mod.index(fd["modalidad_porta"]) if fd["modalidad_porta"] in lista_mod else 0
                fd["modalidad_porta"] = st.selectbox("Modalidad de servicio:", lista_mod, index=idx_mod)
        else:
            fd["num_portar"] = ""
            fd["operador"] = ""
            fd["modalidad_porta"] = ""

    with st.expander("🌐 6. Paquete, Tecnología y Tarifas", expanded=True):
        lista_serv = ["1 PLAY", "1 PLAY TELF", "2 PLAY I+C", "2 PLAY I+T", "3 PLAY"]
        idx_serv = lista_serv.index(fd["servicio_sel"]) if fd["servicio_sel"] in lista_serv else 3
        fd["servicio_sel"] = st.selectbox("SERVICIO:", lista_serv, index=idx_serv)

        lista_tec = ["FTTH", "HFC"]
        idx_tec = lista_tec.index(fd["tec_elegida"]) if fd["tec_elegida"] in lista_tec else 0
        fd["tec_elegida"] = st.selectbox("Tecnología:", lista_tec, index=idx_tec)

        tiene_net = fd["servicio_sel"] in ["1 PLAY", "2 PLAY I+C", "2 PLAY I+T", "3 PLAY"]
        if tiene_net:
            lista_spd = ["200", "300", "400", "800", "1000"]
            idx_spd = lista_spd.index(fd["internet_val"]) if fd["internet_val"] in lista_spd else 2
            fd["internet_val"] = st.selectbox("internet (Velocidad Mbps):", lista_spd, index=idx_spd)
            tarifa_obj = CATALOGO_PRECIOS.get(fd["servicio_sel"], CATALOGO_PRECIOS["1 PLAY"]).get(fd["internet_val"], {"reg": 94.0, "promo": 74.0, "bono": "1000", "meses_promo": 6, "cloud_count": 5})
        else:
            fd["internet_val"] = "NO APLICA"
            tarifa_obj = CATALOGO_PRECIOS["1 PLAY TELF"]["NO APLICA"]
            st.selectbox("internet (Velocidad Mbps):", ["NO APLICA (Solo Telefonía)"], disabled=True)

        if tarifa_obj["meses_promo"] > 0 and tarifa_obj["promo"] < tarifa_obj["reg"]:
            st.info(f"💡 **Tarifa Regular:** S/ {tarifa_obj['reg']:.2f} | **Promo:** S/ {tarifa_obj['promo']:.2f} por {tarifa_obj['meses_promo']} meses | **Bono:** {tarifa_obj['bono']} Mbps")
        else:
            st.info(f"💡 **Tarifa Mensual:** S/ {tarifa_obj['reg']:.2f}")

    with st.expander("📦 7. Repetidores Wi-Fi 360 (MESH) y Decos Adicionales", expanded=True):
        col_eq1, col_eq2 = st.columns(2)
        with col_eq1:
            fd["cant_mesh"] = st.number_input("Cantidad de Repetidores MESH:", min_value=0, max_value=5, value=fd["cant_mesh"], step=1)
        with col_eq2:
            tiene_tv = fd["servicio_sel"] in ["2 PLAY I+C", "3 PLAY"]
            if tiene_tv:
                fd["cant_decos"] = st.number_input("Decodificadores TV Adicionales:", min_value=0, max_value=4, value=fd["cant_decos"], step=1)
            else:
                fd["cant_decos"] = 0
                st.selectbox("Decos TV Adicionales:", ["NO APLICA (Sin TV)"], disabled=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Guardar / Actualizar Datos del Cliente", type="primary", use_container_width=True):
        if not fd["ruc"].strip():
            st.warning("Ingresa un número de RUC para guardar el cliente.")
        else:
            st.session_state.db_clientes[fd["ruc"].strip()] = dict(fd)
            guardar_registros(st.session_state.db_clientes)
            st.success(f"¡Registro guardado exitosamente para {fd['ruc']} - {fd['razon_social']}!")
            st.rerun()

tiene_telf = fd["servicio_sel"] in ["1 PLAY TELF", "2 PLAY I+T", "3 PLAY"]
tiene_tv = fd["servicio_sel"] in ["2 PLAY I+C", "3 PLAY"]

datos_actuales = {
    "asesor": fd["asesor"],
    "fecha": fd["fecha"],
    "hora": fd["hora"],
    "ruc": fd["ruc"],
    "razon_social": fd["razon_social"],
    "titular": fd["titular"],
    "num_doc": fd["num_doc"],
    "lugar_fecha_nac": fd["lugar_fecha_nac"],
    "padres": fd["padres"],
    "contacto": fd["contacto"],
    "direccion": fd["direccion"],
    "correo": fd["correo"],
    "indicar": fd["indicar"]
}

plan_info_actual = {
    "servicio": fd["servicio_sel"],
    "tecnologia": fd["tec_elegida"],
    "internet": fd["internet_val"],
    "tarifa_reg": tarifa_obj["reg"],
    "tarifa_promo": tarifa_obj["promo"],
    "bono": tarifa_obj["bono"],
    "meses_promo": tarifa_obj["meses_promo"],
    "cloud_count": tarifa_obj["cloud_count"],
    "tiene_telf": tiene_telf,
    "tiene_tv": tiene_tv,
    "tiene_net": tiene_net,
    "cant_mesh": fd["cant_mesh"],
    "cant_decos": fd["cant_decos"],
    "es_portabilidad": (fd["tipo_solicitud"] == "Portabilidad"),
    "num_portar": fd["num_portar"],
    "operador": fd["operador"],
    "modalidad_porta": fd["modalidad_porta"]
}

# --- COLUMNA 2: SELECTOR DE VISTA Y VISUALIZACIÓN ---
with col_preview:
    st.markdown("#### 👁️ Seleccionar Vista Previa")
    vista_seleccionada = st.radio(
        "Modo de vista:",
        ["📋 Validación de Datos (Puntos 1 al 7)", "📑 Contrato de Voz Completo"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if vista_seleccionada == "📋 Validación de Datos (Puntos 1 al 7)":
        html_validacion_separada = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 16px;
                background-color: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #111111;
            }}
            .caja-validacion {{
                background: #ffffff;
                border: 2px solid #0056b3;
                border-radius: 6px;
                padding: 30px 34px;
                line-height: 1.8;
                font-size: 14.5px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.12);
            }}
            .linea-val {{
                margin-bottom: 12px;
            }}
            .linea-val b {{
                color: #000000;
                font-weight: 700;
            }}
            .correo-link {{
                color: #0044cc;
                text-decoration: underline;
                font-weight: 500;
            }}
            .box-indicar {{
                margin-top: 24px;
                background-color: #ffff00;
                padding: 8px 14px;
                display: inline-block;
                font-weight: 900;
                color: #d90000;
                font-size: 14px;
                border-radius: 3px;
                border: 1px solid #e6e600;
            }}
        </style>
        </head>
        <body>
            <div class="caja-validacion">
                <div class="linea-val">
                    <b>1) Numero de RUC:</b> {fd['ruc'] or ''}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>2) Razón Social:</b> {fd['razon_social'] or ''}
                </div>
                <div class="linea-val">
                    <b>1) Su nombre y apellidos completos:</b> {fd['titular'] or ''}
                </div>
                <div class="linea-val">
                    <b>2) Tipo y número de documento de identidad:</b> {fd['num_doc'] or ''}
                </div>
                <div class="linea-val">
                    <b>3) Lugar de Nacimiento Y Fecha de Nacimiento:</b> {fd['lugar_fecha_nac'] or ''}
                </div>
                <div class="linea-val">
                    <b>4) Nombres de sus padres:</b> {fd['padres'] or ''}
                </div>
                <div class="linea-val">
                    <b>5) Número de contacto:</b> {fd['contacto'] or ''}
                </div>
                <div class="linea-val">
                    <b>6) Dirección de instalacion y facturación:</b> {fd['direccion'] or ''}
                </div>
                <div class="linea-val">
                    <b>7) Correo electrónico, ya que por ese medio se enviarán las condiciones de su plan y recibo del servicio:</b><br>
                    <span class="correo-link">{fd['correo'] or ''}</span>
                </div>
                <div class="box-indicar">
                    INDICAR: {fd['indicar']}
                </div>
            </div>
        </body>
        </html>
        """
        components.html(html_validacion_separada, height=520, scrolling=True)

    else:
        nom_tec_html = "Fibra Óptica" if fd["tec_elegida"] == "FTTH" else "Fibra Coaxial"
        lista_cloud = obtener_servicios_cloud(tarifa_obj["cloud_count"])
        cloud_items_html = "".join([f"<div>&nbsp;&nbsp;&nbsp;&nbsp;{c}</div>" for c in lista_cloud])

        portabilidad_html = ""
        if fd["tipo_solicitud"] == "Portabilidad":
            portabilidad_html = f"""
            <div style="margin-top: 14px; margin-bottom: 14px; padding: 10px 14px; background-color: #fcfcfc; border-left: 3px solid #DA291C;">
                <div style="font-weight: bold; margin-bottom: 6px;">Por favor indique lo siguiente:</div>
                <div>• Número que desea portar: <b>{fd['num_portar'] or '_________'}</b></div>
                <div>• Empresa operadora actual: <b>{fd['operador'] or '_________'}</b></div>
                <div>Modalidad de servicio: <b>{fd['modalidad_porta'] or '_________'}</b></div>
                <div style="margin-top: 4px;">La portabilidad es gratuita y demora 24 horas desde la solicitud.</div>
            </div>
            """

        telf_html = ""
        if tiene_telf:
            telf_html = """
            <div style="margin-top: 6px;">• Telefonía fija con 5000 minutos para llamar a destinos nacionales fijo y móvil 100 minutos para fijos de: E.E.U.U.(incluido Alaska y Hawái), México, Puerto Rico y Canadá.</div>
            """

        wifi_html = ""
        if fd["cant_mesh"] > 0:
            wifi_html = f"""
            <div style="margin-top: 6px;">• Recibirá un servicio WIFI 360 sin costo que incluye {fd['cant_mesh']} equipo(s) repetidor(es) en préstamo.</div>
            """

        decos_adc_html = ""
        if tiene_tv and fd["cant_decos"] > 0:
            decos_adc_html = f"""
            <div style="margin-top: 6px;">• Incluye {fd['cant_decos']} decodificador(es) adicional(es) para el servicio Claro TV.</div>
            """

        promo_html = ""
        if tarifa_obj["meses_promo"] > 0 and tarifa_obj["promo"] < tarifa_obj["reg"]:
            promo_html = f"""
            <div style="margin-top: 6px;">• Además, por los {tarifa_obj['meses_promo']} primeros meses <b>DEBERÁ PAGAR S/ {tarifa_obj['promo']:.2f} al mes</b>. Luego se le cobrará la tarifa regular. Los servicios adicionales no están incluidos en la promoción.</div>
            """

        tipo_router_html = "ONT" if fd["tec_elegida"] == "FTTH" else "EMTA"
        equipos_prestamo_html = ""
        if tiene_telf:
            equipos_prestamo_html += "<div>• 1 equipo telefónico con pantalla</div>"
        if tiene_net:
            equipos_prestamo_html += f"<div>• 1 equipo router {tipo_router_html} Incluye 4 puertos Ethernet y conexión Wifi</div>"
        if fd["cant_mesh"] > 0:
            equipos_prestamo_html += f"<div>• {fd['cant_mesh']} equipo(s) repetidor(es) Wifi 360</div>"
        if tiene_tv:
            total_decos = 1 + fd["cant_decos"]
            equipos_prestamo_html += f"<div>• {total_decos} equipo(s) decodificador(es) Claro TV</div>"

        html_contrato_exacto = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 12px;
                background-color: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #111111;
            }}
            .hoja {{
                background: #ffffff;
                border: 2px solid #0056b3;
                border-radius: 6px;
                padding: 30px 34px;
                line-height: 1.55;
                font-size: 13.5px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.15);
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #eaeaea;
                padding-bottom: 12px;
                margin-bottom: 16px;
            }}
            .titulo-centro {{
                text-align: right;
            }}
            .titulo-centro .t1 {{
                font-weight: 800;
                font-size: 14px;
                letter-spacing: 0.5px;
                color: #000;
            }}
            .titulo-centro .t2 {{
                font-weight: bold;
                font-size: 11.5px;
                color: #333;
                margin-top: 2px;
            }}
            .renglon {{
                margin-bottom: 8px;
            }}
            .legal {{
                font-size: 11px;
                color: #444;
                line-height: 1.4;
                text-align: justify;
                margin-top: 10px;
            }}
        </style>
        </head>
        <body>
            <div class="hoja">
                <div class="header">
                    <div>{SVG_CLARO_EMPRESAS}</div>
                    <div class="titulo-centro">
                        <div class="t1">CONTRATO DE VOZ</div>
                        <div class="t2">PLANES FIJOS CLARO EMPRESAS</div>
                    </div>
                </div>

                <p style="margin: 0 0 14px 0; text-align: justify;">
                    Yo <b>{fd['asesor'] or '________________'}</b> Asesor (a) de Claro, voy a grabar su solicitud, hoy {fd['fecha']} a las {fd['hora']}. Por favor indique lo siguiente.
                </p>

                <div class="renglon"><b>1) Numero de RUC:</b> {fd['ruc']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>2) Razón Social:</b> {fd['razon_social']}</div>
                <div class="renglon"><b>1) Su nombre y apellidos completos:</b> {fd['titular']}</div>
                <div class="renglon"><b>2) Tipo y número de documento de identidad:</b> {fd['num_doc']}</div>
                <div class="renglon"><b>3) Lugar de Nacimiento Y Fecha de Nacimiento:</b> {fd['lugar_fecha_nac']}</div>
                <div class="renglon"><b>4) Nombres de sus padres:</b> {fd['padres']}</div>
                <div class="renglon"><b>5) Número de contacto:</b> {fd['contacto']}</div>
                <div class="renglon"><b>6) Dirección de instalacion y facturación:</b> {fd['direccion']}</div>
                <div class="renglon">
                    <b>7) Correo electrónico, ya que por ese medio se enviarán las condiciones de su plan y recibo del servicio:</b><br>
                    <span style="color: #0044cc; text-decoration: underline;">{fd['correo']}</span>
                </div>

                {portabilidad_html}

                <hr style="border: 0; border-top: 1px solid #ddd; margin: 16px 0;">

                <p style="margin: 0 0 10px 0; text-align: justify;">
                    Ud, solicitó el paquete <b>{fd['servicio_sel']} {nom_tec_html}</b> con costo mensual de <b>S/{tarifa_obj['reg']:.2f}</b>. La contratación y activación del paquete está sujeta a la verificación de facilidades técnicas en el domicilio indicado. Para lo cual, CLARO se contactará con Ud. al número brindado para coordinar la fecha de la visita de instalación.
                </p>

                <p style="margin: 0 0 10px 0; text-align: justify;">
                    La tarifa de instalación es de <b>S/0</b>. El cual se pagará en 6 cuotas mensuales de <b>S/0</b> durante 6 meses, a partir del primer recibo. Si cancela el servicio antes de los 6 meses, deberá pagar el monto restante.
                </p>

                <div style="font-weight: bold; margin-bottom: 4px;">El paquete incluye:</div>
                {'<div>• Internet fijo con velocidad de <b>' + str(fd['internet_val']) + ' Mbps</b>. CLARO garantiza el 70% de la velocidad contratada.</div>' if tiene_net else ''}
                {('<div style="margin-top: 4px;">• Servicios Cloud: Recibirá ' + str(len(lista_cloud)) + ' herramientas digitales (servicios cloud), las cuales son:</div>' + cloud_items_html + '<div style="font-size: 12px; color: #555; margin-top: 2px;">Se comunicarán con usted para efectuar la activación del beneficio si lo requiere.</div>') if lista_cloud else ''}

                {telf_html}
                {wifi_html}
                {decos_adc_html}
                {('<div style="margin-top: 6px;">• Por promoción los 12 primeros meses navegará a una velocidad de <b>' + str(tarifa_obj["bono"]) + ' Megabits por segundo</b>.</div>') if tarifa_obj["bono"] != "-" else ''}
                {promo_html}
                <div style="margin-top: 6px; font-size: 12px; color: #555;">Perderá la promoción si solicita la baja de uno o más de los servicios contratados, realice un cambio a un plan inferior, cambio de titularidad o cambio de número.</div>

                <div style="font-weight: bold; margin-top: 12px; margin-bottom: 4px;">Ud. obtendrá equipos que serán entregados en préstamo y que deberá devolver en su totalidad al término de su contrato:</div>
                {equipos_prestamo_html}
                <div style="font-size: 12px; color: #555;">De no devolverlos, deberá pagar una penalidad.</div>

                {('<div class="legal">Para activar el servicio Cloud es obligatorio brindar la siguiente información: Nombre, número, correo de la persona de contacto y correo empresarial.<br/>• Para velocidades desde 400 Mbps, si el cliente tiene Email Empresas y Microsoft 365, debe contar con un dominio propio para cada servicio; de lo contrario, solo practicale elegir uno (son excluyentes).<br/>• Para Email Empresas, Microsoft 365 y Tienda Virtual, el cliente debe contar con dominio propio. Si no tiene uno, Claro entregará un dominio .com gratis por 12 meses.<br/><b>Más información sobre Servicios Cloud: https://www.claro.com.pe/negocios/soluciones/cloud/</b></div>') if lista_cloud else ''}

                <div style="margin-top: 14px; background-color: #ffff00; padding: 6px 10px; display: inline-block; font-weight: bold; color: red;">
                    "PARA COMPLETAR EL REGISTRO DE SU SOLICITUD, POR FAVOR, DIGA: '{fd['indicar']}'".
                </div>

                <div class="legal" style="margin-top: 10px;">
                    Le informo que CLARO, ubicado en Av. Nicolás Arriola N° 480, Santa Catalina, La Victoria, Lima, es el responsable del tratamiento de sus datos, los cuales se registran en el banco de datos de "Clientes" para gestionar la contratación de los servicios solicitados. CLARO podrá compartirlos con proveedores que realizan servicios por encargo, los cuales podrá conocer en la Política de Privacidad publicada en Claro.pe. Los datos brindados son necesarios para atender su solicitud, de lo contrario no podría ser atendida. Podrá ejercer sus derechos de Acceso, Rectificación, Cancelación y Oposición al correo electrónico proteccióndedatos@claro.com.pe.
                </div>

                <div style="margin-top: 12px; font-weight: bold;">
                    Su código de solicitud es su número de documento de identidad
                </div>
                <div style="margin-top: 4px; font-weight: bold; color: #DA291C; font-size: 14px;">
                    ¡Te damos la bienvenida A LA FAMILIA CLARO!
                </div>
            </div>
        </body>
        </html>
        """
        components.html(html_contrato_exacto, height=750, scrolling=True)

    st.markdown("<br>", unsafe_allow_html=True)

    pdf_bytes = generar_pdf_contratos_completo(datos_actuales, plan_info_actual)
    nombre_archivo = f"Contrato_Voz_{fd['ruc'] if fd['ruc'].strip() else 'Borrador'}.pdf"

    st.download_button(
        label="📥 Descargar Contrato de Voz en PDF (Formato Oficial Completo)",
        data=pdf_bytes,
        file_name=nombre_archivo,
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )