import "./Legend.css";

export default function Legend() {

    return (

        <div className="legend">

            {/* =====================================================
                HEADER
            ===================================================== */}

            <div className="legend-header">

                <div>

                    <div className="legend-kicker">
                        CANOPYAI • GIS ANALYTICS
                    </div>

                    <h3 className="legend-title">
                        Impact Score
                    </h3>

                </div>


                <div className="legend-badge">
                    0–100
                </div>

            </div>


            {/* =====================================================
                SCORE DESCRIPTION
            ===================================================== */}

            <div className="legend-description">

                Priority intensity across the analyzed area

            </div>


            {/* =====================================================
                GRADIENT
            ===================================================== */}

            <div className="legend-gradient-wrap">

                <div className="legend-gradient" />

            </div>


            {/* =====================================================
                SCALE
            ===================================================== */}

            <div className="legend-scale">

                <span>0</span>

                <span>25</span>

                <span>50</span>

                <span>75</span>

                <span>100</span>

            </div>


            {/* =====================================================
                PRIORITY LABELS
            ===================================================== */}

            <div className="legend-endcaps">

                <div className="legend-priority">

                    <span className="legend-dot low" />

                    <span>
                        Low priority
                    </span>

                </div>


                <div className="legend-priority high">

                    <span className="legend-dot high" />

                    <span>
                        High priority
                    </span>

                </div>

            </div>


            {/* =====================================================
                FOOTER
            ===================================================== */}

            <div className="legend-footer">

                <span className="legend-status-dot" />

                AI-derived spatial impact

            </div>

        </div>

    );

}