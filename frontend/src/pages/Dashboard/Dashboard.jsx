import "./Dashboard.css";
import { useEffect, useState } from "react";

import {
    getDashboard,
    getStatus
} from "../../services/api";

import KPICard from "../../components/KPICard/KPICard";
import Hero from "../../components/Hero/Hero";
import Analytics from "../../components/Analytics/Analytics";
import WardRanking from "../../components/WardRanking/WardRanking";
import Recommendation from "../../components/Recommendation/Recommendation";
import ProgressTracker from "../../components/Progress/ProgressTracker";

import {
    Trees,
    Leaf,
    Thermometer,
    Coins,
    Globe,
    Target
} from "lucide-react";

export default function Dashboard() {

    const [summary, setSummary] = useState({});

    const [dashboard, setDashboard] = useState([]);

    const [recommendations, setRecommendations] = useState([]);
    const [ai, setAI] = useState({});

    const [loading, setLoading] = useState(true);

    const [backendStatus, setBackendStatus] = useState("Offline");

    // ==========================================================
    // LOAD DASHBOARD
    // ==========================================================

    const loadDashboard = async () => {

        try {

            const status = await getStatus();

            if (status.status === 200) {

                setBackendStatus("Online");

            }

            const response = await getDashboard();

            console.log("========== DASHBOARD RESPONSE ==========");
console.log("FULL RESPONSE:", response.data);
console.log("SUMMARY:", response.data.summary);
console.log("DASHBOARD:", response.data.dashboard);
console.log("RECOMMENDATIONS:", response.data.recommendations);
console.log("=======================================");

            setSummary(

                response.data.summary || {}

            );

            setDashboard(

                response.data.dashboard || []

            );

            setRecommendations(

                response.data.recommendations || []

            );
            setAI(

    response.data.ai || {}

);

        }

        catch (error) {

            console.error(error);

            setBackendStatus("Offline");

        }

        finally {

            setLoading(false);

        }

    };

    // ==========================================================
    // INITIAL LOAD
    // ==========================================================

    useEffect(() => {

        loadDashboard();

        // Refresh every 10 sec
        const interval = setInterval(

            loadDashboard,

            10000

        );

        return () => clearInterval(interval);

    }, []);

    // ==========================================================
    // FORMAT SCORE
    // ==========================================================

    const score = (value) => {

        if (value === undefined || value === null)

            return "--";

        return Number(value).toFixed(2);

    };

    return (

        <div className="dashboard">

            {/* ================= KPI ================= */}

            <section className="kpi-grid">

                <KPICard

                    title="Total Wards"

                    value={

                        loading

                            ? "..."

                            : summary.total_wards ?? "--"

                    }

                    subtitle="Analyzed"

                    icon={<Trees size={26}/>}

                    color="#22c55e"

                />

                <KPICard

                    title="Top Ward"

                    value={

                        loading

                            ? "..."

                            : summary.top_ward ?? "--"

                    }

                    subtitle="Highest Priority"

                    icon={<Leaf size={26}/>}

                    color="#16a34a"

                />

                <KPICard

                    title="Highest Score"

                    value={

                        loading

                            ? "..."

                            : score(summary.highest_score)

                    }

                    subtitle="Maximum Impact"

                    icon={<Thermometer size={26}/>}

                    color="#f97316"

                />

                <KPICard

                    title="Average Score"

                    value={

                        loading

                            ? "..."

                            : score(summary.average_score)

                    }

                    subtitle="City Average"

                    icon={<Coins size={26}/>}

                    color="#3b82f6"

                />

                <KPICard

                    title="Lowest Score"

                    value={

                        loading

                            ? "..."

                            : score(summary.lowest_score)

                    }

                    subtitle="Minimum Impact"

                    icon={<Globe size={26}/>}

                    color="#06b6d4"

                />

                <KPICard

                    title="Backend Status"

                    value={backendStatus}

                    subtitle="FastAPI"

                    icon={<Target size={26}/>}

                    color={

                        backendStatus === "Online"

                            ? "#22c55e"

                            : "#ef4444"

                    }

                />

            </section>

            {/* ================= HERO ================= */}
<Hero

    ai={ai}

    backendStatus={backendStatus}

/>

            {/* ================= ANALYTICS ================= */}

            <Analytics

                dashboard={dashboard}

                summary={summary}

            />

            {/* ================= BOTTOM ================= */}

            <section className="bottom-grid">

                <WardRanking

                    wards={dashboard}

                />

                <Recommendation

                    recommendations={recommendations}

                />

            </section>

            {/* ================= PIPELINE ================= */}

            <ProgressTracker />

        </div>

    );

}