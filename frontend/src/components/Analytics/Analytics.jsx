import "./Analytics.css";

import PlantationChart from "../Charts/LineChart";
import LandCoverChart from "../Charts/PieChart";

export default function Analytics({
    dashboard = [],
    summary = {}
}) {

    return (

        <div className="analytics">

            <div className="analytics-chart-card analytics-primary">

                <div className="analytics-chart-header">

                    <div>

                        <span className="analytics-eyebrow">
                            SPATIAL TREND
                        </span>

                        <h3>
                            Plantation & Impact Trend
                        </h3>

                        <p>
                            AI-derived impact distribution across analyzed areas
                        </p>

                    </div>

                    <div className="analytics-chart-badge">
                        LIVE
                    </div>

                </div>

                <div className="analytics-chart-body">

                    <PlantationChart
                        dashboard={dashboard}
                        summary={summary}
                    />

                </div>

            </div>


            <div className="analytics-chart-card">

                <div className="analytics-chart-header">

                    <div>

                        <span className="analytics-eyebrow">
                            LAND COVER
                        </span>

                        <h3>
                            Land Cover Distribution
                        </h3>

                        <p>
                            Composition of classified urban surfaces
                        </p>

                    </div>

                    <div className="analytics-chart-icon">
                        ◔
                    </div>

                </div>

                <div className="analytics-chart-body">

                    <LandCoverChart
                        dashboard={dashboard}
                        summary={summary}
                    />

                </div>

            </div>

        </div>

    );

}