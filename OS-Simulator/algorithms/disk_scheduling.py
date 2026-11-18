"""Disk scheduling algorithms (FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK)."""


def _calculate_result(sequence, raw_requests):
    """Calculate seek steps, total head movement, and average seek distance."""
    seek_steps = []
    total_seek = 0
    for i in range(1, len(sequence)):
        start = sequence[i - 1]
        end = sequence[i]
        seek = abs(end - start)
        total_seek += seek
        seek_steps.append({
            "step": i,
            "from": start,
            "to": end,
            "seek": seek,
            "is_request": end in raw_requests,
        })

    served_count = len(raw_requests)
    avg_seek = (total_seek / served_count) if served_count > 0 else 0.0

    return {
        "sequence": sequence,
        "seek_steps": seek_steps,
        "total_seek": total_seek,
        "average_seek": avg_seek,
    }


def fcfs(requests, head):
    """First-Come, First-Served disk scheduling."""
    sequence = [head] + list(requests)
    return _calculate_result(sequence, set(requests))


def sstf(requests, head):
    """Shortest Seek Time First disk scheduling."""
    sequence = [head]
    pending = list(requests)
    curr = head

    while pending:
        # Pick the track with minimum absolute distance to current head
        closest = min(pending, key=lambda t: abs(t - curr))
        sequence.append(closest)
        pending.remove(closest)
        curr = closest

    return _calculate_result(sequence, set(requests))


def scan(requests, head, disk_size=200, direction="high"):
    """
    SCAN (Elevator) disk scheduling.
    Moves towards the specified end, touches boundary if there are requests on the opposite side,
    then reverses direction.
    """
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    sequence = [head]

    if direction == "high":
        sequence.extend(right)
        if left:
            sequence.append(disk_size - 1)
            sequence.extend(reversed(left))
    else:
        sequence.extend(reversed(left))
        if right:
            sequence.append(0)
            sequence.extend(right)

    return _calculate_result(sequence, set(requests))


def c_scan(requests, head, disk_size=200, direction="high"):
    """
    Circular SCAN disk scheduling.
    Moves towards one end, hits boundary, wraps around to the opposite boundary,
    and continues in the same direction.
    """
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    sequence = [head]

    if direction == "high":
        sequence.extend(right)
        if left:
            sequence.append(disk_size - 1)
            sequence.append(0)
            sequence.extend(left)
    else:
        sequence.extend(reversed(left))
        if right:
            sequence.append(0)
            sequence.append(disk_size - 1)
            sequence.extend(reversed(right))

    return _calculate_result(sequence, set(requests))


def look(requests, head, direction="high"):
    """
    LOOK disk scheduling.
    Like SCAN, but only travels as far as the furthest request in the current direction.
    """
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    sequence = [head]

    if direction == "high":
        sequence.extend(right)
        sequence.extend(reversed(left))
    else:
        sequence.extend(reversed(left))
        sequence.extend(right)

    return _calculate_result(sequence, set(requests))


def c_look(requests, head, direction="high"):
    """
    Circular LOOK disk scheduling.
    Like C-SCAN, but only jumps between the furthest requests in the queue.
    """
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    sequence = [head]

    if direction == "high":
        sequence.extend(right)
        sequence.extend(left)
    else:
        sequence.extend(reversed(left))
        sequence.extend(reversed(right))

    return _calculate_result(sequence, set(requests))
