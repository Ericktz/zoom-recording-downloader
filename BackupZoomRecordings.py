from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
import os
import re

# Configuración de Selenium con Chrome
chrome_options = webdriver.ChromeOptions()
download_directory = "/Users/xxx/Downloads/Backup"  # Ajusta esta ruta según tu directorio de descargas
correo = 'xxx@mail.udp.cl'
clave = 'xxx'
chromeDriverPath = '/usr/local/bin/chromedriver'

# Configuración para permitir múltiples descargas automáticamente
prefs = {
    "profile.default_content_settings.popups": 0,  # Desactivar popups
    "download.prompt_for_download": False,         # No preguntar dónde guardar archivos
    "download.directory_upgrade": True,            # Permitir la descarga de múltiples archivos
    "profile.default_content_setting_values.automatic_downloads": 1,  # Permitir descargas automáticas
    "download.default_directory": download_directory
}

chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")
service = Service(chromeDriverPath)  # Reemplaza con la ruta obtenida

# Inicializa el driver de Chrome usando el nuevo método con `Service`
driver = webdriver.Chrome(service=service, options=chrome_options)

# Función para esperar que haya menos de 'max_active_downloads' descargas activas
def wait_for_download(numNewDownload):
    max_active_downloads=6
    while True:
        # Obtener la lista de archivos que se están descargando (archivos .crdownload)
        downloading_files = [f for f in os.listdir(download_directory) if f.endswith('.crdownload')]
        
        # Si el número de descargas activas es menor que el límite, salir del bucle
        if len(downloading_files) + numNewDownload < max_active_downloads:
            break
        
        # Esperar antes de verificar nuevamente
        print(f"Esperando que se completen descargas activas... ({len(downloading_files)} descargas activas)")
        time.sleep(5)  # Ajusta este tiempo de espera según tus necesidades

# Función para esperar que haya menos de 'max_active_downloads' descargas activas
def wait_for_finish():
    while True:
        # Obtener la lista de archivos que se están descargando (archivos .crdownload)
        downloading_files = [f for f in os.listdir(download_directory) if f.endswith('.crdownload')]

        # cuando termine de descargar odo
        if len(downloading_files) == 0:
            break
        # Esperar antes de verificar nuevamente
        print(f"Esperando que se termine descargas activas... ({len(downloading_files)} descargas activas)")
        time.sleep(5)  # Ajusta este tiempo de espera según tus necesidades


# Abre la página de inicio de sesión de Zoom
driver.get("https://zoom.us/signin")

# Selecciona la opción de iniciar sesión con Google
time.sleep(3)  # Tiempo de espera para cargar la página
google_login_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/div[2]/div/div/a[3]/span")
google_login_button.click()

# Aquí se abrirá la página de autenticación de Google
time.sleep(3)

# Inicia sesión con tu cuenta de Google (Selenium completará los campos)
email_field = driver.find_element(By.ID, "identifierId")
email_field.send_keys(correo)
email_field.send_keys(Keys.RETURN)

# Seleccionar la cuenta de Google Workspace (espera hasta que la opción esté disponible)
time.sleep(3)
workspace_account_xpath = "/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[2]/div/div/div[1]/form/span/section/div/div/div/ul/li[1]/div/div[2]/div[1]"
workspace_account = driver.find_element(By.XPATH, workspace_account_xpath)
workspace_account.click()

# Espera unos segundos y luego ingresa la contraseña (puede que necesites ajustar la espera)
time.sleep(3)
password_field = driver.find_element(By.NAME, "Passwd")
password_field.send_keys(clave)
password_field.send_keys(Keys.RETURN)

# Navega a la página de grabaciones una vez que estés autenticado
time.sleep(3)
driver.get("https://zoom.us/recording")

# Espera a que cargue la página de grabaciones
time.sleep(3)

# Aquí puedes obtener los enlaces de descarga
def download_recordings(driver):
    unavez = True
    while True:
        # Obtener las filas de grabaciones
        rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'table')]//tbody/tr")
        for index, row in enumerate(rows):
            Texto = row.text
            numArchivosActual = re.search(r'(\d+) Archivos', Texto)
            print(int(numArchivosActual.group(1)))
            try:
                # Esperar a que la suma de archivos a descargar + descargas activas sean menos de 6 antes de seguir
                wait_for_download(int(numArchivosActual.group(1)))
                
                # Hacer clic en el icono 'más' en la última columna de cada fila
                more_icon = row.find_element(By.XPATH, ".//div[@class='zm-dropdown']/button")
                time.sleep(1)
                more_icon.click()

                # Obtener el valor de aria-controls del icono que se hizo clic
                aria_controls_value = more_icon.get_attribute("aria-controls")
                print(aria_controls_value)
                time.sleep(1)

                # Esperar a que la tabla virtual aparezca
                time.sleep(2)  # Espera un momento para asegurar que el elemento está cargado
                virtual_table = driver.find_element(By.ID, aria_controls_value)  # Buscar el menú desplegable que maneja el id anterior
                time.sleep(1)

                # Encontrar y hacer clic en el botón de descarga
                download_button = virtual_table.find_element(By.XPATH, ".//li")
                download_button.click()

                # Esperar un momento para que inicie la descarga
                time.sleep(2)
                
                # Desplazar la fila un poco menos
                driver.execute_script("window.scrollTo(0, arguments[0].getBoundingClientRect().top + window.pageYOffset - 150);", row)
                time.sleep(0.5)  # Espera un pequeño tiempo para asegurarse de que la vista se haya desplazado completamente
                
                if unavez:
                    noRecordarDescargasIndependientes = driver.find_element(By.XPATH, '//*[@aria-label="Do not remind me again"]/parent::label')
                    time.sleep(1)
                    noRecordarDescargasIndependientes.click()
                    time.sleep(2)
                    
                    # Paso 3: Haz clic en el botón de descarga en el popup
                    download_button = driver.find_element(By.XPATH, ".//button[contains(@class, 'mr-8 zm-button--primary zm-button--small zm-button')]")
                    time.sleep(1)
                    download_button.click()
                    unavez = False
                    time.sleep(2)  # Espero a que se guarde la ejecución

            except Exception as e:
                print(f"Ocurrió un error al procesar la fila: {e}")
        wait_for_finish()

        # Buscar el botón "siguiente" al final del ciclo
        try:
            next_button = driver.find_element(By.XPATH, "//button[contains(@class, 'zm-button--icon zm-button--plain zm-button--icon zm-button--small zm-button btn-next')]")
            next_button.click()  # Hacer clic en el botón "siguiente"
            time.sleep(5)  # Esperar un momento para que la nueva página cargue
            driver.execute_script("window.scrollTo(0, 0);")  # Desplaza al máximo arriba

        except Exception:
            print("No hay más páginas para procesar.")
            break  # Salir del bucle si no se encuentra el botón

# Llamar a la función de descarga
download_recordings(driver)
# Cierra el navegador
driver.quit()
