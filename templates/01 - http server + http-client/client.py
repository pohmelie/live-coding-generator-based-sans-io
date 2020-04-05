import requests
import time
import reprlib


while True:
    try:
        r = requests.get("http://localhost:8000")
        r.raise_for_status()
        assert r.content
    except Exception as e:
        print(time.time(), reprlib.repr(e))
    else:
        print(time.time(), "ok")
    finally:
        time.sleep(1)
