from pathlib import Path
import datetime

import jwt

from django.conf import settings
from django.shortcuts import render


def try_loom(request):
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(hours=1)
    public_loom_id = settings.LOOM_PUBLIC_ID

    pem_file = Path(settings.LOOM_SDK_PEM)
    with pem_file.open("rb") as pem:
        payloads = {
            "iss": public_loom_id,
            "iat": now,
            "exp": exp
        }

        jws = jwt.encode(payloads, pem.read(), algorithm="RS256")
        return render(request, "try_loom.html", {"jws": jws})
