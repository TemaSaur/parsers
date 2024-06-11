from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime

url = 'https://bankrot.fedresurs.ru/bankrupts?searchString={}'

# searches = ['Вахрушев', 'Лох']
import sys
input_filename = sys.argv[1]


def get_searches(filename):
	df = pd.read_excel(filename)
	searches = []
	for i in df.index:
		row = df.iloc[i]
		if not pd.isna(row['ИНН']):
			search = int(row['ИНН'])
		else:
			search = row['ФИО']
		searches.append(search)
	return searches


find, finds = lambda x: None, lambda x: None

data = []


def switch_phys():
	find('.tab__nav > li.tab__li:nth-child(2) > div:nth-child(1)').click()


def get_search(search):
	driver.get(url.format(search))
	wait_for('.u-card-result, .no-result-msg')


def wait_for(selector):
	return WebDriverWait(driver, 20).until(
		EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


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


def get_info(i, status):
	driver.switch_to.window(driver.window_handles[1])
	info = wait_for('.card .container .info')
	name = find('.subject h2').text

	person = {'Поиск №': i, 'ФИО': name, 'Статус': status}

	personal = find('app-person-info', info).text
	person |= {
		k: v for k, v in
		zip([x for i, x in enumerate(personal.split('\n')) if i % 2 == 0],
			[x for i, x in enumerate(personal.split('\n')) if i % 2 == 1])
	}

	try:
		find('legal-case-list:has(.bankrot_case) .toggle .open_expand_form',
			 info).click()

		person |= {
			k: v
			for k, v in zip(['Дело', 'Суд', 'Заявитель'],
							find('.bankrot_case', info).text.split('\n')[1:])
		}
	except:
		pass

	data.append(person)

	driver.close()
	driver.switch_to.window(driver.window_handles[0])


def search_searches(searches):
	i = 1
	for search in searches:
		get_search(search)
		try:
			switch_phys()
			for card in finds('app-bankrupt-result-card-person .u-card-result'):
				card.click()
				status = find(
					'.d-flex .u-card-result__value.u-card-result__value_item-property',
					card).text
				get_info(i, status)
		except:
			data.append({'Поиск №': i, 'Поиск': search, 'Статус': 'Не найдено'})
		i += 1


if __name__ == "__main__":
	try:
		driver = Firefox()
		driver.get(url)
		find = get_find(driver)
		finds = get_finds(driver)
		searches = get_searches(input_filename)
		search_searches(searches)
		pd.DataFrame(data).to_excel(f'../fedresurs/{datetime.today().strftime("%y%m%d%H%M%S")}.xlsx')
	except:
		import traceback
		print(traceback.format_exc())
		print('Что-то пошло не так. Сохраняю что получилось')
		pd.DataFrame(data).to_excel(f'../fedresurs/failed_{datetime.today().strftime("%y%m%d%H%M%S")}.xlsx')
