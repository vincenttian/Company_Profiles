import oauth2 as oauth
import httplib2
import time, os, simplejson
import urlparse
import BaseHTTPServer 
import json
import pprint
import requests
from xml.etree import ElementTree as ET
from django.core.management.base import BaseCommand, CommandError
from companyapp.companyapp.models import *
from functools import partial
from BeautifulSoup import BeautifulSoup
import re
from companyapp.companyapp.management.commands.company_api import *

consumer_key    =   '452p27539u5f'
consumer_secret =   '3q1iiaeQph2wRH4M'
request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
access_token_url =  'https://api.linkedin.com/uas/oauth/accessToken'
authorize_url =     'https://api.linkedin.com/uas/oauth/authorize'
config_file   = '.service.dat'
xml_file      = '.xml.dat'
http_status_print = BaseHTTPServer.BaseHTTPRequestHandler.responses

LINKEDIN_URL_1 = "http://api.linkedin.com/v1/companies/universal-name="
LINKEDIN_URL_2 = ":(id,name,universal-name,company-type,ticker,website-url,industries,status,employee-count-range,locations,description,stock-exchange,founded-year,end-year)"
CRUNCHBASE_URL_1 = "http://api.crunchbase.com/v/1/company/"
CRUNCHBASE_URL_2 = ".js?api_key=emy48jd7q3k7kv6tx8ft6adb"
GLASSDOOR_API = 'http://www.glassdoor.com/GD/Reviews/company-reviews.htm'

GLASSDOOR_URL = ""

def get_auth():
	consumer = oauth.Consumer(consumer_key, consumer_secret)
	client = oauth.Client(consumer)
	try:
			filehandle = open(config_file)
	except IOError as e:
			filehandle = open(config_file,"w")
			print("We don't have a service.dat file, so we need to get access tokens!");
			content = make_request(client,request_token_url,{},"Failed to fetch request token","POST")
			request_token = dict(urlparse.parse_qsl(content))
			print "Go to the following link in your browser:"
			print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
			oauth_verifier = raw_input('What is the PIN? ')
			token = oauth.Token(request_token['oauth_token'],
			request_token['oauth_token_secret'])
			token.set_verifier(oauth_verifier)
			client = oauth.Client(consumer, token)
			content = make_request(client,access_token_url,{},"Failed to fetch access token","POST")
			access_token = dict(urlparse.parse_qsl(content))
			token = oauth.Token(key=access_token['oauth_token'],secret=access_token['oauth_token_secret'])
			client = oauth.Client(consumer, token)
			simplejson.dump(access_token,filehandle)
	else:
			print filehandle
			config = simplejson.load(filehandle)
			if ("oauth_token" in config and "oauth_token_secret" in config):
					token = oauth.Token(config['oauth_token'],config['oauth_token_secret'])
					client = oauth.Client(consumer, token)
			else:
					print("We had a .service.dat file, but it didn't contain a token/secret?")
					exit()
	return client

# Simple oauth request wrapper to handle responses and exceptions
def make_request(client,url,request_headers={},error_string="Failed Request",method="GET",body=None):
	if body:
			resp,content = client.request(url, method, headers=request_headers, body=body)
	else:
			resp,content = client.request(url, method, headers=request_headers)
	if resp.status >= 200 and resp.status < 300:
			return content
	elif resp.status >= 500 and resp.status < 600:
			error_string = "Status:\n\tRuh Roh! An application error occured! HTTP 5XX response received."
			# log_diagnostic_info(client,url,request_headers,method,body,resp,content,error_string)
	else:
			status_codes = {403: "\n** Status:\n\tA 403 response was received. Usually this means you have reached a throttle limit.",
							401: "\n** Status:\n\tA 401 response was received. Usually this means the OAuth signature was bad.",
							405: "\n** Status:\n\tA 405 response was received. Usually this means you used the wrong HTTP method (GET when you should POST, etc).",
							400: "\n** Status:\n\tA 400 response was received. Usually this means your request was formatted incorrectly or you added an unexpected parameter.",
							404: "\n** Status:\n\tA 404 response was received. The resource was not found."}
			# if resp.status in status_codes:
			# 		log_diagnostic_info(client,url,request_headers,method,body,resp,content,status_codes[resp.status])
			# else:
			# 		log_diagnostic_info(client,url,request_headers,method,body,resp,content,http_status_print[resp.status][1])

