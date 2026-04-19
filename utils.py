import geopandas as gpd
from shapely.geometry import Point
import requests
from zipfile import ZipFile
from io import BytesIO
from pyproj import Transformer
from unidecode import unidecode

class CountryFinder:
    def __init__(self):
        self._transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        self._shapefile = gpd.read_file(
            "mapdata/World_Countries.shp"
        )
        self._cids = dict(
            [(unidecode(x), idx) for idx, x in enumerate(sorted(list(set(self._shapefile['COUNTRY'].tolist()))))]
        )
        
    def finds(self, lat, lon):
        wmcoords = self._transformer.transform(lon, lat)
        point = Point(wmcoords[0], wmcoords[1])
        result = self._shapefile[self._shapefile.contains(point)]
        if not result.empty:
            return unidecode(result.iloc[0]['COUNTRY'])
        return None

    def cid(self, country):
        return self._cids[unidecode(country)]
    
    def findi(self, lat, lon):
        country = self.finds(lat, lon)
        return None if not country else self.cid(country)

    def __len__(self):
        return len(self._cids)

    def __str__(self):
        return f"CountryFinder for {len(self._cids)} Countries"

def main():
    cf = CountryFinder()
    print(cf)
    tests = list(map(lambda x: x[:-1].split(","), open("mapdata/country_tests.csv").readlines()[1:]))
    print(f"{'Expected':44s} | Guess")
    print("------------------+---------------------------------")
    nerr = 0
    nmiss = 0
    guesses = set()
    for test in tests:
        test[1] = unidecode(test[1])
        guess = str(cf.findi(float(test[3]), float(test[2])))
        if guess not in guesses: guesses.add(guess)
        print(f"{test[1]:44s} | {guess if guess is not None else ''}")
        if not guess:
            nmiss += 1
        elif test[1] != guess:
            nerr += 1
    print(f"Number of errors: {nerr}")
    print(f"Number of misses: {nmiss}")
    print(f"Number of unique: {len(guesses)}")

if __name__ == "__main__":
    main()