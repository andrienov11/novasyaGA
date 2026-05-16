import streamlit as st
import pandas as pd
import requests
import time

# =========================
# CONFIG
# =========================
API_URL = "https://kinfolk-directly-activism.ngrok-free.dev"

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

.stSelectbox div[data-baseweb="select"] {
    font-size: 18px !important;
    min-height: 52px !important;
    background-color: #1e1e2e !important;
    border-radius: 8px !important;
    border: 2px solid #37474f !important;
    color: #e0e0e0 !important;
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

.stSuccess,
.stWarning,
.stError,
.stInfo {
    font-size: 18px !important;
    border-radius: 8px;
}

/* Tabel preview sesi */
.sesi-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 16px;
}
.sesi-table th {
    background: #1e3a5f;
    color: #64b5f6;
    padding: 10px 14px;
    text-align: left;
    font-weight: 700;
}
.sesi-table td {
    padding: 9px 14px;
    border-bottom: 1px solid #2a2a3e;
    color: #e0e0e0;
}
.sesi-table tr:nth-child(even) td {
    background: #1a1a2e;
}
.badge-pagi {
    background: #1565c0;
    color: #fff;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 13px;
    font-weight: 700;
}
.badge-sore {
    background: #4a235a;
    color: #ce93d8;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 13px;
    font-weight: 700;
}
.badge-2sks { color: #81c784; font-weight: 700; }
.badge-3sks { color: #ffb74d; font-weight: 700; }
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
# PARAMETER GA (Sidebar)
# =========================
st.sidebar.header("⚙️ Parameter Genetic Algorithm")
POP_SIZE = st.sidebar.number_input("Population Size", 100, 2000, 200, 100)
GENS     = st.sidebar.number_input("Jumlah Generasi", 100, 1000, 300, 50)
MUT_RATE = st.sidebar.slider("Mutation Rate", 0.01, 0.50, 0.08, 0.01)

# =========================
# SESSION STATE
# =========================
default_data = pd.DataFrame({
    "Kode MK"         : pd.Series(dtype="str"),
    "Nama Mata Kuliah": pd.Series(dtype="str"),
    "SKS"             : pd.Series(dtype="float"),
    "Jumlah Kelas"    : pd.Series(dtype="int"),
    "Dosen 1"         : pd.Series(dtype="str"),
    "Dosen 2"         : pd.Series(dtype="str"),
    "Dosen 3"         : pd.Series(dtype="str"),
    "Dosen 4"         : pd.Series(dtype="str"),
})

default_states = {
    "df_input_source"      : default_data.copy(),
    "df_schedule"          : None,
    "df_load"              : None,
    "df_room"              : None,
    "df_lecturer_sks_detail": None,
    "excel_output"         : None,
    "job_id"               : None,
    "auto_polling"         : False,
    "polling_stopped"      : False,
    "last_status"          : None,
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# HELPER FUNCTIONS
# =========================
def clear_previous_result():
    st.session_state.df_schedule          = None
    st.session_state.df_load              = None
    st.session_state.df_room              = None
    st.session_state.df_lecturer_sks_detail = None
    st.session_state.excel_output         = None
    st.session_state.last_status          = None
    st.session_state.polling_stopped      = False


def request_status():
    response = requests.get(
        f"{API_URL}/status/{st.session_state.job_id}",
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def save_result(result):
    st.session_state.df_schedule           = pd.DataFrame(result["schedule"])
    st.session_state.df_load               = pd.DataFrame(result["load"])
    st.session_state.df_room               = pd.DataFrame(result["room"])
    st.session_state.df_lecturer_sks_detail = pd.DataFrame(result["lecturer_detail"])
    st.session_state.excel_output          = bytes.fromhex(result["excel_bytes"])


def show_status(status):
    current_status    = status.get("status", "unknown")
    progress          = int(status.get("progress", 0) or 0)
    generation        = status.get("generation", 0)
    total_generations = status.get("total_generations", GENS)
    current_conflict  = status.get("current_conflict", "-")
    best_conflict     = status.get("best_conflict", "-")

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
    return current_status


def process_status(status):
    current_status = status.get("status", "unknown")
    st.session_state.last_status = status

    if current_status == "done":
        result = status.get("result")
        if result is not None:
            save_result(result)
        st.session_state.auto_polling    = False
        st.session_state.polling_stopped = True
        st.session_state.job_id          = None
        st.success("Jadwal berhasil dibuat.")
        st.rerun()

    elif current_status == "error":
        st.session_state.auto_polling = False
        st.error(status.get("error", "Terjadi error di backend."))

    elif current_status == "not_found":
        st.session_state.auto_polling = False
        st.error("Job tidak ditemukan di backend.")

    else:
        st.info("Proses GA masih berjalan di backend.")


# =========================
# FUNGSI BANGUN DAFTAR SESI
# Mengikuti logika scheduler:
#   - Pagi  (< 14:00) : hanya 3 SKS
#   - Sore (>= 14:00) : boleh 2 SKS atau 3 SKS
#
# SKS_PER_SESSION = 1 artinya 1 slot = 1 sesi.
# Untuk MK 3 SKS → durasi 3 slot berurutan.
# Untuk MK 2 SKS → durasi 2 slot berurutan.
#
# Agar konsisten, tiap slot = blok waktu 50 menit.
# Tapi karena user menggunakan slot besar (2.5 jam / 1.67 jam),
# kita definisikan setiap slot sebagai SATU BLOK PERTEMUAN penuh
# dan SKS_PER_SESSION disesuaikan dengan SKS slot-nya.
#
# Strategi yang dipakai:
#   sks_per_session = 1  → 1 slot = 1 SKS
#   MK 3 SKS → durasi 3 slot
#   MK 2 SKS → durasi 2 slot
#
# Sehingga slot pagi:
#   "08:00 - 08:50", "08:50 - 09:40", "09:40 - 10:30"  → 3 slot untuk 1 MK 3 SKS (sesi 1)
#   "10:30 - 11:20", "11:20 - 12:10", "12:10 - 13:00"  → 3 slot untuk 1 MK 3 SKS (sesi 2)
#
# Slot sore MK 2 SKS:
#   "14:00 - 14:50", "14:50 - 15:40"  → 2 slot → sesi 1
#   "15:40 - 16:30", "16:30 - 17:20"  → 2 slot → sesi 2
#
# Slot sore MK 3 SKS:
#   "14:00 - 14:50", "14:50 - 15:40", "15:40 - 16:30"  → 3 slot → 1 sesi (habiskan sore)
# =========================

# Slot pagi (semua berlabel "morning", hanya 3 SKS)
MORNING_SLOTS = [
    "08:00 - 08:50",
    "08:50 - 09:40",
    "09:40 - 10:30",
    "10:30 - 11:20",
    "11:20 - 12:10",
    "12:10 - 13:00",
]

# Slot sore (boleh 2 SKS dan 3 SKS)
AFTERNOON_SLOTS = [
    "14:00 - 14:50",
    "14:50 - 15:40",
    "15:40 - 16:30",
    "16:30 - 17:20",
]

# Nilai tetap — 1 slot = 1 SKS
SKS_PER_SESSION = 1

# Semua slot yang dikirim ke backend (urutan pagi → sore)
ALL_SESSIONS = MORNING_SLOTS + AFTERNOON_SLOTS

# =========================
# TABEL PREVIEW SESI (helper render)
# =========================
def render_sesi_preview(use_morning, use_afternoon_2sks, use_afternoon_3sks):
    """Render tabel slot yang aktif dikirim ke backend."""
    rows = []

    if use_morning:
        # Pagi sesi 1 = slot 0-2, sesi 2 = slot 3-5
        rows.append(("08:00 - 10:30", "Pagi", "3 SKS", "Sesi 1 pagi"))
        rows.append(("10:30 - 13:00", "Pagi", "3 SKS", "Sesi 2 pagi"))

    if use_afternoon_3sks:
        rows.append(("14:00 - 16:30", "Sore", "3 SKS", "1 sesi (mengisi sore)"))

    if use_afternoon_2sks:
        rows.append(("14:00 - 15:40", "Sore", "2 SKS", "Sesi 1 sore"))
        rows.append(("15:40 - 17:20", "Sore", "2 SKS", "Sesi 2 sore"))

    if not rows:
        st.warning("Tidak ada sesi yang aktif.")
        return

    header = (
        "<table class='sesi-table'>"
        "<tr><th>Jam</th><th>Periode</th><th>Jenis MK</th><th>Keterangan</th></tr>"
    )
    body = ""
    for jam, periode, jenis, ket in rows:
        badge_p = "badge-pagi" if periode == "Pagi" else "badge-sore"
        badge_s = "badge-3sks" if "3" in jenis else "badge-2sks"
        body += (
            f"<tr>"
            f"<td>{jam}</td>"
            f"<td><span class='{badge_p}'>{periode}</span></td>"
            f"<td><span class='{badge_s}'>{jenis}</span></td>"
            f"<td>{ket}</td>"
            f"</tr>"
        )
    st.markdown(header + body + "</table>", unsafe_allow_html=True)


# =========================
# 1. INPUT RUANGAN
# =========================
st.subheader("1. Input Data Ruangan")

room_text = st.text_area(
    "Masukkan nama ruangan, pisahkan dengan koma",
    "Ruang 1, Ruang 2, Ruang 3, Ruang 4",
    height=120
)
rooms = [r.strip() for r in room_text.split(",") if r.strip()]

# =========================
# 2. PENGATURAN DOSEN
# =========================
st.subheader("2. Pengaturan Dosen")

LECTURER_PER_CLASS = st.radio(
    "Pilih jumlah dosen pada setiap kelas",
    [1, 2],
    horizontal=True
)

# =========================
# 3. HARI AKTIF
# =========================
st.subheader("3. Pilih Hari Aktif Kuliah")

selected_days = []
col1, col2, col3 = st.columns(3)

with col1:
    if st.checkbox("Senin",  value=True):  selected_days.append("Senin")
    if st.checkbox("Selasa", value=True):  selected_days.append("Selasa")
with col2:
    if st.checkbox("Rabu",   value=True):  selected_days.append("Rabu")
    if st.checkbox("Kamis",  value=True):  selected_days.append("Kamis")
with col3:
    if st.checkbox("Jumat",  value=True):  selected_days.append("Jumat")
    if st.checkbox("Sabtu",  value=False): selected_days.append("Sabtu")

# =========================
# 4. ATUR SESI KULIAH
# =========================
st.subheader("4. Atur Sesi Kuliah")

st.markdown("""
**Logika sesi yang berlaku:**
- **Pagi (08:00 – 13:00)** → hanya MK **3 SKS**, selalu tersedia **2 sesi**
- **Sore (14:00+)** → boleh MK **2 SKS** (2 sesi) atau **3 SKS** (1 sesi)
""")

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    use_morning = st.checkbox(
        "✅ Aktifkan sesi pagi",
        value=True,
        help="Sesi 08:00–10:30 dan 10:30–13:00. Hanya untuk MK 3 SKS."
    )

with col_s2:
    use_afternoon_3sks = st.checkbox(
        "Aktifkan sore MK 3 SKS",
        value=True,
        help="1 sesi: 14:00–16:30. Mengisi seluruh slot sore untuk MK 3 SKS."
    )

with col_s3:
    use_afternoon_2sks = st.checkbox(
        "Aktifkan sore MK 2 SKS",
        value=True,
        help="2 sesi: 14:00–15:40 dan 15:40–17:20. Untuk MK 2 SKS."
    )

st.markdown("**Preview slot yang akan dikirim ke backend:**")
render_sesi_preview(use_morning, use_afternoon_2sks, use_afternoon_3sks)

# Bangun daftar sessions berdasarkan pilihan user
sessions: list[str] = []

if use_morning:
    sessions.extend(MORNING_SLOTS)   # 6 slot pagi (50 menit × 6)

if use_afternoon_3sks or use_afternoon_2sks:
    sessions.extend(AFTERNOON_SLOTS) # 4 slot sore (50 menit × 4)

# Jika tidak ada sesi sama sekali, beri peringatan saat generate
if not sessions:
    st.warning("⚠️ Tidak ada sesi yang diaktifkan. Aktifkan minimal satu sesi.")

st.caption(
    f"Total slot per hari: **{len(sessions)}** slot  |  "
    f"SKS per slot: **{SKS_PER_SESSION}**  |  "
    f"MK 3 SKS = 3 slot berurutan  |  MK 2 SKS = 2 slot berurutan"
)

# =========================
# 5. INPUT DATA MK
# =========================
st.subheader("5. Input Data Mata Kuliah")

uploaded_file = st.file_uploader(
    "Upload data mata kuliah dari Excel",
    type=["xlsx"]
)

if uploaded_file is not None:
    df_excel = pd.read_excel(uploaded_file)
    st.info("Silakan pilih kolom Excel yang sesuai dengan format sistem.")

    excel_columns   = df_excel.columns.tolist()
    selected_columns = []

    def get_available_columns(extra_option=None):
        available = [col for col in excel_columns if col not in selected_columns]
        if extra_option:
            return [extra_option] + available
        return ["Pilih Kolom"] + available

    col1, col2 = st.columns(2)

    with col1:
        col_kode = st.selectbox("Kolom Kode MK", get_available_columns(), key="kode_mk")
        if col_kode != "Pilih Kolom": selected_columns.append(col_kode)

        col_nama = st.selectbox("Kolom Nama Mata Kuliah", get_available_columns(), key="nama_mk")
        if col_nama != "Pilih Kolom": selected_columns.append(col_nama)

        col_sks = st.selectbox("Kolom SKS", get_available_columns(), key="sks")
        if col_sks != "Pilih Kolom": selected_columns.append(col_sks)

        col_jumlah_kelas = st.selectbox("Kolom Jumlah Kelas", get_available_columns(), key="jumlah_kelas")
        if col_jumlah_kelas != "Pilih Kolom": selected_columns.append(col_jumlah_kelas)

    with col2:
        col_dosen1 = st.selectbox("Kolom Dosen 1", get_available_columns(), key="dosen1")
        if col_dosen1 != "Pilih Kolom": selected_columns.append(col_dosen1)

        col_dosen2 = st.selectbox("Kolom Dosen 2", get_available_columns("Tidak Ada"), key="dosen2")
        if col_dosen2 != "Tidak Ada": selected_columns.append(col_dosen2)

        col_dosen3 = st.selectbox("Kolom Dosen 3", get_available_columns("Tidak Ada"), key="dosen3")
        if col_dosen3 != "Tidak Ada": selected_columns.append(col_dosen3)

        col_dosen4 = st.selectbox("Kolom Dosen 4", get_available_columns("Tidak Ada"), key="dosen4")
        if col_dosen4 != "Tidak Ada": selected_columns.append(col_dosen4)

    if st.button("📤 Ekstrak Data Excel ke Tabel", use_container_width=True):
        required_mapping = {
            "Kode MK"         : col_kode,
            "Nama Mata Kuliah": col_nama,
            "SKS"             : col_sks,
            "Jumlah Kelas"    : col_jumlah_kelas,
            "Dosen 1"         : col_dosen1,
        }
        empty_mapping = [
            name for name, value in required_mapping.items()
            if value == "Pilih Kolom"
        ]

        if empty_mapping:
            st.error(f"Kolom berikut belum dipilih: {', '.join(empty_mapping)}")
        else:
            st.session_state.df_input_source = pd.DataFrame({
                "Kode MK"         : df_excel[col_kode],
                "Nama Mata Kuliah": df_excel[col_nama],
                "SKS"             : df_excel[col_sks],
                "Jumlah Kelas"    : df_excel[col_jumlah_kelas],
                "Dosen 1"         : df_excel[col_dosen1],
                "Dosen 2"         : df_excel[col_dosen2] if col_dosen2 != "Tidak Ada" else "",
                "Dosen 3"         : df_excel[col_dosen3] if col_dosen3 != "Tidak Ada" else "",
                "Dosen 4"         : df_excel[col_dosen4] if col_dosen4 != "Tidak Ada" else "",
            })
            st.success("Data berhasil diekstrak ke tabel input.")
            st.rerun()

df_input = st.data_editor(
    st.session_state.df_input_source,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="df_input_editor"
)
st.session_state.df_input_source = df_input

# =========================
# 6. GENERATE JADWAL
# =========================
st.subheader("6. Generate Jadwal")

if st.button("🚀 Generate Jadwal", use_container_width=True):
    clear_previous_result()

    # Validasi input
    errors = []
    if len(df_input) == 0:
        errors.append("Data mata kuliah masih kosong.")
    if len(rooms) == 0:
        errors.append("Data ruangan masih kosong.")
    if len(selected_days) == 0:
        errors.append("Hari aktif kuliah belum dipilih.")
    if not sessions:
        errors.append("Tidak ada sesi yang diaktifkan.")
    if not use_morning and df_input["SKS"].isin([3]).any():
        errors.append(
            "Ada MK 3 SKS tetapi sesi pagi tidak diaktifkan. "
            "Aktifkan sesi pagi atau tambahkan sesi sore 3 SKS."
        )

    if errors:
        for err in errors:
            st.error(err)
    else:
        payload = {
            "data"              : df_input.to_dict(orient="records"),
            "rooms"             : rooms,
            "days"              : selected_days,
            "sessions"          : sessions,          # slot 50-menit yang sudah dibangun
            "lecturer_per_class": int(LECTURER_PER_CLASS),
            "pop_size"          : int(POP_SIZE),
            "gens"              : int(GENS),
            "mut_rate"          : float(MUT_RATE),
            "sks_per_session"   : int(SKS_PER_SESSION),  # 1 slot = 1 SKS
        }

        try:
            response = requests.post(
                f"{API_URL}/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            job_id = response.json()["job_id"]
            st.session_state.job_id          = job_id
            st.session_state.auto_polling    = True
            st.session_state.polling_stopped = False
            st.session_state.last_status     = None

            st.success(f"Job berhasil dikirim. Job ID: `{job_id}`")
            st.rerun()

        except Exception as e:
            st.error(f"Gagal menghubungi backend: {e}")

# =========================
# 7. STATUS GENERATE
# =========================
st.subheader("7. Status Generate")

col_info, col_btn = st.columns([6, 1])

with col_info:
    if st.session_state.job_id is not None:
        st.caption(f"Job aktif: `{st.session_state.job_id}`")
    else:
        st.caption("Belum ada job GA yang aktif.")

with col_btn:
    manual_status = st.button(
        "🔄 Status",
        key="manual_status_btn",
        use_container_width=True
    )

status_placeholder = st.empty()
progress_bar       = st.progress(0)

if st.session_state.last_status is not None:
    show_status(st.session_state.last_status)

if manual_status:
    if st.session_state.job_id is None:
        st.warning("Belum ada proses GA yang berjalan.")
    else:
        try:
            status = request_status()
            st.session_state.last_status = status
            show_status(status)
            process_status(status)
        except Exception as e:
            st.error(f"Gagal meminta status backend: {e}")

if st.session_state.job_id is not None and st.session_state.auto_polling:
    try:
        status = request_status()
        st.session_state.last_status = status
        show_status(status)
        process_status(status)
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.session_state.auto_polling    = False
        st.session_state.polling_stopped = True
        st.warning("Tampilan status otomatis berhenti.")
        st.caption(f"Detail error: {e}")
        st.info("Klik tombol 🔄 Status untuk meminta status proses GA ke backend.")

# =========================
# 8. TAMPILKAN HASIL
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