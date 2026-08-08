import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip,
    Legend
} from "recharts";

const COLORS = [
    "#22c55e",
    "#f59e0b",
    "#ef4444",
    "#3b82f6",
    "#8b5cf6"
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

                background: "#131d2f",

                borderRadius: "24px",

                padding: "25px",

                height: "360px",

                border: "1px solid rgba(255,255,255,.05)"

            }}

        >

            <h2

                style={{

                    color: "white"

                }}

            >

                Ward Priority Distribution

            </h2>

            <p

                style={{

                    color: "#94a3b8",

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