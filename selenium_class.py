import time
import os
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC

# build a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('log.txt')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


class Util_Selenium:

  def __init__(self, webdriver_path, download_path):
    # Set the path to your web driver executable
    self.webdriver_path = webdriver_path
    self.download_path = download_path
    path = Service(self.webdriver_path)
    # configure your download path
    prefs = {
      'profile.default_content_settings.popups': 0,
      'download.default_directory': self.download_path
    }
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_experimental_option('prefs', prefs)
    self.driver = webdriver.Chrome(service=path, options=options) 

    # set the time for maximum waiting time
    self.wait = WebDriverWait(self.driver, 30)

  def automated_pipe(self, mol_file_txt, download_sleep_time):
    # Navigate to the page with the form
    self.driver.get('http://www.nmrdb.org/service/')

    # Find the Molfile textarea element and change its content
    molfile_textarea = self.driver.find_element(By.ID, 'molfile')

    # molfile
    new_molfile_content = mol_file_txt

    # clear the default content and push your content
    molfile_textarea.clear()
    molfile_textarea.send_keys(new_molfile_content)

    # Find and click the Submit button
    submit_button = self.driver.find_element(By.XPATH, '//input[@type="submit"]')
    submit_button.click()

    # clcick the agree buttom
    el = WebDriverWait(self.driver, timeout=30).until(lambda d: d.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/button[1]'))
    el.click()
    time.sleep(0.1)

    print("wait ...")

    # wait for the page loading
    wait_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="module-12"]/div[2]/div/div/sup')))

    # click the download button
    self.driver.find_element(By.XPATH, '//*[@id="module-2"]/div[1]/div[2]/ul/li[2]').click()
    time.sleep(download_sleep_time)

    # get the 1H NMR data
    # element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="module-12"]/div[2]/div/div')))
    # html = element.get_attribute("innerHTML")

    # close the engine
    self.driver.quit()

    # parse the data
    # soup = BeautifulSoup(html, features='lxml')
    # print(soup.text)

# rename the file
def rename_file(work_directory, new_name):
    os.chdir(work_directory)
    time_ordered_dir = sorted(os.listdir(), key=os.path.getmtime, reverse=True)
    most_recent_file = time_ordered_dir[0]
    os.rename(most_recent_file, os.path.join(os.getcwd(), new_name))

def multiple_run(mol_dir, webdriver_path, download_path):
  os.chdir(mol_dir)
  mol_file_list = os.listdir()
  for mol_file in mol_file_list:
    suffix = re.search(r'\.mol', mol_file)
    if suffix is not None:
      try:
        with open(f"{mol_dir}/{mol_file}") as f:
          content = f.read()
          for match in re.finditer(r'(.+?)\.', mol_file):
            new_name = match.group(1)
          util = Util_Selenium(webdriver_path, download_path)
          util.automated_pipe(content, 5)
          rename_file(download_path, new_name=new_name+'.jdx')
      except:
        logging.info(f"{new_name}.mol downloads failed, please retry")
        continue

# replace with mol file in text form
mol_file_location = "/Users/pastalover/Downloads/GFN2D_re"
webdriver_path = '/Users/pastalover/chromedriver_mac_arm64/chromedriver'
download_path = "/Users/pastalover/Downloads/D_re"
multiple_run(mol_dir=mol_file_location, webdriver_path=webdriver_path, download_path=download_path)

