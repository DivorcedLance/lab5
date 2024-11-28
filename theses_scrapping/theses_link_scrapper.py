from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Configuración del WebDriver
driver = webdriver.Chrome()
base_url = "https://cybertesis.unmsm.edu.pe/community/c7f57711-06e9-4821-8ccb-639c2874b28b"

# Abrir página inicial
driver.get(base_url)

# Hacer clic en el botón para acceder a la lista de tesis
wait = WebDriverWait(driver, 10)
button_selector = "#root > div > main > div > div.MuiStack-root.css-1ov46kg > div:nth-child(3) > div > div:nth-child(3) > div > div > a"

try:
    boton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
    boton.click()
    time.sleep(3)  # Esperar a que la página cargue completamente
except Exception as e:
    print("Error al hacer clic en el botón:", e)
    driver.quit()

# Función para extraer los enlaces de las tesis de la página actual
def extract_thesis_links():
    links = []
    try:
        thesis_elements = driver.find_elements(By.CSS_SELECTOR, "a.MuiTypography-root.MuiTypography-h5.MuiLink-root.MuiLink-underlineNone.css-mr5w6s")
        for element in thesis_elements:
            links.append(element.get_attribute("href"))
    except Exception as e:
        print("Error al extraer enlaces:", e)
    return links

# Recolectar enlaces de todas las páginas
all_links = []
while True:
    # Extraer enlaces de la página actual
    all_links.extend(extract_thesis_links())
    
    try:
        # Intentar hacer clic en el botón "Siguiente" para cambiar de página
        next_button_selector = "#root > div > main > div > div:nth-child(3) > div:nth-child(2) > div.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation1.MuiCard-root.css-10ltzvv > div.MuiCardActions-root.MuiCardActions-spacing.css-1f01y2s > div > div > div.MuiTablePagination-actions > button:nth-child(2)"
        next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
        
        if not next_button.is_enabled():
            break  # Salir si el botón no está habilitado
        next_button.click()
        time.sleep(3)  # Esperar a que la nueva página cargue completamente
    except Exception as e:
        print("No hay más páginas disponibles o error:", e)
        break

# Guardar los enlaces en un archivo CSV
df = pd.DataFrame(all_links, columns=["Link"])
df.to_csv("theses_links.csv", index=False)
print("Enlaces guardados en 'theses_links.csv'")

# Cerrar el navegador
driver.quit()
