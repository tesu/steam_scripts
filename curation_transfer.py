import time
import pickle
import re
from selenium import webdriver

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

if len(driver.find_elements_by_link_text('login')) > 0:
    while len(driver.find_elements_by_link_text('login')) > 0:
        time.sleep(1)
    pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

curations = []
for i in range(0, TRANSFERS):
    driver.get('https://steamcommunity.com/groups/'+GROUP_ONE+'#curation')

    while len(driver.find_elements_by_css_selector('.RecommendedApps_paging_pagelink')) == 0:
        time.sleep(1)
    driver.find_elements_by_css_selector('.RecommendedApps_paging_pagelink') [-1].click()
    time.sleep(2)
    driver.find_elements_by_css_selector('.curation_app_block_name') [-1].click()
    time.sleep(2)
    delete = driver.find_element_by_partial_link_text('Delete this recommendation')
    blurb = driver.find_element_by_css_selector('.curation_app_details_blurb').text.strip()
    appid, app = re.match(r"^Curator_DeleteRecommendation\('"+GROUP_ONE+r"',(\d+),"+r'"(.*)"\);',delete.get_attribute('onclick')).group(1, 2)
    curations.append({'app': app, 'appid': appid, 'blurb': blurb})

    delete.click()
    while len(driver.find_elements_by_css_selector('.btn_green_white_innerfade.btn_medium span')) < 2:
        time.sleep(1)
    driver.find_elements_by_css_selector('.btn_green_white_innerfade.btn_medium span') [1].click()

for curation in curations:
    driver.get('https://steamcommunity.com/groups/'+GROUP_TWO+'#curation/new')

    while len(driver.find_elements_by_id('curationAppInput')) == 0:
        time.sleep(1)
    driver.find_element_by_id('curationAppInput').send_keys(curation['app'])
    driver.execute_script('document.getElementById("curationAppIDInput").style.display = "block"')
    driver.find_element_by_id('curationAppIDInput').send_keys(curation['appid'])
    driver.find_element_by_id('curationBlurbInput').send_keys(curation['blurb'])
    driver.find_element_by_partial_link_text('Post Recommendation').click()

driver.quit()
