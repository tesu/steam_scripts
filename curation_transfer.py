import pickle
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

GROUP_ONE = 'isis-official'
GROUP_TWO = 'isis-official2'
TRANSFERS = 1

driver = webdriver.Chrome()
driver.get('https://steamcommunity.com/');
try:
    cookies = pickle.load(open('cookies.pkl', 'rb'))
    for cookie in cookies:
        if cookie['name'] == 'steamLogin' or cookie['name'] == 'steamLoginSecure' or cookie['name'] == 'steamRememberLogin':
            driver.add_cookie(cookie)
except FileNotFoundError:
    pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

driver.get('https://steamcommunity.com/login/home/')

WebDriverWait(driver, 600).until(ec.presence_of_element_located((By.CSS_SELECTOR, '.username')))

curations = []
for i in range(0, TRANSFERS):
    driver.get('https://steamcommunity.com/groups/'+GROUP_ONE+'#curation')

    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, '.RecommendedApps_paging_pagelink')))
    check = driver.find_elements_by_css_selector('.curation_app_block_name') [-1].text
    driver.find_elements_by_css_selector('.RecommendedApps_paging_pagelink') [-1].click()
    def page_changed(self):
        if check == driver.find_elements_by_css_selector('.curation_app_block_name') [-1].text:
            return False
        return True
    WebDriverWait(driver, 10).until(page_changed)
    driver.find_elements_by_css_selector('.curation_app_block_name') [-1].click()
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Delete this recommendation')))
    delete = driver.find_element_by_partial_link_text('Delete this recommendation')
    blurb = driver.find_element_by_css_selector('.curation_app_details_blurb').text.strip()
    appid, app = re.match(r"^Curator_DeleteRecommendation\('"+GROUP_ONE+r"',(\d+),"+r'"(.*)"\);',delete.get_attribute('onclick')).group(1, 2)
    curations.append({'app': app, 'appid': appid, 'blurb': blurb})

    delete.click()
    def button_exists(self):
        if len(driver.find_elements_by_css_selector('.btn_green_white_innerfade.btn_medium span')) > 1:
            return True
        return False
    WebDriverWait(driver, 10).until(button_exists)
    driver.find_elements_by_css_selector('.btn_green_white_innerfade.btn_medium span') [1].click()

for curation in curations:
    driver.get('https://steamcommunity.com/groups/'+GROUP_TWO+'#curation/new')

    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.ID, 'curationAppInput')))
    driver.find_element_by_id('curationAppInput').send_keys(curation['app'])
    driver.execute_script('document.getElementById("curationAppIDInput").style.display = "block"')
    driver.find_element_by_id('curationAppIDInput').send_keys(curation['appid'])
    driver.find_element_by_id('curationBlurbInput').send_keys(curation['blurb'])
    driver.find_element_by_partial_link_text('Post Recommendation').click()

    print('Successfully transferred {0}\'s curation: {1}'.format(curation['app'], curation['blurb']))

pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))
driver.quit()
