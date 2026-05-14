import streamlit as st
import pandas as pd
import random
import io

# =========================
# KONFIGURASI STREAMLIT
# =========================
st.set_page_config(
    page_title="Sistem Penjadwalan Mata Kuliah",
    layout="wide"
)

# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 50%, #0f0f1e 100%) !important;
    color: #e0e0e0 !important;
}

html, body, [class*="css"] {
    font-size: 18px !important;
    font-family: 'Segoe UI', 'Roboto', sans-serif !important;
    color: #e0e0e0 !important;
}

.block-container {
    max-width: 1180px !important;
    padding-top: 4rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-bottom: 4rem !important;
}

.main-title {
    font-size: 68px !important;
    font-weight: 900 !important;
    line-height: 1.1 !important;
    background: linear-gradient(135deg, #64b5f6 0%, #81c784 50%, #64b5f6 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 15px !important;
}

.subtitle {
    font-size: 25px !important;
    color: #b0bec5 !important;
    margin-bottom: 35px !important;
}

h2, h3,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    font-size: 34px !important;
    color: #64b5f6 !important;
    font-weight: 800 !important;
    margin-top: 28px !important;
    margin-bottom: 18px !important;
}

p, label, span {
    font-size: 18px !important;
    color: #e0e0e0 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a15 0%, #151523 100%) !important;
    border-right: 2px solid #37474f !important;
}

section[data-testid="stSidebar"] * {
    font-size: 17px !important;
    color: #e0e0e0 !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    font-size: 18px !important;
    background: #1e1e2e !important;
    color: #e0e0e0 !important;
    border: 2px solid #37474f !important;
    border-radius: 8px !important;
}

.stTextInput input,
.stNumberInput input {
    height: 52px !important;
}

.stTextArea textarea {
    min-height: 120px !important;
}

.stSelectbox div[data-baseweb="select"] {
    font-size: 18px !important;
    min-height: 52px !important;
    background-color: #1e1e2e !important;
    border-radius: 8px !important;
    border: 2px solid #37474f !important;
    color: #e0e0e0 !important;
}

.stSelectbox div[data-baseweb="select"]:hover {
    border-color: #64b5f6 !important;
}

ul {
    background-color: #1e1e2e !important;
    border: 1px solid #37474f !important;
    border-radius: 8px !important;
}

li {
    color: #e0e0e0 !important;
    font-size: 18px !important;
}

li:hover {
    background-color: #2d2d3f !important;
    font-weight: bold !important;
}

.stCheckbox label,
.stRadio label {
    font-size: 18px !important;
    font-weight: 500 !important;
}

.stButton > button,
.stDownloadButton > button {
    font-size: 20px !important;
    font-weight: 700 !important;
    height: 58px !important;
    background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #42a5f5 0%, #1e88e5 100%) !important;
    color: #ffffff !important;
    
}

[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    background: #1e1e2e !important;
    border: 1px solid #37474f !important;
    border-radius: 8px !important;
}

[data-testid="stDataFrame"] div[role="gridcell"],
[data-testid="stDataEditor"] div[role="gridcell"] {
    font-size: 20px !important;
    color: #e0e0e0 !important;
}

[data-testid="stDataFrame"] div[role="columnheader"],
[data-testid="stDataEditor"] div[role="columnheader"] {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #64b5f6 !important;
}

[data-testid="stDataEditor"] input {
    font-size: 20px !important;
    background: #252535 !important;
    color: #e0e0e0 !important;
}

