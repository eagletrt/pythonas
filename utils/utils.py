def prettify_minutes(hours):
    hours_truncated = int(hours)
    minutes = int((hours-hours_truncated)*60)
    if hours_truncated < 1:
        return f"{minutes} minuti"
    return f"{hours_truncated} ore e {minutes} minuti"
