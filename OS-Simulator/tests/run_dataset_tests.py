"""Headless small/large dataset checks for every simulator module."""

import argparse
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms import cpu_scheduling, disk_scheduling, multiprogramming
from algorithms import page_replacement, segmentation
from module.bankers import find_safe_sequence
from module.paging import calculate_page_counts, translate_logical_address


def check_cpu(dataset):
    if dataset == "small":
        processes = [
            {"pid": "P1", "arrival": 0, "burst": 5, "priority": 2},
            {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1},
            {"pid": "P3", "arrival": 2, "burst": 2, "priority": 3},
        ]
    else:
        processes = [
            {"pid": f"P{i:03}", "arrival": i - 1, "burst": i % 20 + 1,
             "priority": i % 10 + 1}
            for i in range(1, 101)
        ]
    results = [
        cpu_scheduling.fcfs(processes),
        cpu_scheduling.sjf(processes),
        cpu_scheduling.priority_scheduling(processes),
        cpu_scheduling.round_robin(processes, 2),
    ]
    assert all(len(result["results"]) == len(processes) for result in results)
    assert all(result["average_waiting"] >= 0 for result in results)
    return f"{len(processes)} processes; 4 algorithms completed"


def check_bankers(dataset):
    if dataset == "small":
        allocation = ((0, 1, 0), (2, 0, 0), (3, 0, 2), (2, 1, 1), (0, 0, 2))
        maximum = ((7, 5, 3), (3, 2, 2), (9, 0, 2), (2, 2, 2), (4, 3, 3))
        available = (3, 3, 2)
    else:
        allocation = tuple((i % 2, (i + 1) % 2, 0, 0, 0) for i in range(50))
        maximum = allocation
        available = (0, 0, 0, 0, 0)
    sequence = find_safe_sequence(allocation, maximum, available)
    assert sorted(sequence) == list(range(len(allocation)))
    return f"{len(allocation)} processes; safe sequence contains all processes"


def check_paging(dataset):
    if dataset == "small":
        process_size, page_size, memory_size = 1700, 256, 1024
        logical_address, frame = 500, 2
        expected_counts = (7, 4, 0)
    else:
        process_size, page_size, memory_size = 1_000_000, 4096, 16_777_216
        logical_address, frame = 999_999, 100
        expected_counts = (245, 4096, 0)
    assert calculate_page_counts(process_size, page_size, memory_size) == expected_counts
    page, offset, _frame, physical = translate_logical_address(
        logical_address, process_size, page_size, memory_size, {logical_address // page_size: frame}
    )
    assert page == logical_address // page_size
    assert physical == frame * page_size + offset
    assert physical < memory_size
    return f"{expected_counts[0]} pages; address {logical_address} translated to {physical}"


def check_page_replacement(dataset):
    pages = [1, 2, 3, 1, 4, 2] if dataset == "small" else [
        (i * 37) % 100 for i in range(10_000)
    ]
    frames = 3 if dataset == "small" else 20
    outputs = [
        page_replacement.fifo(pages, frames),
        page_replacement.lru(pages, frames),
        page_replacement.optimal(pages, frames),
    ]
    assert all(output["faults"] + output["hits"] == len(pages) for output in outputs)
    return f"{len(pages)} references; FIFO/LRU/Optimal totals verified"


def check_disk(dataset):
    requests = [82, 170, 43, 140] if dataset == "small" else [
        (i * 97) % 100_000 for i in range(1, 1001)
    ]
    head, disk_size = (50, 200) if dataset == "small" else (50_000, 100_000)
    algorithms = (
        lambda: disk_scheduling.fcfs(requests, head),
        lambda: disk_scheduling.sstf(requests, head),
        lambda: disk_scheduling.scan(requests, head, disk_size),
        lambda: disk_scheduling.c_scan(requests, head, disk_size),
        lambda: disk_scheduling.look(requests, head),
        lambda: disk_scheduling.c_look(requests, head),
    )
    outputs = [algorithm() for algorithm in algorithms]
    assert all(len(output["seek_steps"]) >= len(requests) for output in outputs)
    assert all(output["total_seek"] >= 0 for output in outputs)
    return f"{len(requests)} requests; 6 disk algorithms completed"


def check_fragmentation(dataset):
    from PySide6.QtWidgets import QApplication
    from module.fragmentation import FragmentationWindow

    app = QApplication.instance() or QApplication([])
    window = FragmentationWindow()
    if dataset == "large":
        for index in range(1, 50):
            window._add_memory_block(100 + index, refresh=False)
            window._add_process(f"P{index + 4}", 50 + index, refresh=False)
        window._refresh_input_tables()
    window.start_simulation()
    while window.simulation_started and window.process_step < len(window.process_rows):
        window.next_step()
    total, allocated, free, internal, _external, _largest = window._memory_metrics()
    assert allocated + free + internal == total
    window.close()
    app.processEvents()
    return f"{len(window.process_rows)} processes; allocated + free = total ({total})"


def check_multiprogramming(dataset):
    count = 2 if dataset == "small" else 1000
    jobs = [
        {"jid": f"J{i:04}", "arrival": i % 10, "size": 100 + i % 100,
         "burst": i % 5 + 1}
        for i in range(count)
    ]
    result = multiprogramming.simulate_multiprogramming(
        jobs, 1000 if dataset == "small" else 1_000_000,
        200, 2 if dataset == "small" else 50, 0.5
    )
    assert len(result["completed"]) == count
    assert result["total_time"] > 0
    assert all(snapshot["dom"] <= (2 if dataset == "small" else 50)
               for snapshot in result["timeline"])
    return f"{count} jobs; completed in {result['total_time']} time units"


def check_segmentation(dataset):
    count = 3 if dataset == "small" else 1000
    table = {i: {"name": f"S{i}", "base": i * 100, "limit": 100}
             for i in range(count)}
    for segment in (0, count // 2, count - 1):
        result = segmentation.translate_segment_address(table, segment, 99)
        assert result["success"]
        assert result["physical_address"] == segment * 100 + 99
    invalid = segmentation.translate_segment_address(table, 0, 100)
    assert not invalid["success"] and invalid["error_type"] == "SEGMENTATION_FAULT"
    return f"{count} segments; valid and boundary-fault translations verified"


CHECKS = {
    "cpu": check_cpu,
    "bankers": check_bankers,
    "paging": check_paging,
    "page-replacement": check_page_replacement,
    "disk": check_disk,
    "fragmentation": check_fragmentation,
    "multiprogramming": check_multiprogramming,
    "segmentation": check_segmentation,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=("small", "large", "all"), default="all")
    parser.add_argument("--module", choices=tuple(CHECKS), default=None)
    args = parser.parse_args()
    datasets = ("small", "large") if args.dataset == "all" else (args.dataset,)
    checks = {args.module: CHECKS[args.module]} if args.module else CHECKS
    failures = 0
    for dataset in datasets:
        for name, check in checks.items():
            try:
                print(f"[PASS] {name} ({dataset}): {check(dataset)}")
            except Exception as error:
                failures += 1
                print(f"[FAIL] {name} ({dataset}): {error}")
    return failures


if __name__ == "__main__":
    sys.exit(main())
