import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import time

# =========================
# CONFIG
# =========================
API_URL = " https://kinfolk-directly-activism.ngrok-free.dev"
# Jika backend sudah pakai ngrok, ganti menjadi:
# API_URL = "https://xxxx.ngrok-free.app"

st.set_page_config(
    page_title="Novasya Scheduler",
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
st.markdown(
    '<div class="subtitle">Sistem Penjadwalan Mata Kuliah Otomatis Berbasis AI</div>',
    unsafe_allow_html=True
)

# =========================
# SIDEBAR PARAMETER
# =========================
st.sidebar.header("⚙️ Parameter Genetic Algorithm")

POP_SIZE = st.sidebar.number_input("Population Size", 100, 2000, 500, 100)
GENS = st.sidebar.number_input("Jumlah Generasi", 100, 1000, 300, 50)
MUT_RATE = st.sidebar.slider("Mutation Rate", 0.01, 0.50, 0.20, 0.01)

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

default_states = {
    "df_input_source": default_data.copy(),
    "df_schedule": None,
    "df_load": None,
    "df_room": None,
    "df_lecturer_sks_detail": None,
    "excel_output": None,
    "job_id": None,
    "job_status": None
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# INPUT RUANGAN
# =========================
st.subheader("1. Input Data Ruangan")

room_text = st.text_area(
    "Masukkan nama ruangan, pisahkan dengan koma",
    "Ruang 1, Ruang 2, Ruang 3, Ruang 4",
    height=120
)

rooms = [r.strip() for r in room_text.split(",") if r.strip()]

# =========================
# PENGATURAN DOSEN
# =========================
st.subheader("2. Pengaturan Dosen")

LECTURER_PER_CLASS = st.radio(
    "Pilih jumlah dosen pada setiap kelas",
    [1, 2],
    horizontal=True
)

# =========================
# HARI AKTIF
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
# ATUR SESI
# =========================
st.subheader("4. Atur Sesi Kuliah")

st.info("Jam mulai kuliah: 08:00 | 1 SKS = 50 menit | Jam istirahat otomatis: 13:00 - 14:00")

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

sessions = []

START_TIME = datetime.strptime("08:00", "%H:%M")
BREAK_START = datetime.strptime("13:00", "%H:%M").time()
BREAK_END = datetime.strptime("14:00", "%H:%M").time()

duration_minutes = int(SKS_PER_SESSION * 50)
current_time = START_TIME

# dibuat vertikal agar urutan di mobile tetap benar
cols = st.columns(4)

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

    session_key = f"sesi_{i + 1}_{SKS_PER_SESSION}_{TOTAL_SESSIONS_PER_DAY}"

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
# GENERATE JADWAL VIA FASTAPI
# =========================
st.subheader("6. Generate Jadwal")

if st.button("Generate Jadwal", use_container_width=True):

    payload = {
        "data": df_input.to_dict(orient="records"),
        "rooms": rooms,
        "days": selected_days,
        "sessions": sessions,
        "lecturer_per_class": int(LECTURER_PER_CLASS),
        "pop_size": int(POP_SIZE),
        "gens": int(GENS),
        "mut_rate": float(MUT_RATE),
        "sks_per_session": int(SKS_PER_SESSION)
    }

    try:
        response = requests.post(
            f"{API_URL}/generate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        job_id = response.json()["job_id"]

        st.success(f"Job ID: {job_id}")

        status_placeholder = st.empty()
        progress_bar = st.progress(0)

        while True:
            try:
                status_response = requests.get(
                    f"{API_URL}/progress/{job_id}",
                    timeout=10
                )
                status_response.raise_for_status()
                status = status_response.json()

                current_status = status.get("status", "unknown")
                progress = int(status.get("progress", 0) or 0)
                generation = status.get("generation", 0)
                total_generations = status.get("total_generations", GENS)
                current_conflict = status.get("current_conflict", "-")
                best_conflict = status.get("best_conflict", "-")

                status_placeholder.markdown(
                    f"""
                    **Proses Genetic Algorithm**  
                    Status: `{current_status}`  
                    Generasi: `{generation}` dari `{total_generations}`  
                    Konflik saat ini: `{current_conflict}`  
                    Konflik terbaik: `{best_conflict}`  
                    Progress: `{progress}%`
                    """
                )

                progress_bar.progress(min(progress, 100))

                if current_status == "done":
                    result_response = requests.get(
                        f"{API_URL}/result/{job_id}",
                        timeout=60
                    )
                    result_response.raise_for_status()

                    result_data = result_response.json()
                    result = result_data["result"]

                    st.session_state.df_schedule = pd.DataFrame(result["schedule"])
                    st.session_state.df_load = pd.DataFrame(result["load"])
                    st.session_state.df_room = pd.DataFrame(result["room"])
                    st.session_state.df_lecturer_sks_detail = pd.DataFrame(
                        result["lecturer_detail"]
                    )
                    st.session_state.excel_output = bytes.fromhex(
                        result["excel_bytes"]
                    )

                    st.success("Jadwal berhasil dibuat.")
                    break

                if current_status == "error":
                    st.error(status.get("error", "Terjadi error di backend."))
                    break

                if current_status == "not_found":
                    st.error("Job tidak ditemukan di backend.")
                    break

                time.sleep(1)

            except requests.exceptions.RequestException:
                status_placeholder.warning(
                    "Koneksi ke backend sementara terputus. Mencoba lagi..."
                )
                time.sleep(2)
                continue

    except Exception as e:
        st.error(f"Gagal menghubungi backend: {e}")
        
# =========================
# TAMPILKAN HASIL
# =========================
if st.session_state.df_schedule is not None:
    st.success("✅ Jadwal berhasil dibuat tanpa bentrok dosen dan ruangan.")

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