from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import re
import pprint
import json

portal='NameCheckUp'
url = 'https://www.namecheckup.com/'

request_body = {
	"data[name]": username,
	"data[tx]": "1"
}

#--- Get index.js scritp
website = requests.get(url)
scripts = BeautifulSoup(website.text, 'html.parser')
scripts = scripts.find_all('script')
scripts2 = [src for src in scripts]
scripts2 = [i for i in scripts2]
all_scripts = [i.attrs['src'] if len(i) == 0 else i.text for i in scripts2]
index_src = [i if 'index.js' in i else None for i in all_scripts]
index_src = list(filter(None, index_src))[0]
index_src

index_page = requests.get(urljoin(url, index_src))
index_page = BeautifulSoup(index_page.text).text
index_page = index_page.split('var')

def get_index_block(i = 1):
	index_string = index_page[i]
	if i == 1:
		index_string =index_string.replace('mediasMapMain = {\r\n','')
	else:
		index_string = index_string.replace(' mediasMapExtended = {\r\n','')

	index_string = index_string.split('\r\n')
	index_string = [i.strip() for i in index_string]
	index_string = [i if '// ' not in i else None for i in index_string]
	index_string = list(filter(None, index_string))
	index_string = ' '.join(index_string)
	index_string = [i for i in index_string.split('},')]
	[re.findall('/\*',i) for i in index_string]
	[re.match('/\*',i) for i in index_string]
	re.search('/\*',index_string[1])
	r = re.compile('(?!/[*]+|[*]+/)')
	index_string = list(filter(r.match, index_string))
	index_string = [re.sub('/\*+','',o).strip() for o in index_string]
	return index_string

def text_to_dict(single_str):
	if ' // ' not in single_str:
		single_str = " ".join(single_str.split()).strip(',')
		single_str = single_str.split(': {')
		body = [line.strip('\" ').replace("'","") for line in single_str[1].split(',')]
		body = dict([line.strip('\" ').replace("'","").split(': ') for line in body])
		return {single_str[0] : body}

dataset = {}
dataset[portal] = {'mediasMapMain': [text_to_dict(i) for i in get_index_block(i = 1)],
					'mediasMapExtended': [text_to_dict(i) for i in get_index_block(i = 2)]}

pprint.pprint(dataset[portal]['mediasMapMain'])
pprint.pprint(dataset[portal]['mediasMapExtended'])

jsonIndex1 = json.dumps(dataset[portal]['mediasMapMain'], indent = 2)
pprint.pprint(jsonIndex1)

jsonIndex2 = json.dumps(dataset[portal]['mediasMapExtended'],indent = 1)
pprint.pprint(jsonIndex2)

dataset_json = json.dumps(dataset, indent = 3)
pprint.pprint(dataset_json)

file_name = f'./data/'+portal+'/mediasMapMain.json'
with open(file_name,'w') as outfile:
	json.dump(dataset, outfile)

file_name = f'./data/'+portal+'/mediasMapExtended.json'
with open(file_name,'w') as outfile:
	json.dump(dataset, outfile)

file_name = f'./data/'+portal+'/'+portal+'_full.json'
with open(file_name,'w') as outfile:
	json.dump(dataset, outfile)
