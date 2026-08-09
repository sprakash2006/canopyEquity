import "./Hero.css";

import MapCard from "../Map/MapCard";
import AICommandCenter from "../AICommandCenter/AICommandCenter";


export default function Hero({

    ai,

    backendStatus,

    showCommandCenter = true

}) {

    return (

        <section className="hero">


            {/* ==================================================
                GIS MAP
            ================================================== */}

            <div
                className={
                    showCommandCenter
                        ? "hero-left"
                        : "hero-left hero-full"
                }
            >

                <MapCard />

            </div>


            {/* ==================================================
                AI COMMAND CENTER
            ================================================== */}

            {showCommandCenter && (

                <div className="hero-right">

                    <AICommandCenter

                        ai={ai}

                        backendStatus={
                            backendStatus
                        }

                    />

                </div>

            )}

        </section>

    );

}