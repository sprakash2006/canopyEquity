import "./Legend.css";

export default function Legend(){

    return(

        <div className="legend">

            <h3>Priority</h3>

            <div><span className="veryhigh"></span>Very High</div>

            <div><span className="high"></span>High</div>

            <div><span className="medium"></span>Medium</div>

            <div><span className="low"></span>Low</div>

            <div><span className="verylow"></span>Very Low</div>

        </div>

    )

}