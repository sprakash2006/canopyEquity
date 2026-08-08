import "./WardRanking.css";

import {
    Trophy,
    MapPin,
    ArrowUpRight
} from "lucide-react";

export default function WardRanking({ wards = [] }) {

    // Show only top 5 wards
    const topWards = Array.isArray(wards)
        ? wards.slice(0, 5)
        : [];

    return (

        <div className="ward-card">

            {/* ================= HEADER ================= */}

            <div className="ward-header">

                <div>

                    <h2>

                        <Trophy size={22} />

                        Top Priority Wards

                    </h2>

                    <p>

                        AI Generated Plantation Priority Ranking

                    </p>

                </div>

            </div>

            {/* ================= LIST ================= */}

            <div className="ward-list">

                {

                    topWards.length === 0 ? (

                        <div className="no-data">

                            No Ward Ranking Available

                        </div>

                    ) : (

                        topWards.map((ward, index) => (

                            <div
                                className="ward-item"
                                key={ward.id || ward.Ward_ID || index}
                            >

                                {/* Left */}

                                <div className="ward-left">

                                    <div className="rank">

                                        {index + 1}

                                    </div>

                                    <div>

                                        <h3>

                                            <MapPin size={16} />

                                            {

                                                ward.ward_name ||

                                                ward.Ward_Name ||

                                                ward.name ||

                                                "Unknown Ward"

                                            }

                                        </h3>

                                        <span>

                                            {

                                                ward.Priority ||

                                                ward.priority ||

                                                "N/A"

                                            }

                                        </span>

                                    </div>

                                </div>

                                {/* Right */}

                                <div className="ward-right">

                                    <strong>

                                        {

                                            Number(

                                                ward.Composite_Score ??

                                                ward.score ??

                                                ward.Impact_Mean ??

                                                0

                                            ).toFixed(2)

                                        }

                                    </strong>

                                    <ArrowUpRight size={18} />

                                </div>

                            </div>

                        ))

                    )

                }

            </div>

        </div>

    );

}