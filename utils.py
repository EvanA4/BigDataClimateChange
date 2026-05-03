import geopandas as gpd
from shapely.geometry import Point
import requests
from zipfile import ZipFile
from io import BytesIO
from pyproj import Transformer
from unidecode import unidecode

IMF_CLEAN_NAMES = set([
    "United Kingdom",
    "Austria",
    "United States",
    "Germany",
    "Belgium",
    "Italy",
    "Denmark",
    "France",
    "Sweden",
    "Luxembourg",
    "Switzerland",
    "Norway",
    "Finland",
    "Canada",
    "Greece",
    "Japan",
    "Spain",
    "Iceland",
    "Ireland",
    "Portugal",
    "Argentina",
    "New Zealand",
    "Australia",
    "Bolivia",
    "South Africa",
    "Colombia",
    "Costa Rica",
    "Brazil",
    "Ecuador",
    "Chile",
    "Dominican Republic",
    "El Salvador",
    "Mexico",
    "Panama",
    "Haiti",
    "Honduras",
    "Guatemala",
    "Nicaragua",
    "Uruguay",
    "Peru",
    "Paraguay",
    "Antigua and Barbuda",
    "Jamaica",
    "Belize",
    "Guyana",
    "Puerto Rico",
    "Suriname",
    "Trinidad and Tobago",
    "Cyprus",
    "Oman",
    "Jordan",
    "Israel",
    "Qatar",
    "Lebanon",
    "United Arab Emirates",
    "Saudi Arabia",
    "Bangladesh",
    "Bhutan",
    "Sri Lanka",
    "Malaysia",
    "Indonesia",
    "India",
    "Maldives",
    "Nepal",
    "Philippines",
    "Pakistan",
    "Thailand",
    "Vietnam",
    "Botswana",
    "Angola",
    "Algeria",
    "Central African Republic",
    "Cameroon",
    "Burundi",
    "Cabo Verde",
    "Benin",
    "Chad",
    "Guinea-Bissau",
    "Guinea",
    "Gabon",
    "Ghana",
    "Malawi",
    "Kenya",
    "Morocco",
    "Mali",
    "Libya",
    "Mauritius",
    "Niger",
    "Sierra Leone",
    "Senegal",
    "Rwanda",
    "Sudan",
    "Seychelles",
    "Tunisia",
    "Togo",
    "Solomon Islands",
    "Burkina Faso",
    "Uganda",
    "Zambia",
    "Vanuatu",
    "Samoa",
    "Papua New Guinea",
    "Albania",
    "Bulgaria",
    "Mongolia",
    "Hungary",
    "Romania"
])

IMF_CLEANING_DICT = {
    "Netherlands, The": "Netherlands",
    "Türkiye, Republic of": "Turkiye",
    "Venezuela, República Bolivariana de": "Venezuela",
    "Bahamas, The": "Bahamas",
    "Iran, Islamic Republic of": "Iran",
    "Bahrain, Kingdom of": "Bahrain",
    "Syrian Arab Republic": "Syria",
    "Egypt, Arab Republic of": "Egypt",
    "Korea, Republic of": "South Korea",
    "Congo, Democratic Republic of the": "Congo DRC",
    "Equatorial Guinea, Republic of": "Equatorial Guinea",
    "Congo, Republic of": "Congo",
    "Comoros, Union of the": "Comoros",
    "Ethiopia, The Federal Democratic Republic of": "Ethiopia",
    "Gambia, The": "Gambia",
    "Côte d'Ivoire": "Cote d\'Ivoire",
    "Madagascar, Republic of": "Madagascar",
    "Lesotho, Kingdom of": "Lesotho",
    "São Tomé and Príncipe, Democratic Republic of": "Sao Tome and Principe",
    "Mozambique, Republic of": "Mozambique",
    "Tanzania, United Republic of": "Tanzania",
    "Eswatini, Kingdom of": "Eswatini",
    "Fiji, Republic of": "Fiji",
    "China, People's Republic of": "China",
    "Poland, Republic of": "Poland",
    "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
    "St. Lucia": "Saint Lucia"
}

TINY_CIDS = set([
    7,
    19,
    24,
    27,
    30,
    32,
    33,
    48,
    49,
    50,
    59,
    65,
    88,
    91,
    93,
    95,
    100,
    127,
    136,
    141,
    145,
    148,
    153,
    161,
    162,
    165,
    175,
    177,
    186,
    187,
    190,
    192,
    193,
    196,
    203,
    204,
    225,
    226,
    232,
    239,
    243,
    246,
])

class CountryFinder:
    def __init__(self):
        self.__transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        self.__shapefile = gpd.read_file(
            "dependencies/shapes/World_Countries.shp"
        )
        self.countries = sorted(list(set(self.__shapefile['COUNTRY'].tolist())))
        self.__name_to_cid = dict(
            [(unidecode(x), idx) for idx, x in enumerate(self.countries)]
        )
        self.__cid_to_name = dict(
            [(idx, unidecode(x)) for idx, x in enumerate(self.countries)]
        )
        
    def coords_to_name(self, lat, lon):
        wmcoords = self.__transformer.transform(lon, lat)
        point = Point(wmcoords[0], wmcoords[1])
        result = self.__shapefile[self.__shapefile.contains(point)]
        if not result.empty:
            return unidecode(result.iloc[0]['COUNTRY'])
        return None

    def name_to_cid(self, country):
        return self.__name_to_cid[unidecode(country)]

    def cid_to_name(self, cid):
        return self.__cid_to_name[cid]
    
    def coords_to_cid(self, lat, lon):
        country = self.coords_to_name(lat, lon)
        return None if not country else self.name_to_cid(country)

    def __len__(self):
        return len(self.countries)

    def __str__(self):
        return f"CountryFinder for {len(self.countries)} Countries"

def main():
    cf = CountryFinder()
    print(cf)
    tests = list(map(lambda x: x[:-1].split(","), open("dependencies/country_tests.csv").readlines()[1:]))
    print(f"{'Expected':44s} | Guess (CID) | Guess (Name)")
    print("-------------------------------------------------------------------------")
    nerr = 0
    nmiss = 0
    guesses = set()
    for test in tests:
        test[1] = unidecode(test[1])
        guess_cid = cf.coords_to_cid(float(test[3]), float(test[2]))
        guess_cid_s = str(guess_cid) if guess_cid is not None else ''
        guess_name = cf.cid_to_name(guess_cid) if guess_cid is not None else ''
        if guess_cid not in guesses: guesses.add(guess_cid)
        print(f"{test[1]:44s} | {guess_cid_s:11s} | {guess_name}")
        if not guess_cid:
            nmiss += 1
        elif test[1] != guess_cid:
            nerr += 1
    print(f"Number of errors: {nerr}")
    print(f"Number of misses: {nmiss}")
    print(f"Number of unique: {len(guesses)}")

if __name__ == "__main__":
    main()