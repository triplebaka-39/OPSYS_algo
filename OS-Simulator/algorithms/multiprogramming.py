"""Multiprogramming simulation engine (Degree of Multiprogramming, Memory Admittance, and CPU Utilization)."""


def _validate(jobs, total_memory, os_reserved, max_dom, io_fraction):
    if not jobs:
        raise ValueError("At least one job is required.")
    for label, value in (("Total RAM", total_memory), ("OS reserved RAM", os_reserved),
                         ("Maximum degree of multiprogramming", max_dom)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{label} must be a whole number.")
    if total_memory <= 0 or os_reserved < 0 or os_reserved >= total_memory:
        raise ValueError("OS reserved RAM must be non-negative and less than total RAM.")
    if max_dom <= 0:
        raise ValueError("Maximum degree of multiprogramming must be greater than zero.")
    if not isinstance(io_fraction, (int, float)) or isinstance(io_fraction, bool):
        raise ValueError("I/O wait ratio must be a number between 0 and 1.")
    if not 0 <= io_fraction <= 1:
        raise ValueError("I/O wait ratio must be between 0 and 1.")

    available_ram = total_memory - os_reserved
    identifiers = set()
    for index, job in enumerate(jobs, start=1):
        if not isinstance(job, dict):
            raise ValueError(f"Job {index} must include an ID, arrival, size, and burst.")
        jid = str(job.get("jid", "")).strip()
        if not jid:
            raise ValueError(f"Job ID is missing in row {index}.")
        if jid in identifiers:
            raise ValueError(f"Duplicate Job ID: {jid}")
        identifiers.add(jid)
        for field in ("arrival", "size", "burst"):
            value = job.get(field)
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"{field.title()} for {jid} must be a whole number.")
            if (field == "arrival" and value < 0) or (field != "arrival" and value <= 0):
                raise ValueError(f"{field.title()} for {jid} is out of range.")
        if job["size"] > available_ram:
            raise ValueError(
                f"Job {jid} needs {job['size']} KB, more than the "
                f"{available_ram} KB available to jobs."
            )


def calculate_cpu_utilization(io_wait_fraction, degree_of_multiprogramming):
    """
    Computes theoretical CPU utilization based on the probabilistic multiprogramming model:
    CPU Utilization = 1 - (p ^ n)
    where:
        p = fraction of time a process spends waiting for I/O (0.0 to 1.0)
        n = degree of multiprogramming (number of concurrent processes in memory)
    """
    if not isinstance(degree_of_multiprogramming, int) or isinstance(degree_of_multiprogramming, bool):
        raise ValueError("Degree of multiprogramming must be a whole number.")
    if degree_of_multiprogramming < 0:
        raise ValueError("Degree of multiprogramming cannot be negative.")
    if not isinstance(io_wait_fraction, (int, float)) or isinstance(io_wait_fraction, bool):
        raise ValueError("I/O wait fraction must be a number between zero and one.")
    if not 0 <= io_wait_fraction <= 1:
        raise ValueError("I/O wait fraction must be between zero and one.")
    if degree_of_multiprogramming == 0:
        return 0.0
    p = float(io_wait_fraction)
    return (1.0 - (p ** degree_of_multiprogramming)) * 100.0


