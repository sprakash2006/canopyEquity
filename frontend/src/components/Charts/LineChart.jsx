import {
    ResponsiveContainer,
    LineChart,
    Line,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip,
    ReferenceLine
} from "recharts";

import "./LineChart.css";


export default function PlantationChart({

    dashboard = [],

    summary = {}

}) {


    /* =========================================================
       EXISTING DATA LOGIC
       ========================================================= */

    const chartData = dashboard

        .slice(0, 10)

        .map((ward, index) => ({

            name:

                ward.ward_name ||

                ward.Ward_Name ||

                `Ward ${index + 1}`,

            score:

                Number(

                    ward.Composite_Score ??

                    ward.score ??

                    ward.Impact_Mean ??

                    0

                )

        }));


    /* =========================================================
       LOCAL MAXIMUM FOR VISUAL SCALE
       ========================================================= */

    const maxScore = chartData.length

        ? Math.max(
            ...chartData.map(
                item => item.score
            )
        )

        : 100;


    const chartMax =
        Math.ceil(
            Math.max(maxScore, 100) / 10
        ) * 10;


    return (

        <div className="impact-chart">


            {/* =================================================
                CHART
            ================================================= */}

            <div className="impact-chart-container">

                <ResponsiveContainer
                    width="100%"
                    height="100%"
                >

                    <LineChart

                        data={chartData}

                        margin={{
                            top: 8,
                            right: 10,
                            left: -18,
                            bottom: 2
                        }}

                    >

                        <CartesianGrid

                            stroke="#edf1ee"

                            strokeDasharray="3 5"

                            vertical={false}

                        />


                        <XAxis

                            dataKey="name"

                            axisLine={false}

                            tickLine={false}

                            tick={{
                                fill: "#94a3b8",
                                fontSize: 8,
                                fontWeight: 600
                            }}

                            tickMargin={8}

                        />


                        <YAxis

                            domain={[
                                0,
                                chartMax
                            ]}

                            axisLine={false}

                            tickLine={false}

                            tick={{
                                fill: "#94a3b8",
                                fontSize: 8
                            }}

                            width={40}

                        />


                        <ReferenceLine

                            y={
                                summary.average_score
                                    ? Number(
                                        summary.average_score
                                    )
                                    : undefined
                            }

                            stroke="#cbd5e1"

                            strokeDasharray="4 4"

                            ifOverflow="extendDomain"

                        />


                        <Tooltip

                            cursor={{
                                stroke: "#dce8df",
                                strokeWidth: 1
                            }}

                            content={
                                <ImpactTooltip />
                            }

                        />


                        <Line

                            type="monotone"

                            dataKey="score"

                            stroke="#166534"

                            strokeWidth={2.5}

                            dot={{
                                r: 3.5,
                                fill: "#ffffff",
                                stroke: "#166534",
                                strokeWidth: 2
                            }}

                            activeDot={{
                                r: 5,
                                fill: "#166534",
                                stroke: "#ffffff",
                                strokeWidth: 2
                            }}

                            connectNulls

                            isAnimationActive

                            animationDuration={700}

                        />

                    </LineChart>

                </ResponsiveContainer>

            </div>


            {/* =================================================
                CHART FOOTER
            ================================================= */}

            <div className="impact-chart-footer">

                <div className="impact-chart-stat">

                    <span>
                        HIGHEST SCORE
                    </span>

                    <strong>

                        {chartData.length
                            ? Math.max(
                                ...chartData.map(
                                    item => item.score
                                )
                            ).toFixed(2)
                            : "--"
                        }

                    </strong>

                </div>


                <div className="impact-chart-divider" />


                <div className="impact-chart-stat">

                    <span>
                        CITY AVERAGE
                    </span>

                    <strong>

                        {summary.average_score !==
                            undefined &&
                        summary.average_score !==
                            null

                            ? Number(
                                summary.average_score
                            ).toFixed(2)

                            : "--"
                        }

                    </strong>

                </div>


                <div className="impact-chart-divider" />


                <div className="impact-chart-stat">

                    <span>
                        AREAS SHOWN
                    </span>

                    <strong>
                        {chartData.length}
                    </strong>

                </div>

            </div>

        </div>

    );

}


/* ============================================================
   CUSTOM TOOLTIP
   ============================================================ */

function ImpactTooltip({
    active,
    payload,
    label
}) {

    if (
        !active ||
        !payload ||
        !payload.length
    ) {

        return null;

    }


    return (

        <div className="impact-tooltip">

            <span>
                {label}
            </span>

            <strong>
                {Number(
                    payload[0].value
                ).toFixed(2)}
            </strong>

            <small>
                Impact Score
            </small>

        </div>

    );

}