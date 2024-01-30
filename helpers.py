from bs4 import BeautifulSoup
import requests
import fitz

import logging

BASE_URL = "https://sede.valencia.es"

def parse_subtitol(txt):
    # Exemple: EDICTE INFORMACIÓ PÚBLICA - RESIDÈNCIA PER A PERSONES MAJORS
    if ("-" in txt):
        return txt.split("-")[1].strip()
    # Exemple: INFORMACIÓ PÚBLICA ACTIVITAT ECOLLAVAT VEHICLES EN SECO I COMPRAVENDA DE VEHICLES
    elif ("blica" in txt.lower()):
        aux = txt.lower().replace("ú", "u")
        i = aux.index("publica")
        
        return txt[i + 8:]
    # Exemple: Implantació activitat d'hotel en l'Av. Port, 31
    else:
        return txt


def process_url(url):
    
    req = requests.get(BASE_URL + url)
    doc = BeautifulSoup(req.text, 'html.parser')
    
    titol = doc.select("#rotuloAnuncio")[0].get_text().strip()
    data  = titol.split("(")[1].strip()[:-1]

    subtitol = parse_subtitol( doc.select("#detalleCuerpoAnuncio")[0].get_text().strip() )

    pdf_url = doc.select_one(".enlaceAnuncio a")["href"]
    pdf_info, img = download_pdf(pdf_url)
    
    return {"subtitol": subtitol, "data": data, "img": img, **pdf_info}


def parse_pdf(req):
    doc = fitz.open(
        stream=req,
        filetype="pdf"
    )
    
    text = doc[0].get_text()
    
    info = {}
    info["id"] = text.split("\n")[3]
    
    for line in text.split("\n"):
        aux = line.lower()

        if (aux.startswith("titular") or aux.startswith("solicitante")):
            info["qui"] = line.split(":")[1].strip()
        elif (aux.startswith("actividad:")):
            info["que"] = line.split(":")[1].strip()
        elif (aux.startswith("emplazamiento")):
            info["on"] = line.split(":")[1].strip()
    
    return info, doc[0].get_pixmap()


def download_pdf(url):
    req = requests.get(BASE_URL + url)
    txt, img = parse_pdf(req.content)
    
    return txt, img