def intify(s):
	"""Coerce string to int"""
	return int(re.sub("[^0-9]", "", s))

def tryelse(func, default='', exception=Exception):
	"""
	"""
	try:
		return func()
	except exception as e:
		return default

def get(company):
	"""Performs a HTTP GET for a glassdoor page and returns
	BeautifulSoup with a .json() method
	"""
	params = 'clickSource=searchBtn&typedKeyword=&sc.keyword=%s' % company
	r = requests.get('%s?%s' % (GLASSDOOR_API, params))
	global GLASSDOOR_URL
	GLASSDOOR_URL = '%s?%s' % (GLASSDOOR_API, params)
	soup = BeautifulSoup(r.content)
	soup.json = partial(parse, soup, raw=True)
	soup.data = lambda: json.loads(soup.json())
	return soup

def parse_meta(soup):
	data = {'website': '',
			'name': '',
			'location': '',
			'logo': '',
			'connections': None,
			'reviews': None,
			'score': None,
			}

	def _reviews(soup):
		selector_outer = {'class': 'numReviews subtle'}
		selector = {'class': 'txtShadowWhite'}
		reviews_outer = soup.findAll('span', selector_outer)[0]
		reviews = reviews_outer.findAll('span', selector)[0]
		return intify(reviews.text)

	def _score(soup):
		selector = {'class': 'h2 tightVert tightHorz notranslate'}
		score = soup.findAll('span', selector)[0].findAll('strong')[0]
		return float(score.text)

	def _details(soup):
		details = {}
		soup = soup.findAll('div', {'id': 'InfoDetails'})
		if soup:
			metas = soup[0].findAll('div', {'class': 'empInfo cf'})
			for meta in metas:
				label = str(meta.findAll('label')[0].text)
				value = str(meta.findAll('span')[0].text)
				details[label] = value
		return details

	def _connections(soup):
		selector_div = {'id': 'OverviewInsideConnections'}
		selector_tt = {'class': 'notranslate'}
		connections_div = soup.findAll('div', selector_div)
		connections_tt = connections_div[0].findAll('tt', selector_tt)
		connections = connections_tt[0].text
		return intify(connections)

	def _logo(soup):
		selector = {'class': 'sqLogo tighten medSqLogo'}
		logo = soup.findAll('span', selector)[0].findAll('img')[0]['src']
		return logo

	def _website(soup):
		selector = {'class': 'website notranslate txtShadowWhite'}
		website = soup.findAll('span', selector)[0].text
		return website

	def _name(soup):
		selector = {'class': 'i-emp'}
		name = soup.findAll('tt', selector)[0].text
		return name

	def _location(soup):
		location = soup.findAll('span', {'class': 'value i-loc'})[0].text
		return location

	def _size(soup):
		selector_div = {'class': 'moreData margTop5 subtle'}
		selector = {'class': 'notranslate'}
		size_div = soup.findAll('div', selector_div)[0]
		sizes = size_div.findAll('tt', selector)
		return [intify(size.text) for size in sizes]

	data['connections'] = tryelse(partial(_connections, soup),
								  default=0)
	data['website'] = tryelse(partial(_website, soup),
							  default='')
	data['name'] = tryelse(partial(_name, soup),
						   default='')
	data['location'] = tryelse(partial(_location, soup),
							   default='')
	data['size'] = tryelse(partial(_size, soup),
						   default=[None, None])
	data['reviews'] = tryelse(partial(_reviews, soup),
							  default=None)
	data['logo'] = tryelse(partial(_logo, soup),
							  default=None)
	data['score'] = tryelse(partial(_score, soup),
							default=None)
	data.update(_details(soup))
	return data

