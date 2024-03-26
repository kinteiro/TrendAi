import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sys
project_path = Path(__file__).resolve().parents[1].as_posix()
sys.path.append(project_path)
from common.s3_service import S3Connector

import sys

# ---- Variables ----
chrome_options = Options()
# chrome_options.add_argument('--headless')
vogue_url = 'https://www.vogue.com'
# main_url = 'https://www.vogue.com/fashion-shows/seasons' # Para obtener todas las temporadas
main_url = 'https://www.vogue.com/fashion-shows/latest-shows' # Para obtener los últimos desfiles
designer_dict = {}
year = str(datetime.now().year)
fecha_scrapped = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
path = Path.cwd() / "Vogue_srapping/"


# ---- Funciones ----
def get_scrapped_df_designers(path: str) -> pd.DataFrame:
    scrapped_df = pd.read_csv(path)
    scrapped_designers = scrapped_df["designer"].unique().tolist()
    return scrapped_designers


def verify_status_code(url: str) -> bool:
    response = requests.get(url)
    status_code = response.status_code
    if status_code == 200:
        html_content = response.text
        print(f"Pagina obtenida. \nhead de la página: \n{html_content[:30]}")
        return BeautifulSoup(html_content, 'html.parser')
    else:
        print("Error al obtener la página:", status_code)


def get_all_urls(soup):
    enlaces = soup.find_all('a')
    return enlaces


def save_links_to_txt(enlaces, not_included):
    with open(f"{fecha_scrapped}_vogue_enlaces.txt", "w") as file:
        for enlace in enlaces:
            enlace = enlace.get('href')
            if year and "fashion-shows/" in enlace\
                and enlace not in not_included and year in enlace:
                file.write(f"{vogue_url}{enlace}\n")


# def get_designer_name(enlace, not_included, scrapped_designers):
#     enlace = enlace.get('href')
#     if year and "fashion-shows/" in enlace\
#             and enlace not in not_included: # TODO: VER si funciona con el string
#         designer_page = vogue_url+ enlace
#         designer_name = enlace.split('/')[-1]
#         return designer_page, designer_name

def scrape_all_page(enlaces, scrapped_designers: list) -> list: 
    not_included = ["/fashion-shows/latest-shows", "/fashion-shows/seasons", "/fashion-shows/designers", "/fashion-shows/featured"]
    # save_links_to_txt(enlaces, not_included)
    for enlace in enlaces:
        enlace = enlace.get('href')
        if year and "fashion-shows/" in enlace\
                and enlace not in not_included: # TODO: VER si funciona con el string
            designer_page = vogue_url + enlace
            designer_name = enlace.split('/')[-1]
            if designer_name in scrapped_designers:
                print(f"El diseñador {designer_name} ya fue descargado. Continuando con el siguiente diseñador.")
                continue
            print(f"Descargando enlace de {designer_name}: {designer_page}")
            response = requests.get(designer_page)
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                # sacar la pagina de ver las imagenes
                boton = soup.find_all(class_="RunwayShowPageGalleryCta-fmTQJF FtdcL")
                # sacar el link de la pagina de imagenes
                link = boton[0].find('a').get('href')
                scrape_images(link, designer_name)
                

def scrape_images(link, designer_name):
    if link:
        driver = webdriver.Chrome(options=chrome_options)
        collection_page = vogue_url + link
        driver.get(collection_page)
        try:
            terms_button = driver.find_element('xpath', '//*[@id="onetrust-accept-btn-handler"]')
            terms_button.click() 
        except NoSuchElementException:
            print("No se encontró el botón de aceptar términos. Continuando sin hacer clic.")
        time.sleep(3)
        try:
            ad_button = driver.find_element('xpath', '//*[@id="app-root"]/div/div/div[6]/div[1]/div/button')
            ad_button.click() 
        except NoSuchElementException:
            print("No se encontró el botón de publicidad. Continuando sin hacer clic.")
        image_count = 0
        previous_page_source = None
        while True:
            try:
                button = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, 
                            '//*[@id="main-content"]/div[2]/div[1]/div[1]/div/div/div[1]/div[2]/div[3]')))
                if button.is_enabled():
                    image_count += 1
                    button.click()
                    time.sleep(1)
                    img = driver.find_element('xpath', '//*[@id="main-content"]/div/div[1]/div[2]/div/div/ul/li/div[1]/div/span/picture/img')
                    img_url = img.get_attribute('src')
                    current_page_source = driver.page_source
                    print(f"Descargando imagen {image_count} de {designer_name}: {img_url}")
                    if designer_name not in designer_dict:
                        designer_dict[designer_name] = [img_url]
                    else:
                        designer_dict[designer_name].append(img_url)

                    if current_page_source == previous_page_source:
                        print("No hay más imágenes disponibles. Se alcanzó el final de la colección.")
                        driver.quit()
                        break
                    else:
                        previous_page_source = current_page_source
                        
                else:
                    print("El botón está deshabilitado. Se alcanzó el final de la colección.")
                    break
                        
            except Exception as e:
                print("Error:", e)
                break  # Salir del bucle si hay un error o no hay más páginas


def get_temporada(str):
    if "fall" or "winter" in str:
        return "otoño - invierno"
    elif "spring" or "summer" in str:
        return "primavera - verano"
    else:
        return "otro"


def create_df_from_page(designer_dict):
    data = []
    # Recorrer el diccionario y agregar los datos a la lista
    for designer, urls in designer_dict.items():
        for url in urls:
            data.append({'designer': designer, 'url': url})

    # Crear el DataFrame a partir de la lista
    if data:
        df = pd.DataFrame(data)
        df["temporada"]=df["url"].apply(lambda x: get_temporada(x)) if "url" in df.columns else "Error"
        df["fecha_scrapped"] = fecha_scrapped
        df["fuente"] = "vogue"
        df["Year"] = int(year)
        return df
    else:
        print("No se encontraron datos para crear el DataFrame.")
        return None


def df_to_csv(df, s3=None):
    if df is not None:
        df.to_csv(f"{fecha_scrapped}_vogue_scrapped.csv", index=False)
        if s3:
            s3.upload_df_to_s3("vogue_scrapped", df, f"{fecha_scrapped}_vogue_scrapped.csv")
        print(f"Los datos se han guardado en {fecha_scrapped}_vogue_scrapped.csv")
    else:
        print("No se ha creado el DataFrame. No se puede guardar el archivo CSV.")



# ---- Main ----
def main():
    scrapped_designers = get_scrapped_df_designers(f'{path}/vogue_season_2.csv')
    soup = verify_status_code(main_url)
    enlaces = get_all_urls(soup)
    try:
        scrape_all_page(enlaces, scrapped_designers)
        df = create_df_from_page(designer_dict)
        try:
            s3 = S3Connector(project_path)
        except Exception as e:
            print(f"Error al conectar con S3: {e}")
            s3 = None
        df_to_csv(df, s3)
        print("Scraping finalizado.")

    except Exception as e:
        print("Error:", e)
        df = create_df_from_page(designer_dict)
        df_to_csv(df, s3)
        

    finally:
        try:
            driver.quit()
        except NameError:
            print("No se encontró el driver.")


if __name__ == "__main__":
    main()