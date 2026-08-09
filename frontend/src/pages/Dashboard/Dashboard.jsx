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
    Target,
    Activity,
    Sparkles
} from "lucide-react";


export default function Dashboard() {

    const [summary, setSummary] = useState({});

    const [dashboard, setDashboard] = useState([]);

    const [recommendations, setRecommendations] = useState([]);

    const [ai, setAI] = useState({});

    const [loading, setLoading] = useState(true);

    const [backendStatus, setBackendStatus] =
        useState("Offline");


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


            console.log(
                "========== DASHBOARD RESPONSE =========="
            );

            console.log(
                "FULL RESPONSE:",
                response.data
            );

            console.log(
                "SUMMARY:",
                response.data.summary
            );

            console.log(
                "DASHBOARD:",
                response.data.dashboard
            );

            console.log(
                "RECOMMENDATIONS:",
                response.data.recommendations
            );

            console.log(
                "========================================"
            );


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


        const interval = setInterval(
            loadDashboard,
            10000
        );


        return () =>
            clearInterval(interval);

    }, []);


    // ==========================================================
    // FORMAT SCORE
    // ==========================================================

    const score = (value) => {

        if (
            value === undefined ||
            value === null
        ) {

            return "--";

        }


        return Number(value).toFixed(2);

    };


    return (

        <div className="dashboard">


            {/* ==================================================
                PAGE INTRO
            ================================================== */}

            <section className="dashboard-intro">

                <div className="dashboard-intro-copy">

                    <div className="dashboard-eyebrow">

                        <Activity
                            size={13}
                            strokeWidth={2.2}
                        />

                        CITY INTELLIGENCE

                    </div>


                    <h1>
                        Urban Tree Intelligence
                    </h1>


                    <p>
                        AI-powered spatial analysis for
                        canopy equity and planting priorities.
                    </p>

                </div>


                <div className="dashboard-status">

                    <span className="dashboard-status-dot" />

                    <div>

                        <strong>
                            System Operational
                        </strong>

                        <span>
                            AI analysis services connected
                        </span>

                    </div>

                </div>

            </section>


            {/* ==================================================
                PRIMARY KPI
            ================================================== */}

            <section className="primary-kpi">

                <div className="primary-kpi-main">

                    <div className="primary-kpi-icon">

                        <Trees
                            size={22}
                            strokeWidth={2}
                        />

                    </div>


                    <div className="primary-kpi-content">

                        <span className="primary-kpi-label">
                            WARDS ANALYZED
                        </span>


                        <strong>

                            {loading
                                ? "..."
                                : summary.total_wards ?? "--"
                            }

                        </strong>


                        <span className="primary-kpi-description">
                            Urban areas processed by the AI pipeline
                        </span>

                    </div>

                </div>


                <div className="primary-kpi-divider" />


                <div className="primary-kpi-highlight">

                    <span>
                        TOP PRIORITY
                    </span>


                    <strong>

                        {loading
                            ? "..."
                            : summary.top_ward ?? "--"
                        }

                    </strong>


                    <small>
                        Highest impact area
                    </small>

                </div>


                <div className="primary-kpi-score">

                    <span>
                        MAX IMPACT
                    </span>


                    <strong>

                        {loading
                            ? "..."
                            : score(summary.highest_score)
                        }

                    </strong>


                    <small>
                        Priority score
                    </small>

                </div>

            </section>


            {/* ==================================================
                SECONDARY KPI GRID
            ================================================== */}

            <section className="secondary-kpi-grid">


                <div className="dashboard-kpi-wrapper">

                    <KPICard
                        title="Average Score"
                        value={
                            loading
                                ? "..."
                                : score(
                                    summary.average_score
                                )
                        }
                        subtitle="City Average"
                        icon={
                            <Coins size={23} />
                        }
                        color="#16a34a"
                    />

                </div>


                <div className="dashboard-kpi-wrapper">

                    <KPICard
                        title="Lowest Score"
                        value={
                            loading
                                ? "..."
                                : score(
                                    summary.lowest_score
                                )
                        }
                        subtitle="Minimum Impact"
                        icon={
                            <Globe size={23} />
                        }
                        color="#64748b"
                    />

                </div>


                <div className="dashboard-kpi-wrapper">

                    <KPICard
                        title="AI Engine"
                        value={
                            ai?.model ||
                            "SegFormer"
                        }
                        subtitle="Semantic Segmentation"
                        icon={
                            <Sparkles size={23} />
                        }
                        color="#15803d"
                    />

                </div>


                <div className="dashboard-kpi-wrapper">

                    <KPICard
                        title="Backend Status"
                        value={backendStatus}
                        subtitle="FastAPI"
                        icon={
                            <Target size={23} />
                        }
                        color={
                            backendStatus === "Online"
                                ? "#16a34a"
                                : "#ef4444"
                        }
                    />

                </div>

            </section>


            {/* ==================================================
                HERO / AI COMMAND CENTER
            ================================================== */}

            <section className="dashboard-hero-section">

                <div className="dashboard-section-heading">

                    <div>

                        <div className="section-eyebrow">

                            <Sparkles
                                size={13}
                            />

                            AI COMMAND CENTER

                        </div>


                        <h2>
                            Intelligence Overview
                        </h2>

                    </div>


                    <span className="section-live">

                        <span />

                        LIVE ANALYSIS

                    </span>

                </div>


                <Hero
                    ai={ai}
                    backendStatus={backendStatus}
                />

            </section>


            {/* ==================================================
                ANALYTICS
            ================================================== */}

            <section className="dashboard-analytics-section">

                <div className="dashboard-section-heading">

                    <div>

                        <div className="section-eyebrow">
                            SPATIAL INSIGHTS
                        </div>

                        <h2>
                            Impact Analytics
                        </h2>

                    </div>

                </div>


                <Analytics
                    dashboard={dashboard}
                    summary={summary}
                />

            </section>


            {/* ==================================================
                RANKING + RECOMMENDATIONS
            ================================================== */}

            <section className="dashboard-bottom-section">


                <div className="dashboard-panel">

                    <div className="dashboard-panel-header">

                        <div>

                            <span className="panel-eyebrow">
                                PRIORITY AREAS
                            </span>

                            <h2>
                                Ward Ranking
                            </h2>

                            <p>
                                Highest-impact locations identified by AI
                            </p>

                        </div>


                        <div className="panel-icon">

                            <Leaf
                                size={18}
                            />

                        </div>

                    </div>


                    <WardRanking
                        wards={dashboard}
                    />

                </div>


                <div className="dashboard-panel">

                    <div className="dashboard-panel-header">

                        <div>

                            <span className="panel-eyebrow">
                                AI DECISIONS
                            </span>

                            <h2>
                                Planting Recommendations
                            </h2>

                            <p>
                                Optimized interventions for priority zones
                            </p>

                        </div>


                        <div className="panel-icon recommendation-icon">

                            <Trees
                                size={18}
                            />

                        </div>

                    </div>


                    <Recommendation
                        recommendations={
                            recommendations
                        }
                    />

                </div>

            </section>


            {/* ==================================================
                AI PIPELINE
            ================================================== */}

            <section className="dashboard-pipeline-section">

                <div className="dashboard-section-heading">

                    <div>

                        <div className="section-eyebrow">
                            PROCESSING STATUS
                        </div>

                        <h2>
                            AI Pipeline
                        </h2>

                    </div>

                </div>


                <ProgressTracker />

            </section>


        </div>

    );

}