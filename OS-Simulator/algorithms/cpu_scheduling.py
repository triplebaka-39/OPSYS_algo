"""CPU scheduling algorithms used by the simulator."""


def _validate_processes(processes, needs_priority=False):
    if not processes:
        raise ValueError("At least one process is required.")
    seen = set()
    for index, process in enumerate(processes, start=1):
        if not isinstance(process, dict):
            raise ValueError(f"Process {index} must be a mapping of process fields.")
        pid = str(process.get("pid", "")).strip()
        if not pid:
            raise ValueError(f"Process ID is missing for process {index}.")
        if pid in seen:
            raise ValueError(f"Duplicate Process ID: {pid}")
        seen.add(pid)
        for field in ("arrival", "burst"):
            value = process.get(field)
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"{field.title()} time for {pid} must be a whole number.")
            if (field == "arrival" and value < 0) or (field == "burst" and value <= 0):
                raise ValueError(f"{field.title()} time for {pid} is out of range.")
        if needs_priority:
            priority = process.get("priority")
            if not isinstance(priority, int) or isinstance(priority, bool):
                raise ValueError(f"Priority for {pid} must be a whole number.")


def _result(processes, schedule):
    completion = {}
    first_start = {}
    for segment in schedule:
        if segment["pid"] is None:
            continue
        pid = segment["pid"]
        first_start.setdefault(pid, segment["start"])
        completion[pid] = segment["finish"]

    results = []
    for process in processes:
        pid = process["pid"]
        finish = completion[pid]
        turnaround = finish - process["arrival"]
        results.append({
            **process,
            "start": first_start[pid],
            "finish": finish,
            "waiting": turnaround - process["burst"],
            "turnaround": turnaround,
        })

    count = len(results)
    return {
        "results": results,
        "schedule": schedule,
        "average_waiting": sum(row["waiting"] for row in results) / count,
        "average_turnaround": sum(row["turnaround"] for row in results) / count,
    }


def _non_preemptive(processes, key):
    pending = list(enumerate(processes))
    schedule = []
    time = 0

    while pending:
        ready = [(index, process) for index, process in pending
                 if process["arrival"] <= time]
        if not ready:
            next_arrival = min(process["arrival"] for _, process in pending)
            schedule.append({"pid": None, "start": time, "finish": next_arrival})
            time = next_arrival
            continue

        index, process = min(ready, key=lambda pair: key(pair[1], pair[0]))
        pending.remove((index, process))
        finish = time + process["burst"]
        schedule.append({"pid": process["pid"], "start": time, "finish": finish})
        time = finish

    return _result(processes, schedule)


def fcfs(processes):
    _validate_processes(processes)
    return _non_preemptive(processes, lambda process, index: (process["arrival"], index))


def sjf(processes):
    _validate_processes(processes)
    return _non_preemptive(
        processes,
        lambda process, index: (process["burst"], process["arrival"], index),
    )


def priority_scheduling(processes):
    """Non-preemptive priority; a smaller numeric priority means higher priority."""
    _validate_processes(processes, needs_priority=True)
    return _non_preemptive(
        processes,
        lambda process, index: (
            process["priority"], process["arrival"], index
        ),
    )


def round_robin(processes, quantum):
    _validate_processes(processes)
    if not isinstance(quantum, int) or isinstance(quantum, bool):
        raise ValueError("Time quantum must be a whole number.")
    if quantum <= 0:
        raise ValueError("Time quantum must be greater than zero.")

    ordered = sorted(enumerate(processes), key=lambda pair: (pair[1]["arrival"], pair[0]))
    remaining = {process["pid"]: process["burst"] for process in processes}
    schedule = []
    ready = []
    next_index = 0
    time = 0

    while next_index < len(ordered) or ready:
        if not ready and next_index < len(ordered):
            next_arrival = ordered[next_index][1]["arrival"]
            if time < next_arrival:
                schedule.append({"pid": None, "start": time, "finish": next_arrival})
                time = next_arrival
            while next_index < len(ordered) and ordered[next_index][1]["arrival"] <= time:
                ready.append(ordered[next_index][1])
                next_index += 1

        process = ready.pop(0)
        duration = min(quantum, remaining[process["pid"]])
        start, finish = time, time + duration
        schedule.append({"pid": process["pid"], "start": start, "finish": finish})
        time = finish
        remaining[process["pid"]] -= duration

        while next_index < len(ordered) and ordered[next_index][1]["arrival"] <= time:
            ready.append(ordered[next_index][1])
            next_index += 1
        if remaining[process["pid"]] > 0:
            ready.append(process)

    return _result(processes, schedule)
