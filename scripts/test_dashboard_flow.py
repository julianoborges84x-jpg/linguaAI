import time

import requests


BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    stamp = int(time.time())
    email = f"flow{stamp}@example.com"
    password = "123"

    reg = requests.post(
        f"{BASE_URL}/users",
        json={"name": "Flow User", "email": email, "password": password},
        timeout=20,
    )
    reg.raise_for_status()

    login = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password},
        timeout=20,
    )
    login.raise_for_status()
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = requests.get(f"{BASE_URL}/users/me", headers=headers, timeout=20)
    me.raise_for_status()

    chat = requests.post(f"{BASE_URL}/chat", headers=headers, json={"message": "i study english"}, timeout=20)
    chat.raise_for_status()

    progress = requests.get(f"{BASE_URL}/progress", headers=headers, timeout=20)
    progress.raise_for_status()

    print("OK: login/chat/users/me/progress")


if __name__ == "__main__":
    main()
