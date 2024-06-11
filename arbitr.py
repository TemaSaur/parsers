from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import pandas as pd
from time import sleep
from datetime import datetime
import sys

url = 'https://kad.arbitr.ru'

input_filename = sys.argv[1]


def get_searches(filename):
	df = pd.read_excel(filename)
	searches = []
	for i in df.index:
		row = df.iloc[i]
		if pd.isna(row['ИНН']):
			continue
		searches.append(int(row['ИНН']))
	return searches


find, finds = lambda x: None, lambda x: None

data = []


def click_bankruptcy():
	btn = find('#filter-cases li.bankruptcy')
	if 'active' not in btn.get_attribute('class'):
		btn.click()


def get_search(search):
	el = find('textarea[placeholder="название, ИНН или ОГРН"]')
	el.clear()
	el.send_keys(search)
	find('#b-form-submit button').click()
	pass


def wait_for(selector):
	return WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


def wait_clickable(*selectors):
	return WebDriverWait(driver, 10).until(EC.any_of(
		*(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)) for selector in selectors)
	))

def get_find(driver):
	def find(selector, ctx=None):
		if ctx is None:
			ctx = driver
		return ctx.find_element(By.CSS_SELECTOR, selector)

	return find


def get_finds(driver):
	def finds(selector, ctx=None):
		if ctx is None:
			ctx = driver
		return ctx.find_elements(By.CSS_SELECTOR, selector)

	return finds


def add_info(inn, res):
	data.append({'ИНН': inn, 'Нашелся': res})


def search_searches(searches):
	for search in searches:
		get_search(search)
		sleep(.5)
		click_bankruptcy()
		sleep(1)
		el = wait_clickable('.b-results', '.b-noResults')
		add_info(search, el.text.startswith('Дело'))


if __name__ == "__main__":
	driver = Chrome()
	stealth(
		driver,
		languages=["en-US", "en"],
		vendor="Google Inc.",
		platform="Win32",
		webgl_vendor="Intel Inc.",
		renderer="Intel Iris OpenGL Engine",
		fix_hairline=True
	)
	driver.get(url)
	find = get_find(driver)
	finds = get_finds(driver)
	searches = get_searches(input_filename)
	search_searches(searches)
	print([x['Нашелся'] for x in data])
	pd.DataFrame(data).to_excel(f'../arbitr/{datetime.today().strftime("%y%m%d%H%M%S")}.xlsx')
