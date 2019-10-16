from django.core.management import BaseCommand
from jd_parser.entity_matcher import CityMatcher
import spacy
import os
import pickle
from django.conf import settings
from utils_app.models import City
def save_object(obj, filename):

    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

states_dict = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District Of Columbia",
    "FM": "Federated States Of Micronesia",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MH": "Marshall Islands",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "MP": "Northern Mariana Islands",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PW": "Palau",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VI": "Virgin Islands",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}
pickle_city_path = os.path.join(settings.MODELS_PATH, 'cities.pkl')
city_model_path = os.path.join(settings.MODELS_PATH, 'nlp_cities_and_states')
class Command(BaseCommand):
    help = "this command is for training locations with jd  "

    # A command must define handle()
    def handle(self, *args, **options):
        cities = City.objects.all()
        print('____________________________________________________')

        location_list = []

        for city in cities:
            location_list.append(city.name)

        for state in states_dict.items():
            location_list.extend(state)
        nlp = spacy.load('en_core_web_sm')

        cities_matcher = CityMatcher(nlp, location_list, 'USLOC')

        save_object(cities_matcher, pickle_city_path)
        nlp.add_pipe(cities_matcher, before='ner')

        # Place JD here
        jd = ' '
        path = os.path.join(os.path.curdir, city_model_path)
        nlp.to_disk(path)
