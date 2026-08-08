"""
==========================================================
CanopyAI
Recommendation Engine
Loader
==========================================================
"""

from pathlib import Path

import pandas as pd
import json


class RecommendationLoader:

    def __init__(self):

        self.output_dir = Path("outputs")

        self.wards = None

        self.dashboard = None

    # =====================================================
    # LOAD WARD RANKINGS
    # =====================================================

    def load_rankings(self):

        path = self.output_dir / "ward_rankings.csv"

        if not path.exists():

            raise FileNotFoundError(

                "ward_rankings.csv not found."

            )

        self.wards = pd.read_csv(path)

        print()

        print("=" * 70)
        print("WARD RANKINGS LOADED")
        print("=" * 70)

        print(f"Rows : {len(self.wards)}")

        return self.wards

    # =====================================================
    # LOAD DASHBOARD DATA
    # =====================================================

    def load_dashboard(self):

        path = self.output_dir / "dashboard_data.json"

        if not path.exists():

            raise FileNotFoundError(

                "dashboard_data.json not found."

            )

        with open(

            path,

            "r",

            encoding="utf-8"

        ) as f:

            self.dashboard = json.load(f)

        print()

        print("=" * 70)
        print("DASHBOARD DATA LOADED")
        print("=" * 70)

        print(f"Records : {len(self.dashboard)}")

        return self.dashboard

    # =====================================================
    # LOAD EVERYTHING
    # =====================================================

    def load_all(self):

        self.load_rankings()

        self.load_dashboard()

        print()

        print("=" * 70)
        print("RECOMMENDATION DATA READY")
        print("=" * 70)

        return {

            "wards": self.wards,

            "dashboard": self.dashboard

        }