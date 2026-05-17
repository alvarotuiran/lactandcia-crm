import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime, timedelta
import hmac

st.set_page_config(page_title="Lactandcia CRM", page_icon="🤱", layout="wide")

def check_password():
    if "APP_PASSWORD" not in st.secrets:
        st.warning("APP_PASSWORD no configurado en Streamlit Secrets. La app está sin contraseña.")
        return True

    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["APP_PASSWORD"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("Lactandcia CRM")
    st.text_input("Contraseña", type="password", on_change=password_entered, key="password")

    if st.session_state.get("password_correct") is False:
        st.error("Contraseña incorrecta")

    return False

if not check_password():
    st.stop()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

CLIENTES_FILE = DATA_DIR / "clientes.csv"
CASOS_FILE = DATA_DIR / "casos.csv"
TAREAS_FILE = DATA_DIR / "tareas.csv"

PROBLEMAS = [
    "Dolor / grietas",
    "Agarre",
    "Mastitis / obstrucción",
    "Baja producción percibida",
    "Extracción / banco de leche",
    "Vuelta al trabajo",
    "Destete",
    "Relactación",
    "Prematuro / bebé con dificultad",
    "Consulta prenatal",
    "Otro"
]

ESTADOS = ["Nuevo", "En seguimiento", "Resuelto", "Derivado", "Archivado"]
ORIGENES = ["Instagram", "Google", "Recomendación", "Matrona", "Pediatra", "Web", "Otro"]
PRIORIDAD = ["Baja", "Media", "Alta", "Urgente"]

RECURSOS = {
    "Dolor / grietas": [
        "Checklist de agarre profundo",
        "Vídeo: señales de transferencia efectiva",
        "Guía: cuándo consultar por dolor persistente"
    ],
    "Agarre": [
        "Guía rápida de posiciones",
        "Checklist de boca abierta y mentón",
        "Seguimiento recomendado en 24-48h"
    ],
    "Mastitis / obstrucción": [
        "Protocolo de señales de alarma",
        "Guía de manejo inicial",
        "Recomendación: derivar si fiebre o empeoramiento"
    ],
    "Extracción / banco de leche": [
        "Guía banco de leche",
        "Tabla orientativa de conservación",
        "Checklist elección extractor"
    ],
    "Vuelta al trabajo": [
        "Plan de extracción semanal",
        "Guía transición cuidador-bebé",
        "Checklist logística oficina"
    ],
    "Destete": [
        "Guía destete respetuoso",
        "Plan gradual por tomas",
        "Señales de adaptación del bebé"
    ],
    "Consulta prenatal": [
        "Checklist preparación lactancia",
        "Plan primeros 3 días",
        "Señales tempranas de buen inicio"
    ],
}

def load_csv(path, columns):
    if path.exists():
        try:
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df[columns]
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_csv(df, path):
    df.to_csv(path, index=False)

clientes_cols = ["id_cliente", "nombre", "telefono", "email", "fecha_alta", "origen", "consentimiento_rgpd", "notas"]
casos_cols = ["id_caso", "id_cliente", "fecha_inicio", "problema", "estado", "prioridad", "tipo_servicio", "proxima_revision", "resumen", "plan_accion"]
tareas_cols = ["id_tarea", "id_caso", "fecha", "tarea", "responsable", "estado"]

clientes = load_csv(CLIENTES_FILE, clientes_cols)
casos = load_csv(CASOS_FILE, casos_cols)
tareas = load_csv(TAREAS_FILE, tareas_cols)

st.sidebar.title("Lactandcia CRM")
page = st.sidebar.radio("Ir a", ["Dashboard", "Nueva clienta/caso", "Casos", "Seguimientos", "Biblioteca", "Exportar"])

def next_id(df, prefix, col):
    if df.empty or col not in df.columns:
        return f"{prefix}-001"
    nums = []
    for value in df[col].astype(str):
        try:
            nums.append(int(value.split("-")[-1]))
        except Exception:
            pass
    return f"{prefix}-{max(nums + [0]) + 1:03d}"

if page == "Dashboard":
    st.title("Dashboard operativo")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientas", len(clientes))
    c2.metric("Casos", len(casos))
    c3.metric("Casos activos", len(casos[casos["estado"].isin(["Nuevo", "En seguimiento"])]) if not casos.empty else 0)
    c4.metric("Tareas pendientes", len(tareas[tareas["estado"] != "Hecha"]) if not tareas.empty else 0)

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Casos por problema")
        if casos.empty:
            st.info("Aún no hay casos registrados.")
        else:
            st.bar_chart(casos["problema"].value_counts())

    with right:
        st.subheader("Casos por origen")
        if clientes.empty or casos.empty:
            st.info("Aún no hay datos suficientes.")
        else:
            merged = casos.merge(clientes[["id_cliente", "origen"]], on="id_cliente", how="left")
            st.bar_chart(merged["origen"].value_counts())

    st.subheader("Próximas revisiones")
    if casos.empty:
        st.info("Sin revisiones.")
    else:
        tmp = casos.copy()
        tmp["proxima_revision"] = pd.to_datetime(tmp["proxima_revision"], errors="coerce")
        proximas = tmp[(tmp["proxima_revision"].notna()) & (tmp["estado"].isin(["Nuevo", "En seguimiento"]))].sort_values("proxima_revision")
        st.dataframe(proximas[["id_caso", "id_cliente", "problema", "prioridad", "proxima_revision", "estado"]], use_container_width=True)

elif page == "Nueva clienta/caso":
    st.title("Nueva clienta y caso")

    with st.form("alta"):
        st.subheader("Datos de la clienta")
        nombre = st.text_input("Nombre")
        telefono = st.text_input("Teléfono")
        email = st.text_input("Email")
        origen = st.selectbox("Origen", ORIGENES)
        consentimiento = st.checkbox("Consentimiento RGPD registrado")
        notas = st.text_area("Notas generales")

        st.subheader("Datos del caso")
        problema = st.selectbox("Problema principal", PROBLEMAS)
        prioridad = st.selectbox("Prioridad", PRIORIDAD, index=1)
        tipo_servicio = st.selectbox("Tipo de servicio", ["Consulta online", "Consulta presencial", "Domicilio", "Pack seguimiento", "Prenatal", "Otro"])
        proxima_revision = st.date_input("Próxima revisión", value=date.today() + timedelta(days=2))
        resumen = st.text_area("Resumen del caso")
        plan = st.text_area("Plan de acción")
        submitted = st.form_submit_button("Guardar")

    if submitted:
        if not nombre:
            st.error("El nombre es obligatorio.")
        else:
            id_cliente = next_id(clientes, "CLI", "id_cliente")
            id_caso = next_id(casos, "CASO", "id_caso")

            clientes.loc[len(clientes)] = [id_cliente, nombre, telefono, email, str(date.today()), origen, consentimiento, notas]
            casos.loc[len(casos)] = [id_caso, id_cliente, str(date.today()), problema, "Nuevo", prioridad, tipo_servicio, str(proxima_revision), resumen, plan]

            save_csv(clientes, CLIENTES_FILE)
            save_csv(casos, CASOS_FILE)

            st.success(f"Alta guardada: {id_cliente} / {id_caso}")

            recursos = RECURSOS.get(problema, ["Crear recurso específico para este caso."])
            st.subheader("Recursos sugeridos")
            for r in recursos:
                st.write(f"- {r}")

elif page == "Casos":
    st.title("Gestión de casos")

    if casos.empty:
        st.info("No hay casos todavía.")
    else:
        merged = casos.merge(clientes[["id_cliente", "nombre", "telefono", "email", "origen"]], on="id_cliente", how="left")
        filtro_estado = st.multiselect("Estado", ESTADOS, default=["Nuevo", "En seguimiento"])
        filtro_problema = st.multiselect("Problema", PROBLEMAS)

        view = merged.copy()
        if filtro_estado:
            view = view[view["estado"].isin(filtro_estado)]
        if filtro_problema:
            view = view[view["problema"].isin(filtro_problema)]

        st.dataframe(view, use_container_width=True)

        st.subheader("Actualizar caso")
        id_caso = st.selectbox("Selecciona caso", casos["id_caso"].tolist())
        idx = casos.index[casos["id_caso"] == id_caso][0]

        with st.form("update_case"):
            estado = st.selectbox("Estado", ESTADOS, index=ESTADOS.index(casos.loc[idx, "estado"]) if casos.loc[idx, "estado"] in ESTADOS else 0)
            prioridad = st.selectbox("Prioridad", PRIORIDAD, index=PRIORIDAD.index(casos.loc[idx, "prioridad"]) if casos.loc[idx, "prioridad"] in PRIORIDAD else 1)
            fecha_actual = pd.to_datetime(casos.loc[idx, "proxima_revision"], errors="coerce")
            proxima = st.date_input("Próxima revisión", value=fecha_actual.date() if pd.notna(fecha_actual) else date.today())
            resumen = st.text_area("Resumen", value=str(casos.loc[idx, "resumen"]))
            plan = st.text_area("Plan de acción", value=str(casos.loc[idx, "plan_accion"]))
            guardar = st.form_submit_button("Actualizar")

        if guardar:
            casos.loc[idx, ["estado", "prioridad", "proxima_revision", "resumen", "plan_accion"]] = [estado, prioridad, str(proxima), resumen, plan]
            save_csv(casos, CASOS_FILE)
            st.success("Caso actualizado.")

elif page == "Seguimientos":
    st.title("Seguimientos y tareas")

    if casos.empty:
        st.info("Primero crea un caso.")
    else:
        with st.form("nueva_tarea"):
            id_caso = st.selectbox("Caso", casos["id_caso"].tolist())
            fecha = st.date_input("Fecha", value=date.today())
            tarea = st.text_area("Tarea / seguimiento")
            responsable = st.text_input("Responsable", value="Laura")
            submitted = st.form_submit_button("Crear tarea")

        if submitted:
            id_tarea = next_id(tareas, "TAR", "id_tarea")
            tareas.loc[len(tareas)] = [id_tarea, id_caso, str(fecha), tarea, responsable, "Pendiente"]
            save_csv(tareas, TAREAS_FILE)
            st.success("Tarea creada.")

        st.subheader("Tareas")
        if tareas.empty:
            st.info("No hay tareas.")
        else:
            st.dataframe(tareas.sort_values("fecha"), use_container_width=True)
            pendientes = tareas[tareas["estado"] != "Hecha"]["id_tarea"].tolist()
            if pendientes:
                id_tarea = st.selectbox("Marcar tarea como hecha", pendientes)
                if st.button("Marcar como hecha"):
                    tareas.loc[tareas["id_tarea"] == id_tarea, "estado"] = "Hecha"
                    save_csv(tareas, TAREAS_FILE)
                    st.success("Tarea completada.")
            else:
                st.info("No hay tareas pendientes.")

elif page == "Biblioteca":
    st.title("Biblioteca de recursos")
    problema = st.selectbox("Problema", PROBLEMAS)
    recursos = RECURSOS.get(problema, ["Sin recursos definidos todavía."])

    st.subheader("Recursos recomendados")
    for r in recursos:
        st.write(f"- {r}")

    st.warning("Esta biblioteca debe revisarla Laura. No sustituye criterio profesional ni atención sanitaria.")

elif page == "Exportar":
    st.title("Exportar datos")
    st.write("Los datos se guardan en la carpeta `data/`.")

    if not clientes.empty:
        st.download_button("Descargar clientas CSV", clientes.to_csv(index=False), "clientes.csv", "text/csv")
    if not casos.empty:
        st.download_button("Descargar casos CSV", casos.to_csv(index=False), "casos.csv", "text/csv")
    if not tareas.empty:
        st.download_button("Descargar tareas CSV", tareas.to_csv(index=False), "tareas.csv", "text/csv")

    st.info("Antes de usarlo con datos reales, revisad consentimiento, minimización de datos y política RGPD.")
