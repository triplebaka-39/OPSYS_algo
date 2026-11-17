def _validate_input(pages, frame_count):
    if frame_count <= 0:
        raise ValueError("Number of frames must be greater than zero.")
    if not pages:
        raise ValueError("Page reference string cannot be empty.")
    if any(page < 0 for page in pages):
        raise ValueError("Page numbers cannot be negative.")


def _result(pages, frames_history, statuses, faults, hits):
    return {
        "results": [
            {
                "page": page,
                "frames": frames,
                "status": status,
            }
            for page, frames, status in zip(
                pages, frames_history, statuses
            )
        ],
        "faults": faults,
        "hits": hits,
        "fault_rate": faults / len(pages) * 100,
    }


def fifo(pages, frame_count):
    _validate_input(pages, frame_count)

    frames = [None] * frame_count
    frames_history = []
    statuses = []
    next_frame = 0
    faults = 0

    for page in pages:
        if page in frames:
            statuses.append("Hit")
        else:
            frames[next_frame] = page
            next_frame = (next_frame + 1) % frame_count
            faults += 1
            statuses.append("Fault")
        frames_history.append(frames.copy())

    return _result(
        pages,
        frames_history,
        statuses,
        faults,
        len(pages) - faults,
    )


def lru(pages, frame_count):
    _validate_input(pages, frame_count)

    frames = [None] * frame_count
    last_used = {}
    frames_history = []
    statuses = []
    faults = 0

    for index, page in enumerate(pages):
        if page in frames:
            statuses.append("Hit")
        else:
            if None in frames:
                replacement_index = frames.index(None)
            else:
                replacement_index = min(
                    range(frame_count),
                    key=lambda frame_index: last_used[frames[frame_index]],
                )
            frames[replacement_index] = page
            faults += 1
            statuses.append("Fault")

        last_used[page] = index
        frames_history.append(frames.copy())

    return _result(
        pages,
        frames_history,
        statuses,
        faults,
        len(pages) - faults,
    )


def optimal(pages, frame_count):
    _validate_input(pages, frame_count)

    frames = [None] * frame_count
    frames_history = []
    statuses = []
    faults = 0

    for index, page in enumerate(pages):
        if page in frames:
            statuses.append("Hit")
        else:
            if None in frames:
                replacement_index = frames.index(None)
            else:
                replacement_index = max(
                    range(frame_count),
                    key=lambda frame_index: _next_use(
                        pages,
                        index,
                        frames[frame_index],
                    ),
                )
            frames[replacement_index] = page
            faults += 1
            statuses.append("Fault")
        frames_history.append(frames.copy())

    return _result(
        pages,
        frames_history,
        statuses,
        faults,
        len(pages) - faults,
    )


def _next_use(pages, current_index, page):
    try:
        return pages.index(page, current_index + 1)
    except ValueError:
        return len(pages)
