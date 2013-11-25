Company Profiles:

I want to build an application to keep track of and follow recent developments of companies I am interested in. 
Through this project, I will learn more about the tech industry, start-ups, and improve my skills as a developer.

1. Write scripts to find relevant information
2. Store information in dictionary
3. Write webapp to present information

Project Explanation:
1. I load a defined list of companies into the database with $ python manage.py load_data, where the LinkedIn API and Crunchbase API are called.
   To add more companies, edit the load_data.py file under companyapp/companyapp/management/commands
2. To drop the database and reload it, follow these steps:
   rm company_db
   $ python manage.py syncdb
   $ python manage.py load_data
3. companyapp/companyapp
   $ views.py handles the views
   $ urls.py handles the urls stuff
   $ models.py defines the database schema
   $ templates/company_details.html is the template that everything is loaded on

TODO:
1. Add slug so that strings are all changed to a single form: i.e. LinkedIn = Linkedin = linkedin
2. Have 2 rounds of loading so that companies/competitors are not just strings
3. Add search box at the top
4. Add functionality on the front-end

Steps to Run Project:

1. Install everything you need with pip install (insert dependency here)
2. Run server: $ python manage.py runserver
3. Company information is at http://127.0.0.1:8000/company/(company name)