.stSuccess,
.stWarning,
.stError,
.stInfo {
    font-size: 18px !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown('<div class="main-title">Novasya Scheduler</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sistem Penjadwalan Mata Kuliah Otomatis Berbasis AI</div>', unsafe_allow_html=True)

# =========================
# PARAMETER GA
# =========================
st.sidebar.header("⚙️ Parameter Genetic Algorithm")
POP_SIZE = st.sidebar.number_input("Population Size", 100, 2000, 700, 100)
GENS = st.sidebar.number_input("Jumlah Generasi", 50, 1000, 300, 50)
MUT_RATE = st.sidebar.slider("Mutation Rate", 0.01, 0.50, 0.10, 0.01)

# =========================
# SESSION STATE
# =========================
default_data = pd.DataFrame({
    "Kode MK": pd.Series(dtype="str"),
    "Nama Mata Kuliah": pd.Series(dtype="str"),
    "SKS": pd.Series(dtype="float"),
    "Jumlah Kelas": pd.Series(dtype="int"),
    "Dosen 1": pd.Series(dtype="str"),
    "Dosen 2": pd.Series(dtype="str"),
    "Dosen 3": pd.Series(dtype="str"),
    "Dosen 4": pd.Series(dtype="str")
})

for key, value in {
    "df_input_source": default_data.copy(),
    "df_schedule": None,
    "df_history": None,
    "df_load": None,
    "df_room": None,
    "df_lecturer_sks_detail": None,
    "total_conflict": None,
    "excel_output": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# INPUT RUANGAN
# =========================
st.subheader("1. Input Data Ruangan")

room_text = st.text_area(
    "Masukkan nama ruangan (pisahkan dengan koma)",
    "Ruang 1, Ruang 2, Ruang 3, Ruang 4",
    height=120
)

rooms = [r.strip() for r in room_text.split(",") if r.strip()]

# =========================
# INPUT JUMLAH DOSEN
# =========================
st.subheader("2. Pengaturan Dosen")

LECTURER_PER_CLASS = st.radio(
    "Pilih jumlah dosen pada setiap kelas",
    [1, 2],
    horizontal=True
)

# =========================
# INPUT HARI
# =========================
st.subheader("3. Pilih Hari Aktif Kuliah")

selected_days = []

col1, col2, col3 = st.columns(3)

with col1:
    if st.checkbox("Senin", value=True):
        selected_days.append("Senin")
    if st.checkbox("Selasa", value=True):
        selected_days.append("Selasa")

with col2:
    if st.checkbox("Rabu", value=True):
        selected_days.append("Rabu")
    if st.checkbox("Kamis", value=True):
        selected_days.append("Kamis")

with col3:
    if st.checkbox("Jumat", value=True):
        selected_days.append("Jumat")
    if st.checkbox("Sabtu", value=False):
        selected_days.append("Sabtu")

# =========================
# INPUT SESI
# =========================
from datetime import datetime, timedelta

st.subheader("4. Atur Sesi Kuliah")

st.info("Jam istirahat otomatis: 13:00 - 14:00")

col_a, col_b = st.columns(2)

with col_a:
    TOTAL_SESSIONS_PER_DAY = st.number_input(
        "Jumlah sesi kuliah dalam sehari",
        min_value=1,
        max_value=12,
        value=4,
        step=1
    )

with col_b:
    SKS_PER_SESSION = st.number_input(
        "Jumlah SKS dalam 1 sesi",
        min_value=1,
        max_value=6,
        value=2,
        step=1
    )

# =========================
# GENERATE DEFAULT SESSION
# =========================

sessions = []

START_TIME = datetime.strptime("08:00", "%H:%M")
BREAK_START = datetime.strptime("13:00", "%H:%M").time()
BREAK_END = datetime.strptime("14:00", "%H:%M").time()

duration_minutes = int(SKS_PER_SESSION * 50)

cols = st.columns(4)

current_time = START_TIME

for i in range(int(TOTAL_SESSIONS_PER_DAY)):

    session_start = current_time
    session_end = session_start + timedelta(minutes=duration_minutes)

    if session_start.time() < BREAK_END and session_end.time() > BREAK_START:
        session_start = datetime.combine(
            session_start.date(),
            BREAK_END
        )
        session_end = session_start + timedelta(minutes=duration_minutes)

    default_label = (
        f"{session_start.strftime('%H:%M')} - "
        f"{session_end.strftime('%H:%M')}"
    )

    # key dibuat berubah mengikuti SKS dan jumlah sesi
    session_key = f"sesi_{i+1}_{SKS_PER_SESSION}_{TOTAL_SESSIONS_PER_DAY}"

    with cols[i % 4]:
        sesi = st.text_input(
            f"Sesi {i + 1}",
            value=default_label,
            key=session_key
        )

    sessions.append(sesi)

    current_time = session_end
    
# =========================
# INPUT DATA MK
# =========================
st.subheader("5. Input Data Mata Kuliah")

uploaded_file = st.file_uploader(
    "Upload data mata kuliah dari Excel",
    type=["xlsx"]
)

if uploaded_file is not None:
    df_excel = pd.read_excel(uploaded_file)

    st.info("Silakan pilih kolom Excel yang sesuai dengan format sistem.")

    excel_columns = df_excel.columns.tolist()
    selected_columns = []

    def get_available_columns(extra_option=None):
        available = [col for col in excel_columns if col not in selected_columns]

        if extra_option:
            return [extra_option] + available

        return ["Pilih Kolom"] + available

    col1, col2 = st.columns(2)

    with col1:
        col_kode = st.selectbox("Kolom Kode MK", get_available_columns(), key="kode_mk")
        if col_kode != "Pilih Kolom":
            selected_columns.append(col_kode)

        col_nama = st.selectbox("Kolom Nama Mata Kuliah", get_available_columns(), key="nama_mk")
        if col_nama != "Pilih Kolom":
            selected_columns.append(col_nama)

        col_sks = st.selectbox("Kolom SKS", get_available_columns(), key="sks")
        if col_sks != "Pilih Kolom":
            selected_columns.append(col_sks)

        col_jumlah_kelas = st.selectbox("Kolom Jumlah Kelas", get_available_columns(), key="jumlah_kelas")
        if col_jumlah_kelas != "Pilih Kolom":
            selected_columns.append(col_jumlah_kelas)

    with col2:
        col_dosen1 = st.selectbox("Kolom Dosen 1", get_available_columns(), key="dosen1")
        if col_dosen1 != "Pilih Kolom":
            selected_columns.append(col_dosen1)

        col_dosen2 = st.selectbox("Kolom Dosen 2", get_available_columns("Tidak Ada"), key="dosen2")
        if col_dosen2 != "Tidak Ada":
            selected_columns.append(col_dosen2)

        col_dosen3 = st.selectbox("Kolom Dosen 3", get_available_columns("Tidak Ada"), key="dosen3")
        if col_dosen3 != "Tidak Ada":
            selected_columns.append(col_dosen3)

        col_dosen4 = st.selectbox("Kolom Dosen 4", get_available_columns("Tidak Ada"), key="dosen4")
        if col_dosen4 != "Tidak Ada":
            selected_columns.append(col_dosen4)

    if st.button("📤 Ekstrak Data Excel ke Tabel", use_container_width=True):
        required_mapping = {
            "Kode MK": col_kode,
            "Nama Mata Kuliah": col_nama,
            "SKS": col_sks,
            "Jumlah Kelas": col_jumlah_kelas,
            "Dosen 1": col_dosen1
        }

        empty_mapping = [
            name for name, value in required_mapping.items()
            if value == "Pilih Kolom"
        ]

        if empty_mapping:
            st.error(f"Kolom berikut belum dipilih: {', '.join(empty_mapping)}")
        else:
            st.session_state.df_input_source = pd.DataFrame({
                "Kode MK": df_excel[col_kode],
                "Nama Mata Kuliah": df_excel[col_nama],
                "SKS": df_excel[col_sks],
                "Jumlah Kelas": df_excel[col_jumlah_kelas],
                "Dosen 1": df_excel[col_dosen1],
                "Dosen 2": df_excel[col_dosen2] if col_dosen2 != "Tidak Ada" else "",
                "Dosen 3": df_excel[col_dosen3] if col_dosen3 != "Tidak Ada" else "",
                "Dosen 4": df_excel[col_dosen4] if col_dosen4 != "Tidak Ada" else "",
            })

            st.success("Data berhasil diekstrak ke tabel input.")

df_input = st.data_editor(
    st.session_state.df_input_source,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)

# =========================
# FUNGSI PENJADWALAN
# =========================
def prepare_classes(df, lecturer_per_class):
    classes = []
    lecturer_load_sks = {}

    df = df.dropna(how="all")

    for _, row in df.iterrows():
        try:
            kode = str(row["Kode MK"]).strip()
            nama = str(row["Nama Mata Kuliah"]).strip()
            sks = float(row["SKS"])
            jumlah_kelas = int(row["Jumlah Kelas"])
        except:
            continue

        dosen_list = []

        for col in ["Dosen 1", "Dosen 2", "Dosen 3", "Dosen 4"]:
            dosen = str(row[col]).strip()

            if dosen and dosen.lower() != "nan":
                dosen_list.append(dosen)

                if dosen not in lecturer_load_sks:
                    lecturer_load_sks[dosen] = 0

        dosen_list = list(dict.fromkeys(dosen_list))

        if not kode or not nama or jumlah_kelas <= 0:
            continue

        if len(dosen_list) < lecturer_per_class:
            continue

        for i in range(jumlah_kelas):
            sorted_dosen = sorted(dosen_list, key=lambda d: lecturer_load_sks[d])
            selected_dosen = sorted_dosen[:lecturer_per_class]

            sks_per_dosen = sks / lecturer_per_class
            durasi_sesi = int((sks + SKS_PER_SESSION - 1) // SKS_PER_SESSION)

            for d in selected_dosen:
                lecturer_load_sks[d] += sks_per_dosen

            classes.append({
                "Kelas": f"{kode}-K{i+1}",
                "Kode MK": kode,
                "Mata Kuliah": nama,
                "SKS": sks,
                "Dosen": selected_dosen,
                "SKS per Dosen": sks_per_dosen,
                "Durasi Sesi": durasi_sesi
            })

    return classes, lecturer_load_sks


def create_individual(classes, timeslots, total_rooms):
    individual = []

    for item in classes:
        duration = item["Durasi Sesi"]

        max_start = len(timeslots) - duration

        start_slot = random.randint(0, max_start)

        individual.append({
            "timeslot": start_slot,
            "room": random.randint(0, total_rooms - 1)
        })

    return individual


def get_used_slots(start_slot, duration):
    return set(range(start_slot, start_slot + duration))


def fitness(individual, classes):
    conflict = 0

    for i in range(len(individual)):
        for j in range(i + 1, len(individual)):

            slots_i = get_used_slots(
                individual[i]["timeslot"],
                classes[i]["Durasi Sesi"]
            )

            slots_j = get_used_slots(
                individual[j]["timeslot"],
                classes[j]["Durasi Sesi"]
            )

            overlap_timeslot = bool(slots_i & slots_j)
            same_room = individual[i]["room"] == individual[j]["room"]
            same_lecturer = bool(set(classes[i]["Dosen"]) & set(classes[j]["Dosen"]))
            same_course = classes[i]["Kode MK"] == classes[j]["Kode MK"]

            if overlap_timeslot and same_room:
                conflict += 10

            if overlap_timeslot and same_lecturer:
                conflict += 10

            if overlap_timeslot and same_course:
                conflict += 3

    return conflict


def selection(population, classes):
    a, b = random.sample(population, 2)
    return a if fitness(a, classes) < fitness(b, classes) else b


def crossover(parent1, parent2):
    if len(parent1) <= 1:
        return [gene.copy() for gene in parent1]

    point = random.randint(1, len(parent1) - 1)
    return parent1[:point] + parent2[point:]


def mutate(individual, classes, total_timeslots, total_rooms, mutation_rate):
    new_individual = [gene.copy() for gene in individual]

    if random.random() < mutation_rate:
        idx = random.randint(0, len(new_individual) - 1)
        duration = classes[idx]["Durasi Sesi"]

        max_start = total_timeslots - duration

        new_individual[idx] = {
            "timeslot": random.randint(0, max_start),
            "room": random.randint(0, total_rooms - 1)
        }

    return new_individual


def generate_schedule(classes, timeslots, rooms):
    total_classes = len(classes)
    total_timeslots = len(timeslots)
    total_rooms = len(rooms)

    population = [
        create_individual(classes, timeslots, total_rooms)
        for _ in range(POP_SIZE)
    ]

    best_global = None
    best_fitness = float("inf")
    history = []

    st.info("Sedang memproses penjadwalan...")

    progress_bar = st.progress(0)
    status_text = st.empty()

    for gen in range(GENS):
        new_population = []

        for _ in range(POP_SIZE):
            p1 = selection(population, classes)
            p2 = selection(population, classes)

            child = crossover(p1, p2)
            child = mutate(child, classes, total_timeslots, total_rooms, MUT_RATE)

            new_population.append(child)

        population = new_population

        current_best = min(population, key=lambda x: fitness(x, classes))
        current_fitness = fitness(current_best, classes)

        if current_fitness < best_fitness:
            best_fitness = current_fitness
            best_global = current_best

        history.append({
            "Generasi": gen + 1,
            "Konflik Saat Ini": current_fitness,
            "Konflik Terbaik": best_fitness
        })

        progress_bar.progress((gen + 1) / GENS)

        status_text.markdown(
            f"""
            **Proses Genetic Algorithm**  
            Generasi: `{gen + 1}` dari `{GENS}`  
            Konflik saat ini: `{current_fitness}`  
            Konflik terbaik: `{best_fitness}`
            """
        )

        if best_fitness == 0:
            break

    schedule = []

    for i, gene in enumerate(best_global):
        used_slots = list(range(
            gene["timeslot"],
            gene["timeslot"] + classes[i]["Durasi Sesi"]
        ))

        day = timeslots[gene["timeslot"]][0]
        start_label = timeslots[used_slots[0]][1]
        end_label = timeslots[used_slots[-1]][1]

        jam_masuk = start_label.split(" - ")[0]
        jam_keluar = end_label.split(" - ")[1]

        session = f"{jam_masuk} - {jam_keluar}"

        schedule.append({
            "Kelas": classes[i]["Kelas"],
            "Kode MK": classes[i]["Kode MK"],
            "Mata Kuliah": classes[i]["Mata Kuliah"],
            "SKS": classes[i]["SKS"],
            "Dosen": ", ".join(classes[i]["Dosen"]),
            "SKS per Dosen": classes[i]["SKS per Dosen"],
            "Durasi Sesi": classes[i]["Durasi Sesi"],
            "Hari": day,
            "Sesi": session,
            "Ruangan": rooms[gene["room"]]
        })

    return pd.DataFrame(schedule), pd.DataFrame(history), best_fitness


def build_lecturer_sks_detail(classes):
    rows = []

    for item in classes:
        for dosen in item["Dosen"]:
            rows.append({
                "Dosen": dosen,
                "Kelas": item["Kelas"],
                "Kode MK": item["Kode MK"],
                "Mata Kuliah": item["Mata Kuliah"],
                "SKS Mata Kuliah": item["SKS"],
                "Beban SKS Dosen": item["SKS per Dosen"]
            })

    return pd.DataFrame(rows)


# =========================
# GENERATE JADWAL
# =========================
st.subheader("6. Generate Jadwal")

if st.button("Generate Jadwal", use_container_width=True):

    if len(selected_days) == 0:
        st.error("Pilih minimal 1 hari aktif kuliah.")

    elif len(rooms) == 0:
        st.error("Masukkan minimal 1 ruangan.")

    elif df_input.dropna(how="all").empty:
        st.error("Data mata kuliah belum diisi.")

    else:
        timeslots = [(day, session) for day in selected_days for session in sessions]
        classes, lecturer_load_sks = prepare_classes(df_input, LECTURER_PER_CLASS)

        if len(classes) == 0:
            st.error("Data kelas tidak valid. Pastikan mata kuliah, jumlah kelas, dan jumlah dosen sudah sesuai.")

        elif len(classes) > len(timeslots) * len(rooms):
            st.error(
                "Jumlah kelas melebihi kapasitas slot jadwal dan ruangan. "
                "Tambahkan hari aktif, sesi, atau ruangan."
            )

        else:
            df_schedule, df_history, total_conflict = generate_schedule(
                classes,
                timeslots,
                rooms
            )

            day_order = {day: i for i, day in enumerate(selected_days)}
            df_schedule["Urutan Hari"] = df_schedule["Hari"].map(day_order)

            df_schedule = df_schedule.sort_values(
                by=["Urutan Hari", "Sesi", "Ruangan"]
            ).drop(columns=["Urutan Hari"]).reset_index(drop=True)

            df_lecturer_sks_detail = build_lecturer_sks_detail(classes)

            df_load = df_lecturer_sks_detail.groupby("Dosen").agg(
                **{
                    "Jumlah Kelas": ("Kelas", "count"),
                    "Total Beban SKS": ("Beban SKS Dosen", "sum")
                }
            ).reset_index()

            df_room = df_schedule.groupby(
                ["Hari", "Sesi", "Ruangan"]
            ).size().reset_index(name="Jumlah Kelas")

            output = io.BytesIO()

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_schedule.to_excel(writer, index=False, sheet_name="Jadwal")
                df_load.to_excel(writer, index=False, sheet_name="Beban SKS Dosen")
                df_lecturer_sks_detail.to_excel(writer, index=False, sheet_name="Detail Beban Dosen")
                df_room.to_excel(writer, index=False, sheet_name="Penggunaan Ruangan")
                df_history.to_excel(writer, index=False, sheet_name="Proses GA")

            st.session_state.df_schedule = df_schedule
            st.session_state.df_history = df_history
            st.session_state.df_load = df_load
            st.session_state.df_room = df_room
            st.session_state.df_lecturer_sks_detail = df_lecturer_sks_detail
            st.session_state.total_conflict = total_conflict
            st.session_state.excel_output = output.getvalue()

# =========================
# TAMPILKAN HASIL
# =========================
if st.session_state.df_schedule is not None:

    if st.session_state.total_conflict == 0:
        st.success("✅ Jadwal berhasil dibuat tanpa bentrok dosen dan ruangan.")
    else:
        st.warning(f"Jadwal dibuat, tetapi masih terdapat konflik: {st.session_state.total_conflict}")

    st.subheader("📌 Hasil Jadwal Mata Kuliah")
    st.dataframe(
        st.session_state.df_schedule,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("📊 Rekap Beban SKS Dosen")
    st.dataframe(
        st.session_state.df_load,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("📘 Detail Beban SKS Dosen")
    st.dataframe(
        st.session_state.df_lecturer_sks_detail,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🏫 Rekap Penggunaan Ruangan")
    st.dataframe(
        st.session_state.df_room,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="📥 Download Jadwal Excel",
        data=st.session_state.excel_output,
        file_name="jadwal_mata_kuliah.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
