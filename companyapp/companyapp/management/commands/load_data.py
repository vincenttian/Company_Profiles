from django.core.management.base import BaseCommand, CommandError
from companyapp.companyapp.models import *
from companyapp.companyapp.management.commands.company_api import company_api_function

# COMPANY LISTS HERE
# companies = ['delta-air-lines']
# COMPANIES FOR TESTING
# companies = ['microsoft', 'google', 'amazon', 'ebay', 'linkedin', 'yahoo', 'asana', 'flipboard']

# BIG LIST OF COMPANIES THAT WORK:
companies = \
[ \
'23andme', 'Amazon', 'Apple', 'Apportable', 'Asana', 'Autodesk',\
 'box', 'Broadcom', 'Comcast', 'Dell', 'delta-air-lines', 'Dropbox', 'Ebay', 'EMC', \
 'Ericsson', 'Eventbrite', 'Evernote', 'Facebook', 'flipboard', 'Foursquare', \
 'Groupon', 'guidewire-software', 'Hewlett-Packard', 'Hoopla-Software', 'IBM', 'Intel', 'Intuit', 'Jawbone', \
 'Juniper Networks', 'Klout', \
 'Linkedin', 'Magoosh', 'marin software', 'Meebo', 'Microsoft', 'Netapp', 'Nvidia', 'Oracle', 'Palantir-Technologies', \
 'Pinterest', 'Pocket', 'Qualcomm', 'Quora', 'rackspace', 'red hat', \
 'riverbed technology', 'Salesforce', 'Samsung-Electronics', 'Shoretel', 'Shutterfly', 'Skype', \
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
			try:
				d1 = company_api_function(company, 'linkedin', 'all')			
			except Exception:
				print "ERROR: Could not find " + company + " with LinkedIn API"

			# GETS DATA FROM CRUNCHBASE API
			try:
				d2 = company_api_function(company, 'crunchbase', 'all')				
			except Exception:
				print "Could not find " + company + "with Crunchbase API"

			# GETS DATA FROM GLASSDOOR SCRAPING
			sal = company_api_function(company, 'glassdoor', 'sal')
			url = company_api_function(company, 'glassdoor', 'url')

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
				salary.url = url
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
					salary.url = url
					salary.save()
					salary_list[count] = salary
					count += 1
				company.salaries = str(salary_list)
				company.save()
			print "Successfully loaded " + name + " into the database" 

	def handle(self, *args, **options):
		self.set_database()




