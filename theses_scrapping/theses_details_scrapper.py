import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Cargar los enlaces desde el archivo CSV
links_df = pd.read_csv('./theses_scrapping/theses_links.csv')  # Asegúrate de que el archivo esté en el mismo directorio
links = links_df['Link'].tolist()

# Configuración inicial del navegador
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Función auxiliar para manejar fallos al extraer elementos
def safe_get_text(selector_type, selector, multiple=False, attribute=None):
    try:
        if selector_type == "css":
            if multiple:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                return [elem.get_attribute(attribute) if attribute else elem.text for elem in elements]
            element = driver.find_element(By.CSS_SELECTOR, selector)
        elif selector_type == "xpath":
            if multiple:
                elements = driver.find_elements(By.XPATH, selector)
                return [elem.get_attribute(attribute) if attribute else elem.text for elem in elements]
            element = driver.find_element(By.XPATH, selector)
        return element.get_attribute(attribute) if attribute else element.text
    except Exception:
        return "" if not multiple else []

# Función para extraer la información de una tesis
def extract_thesis_details(link):
    driver.get(link)
    time.sleep(0.25)  # Espera breve para cargar la página completamente

    try:
        # Extraer título
        title = safe_get_text("css", "span.MuiCardHeader-title")

        # Extraer autores
        authors = safe_get_text(
            "xpath",
            "//h6[text()='Autor(es)']/following-sibling::div/a",
            multiple=True
        )

        # Extraer fecha de publicación
        publication_date = safe_get_text("xpath", "//h6[text()='Fecha de publicación']/following-sibling::div")

        # Extraer asesor(es)
        advisor = safe_get_text("xpath", "//h6[text()='Asesor(es)']/following-sibling::div")

        # Extraer editorial
        editorial = safe_get_text("xpath", "//h6[text()='Editorial']/following-sibling::div")

        # Extraer resumen
        summary = safe_get_text("xpath", "//h6[text()='Resumen']/following-sibling::div")

        # Extraer palabras clave
        keywords = safe_get_text("xpath", "//h6[text()='Palabras clave']/following-sibling::div/a", multiple=True)

        # Extraer identificador único
        identifier = safe_get_text("xpath", "//h6[text()='Identificador único']/following-sibling::div/a", attribute="href")

        # Extraer tipo de acceso
        access_type = safe_get_text("xpath", "//h6[text()='Tipo de acceso']/following-sibling::div")

        # Extraer colección
        collection = safe_get_text("xpath", "//h6[text()='Pertenece a la colección']/following-sibling::a")

        return {
            "Link": link,
            "Título": title,
            "Autores": ", ".join(authors),
            "Fecha de publicación": publication_date,
            "Asesor(es)": advisor,
            "Editorial": editorial,
            "Resumen": summary,
            "Palabras clave": ", ".join(keywords),
            "Identificador único": identifier,
            "Tipo de acceso": access_type,
            "Colección": collection,
        }
    except Exception as e:
        print(f"Error extrayendo datos de {link}: {e}")
        return None

# Extraer la información de todas las tesis
theses_data = []
for link in links:
    print(f"Extrayendo información de: {link}")
    thesis_details = extract_thesis_details(link)
    if thesis_details:
        theses_data.append(thesis_details)

# Guardar los datos en un archivo CSV
output_df = pd.DataFrame(theses_data)
output_df.to_csv('./theses_details.csv', index=False, encoding='utf-8-sig', sep=';')

print("Extracción completada. Los datos se guardaron en 'theses_details.csv'.")

# Cerrar el navegador
driver.quit()
