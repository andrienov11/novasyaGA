import pandas as pd
import random
import io


def prepare_classes(df, lecturer_per_class, sks_per_session):
    classes = []
    lecturer_load_sks = {}

    df = df.dropna(how="all")

    for _, row in df.iterrows():
        try:
            kode = str(row["Kode MK"]).strip()
            nama = str(row["Nama Mata Kuliah"]).strip()
            sks = float(row["SKS"])
            jumlah_kelas = int(row["Jumlah Kelas"])
        except Exception:
            continue

        dosen_list = []

        for col in ["Dosen 1", "Dosen 2", "Dosen 3", "Dosen 4"]:
            dosen = str(row.get(col, "")).strip()

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
            durasi_sesi = int((sks + sks_per_session - 1) // sks_per_session)

            for d in selected_dosen:
                lecturer_load_sks[d] += sks_per_dosen

            classes.append({
                "Kelas": f"{kode}-K{i + 1}",
                "Kode MK": kode,
                "Mata Kuliah": nama,
                "SKS": sks,
                "Dosen": selected_dosen,
                "SKS per Dosen": sks_per_dosen,
                "Durasi Sesi": durasi_sesi
            })

    return classes, lecturer_load_sks


def valid_start_indices(timeslots, duration):
    valid = []

    for start in range(len(timeslots) - duration + 1):
        day = timeslots[start][0]
        ok = True

        for offset in range(duration):
            if timeslots[start + offset][0] != day:
                ok = False
                break

        if ok:
            valid.append(start)

    return valid


def create_individual(classes, timeslots, total_rooms):
    individual = []

    for item in classes:
        valid_starts = valid_start_indices(timeslots, item["Durasi Sesi"])

        if not valid_starts:
            start_slot = 0
        else:
            start_slot = random.choice(valid_starts)

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
            same_lecturer = bool(
                set(classes[i]["Dosen"]) & set(classes[j]["Dosen"])
            )
            same_course = classes[i]["Kode MK"] == classes[j]["Kode MK"]

            if overlap_timeslot and same_room:
                conflict += 100

            if overlap_timeslot and same_lecturer:
                conflict += 100

            if overlap_timeslot and same_course:
                conflict += 30

    return conflict


def selection(population, classes):
    a, b = random.sample(population, 2)
    return a if fitness(a, classes) < fitness(b, classes) else b


def crossover(parent1, parent2):
    if len(parent1) <= 1:
        return [gene.copy() for gene in parent1]

    point = random.randint(1, len(parent1) - 1)
    return parent1[:point] + parent2[point:]


def mutate(individual, classes, timeslots, total_rooms, mutation_rate):
    new_individual = [gene.copy() for gene in individual]

    if random.random() < mutation_rate:
        idx = random.randint(0, len(new_individual) - 1)
        valid_starts = valid_start_indices(timeslots, classes[idx]["Durasi Sesi"])

        if valid_starts:
            new_individual[idx] = {
                "timeslot": random.choice(valid_starts),
                "room": random.randint(0, total_rooms - 1)
            }

    return new_individual


def generate_schedule(classes, timeslots, rooms, pop_size, gens, mut_rate, progress_callback=None):
    total_rooms = len(rooms)

    population = [
        create_individual(classes, timeslots, total_rooms)
        for _ in range(pop_size)
    ]

    best_global = None
    best_fitness = float("inf")
    history = []

    for gen in range(gens):
        new_population = []

        elite = min(population, key=lambda x: fitness(x, classes))

        for _ in range(pop_size):
            p1 = selection(population, classes)
            p2 = selection(population, classes)

            child = crossover(p1, p2)
            child = mutate(child, classes, timeslots, total_rooms, mut_rate)

            new_population.append(child)

        new_population[0] = elite
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

        if progress_callback:
            progress_callback(gen + 1, gens, current_fitness, best_fitness)

        if best_fitness == 0:
            break

    if best_global is None:
        raise ValueError("Gagal membuat jadwal.")

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

        schedule.append({
            "Kelas": classes[i]["Kelas"],
            "Kode MK": classes[i]["Kode MK"],
            "Mata Kuliah": classes[i]["Mata Kuliah"],
            "SKS": classes[i]["SKS"],
            "Dosen": ", ".join(classes[i]["Dosen"]),
            "SKS per Dosen": classes[i]["SKS per Dosen"],
            "Durasi Sesi": classes[i]["Durasi Sesi"],
            "Hari": day,
            "Sesi": f"{jam_masuk} - {jam_keluar}",
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


def run_scheduler(
    data,
    rooms,
    days,
    sessions,
    lecturer_per_class,
    pop_size,
    gens,
    mut_rate,
    sks_per_session,
    progress_callback=None
):
    df_input = pd.DataFrame(data)

    timeslots = [(day, session) for day in days for session in sessions]

    classes, _ = prepare_classes(
        df_input,
        lecturer_per_class,
        sks_per_session
    )

    if len(classes) == 0:
        raise ValueError("Data kelas tidak valid.")

    total_required_session = sum(item["Durasi Sesi"] for item in classes)
    total_available_session = len(timeslots) * len(rooms)

    if total_required_session > total_available_session:
        raise ValueError(
            f"Kapasitas jadwal tidak cukup. Dibutuhkan {total_required_session} slot, "
            f"tetapi tersedia hanya {total_available_session} slot."
        )

    df_schedule, df_history, total_conflict = generate_schedule(
        classes,
        timeslots,
        rooms,
        pop_size,
        gens,
        mut_rate,
        progress_callback=progress_callback
    )

    if total_conflict != 0:
        raise ValueError(
            f"Jadwal belum valid. Masih terdapat {total_conflict} konflik."
        )

    day_order = {day: i for i, day in enumerate(days)}
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

    return {
        "schedule": df_schedule.to_dict(orient="records"),
        "load": df_load.to_dict(orient="records"),
        "lecturer_detail": df_lecturer_sks_detail.to_dict(orient="records"),
        "room": df_room.to_dict(orient="records"),
        "history": df_history.to_dict(orient="records"),
        "conflict": total_conflict,
        "excel_bytes": output.getvalue().hex()
    }