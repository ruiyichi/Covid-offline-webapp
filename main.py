from flask import Flask, render_template
import json
import COVID19Py
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import dateutil.parser
import numpy as np
from math import ceil, log
import os


covid19 = COVID19Py.COVID19("https://covid-tracker-us.herokuapp.com")

with open("static/countries.json") as json_file:
    countries = json.load(json_file)

class Country(object):
    def __init__(self, country_name):
        self.name = country_name
        self.population = 0
        locations = covid19.getLocations()
        for x in range(len(locations)):
        	if "US" in locations[x]["country"]:
        		locations[x]["country"] = "United States"
        	if self.name in locations[x]["country"]:
	            info = (covid19.getLocationByCountryCode(locations[x]["country_code"]))
	            self.code = locations[x]["country_code"]
	            self.population = f'{info[0]["country_population"]:,}'

    def get_pop(self):
        return self.population

    def get_code(self):	
        return self.code

    def get_cases(self):
        location = covid19.getLocationByCountryCode(self.code)

        if len(location[0]["province"]) > 0:
            raise Exception("Countries with province data will be implemented later")

        return f'{location[0]["latest"]["confirmed"]:,}'

    def get_deaths(self):
        location = covid19.getLocationByCountryCode(self.code)

        if len(location[0]["province"]) > 0:
            raise Exception("Countries with province data will be implemented later")

        return f'{location[0]["latest"]["deaths"]:,}'

    def graph(self, show_deaths=True):
        location = covid19.getLocationByCountryCode(self.code, timelines=True)

        case_dates = []
        cases = []
        deaths = []
        death_dates=[]

        if len(location[0]["province"]) > 0:
            raise Exception("Countries with province data will be implemented later")

        for x in location[0]["timelines"]["confirmed"]["timeline"]:
            case_dates.append(dateutil.parser.parse(x))
            cases.append(int(location[0]["timelines"]["confirmed"]["timeline"][x]))

        plt.yticks(np.arange(min(cases), max(cases) + 1, int(str(max(cases))[0] +
                                                             (len(str(max(cases))) - 1) * '0') / 10))
        plt.ylabel("Cases")
        plt.xlabel("Time")
        plt.title("Covid-19 Cases for " + self.name + "\nLast updated: " + dateutil.parser.parse(
            location[0]["last_updated"]).strftime("%B %d, %Y"))

        if show_deaths:

            for x in location[0]["timelines"]["deaths"]["timeline"]:
                deaths.append(location[0]["timelines"]["deaths"]["timeline"][x])
                death_dates.append(dateutil.parser.parse(x))

            plt.scatter(case_dates, cases, label="Cases", s=20)
            plt.scatter(death_dates, deaths, c='r', label="Deaths", s=7)
            plt.legend()
        else:
            plt.scatter(case_dates, cases, s=20)

        plt.savefig(r'static/covid19plots/plot_' + self.code + '.jpg')
        plt.clf()


class Global(object):
	def __init__(self, name):
		self.name = "Global"
		latest = covid19.getLatest()

		self.cases = f'{latest["confirmed"]:,}'
		self.deaths = f'{latest["deaths"]:,}'

	def get_cases(self):
		return self.cases

	def get_deaths(self):
		return self.deaths


app = Flask(__name__)


@app.route("/home")
@app.route("/")
def home():
	return render_template("home.html")

@app.route("/stats/")
@app.route("/stats")
def stats():

	countrylist = []

	locations = covid19.getLocations()

	for x in locations:
	    if (x["country"]) not in countrylist:
	    	countrylist.append(x["country"])

	countrylist = ["Taiwan" if x == "Taiwan*" else x for x in countrylist]
	countrylist = ["United States" if x =="US" else x for x in countrylist]
	countrylist.remove("MS Zaandam")
	countrylist = sorted(countrylist)

	return render_template("coronavirus.html", list=countrylist)

@app.route("/stats/<country>")
def countrystats(country):
	
	if country == "global":
		newCountry = Global(country)
		return render_template("global.html", countrycases=newCountry.get_cases(), countrydeaths=newCountry.get_deaths())
	else:
		while True:
			try:
				newCountry = Country(country)
			except requests.exceptions.HTTPError:
				continue
			break
		
		try:
			newCountry.graph()
		except Exception:
			return "Countries with province data will be implemented later"

		"""try:
							
		

					except Exception:
						return "No data"
					except:
						return No data"""

		
		full_filename = '/static/covid19plots/plot_' + str(newCountry.get_code()) + '.jpg'
		"""try:
						return render_template("stats.html", countryname=country, countrypop=newCountry.get_pop(), countrycases=newCountry.get_cases(), countrydeaths=newCountry.get_deaths(), user_image=full_filename)
					except Exception:
						return "Countries with province data will be implemented later"""
		return render_template("stats.html", countryname=country, countrypop=newCountry.get_pop(), countrycases=newCountry.get_cases(), countrydeaths=newCountry.get_deaths(), user_image=full_filename)

@app.route("/about")
def about():
	return render_template("about.html")

if __name__ == "__main__":
	app.run(debug=True)