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
    if seg_num not in segment_table:
        return {
            "success": False,
            "error_type": "INVALID_SEGMENT",
            "message": f"Segment #{seg_num} does not exist in the Segment Table."
        }

    entry = segment_table[seg_num]
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
