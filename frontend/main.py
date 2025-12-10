import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
import time

st.set_page_config(layout="wide", page_title="Clínica Veterinaria")

# ------------------- CONFIG + HELPERS -------------------
API_BASE = st.secrets.get("API_BASE", "http://127.0.0.1:8000").rstrip("/")
ROUTE_CLIENTES = "/clientes/"
ROUTE_MASCOTAS = "/mascotas/"
ROUTE_CITAS = "/citas/"
ROUTE_FACTURAS = "/facturas/"
ROUTE_TOKEN = "/auth/token"
ROUTE_INFORMES_INGRESOS = "/informes/ingresos"

# Ensure session_state keys
if "token" not in st.session_state:
    st.session_state["token"] = None
if "email" not in st.session_state:
    st.session_state["email"] = ""
if "last_api_error" not in st.session_state:
    st.session_state["last_api_error"] = None

def headers_with_token():
    t = st.session_state.get("token")
    return {"Authorization": f"Bearer {t}"} if t else {}

def api_get(path, params=None):
    try:
        r = requests.get(API_BASE + path, headers=headers_with_token(), params=params, timeout=6)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        st.session_state["last_api_error"] = f"{r.status_code}: {r.text}"
        return None
    except Exception as e:
        st.session_state["last_api_error"] = str(e)
        return None

def api_post(path, payload):
    try:
        r = requests.post(API_BASE + path, headers={**headers_with_token(), "Content-Type":"application/json"}, json=payload, timeout=6)
        r.raise_for_status()
        # Return JSON if exists, else True
        try:
            return r.json()
        except:
            return True
    except requests.HTTPError as e:
        st.session_state["last_api_error"] = f"{r.status_code}: {r.text}"
        return None
    except Exception as e:
        st.session_state["last_api_error"] = str(e)
        return None

def api_delete(path):
    try:
        r = requests.delete(API_BASE + path, headers=headers_with_token(), timeout=6)
        r.raise_for_status()
        return True
    except requests.HTTPError as e:
        st.session_state["last_api_error"] = f"{r.status_code}: {r.text}"
        return False
    except Exception as e:
        st.session_state["last_api_error"] = str(e)
        return False

def short_token():
    t = st.session_state.get("token")
    return (t[:40] + "…") if t else "(no token)"