def simulate_multiprogramming(jobs, total_memory, os_reserved, max_dom, io_fraction=0.60):
    """
    Simulates multiprogramming job scheduling and concurrent memory allocation.

    Args:
        jobs: list of dicts [{"jid": str, "arrival": int, "size": int, "burst": int}]
        total_memory: int (total RAM in KB)
        os_reserved: int (OS reserved memory in KB)
        max_dom: int (maximum Degree of Multiprogramming allowed)
        io_fraction: float (0.0 to 1.0)

    Returns:
        dict with execution timeline, per-job results, utilization stats, and memory logs.
    """
    _validate(jobs, total_memory, os_reserved, max_dom, io_fraction)
    available_ram = total_memory - os_reserved

    # Sort jobs by arrival time
    sorted_jobs = sorted(jobs, key=lambda j: (j["arrival"], j["jid"]))

    time = 0
    in_memory = []       # currently active in RAM [{"job": dict, "admitted_at": int, "remaining": int, "start": int}]
    waiting_queue = []   # jobs that arrived but waiting for RAM or DOM slot
    completed = []
    timeline = []        # snapshots over time: {"time": int, "dom": int, "ram_used": int, "cpu_util": float, "active_jids": list}

    unadmitted_idx = 0
    total_jobs = len(sorted_jobs)

    while len(completed) < total_jobs:
        # Check newly arrived jobs
        while unadmitted_idx < total_jobs and sorted_jobs[unadmitted_idx]["arrival"] <= time:
            waiting_queue.append(sorted_jobs[unadmitted_idx])
            unadmitted_idx += 1

        # Admit jobs from waiting queue into memory if RAM and DOM permit
        admitted_any = True
        while admitted_any and waiting_queue:
            admitted_any = False
            for cand in list(waiting_queue):
                current_used_ram = sum(item["job"]["size"] for item in in_memory)
                if len(in_memory) < max_dom and (current_used_ram + cand["size"]) <= available_ram:
                    waiting_queue.remove(cand)
                    in_memory.append({
                        "job": cand,
                        "admitted_at": time,
                        "remaining": cand["burst"],
                        "start_time": time,
                        "finish_time": None,
                    })
                    admitted_any = True
                    break

        current_used_ram = sum(item["job"]["size"] for item in in_memory)
        dom = len(in_memory)
        utilization = calculate_cpu_utilization(io_fraction, dom)

        timeline.append({
            "time": time,
            "dom": dom,
            "ram_used": current_used_ram + os_reserved,
            "cpu_util": utilization,
            "active_jids": [item["job"]["jid"] for item in in_memory],
            "waiting_jids": [w["jid"] for w in waiting_queue],
        })

        if not in_memory:
            # Advance to next arrival if nothing is in memory
            if unadmitted_idx < total_jobs:
                time = sorted_jobs[unadmitted_idx]["arrival"]
            else:
                waiting = ", ".join(job["jid"] for job in waiting_queue)
                raise ValueError(
                    "Jobs could not be admitted with the selected memory and "
                    f"degree limits: {waiting}."
                )
            continue

        # Execute processes: In multiprogramming, processes advance concurrently
        # Find step until the next earliest finishing job or next arriving job
        time_to_finish = min(item["remaining"] for item in in_memory)
        if unadmitted_idx < total_jobs and sorted_jobs[unadmitted_idx]["arrival"] > time:
            time_to_arrival = sorted_jobs[unadmitted_idx]["arrival"] - time
            step = min(time_to_finish, time_to_arrival)
        else:
            step = time_to_finish

        step = max(step, 1)

        # Advance remaining burst for the currently running job(s)
        # In a single CPU model with time-sharing among active memory jobs:
        # Each active job gets a slice of execution
        for item in in_memory:
            item["remaining"] -= step

        time += step

        # Check for completed jobs
        for item in list(in_memory):
            if item["remaining"] <= 0:
                item["finish_time"] = time
                j = item["job"]
                tat = time - j["arrival"]
                wait = tat - j["burst"]
                completed.append({
                    "jid": j["jid"],
                    "size": j["size"],
                    "burst": j["burst"],
                    "arrival": j["arrival"],
                    "admitted_at": item["admitted_at"],
                    "finish_time": time,
                    "turnaround": tat,
                    "waiting": wait,
                })
                in_memory.remove(item)

    # Average metrics
    n = len(completed)
    avg_tat = sum(c["turnaround"] for c in completed) / n if n > 0 else 0
    avg_wait = sum(c["waiting"] for c in completed) / n if n > 0 else 0
    avg_dom = sum(t["dom"] for t in timeline) / len(timeline) if timeline else 0
    avg_cpu_util = sum(t["cpu_util"] for t in timeline) / len(timeline) if timeline else 0

    return {
        "completed": completed,
        "timeline": timeline,
        "total_time": time,
        "avg_tat": avg_tat,
        "avg_wait": avg_wait,
        "avg_dom": avg_dom,
        "avg_cpu_util": avg_cpu_util,
        "available_ram": available_ram,
    }
