import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip,
    Legend
} from "recharts";

/* Risk/priority scale — order: VERY HIGH, HIGH, MEDIUM, LOW, VERY LOW */
const COLORS = [
    "#ba1a1a",
    "#f48c24",
    "#eab552",
    "#3e6752",
    "#7fa38f"
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

        if (priorityCount[priority] !== undefined) {

            priorityCount[priority]++;

        }

    });

    const data = Object.entries(priorityCount).map(

        ([name, value]) => ({

            name,

            value

        })

    );

    return (

        <div

            style={{

                background: "var(--card)",

                borderRadius: "24px",

                padding: "25px",

                height: "360px",

                border: "1px solid var(--border)"

            }}

        >

            <h2

                style={{

                    color: "var(--text)"

                }}

            >

                Ward Priority Distribution

            </h2>

            <p

                style={{

                    color: "var(--text-muted)",

                    marginBottom: "20px"

                }}

            >

                AI Recommendation Summary

            </p>

            <ResponsiveContainer width="100%" height="85%">

                <PieChart>

                    <Pie

                        data={data}

                        dataKey="value"

                        nameKey="name"

                        innerRadius={65}

                        outerRadius={100}

                        paddingAngle={3}

                    >

                        {

                            data.map((entry, index) => (

                                <Cell

                                    key={index}

                                    fill={COLORS[index % COLORS.length]}

                                />

                            ))

                        }

                    </Pie>

                    <Tooltip />

                    <Legend />

                </PieChart>

            </ResponsiveContainer>

        </div>

    );

}