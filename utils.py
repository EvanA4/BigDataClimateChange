import geopandas as gpd
from shapely.geometry import Point


WORLD_DATA = gpd.read_file(
    "ne_110m_admin_0_countries.shp"
)


def get_country(lat, lon):
    point = Point(lon, lat)
    result = WORLD_DATA[WORLD_DATA.contains(point)]
    
    if not result.empty:
        return result.iloc[0]['NAME']
    return None


def main():
    tests = list(map(lambda x: x[:-1].split(","), open("country_tests.csv").readlines()[1:]))
    print(f"{"Expected":44s} | Guess")
    print("------------------+---------------------------------")
    for test in tests:
        guess = get_country(float(test[3]), float(test[2]))
        print(f"{test[1]:44s} | {guess if guess is not None else ""}")

if __name__ == "__main__":
    main()