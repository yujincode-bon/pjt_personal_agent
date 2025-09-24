import re

def parse_raw_line(raw_line: str) -> list[dict]:
    results = []

    pattern = re.compile(
        r"(?P<name>[A-Za-z0-9\- ()+]+?)\s*[:\-]?\s*(?P<amount>\d+(\.\d+)?)\s*(?P<unit>mg|mcg|g|iu)",
        re.IGNORECASE
    )

    for match in pattern.finditer(raw_line):
        name = match.group("name").strip()
        name = re.sub(r"\s*\(.*?\)", "", name).strip()

        try:
            amount = float(match.group("amount"))
        except (TypeError, ValueError):
            continue

        unit = match.group("unit").strip().lower()

        results.append({
            "name": name,
            "amount": amount,
            "unit": unit
        })

    return results