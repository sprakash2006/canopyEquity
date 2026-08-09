import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip
} from "recharts";

import "./PieChart.css";


/*
    Risk / priority scale
    VERY HIGH → HIGH → MEDIUM → LOW → VERY LOW
*/

const COLORS = [
    "#ba1a1a",
    "#f48c24",
    "#eab552",
    "#7fa38f",
    "#3e6752"
];


export default function LandCoverChart({
    dashboard = []
}) {

    const priorityCount = {

        "VERY HIGH": 0,

        "HIGH": 0,

        "MEDIUM": 0,

        "LOW": 0,

        "VERY LOW": 0

    };


    dashboard.forEach((ward) => {

        const priority = (

            ward.Priority ||

            ward.priority ||

            "LOW"

        ).toUpperCase();


        if (
            priorityCount[priority] !== undefined
        ) {

            priorityCount[priority]++;

        }

    });


    const data = Object.entries(
        priorityCount
    ).map(
        ([name, value]) => ({
            name,
            value
        })
    );


    const total = dashboard.length;


    return (

        <div className="priority-chart">


            {/* =================================================
                CHART
            ================================================= */}

            <div className="priority-chart-visual">

                <ResponsiveContainer
                    width="100%"
                    height="100%"
                >

                    <PieChart>

                        <Pie

                            data={data}

                            dataKey="value"

                            nameKey="name"

                            cx="50%"

                            cy="50%"

                            innerRadius="55%"

                            outerRadius="78%"

                            paddingAngle={2}

                            stroke="#ffffff"

                            strokeWidth={2}

                            isAnimationActive={true}

                            animationDuration={700}

                        >

                            {data.map(
                                (entry, index) => (

                                    <Cell
                                        key={`cell-${index}`}
                                        fill={
                                            COLORS[
                                                index %
                                                COLORS.length
                                            ]
                                        }
                                    />

                                )
                            )}

                        </Pie>


                        <Tooltip
                            content={
                                <PriorityTooltip />
                            }
                        />

                    </PieChart>

                </ResponsiveContainer>


                {/* =================================================
                    CENTER VALUE
                ================================================= */}

                <div className="priority-center">

                    <strong>
                        {total}
                    </strong>

                    <span>
                        Wards
                    </span>

                </div>

            </div>


            {/* =================================================
                CUSTOM LEGEND
            ================================================= */}

            <div className="priority-legend">

                {data.map(
                    (item, index) => (

                        <div
                            className="priority-legend-item"
                            key={item.name}
                        >

                            <span
                                className="priority-dot"
                                style={{
                                    backgroundColor:
                                        COLORS[
                                            index %
                                            COLORS.length
                                        ]
                                }}
                            />


                            <span className="priority-name">
                                {item.name}
                            </span>


                            <strong className="priority-value">
                                {item.value}
                            </strong>


                            <span className="priority-percent">

                                {total > 0
                                    ? `${Math.round(
                                        (
                                            item.value /
                                            total
                                        ) * 100
                                    )}%`
                                    : "0%"
                                }

                            </span>

                        </div>

                    )
                )}

            </div>

        </div>

    );

}


/* ============================================================
   CUSTOM TOOLTIP
   ============================================================ */

function PriorityTooltip({
    active,
    payload
}) {

    if (
        !active ||
        !payload ||
        !payload.length
    ) {

        return null;

    }


    const item = payload[0];


    return (

        <div className="priority-tooltip">

            <span>
                {item.name}
            </span>

            <strong>
                {item.value} wards
            </strong>

        </div>

    );

}