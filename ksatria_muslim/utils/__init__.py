
def sentry_before_send(event, hint):
    # skip disallowed host
    logger = event.get("logger")
    if logger and logger == "django.security.DisallowedHost":
        return

    return event
