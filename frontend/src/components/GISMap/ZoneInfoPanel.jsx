import "./ZoneInfoPanel.css";


const PRIORITY_COLORS = {
    "VERY HIGH": "var(--risk-veryhigh)",
    "HIGH":      "var(--risk-high)",
    "MEDIUM":    "var(--risk-moderate)",
    "LOW":       "#7fa38f",
    "VERY LOW":  "var(--risk-low)"
};


export default function ZoneInfoPanel({ zone, onClose }) {

    if (!zone) return null;

    const p = zone.properties || {};

    const priority = p.priority || "-";
    const priorityColor = PRIORITY_COLORS[priority] || "var(--text-muted)";


    return (

        <div className="zone-info-panel">

            <div className="zone-panel-header">

                <div>
                    <div className="zone-panel-label">Selected Zone</div>
                    <h3>{p.zone_id || "Zone"}</h3>
                </div>

                <button
                    className="zone-close-btn"
                    onClick={onClose}
                    aria-label="Deselect zone"
                >
                    <span className="material-symbols-outlined">close</span>
                </button>

            </div>


            <div
                className="zone-priority-chip"
                style={{ background: priorityColor }}
            >
                {priority} priority
            </div>


            <div className="zone-stats-grid">

                <div className="zone-stat">
                    <span>Mean Impact</span>
                    <strong>{Number(p.impact_mean || 0).toFixed(1)}</strong>
                </div>

                <div className="zone-stat">
                    <span>Max Impact</span>
                    <strong>{Number(p.impact_max || 0).toFixed(1)}</strong>
                </div>

                <div className="zone-stat">
                    <span>Std Dev</span>
                    <strong>{Number(p.impact_std || 0).toFixed(1)}</strong>
                </div>

                <div className="zone-stat">
                    <span>Pixels</span>
                    <strong>{Number(p.impact_count || 0).toLocaleString()}</strong>
                </div>

            </div>


            <div className="zone-panel-footnote">
                {Number(p.impact_max || 0) === 0 ? (
                    <>
                        <strong>No plantation opportunity</strong> in this
                        zone — every pixel scored 0 (likely dense built-up
                        or unplantable land). Heatmap renders solid green.
                    </>
                ) : (
                    "Pixel-level heatmap enabled for this zone."
                )}
            </div>

        </div>

    );
}
