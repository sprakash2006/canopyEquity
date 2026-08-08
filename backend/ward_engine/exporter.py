"""
==========================================================
CanopyAI
Ward Engine
Exporter
==========================================================
"""

from pathlib import Path
import json


class WardExporter:

    def __init__(self, wards):

        self.wards = wards

        self.output_dir = Path("outputs")

        self.output_dir.mkdir(exist_ok=True)

    # =====================================================
    # EXPORT CSV
    # =====================================================

    def export_csv(self):

        path = self.output_dir / "ward_rankings.csv"

        self.wards.to_csv(
            path,
            index=False
        )

        print(f"Saved : {path}")

    # =====================================================
    # EXPORT GEOJSON
    # =====================================================

    def export_geojson(self):

        print("\nExporting GeoJSON...")

        # ------------------------------------------
        # Original CRS (UTM)
        # ------------------------------------------

        original_path = self.output_dir / "ward_rankings.geojson"

        self.wards.to_file(
            original_path,
            driver="GeoJSON"
        )

        print(f"Saved : {original_path}")

        # ------------------------------------------
        # Web CRS (Leaflet)
        # ------------------------------------------

        try:

            web = self.wards.to_crs(epsg=4326)

            web_path = self.output_dir / "ward_rankings_web.geojson"

            web.to_file(
                web_path,
                driver="GeoJSON"
            )

            print(f"Saved : {web_path}")

        except Exception as e:

            print("Failed to create web GeoJSON")

            print(e)

    # =====================================================
    # EXPORT TOP 10
    # =====================================================

    def export_top10(self):

        path = self.output_dir / "top10_wards.json"

        cols = [

            "Rank",
            "ward_name",
            "Composite_Score",
            "Priority",
            "Impact_Mean"

        ]

        top10 = (

            self.wards[cols]

            .head(10)

            .to_dict(
                orient="records"
            )

        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                top10,
                f,
                indent=4
            )

        print(f"Saved : {path}")

    # =====================================================
    # EXPORT TOP 25
    # =====================================================

    def export_top25(self):

        path = self.output_dir / "top25_wards.csv"

        self.wards.head(25).to_csv(
            path,
            index=False
        )

        print(f"Saved : {path}")

    # =====================================================
    # DASHBOARD
    # =====================================================

    def export_dashboard(self):

        path = self.output_dir / "dashboard_data.json"

        cols = [

            "ward_name",
            "Rank",
            "Composite_Score",
            "Priority",
            "Impact_Mean"

        ]

        dashboard = (

            self.wards[cols]

            .to_dict(
                orient="records"
            )

        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                dashboard,
                f,
                indent=4
            )

        print(f"Saved : {path}")

    # =====================================================
    # SUMMARY
    # =====================================================

    def export_summary(self):

        path = self.output_dir / "summary_report.json"

        summary = {

            "total_wards": int(len(self.wards)),

            "highest_score": float(
                self.wards["Composite_Score"].max()
            ),

            "lowest_score": float(
                self.wards["Composite_Score"].min()
            ),

            "average_score": float(
                self.wards["Composite_Score"].mean()
            ),

            "top_ward": str(
                self.wards.iloc[0]["ward_name"]
            )

        }

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                summary,
                f,
                indent=4
            )

        print(f"Saved : {path}")

    # =====================================================
    # EXPORT EVERYTHING
    # =====================================================

    def export_all(self):

        print()

        print("=" * 70)

        print("EXPORTING WARD RESULTS")

        print("=" * 70)

        self.export_csv()

        self.export_geojson()

        self.export_top10()

        self.export_top25()

        self.export_dashboard()

        self.export_summary()

        print()

        print("=" * 70)

        print("ALL FILES EXPORTED")

        print("=" * 70)