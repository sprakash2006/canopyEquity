import "./ThresholdSlider.css";


export default function ThresholdSlider({
    value,
    onChange,
    opacity,
    onOpacityChange
}) {

    return (

        <div className="threshold-panel">

            <div className="threshold-header">
                <span className="material-symbols-outlined">tune</span>
                <h4>Impact Heatmap</h4>
            </div>


            {/* Vertical thermometer — gradient bar + slider running
                along it. Red top (high impact), green bottom (low). */}
            <div className="thermometer">

                <div className="thermometer-labels">
                    <span>100</span>
                    <span>75</span>
                    <span>50</span>
                    <span>25</span>
                    <span>0</span>
                </div>

                <div className="thermometer-bar-wrap">
                    <div className="thermometer-bar" />

                    <input
                        type="range"
                        className="thermometer-slider"
                        min="0"
                        max="100"
                        step="1"
                        value={value}
                        onChange={(e) =>
                            onChange(Number(e.target.value))
                        }
                        orient="vertical"
                        aria-label="Impact threshold"
                    />
                </div>

                <div className="thermometer-caption">
                    <span className="high">High</span>
                    <span className="value">
                        ≥ <strong>{value}</strong>
                    </span>
                    <span className="low">Low</span>
                </div>

            </div>


            {/* Opacity — secondary control below */}
            <div className="opacity-row">
                <label>
                    Opacity <strong>{Math.round(opacity * 100)}%</strong>
                </label>
                <input
                    type="range"
                    min="10"
                    max="100"
                    step="5"
                    value={opacity * 100}
                    onChange={(e) =>
                        onOpacityChange(
                            Number(e.target.value) / 100
                        )
                    }
                />
            </div>

        </div>

    );
}
