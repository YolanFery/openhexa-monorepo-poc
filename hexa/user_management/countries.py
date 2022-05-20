from pathlib import Path

import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import mapping

WHO_REGION_NAMES = {
    "AMRO": "Region of the Americas",
    "AFRO": "African Region",
    "EMRO": "Eastern Mediterranean Region",
    "EURO": "European Region",
    "WPRO": "Western Pacific Region",
    "SEARO": "South-East Asian Region",
}


class WHOInfo:
    def __init__(self, data: GeoDataFrame):
        self.data = data

    @property
    def region(self):
        return {
            "code": self.data["WHO_REGION"],
            "name": WHO_REGION_NAMES[self.data["WHO_REGION"]],
        }

    @property
    def default_crs(self):
        return self.data["DEFAULT_EPSG"]

    @property
    def simplified_extent(self):
        return mapping(self.data["geometry"])["coordinates"][0]


def get_who_info(alpha3):
    """Get miscellaneous WHO-provided info for the country corresponding to the provided alpha3."""

    path_to_file = Path(__file__).resolve().parent / "data/WHO_ADM0_SIMPLIFIED.geojson"
    gdf = gpd.read_file(path_to_file)

    try:
        country_data = gdf.loc[gdf.ISO_3_CODE == alpha3].iloc[0]
        return WHOInfo(country_data)
    except IndexError:
        return None
