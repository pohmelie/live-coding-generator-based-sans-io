import requests
import time
import reprlib


proxies = {
    "http": "socks4://localhost:8081",
}
while True:
    try:
        r = requests.get("http://localhost:8000", proxies=proxies)
        r.raise_for_status()
        assert r.content
    except Exception as e:
        print(time.time(), reprlib.repr(e))
    else:
        print(time.time(), "ok")
    finally:
        time.sleep(1)
