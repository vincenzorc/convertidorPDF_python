def parse_page_ranges(range_str: str, total_pages: int) -> list[int]:
    """
    Parse a string of page ranges and return a list of page numbers (1-indexed).
    Example: "1,3,5-8" -> [1, 3, 5, 6, 7, 8]
    Pages outside the range 1..total_pages are ignored.
    """
    pages = set()
    if not range_str.strip():
        return []
    parts = range_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            try:
                start = int(start.strip())
                end = int(end.strip())
            except ValueError:
                continue
            if start > end:
                start, end = end, start
            for p in range(start, end + 1):
                if 1 <= p <= total_pages:
                    pages.add(p)
        else:
            try:
                p = int(part)
            except ValueError:
                continue
            if 1 <= p <= total_pages:
                pages.add(p)
    return sorted(pages)


def parse_reorder_range(range_str: str, total_pages: int) -> list[int]:
    """
    Parse a string for reordering, e.g., "3,1,2,4".
    Returns a list of page numbers (1-indexed) in the new order.
    Must contain exactly total_pages unique numbers from 1..total_pages.
    """
    if not range_str.strip():
        return []
    parts = range_str.split(',')
    pages = []
    for part in parts:
        part = part.strip()
        try:
            p = int(part)
        except ValueError:
            return []
        if p < 1 or p > total_pages:
            return []
        pages.append(p)
    # Check for duplicates and correct length
    if len(pages) != total_pages or len(set(pages)) != total_pages:
        return []
    return pages