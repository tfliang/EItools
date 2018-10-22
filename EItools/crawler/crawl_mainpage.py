import datetime

import bs4
import re
import requests
import pextract as pe
from EItools.log.log import logger
from EItools.magic_search.magic_search import MagicSearch
from EItools.extract.interface import interface

magic_search=MagicSearch()
def get_main_page(url,person=None):
	try:
		source_code = magic_search.get_webpage_content(url)
		source_code=re.sub(r'(<BR>|<br>|</br>|<br />|<br/>)','\n\r',source_code)
		source_code = re.sub(r'(<li>|</li>)', '\n\r', source_code)
		source_code = re.sub(r'(<p>|</p>)', '\n\r', source_code)
		source_code=re.sub(r'(<ul>)','<ol>',source_code)
		source_code=re.sub(r'<ur/>','<ol/>',source_code)
		soup = bs4.BeautifulSoup(source_code, 'html.parser')
		scripts = soup.find_all(name='div', attrs={
			"class": re.compile(r'.*(foot|nav|Nav|footer|bottom|menu|before-content|polysemyAll).*$')})
		scriptsId = soup.find_all(name='div', attrs={
			"id": re.compile(r'.*(foot|nav|Nav|footer|bottom|menu).*$')})
		for script in scripts + scriptsId:
			script.extract()
		for script in soup(["script", "style","select"]):
			script.extract()

		text = soup.get_text()

		#lines = (line.strip() for line in text.splitlines())
		# text = '\n\r'.join(chunk for chunk in lines if chunk)
		lines = (line.strip() for line in text.split('\n'))
		# for line in lines:
		# 	if line !='':
		# 		print(line)
		if person is not None and 'org' in person and person['org'].find("公司") != -1:
			text = '\n'.join(chunk for chunk in lines if chunk.find(person['org'].split()[0]) != -1)
		else:
			text = '\n'.join(chunk for chunk in lines if chunk!='')
	except Exception as e:
		logger.info(e)
		text = ""
	text=re.sub('&nbsp',' ',text)
	return text


def get_mainpage_by_algo(url):
	r =magic_search.get_webpage_content(url)
	soup = bs4.BeautifulSoup(r, 'lxml')
	html, pval = pe.extract(soup, text_only=False, remove_img=False)
	text, pval = pe.extract(soup)
	return text

year_now=datetime.datetime.now().year
pattern_year='[1-2]{1}[0-9]{3}'
def get_lasttime_from_mainpage(url):
	text=get_main_page(url)
	all_years=re.compile(pattern_year).findall(text)
	all_years=sorted(set(all_years),reverse=True)
	for year in all_years:
		if int(year)<=year_now:
			return int(year)
	return 0




#print(get_main_page("http://www.genetics.cas.cn/huangxun/"))
#print(get_main_page("http://people.ucas.edu.cn/~pchen1901"))

