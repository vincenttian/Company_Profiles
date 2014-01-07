from django.db import models

# Create your models here.
class API(models.Model):
	company = models.CharField(max_length=50)
	linkedin_content = models.TextField()
	glassdoor = models.TextField()
	crunchbase_content = models.TextField()

	def __unicode__(self):
		return "Content: " + self.content
