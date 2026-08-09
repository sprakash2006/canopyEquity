import "./Hero.css";

import MapCard from "../Map/MapCard";
import AICommandCenter from "../AICommandCenter/AICommandCenter";

export default function Hero({
    ai,
    backendStatus
}) {

    return (

        <section className="hero">

            {/* =================================================
                GIS INTELLIGENCE
            ================================================= */}

            <div className="hero-left">

                <div className="hero-panel-label">

                    <span className="hero-panel-status" />

                    GIS INTELLIGENCE

                </div>

                <MapCard />

            </div>


            {/* =================================================
                AI COMMAND CENTER
            ================================================= */}

            <div className="hero-right">

                <div className="hero-panel-label">

                    <span className="hero-ai-indicator" />

                    AI COMMAND CENTER

                </div>

                <AICommandCenter
                    ai={ai}
                    backendStatus={backendStatus}
                />

            </div>

        </section>

    );

}