def parse_satisfaction(soup):
	"""
	"""
	data = {'ratings': 0,
			'score': None,
			}

	def _ratings(soup):
		"""Number of times this company has been rated by employees"""
		ratings = soup.findAll('h3')[0]
		selector = {'class': 'notranslate'}
		ratings = ratings.findAll('span', selector)[0]
		return intify(ratings.text.strip())

	def _score(soup):                            
		selector = {'class': 'gdRatingValueBar gdrHighmed'}
		score = soup.findAll('span', selector)[0]
		return float(score.text)

	_soups = soup.findAll('div', {'id': 'EmployerRatings'})

	if _soups:
		_soup = _soups[0]
		data['ratings'] = tryelse(partial(_ratings, _soup),
								  default=data['ratings'])
		data['score'] = tryelse(partial(_score, _soup),
								default=data['score'])
	return data

def parse_ceo(soup):
	data = {'reviews': 0,
			'%approval': None,
			'avatar': '',
			'name': ''
			}

	def _name(soup):
		selector = {'class': 'ceoName notranslate'}
		return soup.findAll('h4', selector)[0].text

	def _reviews(soup):
		selector_span = {'class': 'numCEORatings minor'}
		selector_tt = {'class': 'notranslate'}        
		reviews_span = soup.findAll('span', selector_span)[0]
		reviews_tt = reviews_span.findAll('tt', selector_tt)[0]
		reviews = reviews_tt.text
		return intify(reviews)

	def _avatar(soup):
		selector_div = {'id': 'CEOHeadShot'}
		avatar_div = soup.findAll('div', selector_div)[0]
		avatar = avatar_div.findAll('img')[0]
		return avatar['src']

	def _approval(soup):
		selector_span = {'class': 'approvalPercent'}
		selector_tt = {'class': 'notranslate'}
		approval_span = soup.findAll('span', selector_span)[0]
		approval_tt = approval_span.findAll('tt', selector_tt)[0]
		approval = approval_tt.text
		return intify(approval)

	_soups = soup.findAll('div', {'class': 'ceoRating cf'})
	if _soups:
		_soup = _soups[0]
		data['name'] = tryelse(partial(_name, _soup),
							   default='')
		data['reviews'] = tryelse(partial(_reviews, _soup),
								  default=0)
		data['avatar'] = tryelse(partial(_avatar, _soup),
								 default='')
		data['%approval'] = tryelse(partial(_approval, _soup),
									default=None)
	return data

def parse_salary(soup):
	data = []

	def _samples(soup):
		selector = {'class': 'rowCounts'}
		rows = soup.findAll('p', selector)[0]
		samples = rows.findAll('tt')[0].text
		return intify(samples)

	def _position(soup):
		selector = {'class': 'i-occ'}
		position_tt = soup.findAll('tt', selector)[0]
		position = position_tt.text
		return position

	def _mean(soup):
		"""Calculates the mean of this row and return an indicator for
		the period, i.e. whether its for a monthly period, as opposed
		to yearly.
		"""
		selector_td = {'class': 'mean'}
		selector_span = {'class': 'minor'}
		mean_td = soup.findAll('td', selector_td)[0]
		mean_span = mean_td.findAll('span', selector_span)[0]
		mean = mean_span.text
		monthly = True if "mo" in mean else False
		mean = intify(mean) * 12 if monthly else intify(mean)
		return mean, monthly

	def _range(soup):
		selector_low = {'class': 'lowValue'}
		selector_high = {'class': 'highValue'}
		low = row.findAll('div', selector_low)[0].text
		high = row.findAll('div', selector_high)[0].text
		return low, high

	def _normalize(range_, monthly):
		"""nomalize: multiply ranges by # months or by $1k"""
		period = 12 if monthly else 1000
		low, high = (intify(v) * period for v in range_)
		return low, high

	_soups = soup.findAll('table', {'id': 'SalaryChart'})
	if _soups:
		_soup = _soups[0]
		for row in _soup.findAll('tr')[1:]:
			try:
				mean, monthly = _mean(row)
				low, high = _normalize(_range(row), monthly)
				data.append({'position': _position(row),
							 'samples': _samples(row),
							 'mean': mean,
							 'range': (low, high)
							 })
			except Exception as e:
				print e
	return data

