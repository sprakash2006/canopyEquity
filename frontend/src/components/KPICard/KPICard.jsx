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

}){

    return(

        <motion.div

            className="kpi-card"

            whileHover={{

                y:-8,

                scale:1.02

            }}

            transition={{

                duration:.25

            }}

        >

            <div className="kpi-top">

                <div

                    className="icon-box"

                    style={{

                        background:color

                    }}

                >

                    {icon}

                </div>

                {

                    trend &&

                    <div className="trend">

                        {trend}

                    </div>

                }

            </div>

            <h4>

                {title}

            </h4>

            {

                loading ?

                (

                    <div className="loading"/>

                )

                :

                (

                    <h2>

                        {value}

                    </h2>

                )

            }

            <p>

                {subtitle}

            </p>

        </motion.div>

    )

}