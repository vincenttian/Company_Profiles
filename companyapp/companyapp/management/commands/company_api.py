
from api_helper import *

# BEGIN VINCENT'S COMPANY API
def company_api_function(company, api, data):

	"""
	To Use this API, set:

		company = string of the name of the company you want information on
		Ex. 23andMe

		api = string of the API that you want to use to get information.
		Choose from:
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
		except Exception:
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
			try: 
				return d1["companyType"]["name"]
			except Exception:
				return "Sorry. The LinkedIn API could not find " + data + "for company " + company

		"""
		Returns a string that contains a short description of the company.
		"""
		if data == 'description':
			try:
				return d1["description"]
			except Exception:
				return "Sorry. The LinkedIn API could not find " + data + "for company " + company

		"""
		Returns a string that contains an approximate range for number of employees.
		"""
		if data == 'employee_range':
			try:
				return d1["employeeCountRange"]["name"]
			except Exception:
				return "Sorry. The LinkedIn API could not find " + data + "for company " + company

		"""
		Returns an integer that contains the year the company was founded.
		"""
		if data == 'founded_year':
			try:
				return d1["foundedYear"]
			except Exception:
				return "Sorry. The LinkedIn API could not find " + data + "for company " + company

		"""
		Returns a JSON object that contains the industries the company is involved with.

		Ex.
		{u'industries': {u'_total': 1,
         u'values': [{u'code': u'12', u'name': u'Biotechnology'}]}
		"""
		if data == 'industry':
			try:
				return d1["industries"]
			except Exception:
				return "Sorry. The LinkedIn API could not find " + data + "for company " + company

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
			try:
				return d1["locations"]
			except Exception:
				return "Sorry. The LinkedIn API could not find " + data + "for company " + company

		"""
		Returns a string that contains the status of the company: operating or not.
		"""
		if data == 'status':
			try:
				return d1["status"]["name"]
			except Exception:
				return "Sorry. The LinkedIn API could not find " + data + "for company " + company

		"""
		Returns a string that contains the website url of the company.
		"""
		if data == 'website_url':
			try:
				return d1["websiteUrl"]
			except Exception:
				return "Sorry. The LinkedIn API could not find " + data + "for company " + company

	# GET INFORMATION FROM CRUNCHBASE
	if api == 'crunchbase':

		# DATA FROM CRUNCHBASE
		r = requests.get(CRUNCHBASE_URL_1 + company + CRUNCHBASE_URL_2)
		data_crunch = r.text
		try:
			d2 = json.loads(data_crunch)
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
			try:
				return d2["acquisitions"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains the blog url of the company
		"""
		if data == 'blog_url':
			try:
				return d2["blog_url"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

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
			try:
				return d2["competitions"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains a description of the company
		"""
		if data == 'description':
			try:
				return d2["description"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains the company email address
		"""
		if data == 'email_address':
			try:
				return d2["email_address"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

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
			try:
				return d2["funding_rounds"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains the company homepage url 
		"""
		if data == 'homepage_url':
			try:
				return d2["homepage_url"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a JSON Object that contains the company investments
		"""
		if data == 'investments':
			try:
				return d2["investments"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

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
			try:
				return d2["milestones"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains the number of employees
		"""
		if data == 'number_employees':
			try:
				return d2["number_of_employees"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

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
			try:
				return d2["offices"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains the 
		"""
		if data == 'overview':
			try:
				return d2["overview"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains the company overview
		"""
		if data == 'phone_number':
			try:
				return d2["phone_number"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

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
			try:
				return d2["relationships"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains the total money raised 
		"""
		if data == 'total_money_raised':
			try:
				return d2["total_money_raised"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

		"""
		Returns a string that contains the twitter username 
		"""
		if data == 'twitter_username':
			try:
				return d2["twitter_username"]
			except Exception:
				return "Sorry. The Crunchbase API could not find " + data + "for company " + company

	# GET INFORMATION FROM GLASSDOOR
	if api == 'glassdoor':
	
		# GETS DATA FROM GLASSDOOR SCRAPING
		x, GLASSDOOR_URL = get(company)
		x_json = x.json()
		try:
			d3 = json.loads(x_json)
		except Exception:
			"Sorry. The Glassdoor API could not find information for company " + company			

		"""

		"""
		if data == 'url':
			return GLASSDOOR_URL

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
			try:
				return d3["ceo"]
			except Exception:
				return "Sorry. The Glassdoor API could not find " + data + "for company " + company

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
			try:
				return d3["meta"]
			except Exception:
				return "Sorry. The Glassdoor API could not find " + data + "for company " + company

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
			try:
				return d3["salary"]
			except Exception:
				return "Sorry. The Glassdoor API could not find " + data + "for company " + company

		"""
		Returns a JSON object that contains the satisfaction of employees

		Ex. 
		{ u'satisfaction': {u'ratings': 9, u'score': None }}
		"""
		if data == 'satisfaction':
			try:
				return d3["satisfaction"]
			except Exception:
				return "Sorry. The Glassdoor API could not find " + data + "for company " + company

# TESTING API
if __name__ == "__main__":
	print "Initial Test"

	company = "amazon"


	# CRUNCHBASEEE -----------------------------------	
	d2 = company_api_function(company, 'crunchbase', 'all')
	print "API: crunchbase"			
	pprint.pprint(d2)

	# GLASSDOORRR -----------------------------------	
	d3 = company_api_function(company, 'glassdoor', 'all')
	print "\n\n\n\nAPI: glassdoor"
	pprint.pprint(d3)

	# LINKEDINNNN -----------------------------------	
	d1 = company_api_function(company, 'linkedin', 'all')
	print "\n\n\n\nAPI: linkedin"	
	pprint.pprint(d1)
	





