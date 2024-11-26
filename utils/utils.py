def prettify_minutes(hours):
    hours_truncated = int(hours)
    minutes = int((hours-hours_truncated)*60)
    return f"{hours_truncated} ore e {minutes} minuti"
