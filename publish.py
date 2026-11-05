"""Publica o carrossel de hoje no Instagram via Graph API."""
import os, sys, time, requests
from generate import carregar_posts, hoje

API = "https://graph.facebook.com/v23.0"
IG_ID = os.environ["IG_USER_ID"]
TOKEN = os.environ["IG_ACCESS_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")

def chamar(metodo, url, **kw):
    r = requests.request(metodo, url, timeout=60, **kw)
    if not r.ok:
        sys.exit(f"Erro {r.status_code}: {r.text}")
    return r.json()

def esperar_container(cid):
    for _ in range(30):
        s = chamar("GET", f"{API}/{cid}", params={"fields": "status_code", "access_token": TOKEN})
        if s["status_code"] == "FINISHED":
            return
        if s["status_code"] in ("ERROR", "EXPIRED"):
            sys.exit(f"Container {cid} falhou: {s}")
        time.sleep(5)
    sys.exit("Tempo esgotado esperando o container.")

def esperar_url(url):
    for _ in range(24):  # o GitHub pode levar alguns segundos para servir o arquivo
        if requests.head(url, timeout=30).status_code == 200:
            return
        time.sleep(5)
    sys.exit(f"Imagem não ficou pública: {url}")

def main():
    data = hoje()
    post = next((p for p in carregar_posts() if p["data"] == data), None)
    if not post:
        print("Nenhum post agendado para hoje.")
        return
    if os.path.exists("posted.txt") and data in open("posted.txt").read().split():
        print("Hoje já foi publicado.")
        return

    filhos = []
    for i in range(1, len(post["slides"]) + 1):
        url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/images/{data}/slide_{i}.jpg"
        esperar_url(url)
        c = chamar("POST", f"{API}/{IG_ID}/media",
                   data={"image_url": url, "is_carousel_item": "true", "access_token": TOKEN})
        filhos.append(c["id"])

    for cid in filhos:
        esperar_container(cid)

    carrossel = chamar("POST", f"{API}/{IG_ID}/media", data={
        "media_type": "CAROUSEL", "children": ",".join(filhos),
        "caption": post["legenda"], "access_token": TOKEN})
    esperar_container(carrossel["id"])

    pub = chamar("POST", f"{API}/{IG_ID}/media_publish",
                 data={"creation_id": carrossel["id"], "access_token": TOKEN})
    print("Publicado! ID:", pub["id"])
    with open("posted.txt", "a") as f:
        f.write(data + "\n")

if __name__ == "__main__":
    main()
