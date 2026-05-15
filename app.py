import streamlit as st
import pandas as pd
import requests
import time
import io
from datetime import datetime, timedelta

API_URL = "https://kinfolk-directly-activism.ngrok-free.dev"

st.set_page_config(
    page_title="Novasya Scheduler",
    layout="wide"
)

st.title("Novasya Scheduler")
st.write("Sistem Penjadwalan Mata Kuliah Otomatis Berbasis AI")

POP_SIZE = st.sidebar.number_input("Population Size", 100, 2000, 500, 100)
GENS = st.sidebar.number_input("Jumlah Generasi", 100, 1000, 300, 50)
MUT_RATE = st.sidebar.slider("Mutation Rate", 0.01, 0.50, 0.20, 0.01)

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
    "df_load": None,
    "df_room": None,
    "df_lecturer_sks_detail": None,
    "excel_output": None,
    "job_id": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


st.subheader("1. Input Data Ruangan")

room_text = st.text_area(
    "Masukkan nama ruangan, pisahkan dengan koma",
    "Ruang 1, Ruang 2, Ruang 3, Ruang 4"
)

rooms = [r.strip() for r in room_text.split(",") if r.strip()]


st.subheader("2. Pengaturan Dosen")

LECTURER_PER_CLASS = st.radio(
    "Pilih jumlah dosen pada setiap kelas",
    [1, 2],
    horizontal=True
)


st.subheader("3. Pilih Hari Aktif Kuliah")

selected_days = []

for day in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]:
    if st.checkbox(day, value=(day != "Sabtu")):
        selected_days.append(day)


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

sessions = []

START_TIME = datetime.strptime("08:00", "%H:%M")
BREAK_START = datetime.strptime("13:00", "%H:%M").time()
BREAK_END = datetime.strptime("14:00", "%H:%M").time()

duration_minutes = int(SKS_PER_SESSION * 50)
current_time = START_TIME

for i in range(int(TOTAL_SESSIONS_PER_DAY)):
    session_start = current_time
    session_end = session_start + timedelta(minutes=duration_minutes)

    if session_start.time() < BREAK_END and session_end.time() > BREAK_START:
        session_start = datetime.combine(session_start.date(), BREAK_END)
        session_end = session_start + timedelta(minutes=duration_minutes)

    default_label = (
        f"{session_start.strftime('%H:%M')} - "
        f"{session_end.strftime('%H:%M')}"
    )

    session_key = f"sesi_{i + 1}_{SKS_PER_SESSION}_{TOTAL_SESSIONS_PER_DAY}"

    sesi = st.text_input(
        f"Sesi {i + 1}",
        value=default_label,
        key=session_key
    )

    sessions.append(sesi)
    current_time = session_end


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

    if st.button("Ekstrak Data Excel ke Tabel"):
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

            st.success("Data berhasil diekstrak.")

df_input = st.data_editor(
    st.session_state.df_input_source,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)


st.subheader("6. Generate Jadwal")

if st.button("Generate Jadwal"):
    if len(selected_days) == 0:
        st.error("Pilih minimal 1 hari aktif.")

    elif len(rooms) == 0:
        st.error("Masukkan minimal 1 ruangan.")

    elif df_input.dropna(how="all").empty:
        st.error("Data mata kuliah belum diisi.")

    else:
        payload = {
            "data": df_input.to_dict(orient="records"),
            "rooms": rooms,
            "days": selected_days,
            "sessions": sessions,
            "lecturer_per_class": LECTURER_PER_CLASS,
            "pop_size": POP_SIZE,
            "gens": GENS,
            "mut_rate": MUT_RATE,
            "sks_per_session": SKS_PER_SESSION
        }

        try:
            res = requests.post(f"{API_URL}/generate", json=payload, timeout=30)
            res.raise_for_status()

            st.session_state.job_id = res.json()["job_id"]
            st.success(f"Job dikirim ke backend. Job ID: {st.session_state.job_id}")

        except Exception as e:
            st.error(f"Gagal menghubungi backend: {e}")


if st.session_state.job_id is not None:
    st.subheader("Status Generate")

    status_box = st.empty()

    if st.button("Cek Status / Ambil Hasil"):
        try:
            status = requests.get(
                f"{API_URL}/status/{st.session_state.job_id}",
                timeout=30
            ).json()

            status_box.write(status["status"])

            if status["status"] == "done":
                result = status["result"]

                st.session_state.df_schedule = pd.DataFrame(result["schedule"])
                st.session_state.df_load = pd.DataFrame(result["load"])
                st.session_state.df_room = pd.DataFrame(result["room"])
                st.session_state.df_lecturer_sks_detail = pd.DataFrame(result["lecturer_detail"])
                st.session_state.excel_output = bytes.fromhex(result["excel_bytes"])

                st.success("Jadwal berhasil diambil dari backend.")

            elif status["status"] == "error":
                st.error(status["error"])

            else:
                st.info("Proses masih berjalan. Klik lagi beberapa saat kemudian.")

        except Exception as e:
            st.error(f"Gagal mengambil status: {e}")


if st.session_state.df_schedule is not None:
    st.subheader("Hasil Jadwal Mata Kuliah")
    st.dataframe(st.session_state.df_schedule, use_container_width=True, hide_index=True)

    st.subheader("Rekap Beban SKS Dosen")
    st.dataframe(st.session_state.df_load, use_container_width=True, hide_index=True)

    st.subheader("Detail Beban SKS Dosen")
    st.dataframe(st.session_state.df_lecturer_sks_detail, use_container_width=True, hide_index=True)

    st.subheader("Rekap Penggunaan Ruangan")
    st.dataframe(st.session_state.df_room, use_container_width=True, hide_index=True)

    st.download_button(
        label="Download Jadwal Excel",
        data=st.session_state.excel_output,
        file_name="jadwal_mata_kuliah.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )