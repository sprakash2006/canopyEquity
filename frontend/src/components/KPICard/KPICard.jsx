import "./KPICard.css";
import { motion } from "framer-motion";

export default function KPICard({
    title,
    value,
    subtitle,
    icon,
    color = "#22c55e",
    loading = false,
    trend = null
}) {

    return (

        <motion.div

            className="kpi-card"

            style={{
                "--kpi-accent": color
            }}

            whileHover={{
                y: -3
            }}

            transition={{
                duration: 0.18
            }}

        >

            {/* =================================================
                TOP ROW
            ================================================= */}

            <div className="kpi-top">

                <div className="icon-box">

                    {icon}

                </div>


                {trend && (

                    <div className="trend">

                        {trend}

                    </div>

                )}

            </div>


            {/* =================================================
                TITLE
            ================================================= */}

            <h4>
                {title}
            </h4>


            {/* =================================================
                VALUE
            ================================================= */}

            {loading ? (

                <div className="loading" />

            ) : (

                <h2>
                    {value}
                </h2>

            )}


            {/* =================================================
                SUBTITLE
            ================================================= */}

            <p>
                {subtitle}
            </p>


            {/* =================================================
                ACCENT
            ================================================= */}

            <div className="kpi-accent-line" />

        </motion.div>

    );

}