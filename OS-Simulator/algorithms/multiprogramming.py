"""Multiprogramming simulation engine (Degree of Multiprogramming, Memory Admittance, and CPU Utilization)."""


def calculate_cpu_utilization(io_wait_fraction, degree_of_multiprogramming):
    """
    Computes theoretical CPU utilization based on the probabilistic multiprogramming model:
    CPU Utilization = 1 - (p ^ n)
    where:
        p = fraction of time a process spends waiting for I/O (0.0 to 1.0)
        n = degree of multiprogramming (number of concurrent processes in memory)
    """
    if degree_of_multiprogramming <= 0:
        return 0.0
    p = max(0.0, min(1.0, float(io_wait_fraction)))
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
    available_ram = total_memory - os_reserved
    if available_ram <= 0:
        raise ValueError("OS reserved memory exceeds or equals total RAM.")

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
                break
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