def parse_suggestions(soup):
	def _suggestions(soup):
		"""Suggests similar/related companies to query"""
		selector_id = {'id': 'SearchResults'}
		selector_h3 = {'class': 'tightTop'}
		companies_div = soup.findAll('div', selector_id)[0]
		companies = companies_div.findAll('h3', selector_h3)
		suggestions = [company.text for company in companies]
		return suggestions

	return {'error': 'company not found',
			'suggestions': _suggestions(soup)
			}

def parse(soup, raw=False):
	"""
	If none found, show top recommendations as json list
	"""
	if soup.findAll('div', {'class': 'sortBar'}):
		data = parse_suggestions(soup)
	else:
		data = {'satisfaction': parse_satisfaction(soup),
				'ceo': parse_ceo(soup),
				'meta': parse_meta(soup),
				'salary': parse_salary(soup)
				}
	if raw:
		return json.dumps(data)
	return data

# COMPANY LISTS HERE
# companies = ['delta-air-lines']
# COMPANIES FOR TESTING
# companies = ['microsoft', 'google', 'amazon', 'ebay', 'linkedin', 'yahoo', 'asana', 'flipboard']

# BIG LIST OF COMPANIES THAT WORK:
companies = \
['23andme', 'Amazon', 'Apple', 'Apportable', 'Asana', 'Autodesk',\
 'box', 'Broadcom', 'Comcast', 'Dell', 'delta-air-lines', 'Dropbox', 'Ebay', 'EMC', \
 'Ericsson', 'Eventbrite', 'Evernote', 'Facebook', 'flipboard', 'Foursquare', 'Google', \
 'Groupon', 'guidewire-software', 'Hewlett-Packard', 'Hoopla-Software', 'IBM', 'Intel', 'Intuit', 'Jawbone', \
 'Juniper Networks', 'Klout', \
 'Linkedin', 'Magoosh', 'marin software', 'Meebo', 'Microsoft', 'Netapp', 'Nvidia', 'Oracle', 'Palantir-Technologies', \
 'Pinterest', 'Pocket', 'Qualcomm', 'Quora', 'rackspace', 'red hat', 'riot games', 'riverbed technology', \
 'Salesforce', 'Samsung-Electronics', 'Shoretel', 'Shutterfly', 'Skype', \
 'Snapchat', 'Spotify', 'Square', 'sun microsystems', 'Symantec', 'Tesla-Motors', 'Texas Instruments', \
 'Twitter', 'tubemogul', 'Verizon', 'VMWare', 'Western Digital', \
 'Workday', 'Yahoo', 'yelp'
]


