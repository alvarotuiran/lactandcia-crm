import hmac
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Lactandcia CRM",
    page_icon="🤱",
    layout="wide"
)


# =========================
# SEGURIDAD BÁSICA
# =========================

def check_password():
    """
    Protección básica por contraseña.
    En local: crea .streamlit/secrets.toml con:
    APP_PASSWORD = "tu_password"
    En Streamlit Cloud: Settings > Secrets.
    """
    if "APP_PASSWORD" not in st.secrets:
        st.warning("APP_PASSWORD no configurado. La app está sin contraseña.")
        return True

    def password_entered():
        if hmac.compare_digest(
            st.session_state["password"],
            st.secrets["APP_PASSWORD"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    show_header()
    st.text_input(
        "Contraseña",
        type="password",
        on_change=password_entered,
        key="password"
    )

    if st.session_state.get("password_correct") is False:
        st.error("Contraseña incorrecta")

    return False


# =========================
# CONFIGURACIÓN / ASSETS
# =========================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

ASSETS_DIR = Path("assets")
LOGO_FILE = ASSETS_DIR / "logo.jpeg"

CLIENTES_FILE = DATA_DIR / "clientes.csv"
CASOS_FILE = DATA_DIR / "casos.csv"
TAREAS_FILE = DATA_DIR / "tareas.csv"

# La entrevista inicial de Laura incluye estos datos base:
# mamá, pareja, bebé, nacimiento, hospital, teléfono, mail, ciudad,
# embarazo, parto, anestesia, semanas, pesos, piel con piel, separación,
# lactancia primera hora, medicación, enfermedad, sueño, chupete,
# cómo conoció Lactandcia, autorización uso pedagógico de imágenes y motivo.
CLIENTES_COLS = [
    "id_cliente",
    "nombre_mama",
    "nombre_pareja",
    "telefono",
    "email",
    "ciudad",
    "fecha_alta",
    "como_me_conociste",
    "consentimiento_rgpd",
    "autorizacion_imagenes",
    "notas_generales"
]

BEBES_COLS = [
    "id_bebe",
    "id_cliente",
    "nombre_bebe",
    "fecha_nacimiento",
    "semanas_gestacion",
    "peso_nacimiento",
    "peso_alta",
    "hospital",
    "bebe_sano_o_problema",
    "como_duerme",
    "usa_chupete"
]

ENTREVISTA_COLS = [
    "id_entrevista",
    "id_cliente",
    "id_bebe",
    "fecha_entrevista",
    "embarazo",
    "tipo_parto",
    "anestesia",
    "parto_respetado",
    "acompanada",
    "piel_con_piel",
    "lactancia_primera_hora",
    "separacion_mama_bebe",
    "agarre_primeros_dias",
    "problemas_lactancia",
    "apoyo_familia",
    "medicacion_mama",
    "enfermedad_mama",
    "motivo_consulta",
    "informacion_relevante"
]

CASOS_COLS = [
    "id_caso",
    "id_cliente",
    "id_bebe",
    "fecha_inicio",
    "problema",
    "estado",
    "prioridad",
    "tipo_servicio",
    "proxima_revision",
    "resumen",
    "plan_accion"
]

TAREAS_COLS = [
    "id_tarea",
    "id_caso",
    "fecha",
    "tarea",
    "responsable",
    "estado"
]


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

TIPOS_PARTO = [
    "Vaginal",
    "Cesárea",
    "Instrumental",
    "No informado"
]

SI_NO_NC = ["No informado", "Sí", "No"]

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


# =========================
# HELPERS
# =========================

def show_header():
    left, right = st.columns([1, 5])
    with left:
        if LOGO_FILE.exists():
            st.image(str(LOGO_FILE), width=145)
        else:
            st.markdown("## Lactandcia")
    with right:
        st.title("Lactandcia CRM")
        st.caption("Gestión de clientas, entrevista inicial, bebés, casos y seguimientos")


def load_csv(path: Path, columns: list[str]) -> pd.DataFrame:
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


def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def next_id(df: pd.DataFrame, prefix: str, col: str) -> str:
    if df.empty or col not in df.columns:
        return f"{prefix}-001"

    nums = []
    for value in df[col].astype(str):
        try:
            nums.append(int(value.split("-")[-1]))
        except Exception:
            pass

    return f"{prefix}-{max(nums + [0]) + 1:03d}"


def safe_date(value, default=None):
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.notna(parsed):
        return parsed.date()
    return default or date.today()


def cliente_label(row) -> str:
    nombre = str(row.get("nombre_mama", "")).strip()
    telefono = str(row.get("telefono", "")).strip()
    return f"{row['id_cliente']} · {nombre or 'Sin nombre'} · {telefono or 'Sin teléfono'}"


# =========================
# LOAD DATA
# =========================

clientes = load_csv(CLIENTES_FILE, CLIENTES_COLS)
bebes = load_csv(DATA_DIR / "bebes.csv", BEBES_COLS)
entrevistas = load_csv(DATA_DIR / "entrevistas.csv", ENTREVISTA_COLS)
casos = load_csv(CASOS_FILE, CASOS_COLS)
tareas = load_csv(TAREAS_FILE, TAREAS_COLS)


# =========================
# APP
# =========================

if not check_password():
    st.stop()

st.sidebar.title("Lactandcia CRM")
page = st.sidebar.radio(
    "Ir a",
    [
        "Dashboard",
        "Nueva entrevista",
        "Clientas",
        "Casos",
        "Seguimientos",
        "Biblioteca",
        "Exportar",
        "Avisos RGPD"
    ]
)

if page == "Dashboard":
    show_header()
    st.subheader("Dashboard operativo")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Clientas", len(clientes))
    c2.metric("Bebés", len(bebes))
    c3.metric("Entrevistas", len(entrevistas))
    c4.metric("Casos", len(casos))
    c5.metric("Tareas pendientes", len(tareas[tareas["estado"] != "Hecha"]) if not tareas.empty else 0)

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Casos por problema")
        if casos.empty:
            st.info("Aún no hay casos registrados.")
        else:
            st.bar_chart(casos["problema"].value_counts())

    with right:
        st.subheader("Origen de clientas")
        if clientes.empty:
            st.info("Aún no hay clientas registradas.")
        else:
            st.bar_chart(clientes["como_me_conociste"].replace("", "No informado").value_counts())

    st.subheader("Próximas revisiones")
    if casos.empty:
        st.info("Sin revisiones.")
    else:
        tmp = casos.copy()
        tmp["proxima_revision"] = pd.to_datetime(tmp["proxima_revision"], errors="coerce")
        proximas = tmp[
            (tmp["proxima_revision"].notna()) &
            (tmp["estado"].isin(["Nuevo", "En seguimiento"]))
        ].sort_values("proxima_revision")
        st.dataframe(
            proximas[["id_caso", "id_cliente", "id_bebe", "problema", "prioridad", "proxima_revision", "estado"]],
            use_container_width=True
        )


elif page == "Nueva entrevista":
    show_header()
    st.subheader("Nueva entrevista inicial")

    with st.form("nueva_entrevista"):
        st.markdown("### Datos de la mamá")
        c1, c2 = st.columns(2)
        with c1:
            nombre_mama = st.text_input("Nombre de la mamá")
            nombre_pareja = st.text_input("Nombre de la pareja")
            telefono = st.text_input("Teléfono")
            email = st.text_input("Mail")
        with c2:
            ciudad = st.text_input("Ciudad")
            como_me_conociste = st.selectbox("¿Cómo me conociste?", ORIGENES)
            consentimiento_rgpd = st.checkbox("Consentimiento RGPD registrado")
            autorizacion_imagenes = st.selectbox(
                "Autorizo uso pedagógico de imágenes realizadas durante la sesión",
                SI_NO_NC
            )

        st.markdown("### Datos del bebé")
        c3, c4 = st.columns(2)
        with c3:
            nombre_bebe = st.text_input("Nombre del bebé")
            fecha_nacimiento = st.date_input("Fecha de nacimiento", value=date.today())
            hospital = st.text_input("Hospital")
            semanas_gestacion = st.text_input("¿De cuántas semanas nació el bebé?")
        with c4:
            peso_nacimiento = st.text_input("¿Cuánto pesó al nacer?")
            peso_alta = st.text_input("¿Cuánto pesó al alta?")
            bebe_sano_o_problema = st.text_area("¿El bebé nació sano o hubo algún problema?")
            como_duerme = st.text_area("¿Cómo duerme el bebé?")
            usa_chupete = st.selectbox("¿Usa chupete?", SI_NO_NC)

        st.markdown("### Embarazo, parto y primeros días")
        embarazo = st.text_area("¿Cómo fue tu embarazo?, ¿tuviste algún problema?")
        c5, c6, c7 = st.columns(3)
        with c5:
            tipo_parto = st.selectbox("¿El parto fue cesárea o vaginal?", TIPOS_PARTO)
            anestesia = st.selectbox("¿Tuvo anestesia?", SI_NO_NC)
        with c6:
            parto_respetado = st.selectbox("¿Fue un parto respetado?", SI_NO_NC)
            acompanada = st.selectbox("¿Estuviste acompañada?", SI_NO_NC)
        with c7:
            piel_con_piel = st.selectbox("¿Hicisteis piel con piel?", SI_NO_NC)
            lactancia_primera_hora = st.selectbox("¿La lactancia empezó en la primera hora de vida?", SI_NO_NC)

        separacion_mama_bebe = st.selectbox("¿Hubo separación mamá-bebé?", SI_NO_NC)
        agarre_primeros_dias = st.text_area("¿Cómo fue el agarre del bebé en los primeros días?")

        st.markdown("### Lactancia, salud y entorno")
        problemas_lactancia = st.text_area("¿Has tenido algún problema con la lactancia?")
        apoyo_familia = st.text_area("¿Cómo ha sido el apoyo de la familia?")
        medicacion_mama = st.text_area("¿Toma la mamá alguna medicación?")
        enfermedad_mama = st.text_area("¿Tiene la mamá alguna enfermedad?")

        st.markdown("### Consulta")
        problema = st.selectbox("Problema principal / categoría interna", PROBLEMAS)
        prioridad = st.selectbox("Prioridad", PRIORIDAD, index=1)
        tipo_servicio = st.selectbox(
            "Tipo de servicio",
            ["Consulta online", "Consulta presencial", "Domicilio", "Pack seguimiento", "Prenatal", "Otro"]
        )
        proxima_revision = st.date_input("Próxima revisión", value=date.today() + timedelta(days=2))
        motivo_consulta = st.text_area("Motivo de la consulta")
        informacion_relevante = st.text_area("Información adicional relevante")
        plan_accion = st.text_area("Plan de acción")
        notas_generales = st.text_area("Notas generales de la clienta")

        submitted = st.form_submit_button("Guardar entrevista y crear caso")

    if submitted:
        if not nombre_mama:
            st.error("El nombre de la mamá es obligatorio.")
        else:
            id_cliente = next_id(clientes, "CLI", "id_cliente")
            id_bebe = next_id(bebes, "BEBE", "id_bebe")
            id_entrevista = next_id(entrevistas, "ENT", "id_entrevista")
            id_caso = next_id(casos, "CASO", "id_caso")

            clientes.loc[len(clientes)] = [
                id_cliente,
                nombre_mama,
                nombre_pareja,
                telefono,
                email,
                ciudad,
                str(date.today()),
                como_me_conociste,
                consentimiento_rgpd,
                autorizacion_imagenes,
                notas_generales
            ]

            bebes.loc[len(bebes)] = [
                id_bebe,
                id_cliente,
                nombre_bebe,
                str(fecha_nacimiento),
                semanas_gestacion,
                peso_nacimiento,
                peso_alta,
                hospital,
                bebe_sano_o_problema,
                como_duerme,
                usa_chupete
            ]

            entrevistas.loc[len(entrevistas)] = [
                id_entrevista,
                id_cliente,
                id_bebe,
                str(date.today()),
                embarazo,
                tipo_parto,
                anestesia,
                parto_respetado,
                acompanada,
                piel_con_piel,
                lactancia_primera_hora,
                separacion_mama_bebe,
                agarre_primeros_dias,
                problemas_lactancia,
                apoyo_familia,
                medicacion_mama,
                enfermedad_mama,
                motivo_consulta,
                informacion_relevante
            ]

            casos.loc[len(casos)] = [
                id_caso,
                id_cliente,
                id_bebe,
                str(date.today()),
                problema,
                "Nuevo",
                prioridad,
                tipo_servicio,
                str(proxima_revision),
                motivo_consulta,
                plan_accion
            ]

            save_csv(clientes, CLIENTES_FILE)
            save_csv(bebes, DATA_DIR / "bebes.csv")
            save_csv(entrevistas, DATA_DIR / "entrevistas.csv")
            save_csv(casos, CASOS_FILE)

            st.success(f"Guardado: {id_cliente} / {id_bebe} / {id_entrevista} / {id_caso}")

            recursos = RECURSOS.get(problema, ["Crear recurso específico para este caso."])
            st.subheader("Recursos sugeridos")
            for r in recursos:
                st.write(f"- {r}")


elif page == "Clientas":
    show_header()
    st.subheader("Clientas, bebés y entrevistas")

    if clientes.empty:
        st.info("No hay clientas todavía.")
    else:
        st.markdown("### Clientas")
        st.dataframe(clientes, use_container_width=True)

        st.markdown("### Bebés")
        st.dataframe(bebes, use_container_width=True)

        st.markdown("### Entrevistas")
        st.dataframe(entrevistas, use_container_width=True)


elif page == "Casos":
    show_header()
    st.subheader("Gestión de casos")

    if casos.empty:
        st.info("No hay casos todavía.")
    else:
        merged = casos.merge(
            clientes[["id_cliente", "nombre_mama", "telefono", "email", "ciudad"]],
            on="id_cliente",
            how="left"
        ).merge(
            bebes[["id_bebe", "nombre_bebe", "fecha_nacimiento"]],
            on="id_bebe",
            how="left"
        )

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
            fecha_actual = safe_date(casos.loc[idx, "proxima_revision"])
            proxima = st.date_input("Próxima revisión", value=fecha_actual)
            resumen = st.text_area("Resumen", value=str(casos.loc[idx, "resumen"]))
            plan = st.text_area("Plan de acción", value=str(casos.loc[idx, "plan_accion"]))
            guardar = st.form_submit_button("Actualizar")

        if guardar:
            casos.loc[idx, ["estado", "prioridad", "proxima_revision", "resumen", "plan_accion"]] = [
                estado,
                prioridad,
                str(proxima),
                resumen,
                plan
            ]
            save_csv(casos, CASOS_FILE)
            st.success("Caso actualizado.")


elif page == "Seguimientos":
    show_header()
    st.subheader("Seguimientos y tareas")

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
    show_header()
    st.subheader("Biblioteca de recursos")

    problema = st.selectbox("Problema", PROBLEMAS)
    recursos = RECURSOS.get(problema, ["Sin recursos definidos todavía."])

    for r in recursos:
        st.write(f"- {r}")

    st.warning("Esta biblioteca debe revisarla Laura. No sustituye criterio profesional ni atención sanitaria.")


elif page == "Exportar":
    show_header()
    st.subheader("Exportar datos")

    st.write("Los datos se guardan localmente en la carpeta `data/`.")

    datasets = {
        "clientas.csv": clientes,
        "bebes.csv": bebes,
        "entrevistas.csv": entrevistas,
        "casos.csv": casos,
        "tareas.csv": tareas
    }

    for filename, df in datasets.items():
        if not df.empty:
            st.download_button(
                f"Descargar {filename}",
                df.to_csv(index=False),
                filename,
                "text/csv"
            )

    st.info("Antes de usarlo con datos reales, revisad consentimiento, minimización de datos, base jurídica, accesos, backups y política RGPD.")


elif page == "Avisos RGPD":
    show_header()
    st.subheader("Avisos mínimos antes de usar datos reales")

    st.error(
        "Esta versión sigue siendo un prototipo. No debe usarse con datos reales sensibles "
        "hasta revisar seguridad, consentimiento, backups, control de accesos y base de datos."
    )

    st.markdown(
        """
        **Riesgos actuales:**
        - Los datos se guardan en CSV.
        - No hay control de usuarios por rol.
        - No hay registro de accesos.
        - No hay cifrado específico de base de datos.
        - No hay backups automáticos.
        - No hay política de retención/borrado.

        **Uso recomendado ahora:**
        - Datos ficticios o anonimizados.
        - Pruebas internas.
        - Validación de flujo de trabajo.
        """
    )
