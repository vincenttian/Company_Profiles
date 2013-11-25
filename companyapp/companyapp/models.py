from django.db import models

# Create your models here.
class Product(models.Model):
	name = models.CharField(max_length=50)

class Company(models.Model):
	name = models.CharField(max_length=50, primary_key=True)
	ticker = models.CharField(max_length=50, blank=True)
	stock_exchange = models.CharField(max_length=50, blank=True)
	website = models.URLField(max_length=50)
	CEO = models.CharField(max_length=50)
	size = models.CharField(max_length=50)
	company_type = models.CharField(max_length=50)
	founded = models.CharField(max_length=50)
	IPO_year = models.CharField(max_length=50)
	# founded = models.DateTimeField()
	# IPO_year = models.DateTimeField()
	location = models.CharField('State', max_length=255, blank=True)
	industry = models.CharField(max_length=50)
	description = models.CharField(max_length=50)
	competitors = models.TextField()
	acquisitions = models.TextField()
	investments = models.TextField()
	products = models.TextField()

	# KEEPING THINGS SIMPLE FOR NOW
	# competitors = models.ForeignKey('self', related_name = 'competitor')
	# acquisitions = models.ForeignKey('self', related_name = 'acquisition')
	# investments = models.ForeignKey('self', related_name = 'investment')
	# products = models.ForeignKey(Product)
	overview = models.TextField(blank=True)

	def __unicode__(self):
		#return "%(name)s %(ticker)s %(stock_exchange)s %(website)s %(CEO)s %(size)s %(company_type)s %(founded)s %(IPO_year)s %(location)s %(industry)s %(description)s %(competitors)s %(acquisitions)s %(investments)s %(products)s %(overview)s" %\
		return "%(name)s" %\
		 {"name": self.name}#, "ticker": self.ticker, "stock_exchange": self.stock_exchange, "website":self.website, "CEO":self.CEO, "size": self.size, "company_type": self.company_type, "founded": self.founded, "IPO_year": self.IPO_year, "location": self.location, "industry": self.industry, "description": self.description, "competitors": self.competitors, "acquisitions": self.acquisitions, "investments": self.investments, "products": self.products, "overview": self.overview}

	list_filter = ['founded', 'IPO_year']
	search_fields = ['name', 'ticker', 'location', 'industry', 'products']

	# class Meta:
	# 	unique_together = ('name', 'ticker')

	# ADDITIONAL METHODS HERE FOR 
	# def 