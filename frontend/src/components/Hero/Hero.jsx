import "./Hero.css";

import MapCard from "../Map/MapCard";
import AICommandCenter from "../AICommandCenter/AICommandCenter";

export default function Hero({

    ai,

    backendStatus

}) {

    return (

        <section className="hero">

            <div className="hero-left">

                <MapCard />

            </div>

            <div className="hero-right">

                <AICommandCenter

                    ai={ai}

                    backendStatus={backendStatus}

                />

            </div>

        </section>

    );

}