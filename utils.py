import geopandas as gpd
from shapely.geometry import Point
import requests
from zipfile import ZipFile
from io import BytesIO

def download_data():
    url = 'https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip'
    response = requests.get(url)
    if response.status_code == 200:
        with ZipFile(BytesIO(response.content)) as zip_file:
            zip_file.extractall('mapdata')
    else:
        print(f"Failed to download file: {response.status_code}")
        exit(1)

download_data()
WORLD_DATA = gpd.read_file(
    "mapdata/ne_110m_admin_0_countries.shp"
)

def get_country(lat, lon):
    point = Point(lon, lat)
    result = WORLD_DATA[WORLD_DATA.contains(point)]
    
    if not result.empty:
        return result.iloc[0]['NAME']
    return None


def main():
    tests = list(map(lambda x: x[:-1].split(","), open("mapdata/country_tests.csv").readlines()[1:]))
    print(f"{'Expected':44s} | Guess")
    print("------------------+---------------------------------")
    for test in tests:
        guess = get_country(float(test[3]), float(test[2]))
        print(f"{test[1]:44s} | {guess if guess is not None else ''}")

if __name__ == "__main__":
    pass
    # main()