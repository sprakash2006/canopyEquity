import "./WardInfoPanel.css";

import {
    MapPinned,
    Trees,
    IndianRupee,
    Leaf,
    Thermometer,
    Award
} from "lucide-react";

export default function WardInfoPanel({ ward }) {

    if (!ward) {

        return (

            <div className="ward-panel empty">

                <h2>Select a Ward</h2>

                <p>

                    Click on any ward to view detailed AI analysis.

                </p>

            </div>

        );

    }

    return (

        <div className="ward-panel">

            <div className="panel-header">

                <MapPinned size={26} />

                <div>

                    <h2>

                        {ward.ward_name ||
                         ward.Ward_Name ||
                         ward.NAME ||
                         "Unknown Ward"}

                    </h2>

                    <span>

                        {ward.Priority || "-"}

                    </span>

                </div>

            </div>

            <div className="panel-grid">

                <div className="panel-card">

                    <Award />

                    <div>

                        <span>Impact Score</span>

                        <h3>

                            {ward.Composite_Score ?? "--"}

                        </h3>

                    </div>

                </div>

                <div className="panel-card">

                    <Trees />

                    <div>

                        <span>Trees</span>

                        <h3>

                            {ward.Recommended_Trees ?? "--"}

                        </h3>

                    </div>

                </div>

                <div className="panel-card">

                    <IndianRupee />

                    <div>

                        <span>Budget</span>

                        <h3>

                            ₹ {ward.Estimated_Budget ?? "--"}

                        </h3>

                    </div>

                </div>

                <div className="panel-card">

                    <Leaf />

                    <div>

                        <span>Carbon Capture</span>

                        <h3>

                            {ward.Carbon_Capture ?? "--"}

                        </h3>

                    </div>

                </div>

                <div className="panel-card">

                    <Thermometer />

                    <div>

                        <span>Cooling Effect</span>

                        <h3>

                            {ward.Cooling_Effect ?? "--"}

                        </h3>

                    </div>

                </div>

            </div>

        </div>

    );

}