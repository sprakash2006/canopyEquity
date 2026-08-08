import "./Analytics.css";

import PlantationChart from "../Charts/LineChart";
import LandCoverChart from "../Charts/PieChart";

export default function Analytics({

    dashboard = [],

    summary = {}

}) {

    return (

        <div className="analytics">

            <PlantationChart

                dashboard={dashboard}

                summary={summary}

            />

            <LandCoverChart

                dashboard={dashboard}

                summary={summary}

            />

        </div>

    );

}