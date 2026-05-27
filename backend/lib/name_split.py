def split_full_name(full_name: str) -> dict[str, str]:
    t = full_name.strip()
    if not t:
        return {"first_name": "User", "last_name": "User"}
    parts = [p for p in t.split() if p]
    if len(parts) == 1:
        p = parts[0]
        return {"first_name": p[:15], "last_name": p[:20]}
    first = parts[0][:15]
    last = " ".join(parts[1:])[:20]
    return {"first_name": first, "last_name": last}
