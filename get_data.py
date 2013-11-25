import oauth2 as oauth
import httplib2
import time, os, simplejson
import urlparse
import BaseHTTPServer 
import json
import pprint
import requests
from xml.etree import ElementTree as ET
 
consumer_key    =   '452p27539u5f'
consumer_secret =   '3q1iiaeQph2wRH4M'
request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
access_token_url =  'https://api.linkedin.com/uas/oauth/accessToken'
authorize_url =     'https://api.linkedin.com/uas/oauth/authorize'
config_file   = '.service.dat'
xml_file      = '.xml.dat'
http_status_print = BaseHTTPServer.BaseHTTPRequestHandler.responses
 
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
                log_diagnostic_info(client,url,request_headers,method,body,resp,content,error_string)
        else:
                status_codes = {403: "\n** Status:\n\tA 403 response was received. Usually this means you have reached a throttle limit.",
                                                401: "\n** Status:\n\tA 401 response was received. Usually this means the OAuth signature was bad.",
                                                405: "\n** Status:\n\tA 405 response was received. Usually this means you used the wrong HTTP method (GET when you should POST, etc).",
                                                400: "\n** Status:\n\tA 400 response was received. Usually this means your request was formatted incorrectly or you added an unexpected parameter.",
                                                404: "\n** Status:\n\tA 404 response was received. The resource was not found."}
                if resp.status in status_codes:
                        log_diagnostic_info(client,url,request_headers,method,body,resp,content,status_codes[resp.status])
                else:
                        log_diagnostic_info(client,url,request_headers,method,body,resp,content,http_status_print[resp.status][1])

# COMPANY LIST HERE
companies = ["palantir"]#, "apple", "microsoft"]

if __name__ == "__main__":
               
        LINKEDIN_URL_1 = "http://api.linkedin.com/v1/companies/universal-name="
        LINKEDIN_URL_2 = ":(id,name,universal-name,company-type,ticker,website-url,industries,status,employee-count-range,locations,description,stock-exchange,founded-year,end-year)"
        CRUNCHBASE_URL_1 = "http://api.crunchbase.com/v/1/company/"
        CRUNCHBASE_URL_2 = ".js?api_key=emy48jd7q3k7kv6tx8ft6adb"
        
        for company in companies:   

            # GETS DATA FROM LINKEDIN API
            # Get authorization set up and create the OAuth client
            client = get_auth() 
            response = make_request(client, LINKEDIN_URL_1 + company + LINKEDIN_URL_2, {"x-li-format":'json'})
            d1 = json.loads(response)
            
            # GETS DATA FROM CRUNCHBASE API
            r = requests.get(CRUNCHBASE_URL_1 + company + CRUNCHBASE_URL_2)
            data = r.text
            d2 = json.loads(data)

            print "\nCompany name: " + d1["name"]
            print "Company ticker: " + d1["ticker"] + " on " + d1["stockExchange"]["name"] 
            print "Company website: " + d1["websiteUrl"]
            print "Company CEO: " + d2["relationships"][0]["person"]["first_name"] + " " + d2["relationships"][0]["person"]["last_name"]
            print "Company size: " + d1["employeeCountRange"]["name"]
            print "Company type: " + d1["companyType"]["name"]
            print "Company founded: " + str(d1["foundedYear"])
            print "Company IPO Year: " + str(d2["ipo"]["pub_year"])
            print "Company location: " + d1["locations"]["values"][0]["address"]["city"]
            print "Company industry: " + d1["industries"]["values"][0]["name"]
            print "Company description: " + d2["description"]
            # PRODUCTS
            product_list = {}
            count = 0
            for product in d2["products"]:
                # print product["name"]
                product_list[count] = str(product["name"])
                count += 1
            print "\nCompany products: " + str(product_list)
            # COMPETITORS
            competitor_list = {}
            count = 0
            for competitor in d2["competitions"]:
                competitor_list[count] = str(competitor["competitor"]["name"])
                count += 1
            print "\nCompany competitors: " + str(competitor_list)
            # ACQUISITIONS
            acquisition_list = {}
            count = 0
            for acquisition in d2["acquisitions"]:
                acquisition_list[count] = acquisition["company"]["name"]
                count += 1
            print "\nCompany acquisitions: " + str(acquisition_list)
            # INVESTMENTS
            investment_list = {}
            count = 0
            for investment in d2["investments"]:
                investment_list[count] = [investment["funding_round"]["company"]["name"], investment["funding_round"]["raised_amount"], investment["funding_round"]["funded_year"]]
                count += 1
            print "\nCompany investments: " + str(investment_list)
            print "\nCompany overview: " + d2["overview"]