# ------------------- SIDEBAR: AUTH + NAV -------------------
with st.sidebar:
    st.title("Clínica Veterinaria")
    st.markdown("Ir a:")
    # keep nav visually left but accessible
    page = st.radio("", ("Inicio","Pacientes","Citas","Facturación","Análisis"), index=0)
    st.divider()

    st.header("Autenticación")
    email_input = st.text_input("Email", value=st.session_state.get("email",""))
    password_input = st.text_input("Password", type="password", value="", help="Password para obtener token")
    if st.button("Obtener token"):
        # form login to /auth/token (OAuth2PasswordRequestForm)
        try:
            resp = requests.post(
                API_BASE + ROUTE_TOKEN,
                data={"username": email_input, "password": password_input},
                headers={"Content-Type":"application/x-www-form-urlencoded"},
                timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("access_token")
                if token:
                    st.session_state["token"] = token
                    st.session_state["email"] = email_input
                    st.success("Token almacenado.")
                else:
                    st.error("Respuesta sin token.")
            else:
                st.error(f"Error obteniendo token: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"Excepción: {e}")

    st.write("Token:")
    st.code(short_token())
    if st.button("Cerrar sesión"):
        st.session_state["token"] = None
        st.session_state["email"] = ""
        st.success("Sesión cerrada")
    st.divider()
    st.markdown("API base:")
    st.write(API_BASE)
    if st.session_state.get("last_api_error"):
        st.error(f"Último error API: {st.session_state.get('last_api_error')}")
# ------------------- END SIDEBAR -------------------

# ------------------- MAIN CONTENT -------------------
st.markdown("<br/>", unsafe_allow_html=True)

def page_inicio():
    st.title("Clínica Veterinaria")
    st.write("Interfaz mínima para la API. Use el menú para navegar.")
    st.markdown(f"API base: `{API_BASE}`")
    st.info("Necesitas autenticarte para operaciones protegidas. Usa la sección 'Autenticación' en la barra lateral.")

def page_pacientes():
    st.title("Pacientes / Clientes y Mascotas")

    # CLIENTES
    st.subheader("Listado de clientes")
    clientes_data = api_get(ROUTE_CLIENTES)
    if clientes_data is None:
        st.error(f"Error listando clientes: {st.session_state.get('last_api_error')}")
    else:
        dfc = pd.DataFrame(clientes_data)
        if not dfc.empty:
            cols_show = [c for c in ("dni","name","email","phone","id") if c in dfc.columns]
            st.dataframe(dfc[cols_show].rename(columns={"name":"Nombre","dni":"DNI","phone":"Teléfono","id":"ID","email":"Email"}))
        else:
            st.info("No hay clientes registrados.")

    st.markdown("---")
    # Crear cliente (phone requested)
    st.subheader("Crear nuevo cliente")
    with st.form("form_crear_cliente"):
        dni = st.text_input("DNI", key="dni_create")
        nombre = st.text_input("Nombre", key="name_create")
        email_cli = st.text_input("Email", key="email_create")
        telefono = st.text_input("Teléfono", key="phone_create")
        submitted = st.form_submit_button("Crear cliente")
        if submitted:
            payload = {"dni": dni, "name": nombre, "email": email_cli, "phone": telefono}
            res = api_post(ROUTE_CLIENTES, payload)
            if res is None:
                st.error(f"No creado: {st.session_state.get('last_api_error')}")
            else:
                st.success("Cliente creado")
                st.experimental_rerun()

    st.markdown("---")
    # Eliminar cliente por fila (botón por fila, admin only)
    st.subheader("Eliminar cliente (por fila)")
    if clientes_data:
        for c in clientes_data:
            cid = c.get("id")
            cols = st.columns([8,1])
            cols[0].write(f"ID: {cid} — {c.get('name')} — {c.get('email')} — {c.get('phone')}")
            disabled = (st.session_state.get("email") != "admin@example.com")
            if cols[1].button("Eliminar", key=f"del_cliente_{cid}", disabled=disabled):
                confirm_key = f"confirm_cliente_{cid}"
                if not st.session_state.get(confirm_key):
                    st.session_state[confirm_key] = False
                st.session_state[confirm_key] = st.checkbox("Confirmar", key=confirm_key)
                if st.session_state[confirm_key]:
                    ok = api_delete(f"{ROUTE_CLIENTES}{cid}/")
                    if ok:
                        st.success("Cliente eliminado")
                        st.experimental_rerun()
                    else:
                        st.error(f"Error borrando: {st.session_state.get('last_api_error')}")
    else:
        st.info("Sin datos de clientes para eliminar.")

    # MASCOTAS (side-by-side)
    st.markdown("---")
    st.subheader("Mascotas (CRUD)")
    mascotas_data = api_get(ROUTE_MASCOTAS)
    if mascotas_data is None:
        st.error(f"Error listando mascotas: {st.session_state.get('last_api_error')}")
    else:
        dfm = pd.DataFrame(mascotas_data)
        if not dfm.empty:
            cols_show = [c for c in ("name","species","breed","age","owner_id","id") if c in dfm.columns]
            st.dataframe(dfm[cols_show].rename(columns={"name":"Nombre","species":"Especie","breed":"Raza","age":"Edad","owner_id":"Owner ID","id":"ID"}))
        else:
            st.info("No hay mascotas.")

    st.markdown("---")
    st.subheader("Crear mascota")
    with st.form("form_crear_mascota"):
        owner_id = st.number_input("Owner ID (client_id)", min_value=1, value=1, key="owner_id")
        pet_name = st.text_input("Nombre mascota", key="pet_name")
        especie = st.text_input("Especie", value="Perro", key="especie")
        raza = st.text_input("Raza", key="raza")
        edad = st.number_input("Edad", min_value=0, value=0, key="edad")
        submitted_pet = st.form_submit_button("Crear mascota")
        if submitted_pet:
            payload = {"client_id": owner_id, "name": pet_name, "species": especie, "breed": raza, "age": edad}
            res = api_post(ROUTE_MASCOTAS, payload)
            if res is None:
                st.error(f"No creado: {st.session_state.get('last_api_error')}")
            else:
                st.success("Mascota creada")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("Eliminar mascota (por fila)")
    if mascotas_data:
        for m in mascotas_data:
            mid = m.get("id")
            cols = st.columns([8,1])
            cols[0].write(f"ID: {mid} — {m.get('name')} — {m.get('species')} — {m.get('breed')} — {m.get('age')}")
            disabled = (st.session_state.get("email") != "admin@example.com")
            if cols[1].button("Eliminar", key=f"del_mascota_{mid}", disabled=disabled):
                confirm_key = f"confirm_mascota_{mid}"
                if not st.session_state.get(confirm_key):
                    st.session_state[confirm_key] = False
                st.session_state[confirm_key] = st.checkbox("Confirmar", key=confirm_key)
                if st.session_state[confirm_key]:
                    ok = api_delete(f"{ROUTE_MASCOTAS}{mid}/")
                    if ok:
                        st.success("Mascota eliminada")
                        st.experimental_rerun()
                    else:
                        st.error(f"Error al borrar: {st.session_state.get('last_api_error')}")
    else:
        st.info("Sin mascotas para eliminar.")

def page_citas():
    st.title("Citas")
    st.subheader("Crear cita")
    with st.form("form_crear_cita"):
        fecha_hora = st.text_input("Fecha y hora (YYYY/MM/DD HH:MM)", value=datetime.now().strftime("%Y/%m/%d %H:%M"), key="c_fecha")
        motivo = st.text_input("Motivo", key="c_motivo")
        veterinario = st.text_input("Veterinario", value="Dr. Ana", key="c_vet")
        pet_id = st.number_input("pet_id", min_value=1, value=1, key="c_pet")
        client_id = st.number_input("client_id", min_value=1, value=1, key="c_client")
        created = st.form_submit_button("Crear cita")
        if created:
            payload = {"date": fecha_hora, "reason": motivo, "veterinarian": veterinario, "pet_id": int(pet_id), "client_id": int(client_id)}
            res = api_post(ROUTE_CITAS, payload)
            if res is None:
                st.error(f"Error creando cita: {st.session_state.get('last_api_error')}")
            else:
                st.success("Cita creada")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("Listado de citas y eliminar")
    citas_data = api_get(ROUTE_CITAS)
    if citas_data is None:
        st.error(f"Error listando citas: {st.session_state.get('last_api_error')}")
    else:
        if not isinstance(citas_data, list) or len(citas_data) == 0:
            st.info("No hay citas.")
        else:
            for c in citas_data:
                cid = c.get("id")
                cols = st.columns([8,1])
                cols[0].write(f"ID: {cid} — {c.get('date')} — {c.get('reason')} — pet {c.get('pet_id')} — client {c.get('client_id')}")
                if cols[1].button("Eliminar", key=f"del_cita_{cid}"):
                    confirm_key = f"confirm_cita_{cid}"
                    if not st.session_state.get(confirm_key):
                        st.session_state[confirm_key] = False
                    st.session_state[confirm_key] = st.checkbox("Confirmar", key=confirm_key)
                    if st.session_state[confirm_key]:
                        ok = api_delete(f"{ROUTE_CITAS}{cid}/")
                        if ok:
                            st.success("Cita eliminada")
                            st.experimental_rerun()
                        else:
                            st.error(f"Error al borrar cita: {st.session_state.get('last_api_error')}")

def page_facturacion():
    st.title("Facturación")
    st.subheader("Crear factura")
    with st.form("form_crear_factura"):
        client_id = st.number_input("client_id", min_value=1, value=1, key="f_client")
        fecha = st.date_input("Fecha", value=datetime.now().date(), key="f_date")
        total = st.number_input("Total", min_value=0.0, value=0.0, step=0.5, key="f_total")
        created = st.form_submit_button("Crear factura")
        if created:
            payload = {"client_id": int(client_id), "date": fecha.isoformat(), "total": float(total)}
            res = api_post(ROUTE_FACTURAS, payload)
            if res is None:
                st.error(f"API error: {st.session_state.get('last_api_error')}")
            else:
                st.success("Factura creada")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("Listado de facturas (últimas 50)")
    facturas = api_get(ROUTE_FACTURAS)
    if facturas is None:
        st.error(f"API error: {st.session_state.get('last_api_error')}")
    else:
        dff = pd.DataFrame(facturas)
        if not dff.empty:
            if "date" in dff.columns:
                dff["date"] = pd.to_datetime(dff["date"], errors="coerce")
            cols_show = [c for c in ("client_id","date","total","id","paid") if c in dff.columns]
            st.dataframe(dff[cols_show].rename(columns={"client_id":"Cliente","date":"Fecha","total":"Total","id":"ID","paid":"Pagada"}))
        else:
            st.info("No hay facturas.")

def page_analisis():
    st.title("Análisis y métricas")
    fecha_inicio = st.date_input("Fecha inicio", value=datetime(2025,1,1).date(), key="a_inicio")
    fecha_fin = st.date_input("Fecha fin", value=datetime.now().date(), key="a_fin")

    if st.button("Obtener ingresos (informe)"):
        params = {"fecha_inicio": fecha_inicio.isoformat(), "fecha_fin": fecha_fin.isoformat()}
        informe = api_get(ROUTE_INFORMES_INGRESOS, params=params)
        if informe is None:
            st.error(f"Error informe: {st.session_state.get('last_api_error')}")
        else:
            st.success("Informe obtenido")
            st.json(informe)

    st.markdown("---")
    st.header("Gráfico: ingresos mensuales (si hay endpoint de facturas)")
    facturas = api_get(ROUTE_FACTURAS)
    if facturas is None:
        st.info(f"No disponible endpoint de facturas: {st.session_state.get('last_api_error')}")
        return
    dff = pd.DataFrame(facturas)
    if dff.empty:
        st.info("No hay facturas para graficar")
        return
    # prepare date and filter
    if "date" in dff.columns:
        dff["date"] = pd.to_datetime(dff["date"], errors="coerce")
    dff = dff[(dff["date"] >= pd.to_datetime(fecha_inicio)) & (dff["date"] <= pd.to_datetime(fecha_fin))]
    if dff.empty:
        st.info("No hay facturas en el rango seleccionado.")
        return
    dff["month"] = dff["date"].dt.to_period("M").astype(str)
    monthly = dff.groupby("month")["total"].sum().reset_index()
    if monthly.empty:
        st.info("No hay datos mensuales.")
        return
    fig = px.bar(monthly, x="month", y="total", title="Ingresos por mes", labels={"total":"Ingresos", "month":"Mes"})
    st.plotly_chart(fig, use_container_width=True)

# Router
if page == "Inicio":
    page_inicio()
elif page == "Pacientes":
    page_pacientes()
elif page == "Citas":
    page_citas()
elif page == "Facturación":
    page_facturacion()
elif page == "Análisis":
    page_analisis()
else:
    page_inicio()