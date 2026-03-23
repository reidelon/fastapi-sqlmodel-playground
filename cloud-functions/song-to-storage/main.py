import base64
import json
import os
from datetime import datetime

from google.cloud import storage

BUCKET_NAME = os.environ.get("BUCKET_NAME", "fastapi-demo-2026-songs")
REQUIRED_FIELDS = {"event", "song_id", "name", "artist", "year", "timestamp"}


def save_song_to_storage(request):
    # 1. Extraer el body del request como JSON
    envelope = request.get_json(silent=True)
    if not envelope or "message" not in envelope:
        return ("Bad Request: missing Pub/Sub message", 400)

    # 2. Extraer y decodificar el campo message.data (viene en base64)
    pubsub_message = envelope["message"]
    try:
        data = json.loads(base64.b64decode(pubsub_message["data"]).decode("utf-8"))
    except Exception:
        return ("Bad Request: could not decode message data", 400)

    # 3. Validar que los campos esperados estén presentes con el tipo correcto
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        return (f"Bad Request: missing fields {missing}", 400)
    if not isinstance(data["song_id"], int):
        return ("Bad Request: song_id must be an integer", 400)

    # 4. Escribir el JSON en el bucket
    filename = f"song_{data['song_id']}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')}.json"
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(json.dumps(data), content_type="application/json")

    return ("OK", 200)
