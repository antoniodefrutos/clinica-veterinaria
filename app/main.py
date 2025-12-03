import streamlit as st

st.set_page_config(
    page_title="Clínica Veterinaria",
    page_icon="🐍",
    layout="wide",
)

# --- Sidebar de navegación ---
st.sidebar.title("Clínica Veterinaria")
section = st.sidebar.radio(
    "Ir a:",
    ["🏠 Inicio", "🐾 Pacientes", "📅 Citas", "💶 Facturación", "📊 Análisis"],
)

# --- Contenido según la sección seleccionada ---
if section == "🏠 Inicio":
    st.title("Clínica Veterinaria")
    st.write(
        """
        Bienvenido al sistema de gestión de la **Clínica Veterinaria**.

        Desde esta aplicación podrás:
        - Registrar y consultar pacientes (mascotas).
        - Gestionar citas.
        - Controlar la facturación.
        - Ver análisis básicos de la actividad de la clínica.
        """
    )

elif section == "🐾 Pacientes":
    st.title("Gestión de pacientes")
    st.info("Aquí irá el listado y registro de mascotas (CRUD).")

elif section == "📅 Citas":
    st.title("Gestión de citas")
    st.info("Aquí podrás ver, crear y modificar citas.")

elif section == "💶 Facturación":
    st.title("Facturación")
    st.info("Aquí se mostrarán facturas, importes y estados de pago.")

elif section == "📊 Análisis":
    st.title("Análisis y métricas")
    st.info("Aquí irán gráficos y KPIs de la clínica.")
