"""
==========================================================
CanopyAI
Ward Engine
==========================================================
"""

from backend.ward_engine.loader import WardLoader
from backend.ward_engine.zonal_stats import ZonalStatistics
from backend.ward_engine.ranking import WardRanking
from backend.ward_engine.exporter import WardExporter


def run():

    # ==========================================================
    # HEADER
    # ==========================================================

    print("=" * 70)
    print("CANOPY AI - WARD ENGINE")
    print("=" * 70)

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    loader = WardLoader()

    datasets = loader.load_all()

    # ==========================================================
    # ZONAL STATISTICS
    # ==========================================================

    zonal = ZonalStatistics(

        datasets["wards"],

        datasets["impact"]

    )

    ward_stats = zonal.compute()

    zonal.summary()

    # ==========================================================
    # WARD RANKING
    # ==========================================================

    ranking = WardRanking(

        ward_stats

    )

    ward_stats = ranking.compute()

    ranking.summary()

    # ==========================================================
    # EXPORT RESULTS
    # ==========================================================

    exporter = WardExporter(

        ward_stats

    )

    exporter.export_all()

    # ==========================================================
    # PIPELINE STATUS
    # ==========================================================

    print()

    print("=" * 70)

    print("WARD ENGINE STATUS")

    print("=" * 70)

    print("✔ Load Ward Boundaries")
    print("✔ Load Impact Raster")
    print("✔ CRS Reprojection")
    print("✔ Zonal Statistics")
    print("✔ Ward Ranking")
    print("✔ Export CSV")
    print("✔ Export GeoJSON")
    print("✔ Export Dashboard JSON")
    print("✔ Export Summary Report")

    print()

    print("=" * 70)

    print("WARD ENGINE COMPLETED SUCCESSFULLY")

    print("=" * 70)

    return {

        "status": "success",

        "outputs": {

            "ward_rankings_csv": "outputs/ward_rankings.csv",

            "ward_rankings_geojson": "outputs/ward_rankings.geojson",

            "dashboard": "outputs/dashboard_data.json",

            "summary": "outputs/summary_report.json",

            "top25": "outputs/top25_wards.csv"

        }

    }


if __name__ == "__main__":
    run()