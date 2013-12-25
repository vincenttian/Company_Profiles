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
from functools import partial
from BeautifulSoup import BeautifulSoup
import re

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
			print "We don't have a service.dat file, so we need to get access tokens!"
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


# BEGIN VINCENT'S COMPANY API
def company_api(company, api, data):

	"""
	To Use this API, set:

		company = string of the name of the company you want information open

		api = string of the API that you want to use to get information: choose from
			1. linkedin
			2. crunchbase
			3. glassdoor

		data = string of the data you are interested in

			For linkedin, there is
				1. company_type
				2. description
				3. employee_range
				4. founded_year
				5. industry
				6. location
				7. status
				8. website_url

			For crunchbase, there is 
				1. acquisitions
				2. blog_url
				3. competition
				4. description
				5. email_address
				6. funding_rounds
				7. homepage_url
				8. investments
				9. milestones
				10. number_employees
				11. offices
				12. overview
				13. phone_number
				14. company_staff
				15. total_money_raised
				16. twitter_username

			For glassdoor, there is 
				1. ceo
				2. meta
				3. salary
				4. satisfaction
	"""

	api = api.lower()
	company = company.lower()

	# GET INFORMATION FROM LINKEDIN
	if api == 'linkedin':
		
		# GETS DATA FROM LINKEDIN API
		# Get authorization set up and create the OAuth client
		client = get_auth() 
		response = make_request(client, LINKEDIN_URL_1 + company + LINKEDIN_URL_2, {"x-li-format":'json'})
		d1 = json.loads(response)
		try:
			d1 = json.loads(response)
		except:
			return "Sorry. The LinkedIn API could not find information for company " + company
		
		"""
		Returns a JSON object of all information about company provided by linkedin
		"""
		if data == 'all':
			return d1

		"""
		Returns a string that contains the company type: private or public.
		"""
		if data == 'company_type':
			return d1["companyType"]["name"]

		"""
		Returns a string that contains a short description of the company.
		"""
		if data == 'description':
			return d1["description"]

		"""
		Returns a string that contains an approximate range for number of employees.
		"""
		if data == 'employee_range':
			return d1["employeeCountRange"]["name"]

		"""
		Returns an integer that contains the year the company was founded.
		"""
		if data == 'founded_year':
			return d1["foundedYear"]

		"""
		Returns a JSON object that contains the industries the company is involved with.

		Ex.
		{u'industries': {u'_total': 1,
         u'values': [{u'code': u'12', u'name': u'Biotechnology'}]}
		"""
		if data == 'industry':
			return d1["industries"]

		"""
		Returns a JSON object that contains the locations of the company.

		Ex. 
		{u'locations': {u'_total': 1,
        u'values': [{u'address': {u'city': u'Mountain View',
                                  u'postalCode': u'94043',
                                  u'street1': u'1390 Shorebird Way'},
                     u'contactInfo': {u'fax': u'',
                                      u'phone1': u'650.938.6300'}}]}
		"""
		if data == 'location':
			return d1["locations"]

		"""
		Returns a string that contains the status of the company: operating or not.
		"""
		if data == 'status':
			return d1["status"]["name"]

		"""
		Returns a string that contains the website url of the company.
		"""
		if data == 'website_url':
			return d1["websiteUrl"]

	# GET INFORMATION FROM CRUNCHBASE
	if api == 'crunchbase':

		# DATA FROM CRUNCHBASE
		r = requests.get(CRUNCHBASE_URL_1 + company + CRUNCHBASE_URL_2)
		data = r.text
		try:
			d2 = json.loads(data)
		except:
			return "Sorry. The Crunchbase API could not find information for company " + company

		"""
		Returns a JSON object of all information about company provided by crunchbase
		"""
		if data == 'all':
			return d2

		"""
		Returns a JSON Object that contains the acquisitions the company has made

		Ex. 
		{u'acquisitions': [{u'acquired_day': 10,
	        u'acquired_month': 7,
	        u'acquired_year': 2012,
	        u'company': {u'name': u'CureTogether',
	                     u'permalink': u'curetogether'},
	        u'price_amount': None,
	        u'price_currency_code': u'USD',
	        u'source_description': u'23andMe Acquires CureTogether, Inc.',
	        u'source_url': u'http://www.freshnews.com/news/673729/23andme-acquires-curetogether-inc-',
	        u'term_code': None}]
		"""
		if data == 'acquisitions':
			return d2["acquisitions"]

		"""
		Returns a string that contains the blog url of the company
		"""
		if data == 'blog_url':
			return d2["blog_url"]

		"""
		Returns a JSON object that contains the competitors of the comapny 

		Ex.  
		{u'competitions': [{u'competitor': {u'name': u'GenePartner',
                                    u'permalink': u'genepartner'}},
		                   {u'competitor': {u'name': u'ScientificMatch',
                                    u'permalink': u'scientificmatch'}},
		                   {u'competitor': {u'name': u'Navigenics',
                                    u'permalink': u'navigenics'}},
		                   {u'competitor': {u'name': u'AIBioTech',
                                    u'permalink': u'aibiotech'}}]
		"""
		if data == 'competition':
			return d2["competitions"]

		"""
		Returns a string that contains a description of the company
		"""
		if data == 'description':
			return d2["description"]

		"""
		Returns a string that contains the company email address
		"""
		if data == 'email_address':
			return d2["email_address"]

		"""
		Returns a JSON Object that contains the funding rounds of a company

		Ex. 
		{u'funding_rounds': [{u'funded_day': 1,
	          u'funded_month': 5,
	          u'funded_year': 2007,
	          u'id': 764,
	          u'investments': [{u'company': {u'name': u'Genentech',
	                                         u'permalink': u'genentech'},
	                            u'financial_org': None,
	                            u'person': None},
	                           {u'company': {u'name': u'Google',
	                                         u'permalink': u'google'},
	                            u'financial_org': None,
	                            u'person': None},
	                           {u'company': None,
	                            u'financial_org': {u'name': u'Mohr Davidow Ventures',
	                                               u'permalink': u'mohr-davidow-ventures'},
	                            u'person': None},
	                           {u'company': None,
	                            u'financial_org': {u'name': u'New Enterprise Associates',
	                                               u'permalink': u'new-enterprise-associates'},
	                            u'person': None}],
	          u'raised_amount': 9000000.0,
	          u'raised_currency_code': u'USD',
	          u'round_code': u'a',
	          u'source_description': u'',
	          u'source_url': u'http://23andme.com/press.html'}
		"""
		if data == 'funding_rounds':
			return d2["funding_rounds"]

		"""
		Returns a string that contains the company homepage url 
		"""
		if data == 'homepage_url':
			return d2["homepage_url"]

		"""
		Returns a JSON Object that contains the company investments
		"""
		if data == 'investments':
			return d2["investments"]

		"""
		Returns a JSON Object that contains company milestones

		Ex.  
		 {u'milestones': [{u'description': u'Price dropped to $399 per test. ',
	          u'id': 579,
	          u'source_description': u'23andMe Democratizes Personal Genomics With New Analytical Platform',
	          u'source_text': u'',
	          u'source_url': u'http://spittoon.23andme.com/2008/09/08/23andme-democratizes-personal-genomics-with-new-analytical-platform/',
	          u'stoneable': {u'name': u'23andMe',
	                         u'permalink': u'23andme'},
	          u'stoneable_type': u'Company',
	          u'stoned_acquirer': None,
	          u'stoned_day': 8,
	          u'stoned_month': 9,
	          u'stoned_value': None,
	          u'stoned_value_type': None,
	          u'stoned_year': 2008}]
		"""
		if data == 'milestones':
			return d2["milestones"]

		"""
		Returns a string that contains the number of employees
		"""
		if data == 'number_employees':
			return d2["number_of_employees"]

		"""
		Returns a JSON Object that contains the company offices 

		Ex.  
		 {u'offices': [{u'address1': u'2606 Bayshore Parkway',
           u'address2': u'',
           u'city': u'Mountain View',
           u'country_code': u'USA',
           u'description': u'',
           u'latitude': 37.09024,
           u'longitude': -95.712891,
           u'state_code': u'CA',
           u'zip_code': u'94042'}]
		"""
		if data == 'offices':
			return d2["offices"]

		"""
		Returns a string that contains the 
		"""
		if data == 'overview':
			return d2["overview"]

		"""
		Returns a string that contains the company overview
		"""
		if data == 'phone_number':
			return d2["phone_number"]

		"""
		Returns a JSON Object that contains the company staff 

		Ex. 
		{u'relationships': [{u'is_past': False,
         u'person': {u'first_name': u'Anne',
                     u'last_name': u'Wojcicki',
                     u'permalink': u'anne-wojcicki'},
         u'title': u'CEO and Co-founder'}
        }
		"""
		if data == 'company_staff':
			return d2["relationships"]

		"""
		Returns a string that contains the total money raised 
		"""
		if data == 'total_money_raised':
			return d2["total_money_raised"]

		"""
		Returns a string that contains the twitter username 
		"""
		if data == 'twitter_username':
			return d2["twitter_username"]

	# GET INFORMATION FROM GLASSDOOR
	if api == 'glassdoor':
	
		# GETS DATA FROM GLASSDOOR SCRAPING
		x = get(company)
		x_json = x.json()
		d3 = json.loads(x_json)

		"""
		Returns a JSON object of all information about company provided by linkedin
		"""
		if data == 'all':
			return d3

		"""
		Returns a JSON object that contains CEO information 

		Ex. 
		{u'ceo': {u'%approval': None,
          u'avatar': u'http://static.glassdoor.com/static/img/illustration/generic-person.png?v=dc63ecds',
          u'name': u'Anne Wojcicki',
          u'reviews': 0}
		"""
		if data == 'ceo':
			return d3["ceo"]

		"""
		Returns a JSON object that contains information including competitors, year founded,
		industry, revenue, type, location, logo, score, size, and website

		Ex. 
		{ u'meta': {u'Competitors': u'Unknown',
           u'Founded': u'Unknown',
           u'Industry': u'Business Services',
           u'Revenue': u'Unknown / Non-Applicable per year',
           u'Type': u'Company - Private',
           u'connections': 0,
           u'location': u'Mountain View, CA',
           u'logo': u'http://static.glassdoor.com/static/img/sqLogo/generic-150.png?v=7fc3122vf',
           u'name': u'23andMe',
           u'reviews': 9,
           u'score': None,
           u'size': [],
           u'website': u'www.23andme.com'}}
		"""
		if data == 'meta':
			return d3["meta"]

		"""
		Returns a JSON object that contains salary information 

		Ex. 
		{ u'position': u'Computational Biologist',
              u'range': [94000, 106000],
              u'samples': 4},
             {u'mean': 117763,
              u'position': u'Software Engineer',
              u'range': [113000, 123000],
              u'samples': 2},
             {u'mean': 96672,
              u'position': u'Scientist',
              u'range': [84000, 109000],
              u'samples': 2}]
        }
		"""
		if data == 'salary':
			return d3["salary"]


		"""
		Returns a JSON object that contains the satisfaction of employees

		Ex. 
		{ u'satisfaction': {u'ratings': 9, u'score': None }}
		"""
		if data == 'satisfaction':
			return d3["satisfaction"]

# TESTING API
if __name__ == "__main__":
	print "Initial Test"

	company = "23andme"


	# CRUNCHBASEEE -----------------------------------	
	# d2 = company_api(company, 'crunchbase', 'all')			
	# pprint.pprint(d2)

	# r = requests.get(CRUNCHBASE_URL_1 + company + CRUNCHBASE_URL_2)
	# data = r.text
	# try:
	# 	d2 = json.loads(data)
	# except:
	# 	print "Sorry"
	# pprint.pprint(d2)



	# GLASSDOORRR -----------------------------------	
	# x = get(company)
	# x_json = x.json()
	# d3 = json.loads(x_json)
	# print d3["salary"]
	# pprint.pprint(d3)



	# LINKEDINNNN -----------------------------------	
	# client = get_auth() 
	# response = make_request(client, LINKEDIN_URL_1 + company + LINKEDIN_URL_2, {"x-li-format":'json'})
	# d1 = json.loads(response)
	# try:
	# 	d1 = json.loads(response)
	# except:
	# 	print "Sorry. The LinkedIn API could not find information for company " + company
	# pprint.pprint(d1)

	# TESTS ##############

	# d2 = company_api(company, 'linkedin', 'all')	
	# print d2
	







