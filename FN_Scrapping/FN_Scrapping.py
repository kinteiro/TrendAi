import pandas as pd
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import re
import json
from io import StringIO

# Variables globales y constante
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
chrome_options = Options()
chrome_options.add_argument(f"user-agent={headers['user-agent']}")
chrome_options.add_argument('--log-level=3')
year = str(datetime.now().year)
fecha_scrapped = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
root_data = Path.cwd() / "data"
processed_links_path = list(root_data.glob('FN*.csv'))
processed_links_file = processed_links_path[0].as_posix()
url = "https://es.fashionnetwork.com/galeries/fashion-week,1.html"
main_url = "https://es.fashionnetwork.com"


def is_valid_link(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al verificar la validez del enlace {url}: {e}")
        return False



def scroll_to_bottom(driver):
    enlaces_actuales = 0
    
    for _ in range(50):  # Cambia el número según tus necesidades
        # Hacer scroll hasta el final de la página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Esperar un momento para que carguen más elementos
        time.sleep(3)

        # Obtener el contenido HTML actualizado de la página
        html = driver.page_source
        # Parsear el HTML actualizado con BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Obtener el número de enlaces actualizado
        enlaces_nuevos = len(soup.find_all("a", href=True))

        # Si no hay nuevos enlaces, detener el bucle
        if enlaces_nuevos == enlaces_actuales:
            break

        # Actualizar el número actual de enlaces
        enlaces_actuales = enlaces_nuevos


def get_links(links_df):
    existing_links = set(links_df["page_url"])

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(2)
    scroll_to_bottom(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    enlaces = soup.find_all("a", href=True)
    for enlace in enlaces:
        shows_path = enlace["href"]
        if "/galeries/photos/" in shows_path:
            shows_url = main_url + shows_path 
            if shows_url not in existing_links:
                print(shows_url)
                existing_links.add(shows_url)
    driver.quit()
    return existing_links


def verify_processed_image_inks(processed_links, existing_links):
    links_to_process  = list(set(existing_links) - set(processed_links))
    return links_to_process


def get_images_from_links(links):
    driver = webdriver.Chrome(options=chrome_options)
    designer_and_images = []
    if links:
        try:
            for url in links:
                print(f"Procesando la página: {url}")
                url = url.strip()
                if not is_valid_link(url):
                    print(f"El enlace {url} no es válido. Saltando...")
                    continue
                designer_name = get_designer_names(url)
                driver.get(url)
                time.sleep(2)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                image_info = soup.find_all("div", class_="informations")
                if not image_info:
                    print(f"No se encontró información en el enlace {url}. Saltando...")
                    continue
                image_info = image_info[0].text
                temporada, year, ciudad, tipo = procesar_linea(image_info)
                images = soup.find_all("img", class_="item__img gallery-photo")
                if not images:
                    print(f"No se encontraron imágenes en el enlace {url}. Saltando...")
                    continue
                for image in images:
                    image_url = image["src"]

                    designer_data = {
                        "designer": designer_name,
                        "page_url": url,
                        "year": year,
                        "temporada": temporada,
                        "city": ciudad,
                        "tipo": tipo,
                        "url": image_url
                    }
                    designer_and_images.append(designer_data)

            if not designer_and_images:
                print("No se encontraron datos válidos en los enlaces.")
                return None

            json_data = json.dumps(designer_and_images, indent=4)
            return json_data
        except Exception as e:
            print(f"Error al procesar los enlaces: {e}")
            return None
    else:
        print("No se proporcionaron enlaces para procesar.")
        return None



def process_df(df):
    df["designer"] =  df["designer"].map(lambda x: x[:-1].replace("-", "") if x.endswith("-") else x)
    df["designer"] =  df["designer"].map(lambda x: x[:-1].replace(" ", "") if x.startswith(" ") else x)
    df["designer"] =  df["designer"].map(lambda x: x.replace("-", " ") if len(x) > 4 else x)
    df["temporada"] = df["temporada"].map(lambda x: x.replace("/", " - "))
    df["year"] = df["year"].map(lambda x: int(x[0:4]))
    return df


def get_processed_links():
    df = pd.read_csv(processed_links_file)
    processed_links = df["page_url"].unique().tolist()
    return processed_links


def get_designer_names(link):
    match = re.search(r"\/([^\/,]+),\d+\.html", link)
    if match:
        return match.group(1)


def procesar_linea(linea):
    partes = linea.strip().split(' - ')
    info_principal = partes[0]
    info_temp = info_principal.split(' ')
    temporada = info_temp[0]
    year = info_temp[1]
    ciudad = ''
    if len(info_temp) > 2:
        ciudad = ' '.join(info_temp[2:])
    tipo = partes[1] if len(partes) > 1 else ''
    return temporada, year, ciudad, tipo


def main():
    chrome_options.add_argument('--headless')
    processed_links_df = pd.read_csv(processed_links_file)
    existing_links = set(processed_links_df["page_url"])
    new_links = get_links(processed_links_df)
    links_to_process = verify_processed_image_inks(get_processed_links(), existing_links | new_links)
    json_data = get_images_from_links(links_to_process)
    if json_data:
        df = pd.read_json(StringIO(json_data))
        df = process_df(df)
        df.to_csv(processed_links_file, mode="a", index=False, header=False)
    else:
        print("No hay enlaces para procesar")


if __name__ == "__main__":
    main()