class Command(BaseCommand):
	help = 'Puts all the company information in the database'

	def set_database(self):

		for company in companies:
			
			company = company.lower()
			name = company

			print "Loading " + company + " into the database"

			# GETS DATA FROM LINKEDIN API
			# Get authorization set up and create the OAuth client
			client = get_auth() 
			response = make_request(client, LINKEDIN_URL_1 + company + LINKEDIN_URL_2, {"x-li-format":'json'})
			d1 = json.loads(response)
			try:
				d1 = json.loads(response)
			except:
				d1 = None
			pprint.pprint(d1)

			# GETS DATA FROM CRUNCHBASE API
			r = requests.get(CRUNCHBASE_URL_1 + company + CRUNCHBASE_URL_2)
			data = r.text
			try:
				d2 = json.loads(data)
			except:
				d2 = None
			# d2 = company_api(company, 'crunchbase', 'all')			
			# pprint.pprint(d2)

			# GETS DATA FROM GLASSDOOR SCRAPING
			x = get(company)
			x_json = x.json()
			d3 = json.loads(x_json)
			# d3 = company_api(company, 'glassdoor', 'all')


			try:
				sal = d3["salary"]
			except:
				company = company + ".com"
				x = get(company)
				x_json = x.json()
				d3 = json.loads(x_json)
				try:
					sal = d3["salary"]
				except:
					sal = None

			company = Company()
			company.name = name

			try:
				company.ticker = d2["ipo"]["stock_symbol"]
			except:
				company.ticker = "Not publicly traded"

			if d2["homepage_url"] == None:
				company.website = "Could not find homepage"
			else:
				company.website = d2["homepage_url"]
			
			if d2 == None:
				pass
			else:
				try:
					company.CEO = d2["relationships"][0]["person"]["first_name"] + " " + d2["relationships"][0]["person"]["last_name"]
				except:
					company.CEO = "Who is the CEO?" 

			if d2["number_of_employees"] == None:
				company.size = "Could not find company size"
			else:
				company.size = d2["number_of_employees"]

			try:
				if d2["ipo"]["pub_year"] != None:
					company.company_type = "Public company"
				else:
					company.company_type = "Private company"
			except:
				company.company_type = "Private company"

			try:
				company.founded = str(d2["founded_year"])
			except:
				company.founded = "Could not find founded year"
			
			if d2 == None:
				pass
			else:
				try:
					company.IPO_year = str(d2["ipo"]["pub_year"])
				except:
					company.IPO_year = "Has not IPO'ed yet"
			
			office_locations = {}
			counter = 0
			for office in d2["offices"]:
				if office["state_code"] != None:
					office_locations[counter] = (office["city"], office["state_code"])
				else:
					office_locations[counter] = (office["city"], office["country_code"])
				counter += 1
			company.location = office_locations

			if d2["category_code"] == None:
				company.industry = "Could not find industry"
			else:
				company.industry = d2["category_code"]

			# try:
			if d2["description"] == None:
				company.description = "No available description"
			else:
				company.description = d2["description"]
			# except:
			# 	company.description = "No description"
			
			# COMPETITORS
			competitor_list = {}
			count = 0
			try:
				for competitor in d2["competitions"]:
					competitor_list[count] = str(competitor["competitor"]["name"])
					count += 1
				company.competitors = str(competitor_list)
			except:
				company.competitors = "No competitors"


			# ACQUISITIONS
			acquisition_list = {}
			count = 0
			try:
				for acquisition in d2["acquisitions"]:
					acquisition_list[count] = acquisition["company"]["name"]
					count += 1
				company.acquisitions = str(acquisition_list)
			except:
				company.acquisitions = "No acquisitions"

			# INVESTMENTS
			investment_list = {}
			count = 0
			try:
				for investment in d2["investments"]:
					investment_list[count] = [investment["funding_round"]["company"]["name"], investment["funding_round"]["raised_amount"], investment["funding_round"]["funded_year"]]
					count += 1
				company.investments = str(investment_list)
			except:
				company.investments = "No investments"

			# PRODUCTS
			product_list = {}
			count = 0
			try:
				for product in d2["products"]:
					prod = Product()
					prod.name = str(product["name"])
					prod.save()
					product_list[count] = prod
					count += 1
				company.products = str(product_list)
			except:
				company.products = "No products"

			if d2["overview"] != None:
				company.overview = d2["overview"]
			else:
				company.overview = "No overview"

			# SALARIES
			salary_list = {}
			count = 0
			if sal == None:
				salary = Salary()
				salary.company_name = company
				salary.position = "Could not find"  
				# salary.ranges = "Could not find" 
				# salary.mean = "Could not find" 
				# salary.samples = "Could not find" 
				salary.url = GLASSDOOR_URL
				company.salaries = str(salary)
				company.save()
			else:
				for sa in sal:
					salary = Salary()
					salary.company_name = company
					salary.position = str(sa["position"]) 
					salary.ranges = str(sa["range"])
					salary.mean = str(sa["mean"])
					salary.samples = str(sa["samples"])
					salary.url = GLASSDOOR_URL
					salary.save()
					salary_list[count] = salary
					count += 1
				company.salaries = str(salary_list)
				company.save()
			print "Successfully loaded " + name + " into the database" 

	def handle(self, *args, **options):
		self.set_database()




