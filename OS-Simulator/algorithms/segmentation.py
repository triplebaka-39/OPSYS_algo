"""Segmentation translation algorithm and validation engine."""


def translate_segment_address(segment_table, seg_num, offset):
    """
    Translates a logical address (seg_num, offset) to a physical memory address.

    Args:
        segment_table: dict {seg_num: {"name": str, "base": int, "limit": int}}
        seg_num: int (Segment ID)
        offset: int (Logical Offset d)

    Returns:
        dict containing translation status, physical address, or error details.
    """
    if not isinstance(segment_table, dict):
        return {
            "success": False,
            "error_type": "INVALID_SEGMENT_TABLE",
            "message": "Segment table must be a mapping of segment numbers to entries.",
        }
    ranges = []
    for number, segment in segment_table.items():
        if (not isinstance(number, int) or isinstance(number, bool) or number < 0
                or not isinstance(segment, dict) or "base" not in segment
                or "limit" not in segment):
            return {
                "success": False,
                "error_type": "INVALID_SEGMENT_TABLE",
                "message": "Every segment must define a non-negative number, base, and limit.",
            }
        base, limit = segment["base"], segment["limit"]
        if (not isinstance(base, int) or isinstance(base, bool) or base < 0
                or not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0):
            return {
                "success": False,
                "error_type": "INVALID_SEGMENT_TABLE",
                "message": f"Segment #{number} needs a non-negative base and positive limit.",
            }
        ranges.append((base, base + limit, number))
    ranges.sort()
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            return {
                "success": False,
                "error_type": "OVERLAPPING_SEGMENTS",
                "message": "Segments %d and %d overlap in physical memory."
                % (previous[2], current[2]),
            }
    if not isinstance(seg_num, int) or isinstance(seg_num, bool) or seg_num < 0:
        return {
            "success": False,
            "error_type": "INVALID_SEGMENT",
            "message": "Segment number must be a non-negative whole number.",
        }
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        return {
            "success": False,
            "error_type": "INVALID_OFFSET",
            "message": "Offset must be a non-negative whole number.",
        }
    if seg_num not in segment_table:
        return {
            "success": False,
            "error_type": "INVALID_SEGMENT",
            "message": f"Segment #{seg_num} does not exist in the Segment Table."
        }

    entry = segment_table[seg_num]
    if not isinstance(entry, dict) or "base" not in entry or "limit" not in entry:
        return {
            "success": False,
            "error_type": "INVALID_SEGMENT_TABLE",
            "message": f"Segment #{seg_num} must define a base address and limit.",
        }
    base = entry["base"]
    limit = entry["limit"]
    name = entry.get("name", f"Segment {seg_num}")

    # MMU Limit Validation Check: Offset must be strictly strictly less than Limit
    if offset >= limit:
        return {
            "success": False,
            "error_type": "SEGMENTATION_FAULT",
            "seg_num": seg_num,
            "name": name,
            "base": base,
            "limit": limit,
            "offset": offset,
            "message": f"TRAP: Segmentation Fault! Offset ({offset}) exceeds Limit ({limit}) for {name}."
        }

    physical_address = base + offset
    return {
        "success": True,
        "error_type": None,
        "seg_num": seg_num,
        "name": name,
        "base": base,
        "limit": limit,
        "offset": offset,
        "physical_address": physical_address,
        "message": (
            f"Valid Translation: Offset ({offset}) < Limit ({limit}).\n"
            f"Physical Address = Base ({base}) + Offset ({offset}) = {physical_address}"
        )
    }
