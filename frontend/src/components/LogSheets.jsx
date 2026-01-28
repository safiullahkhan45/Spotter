import './LogSheets.css';

const LogSheets = ({ logSheets }) => {
  return (
    <div className="log-sheets">
      {logSheets.map((log, index) => (
        <LogSheet key={log.id || index} logData={log} />
      ))}
    </div>
  );
};

const LogSheet = ({ logData }) => {
  const STATUS_COLORS = {
    'OFF_DUTY': '#4CAF50',
    'SLEEPER_BERTH': '#2196F3',
    'DRIVING': '#FFC107',
    'ON_DUTY': '#FF5722'
  };

  const renderTimeline = () => {
    const hours = Array.from({ length: 24 }, (_, i) => i);

    return (
      <div className="timeline-grid">
        {/* Hour labels at top */}
        <div className="timeline-hours-row">
          <div className="timeline-label-cell"></div>
          <div className="timeline-hours-container">
            {hours.map(hour => (
              <div key={hour} className="hour-label">
                {hour === 0 ? 'M' : hour === 12 ? 'N' : hour}
              </div>
            ))}
          </div>
        </div>

        {/* Vertical grid lines */}
        <div className="vertical-grid-lines">
          {hours.map(hour => (
            <div key={hour} className="grid-line" style={{ left: `${(hour / 24) * 100}%` }} />
          ))}
        </div>

        {/* Status rows with connecting lines */}
        <div className="timeline-row">
          <div className="row-label">1. Off Duty</div>
          <div className="row-timeline">
            {renderStatusLine(logData.timeline_data, 'OFF_DUTY')}
          </div>
        </div>

        <div className="timeline-row">
          <div className="row-label">2. Sleeper Berth</div>
          <div className="row-timeline">
            {renderStatusLine(logData.timeline_data, 'SLEEPER_BERTH')}
          </div>
        </div>

        <div className="timeline-row">
          <div className="row-label">3. Driving</div>
          <div className="row-timeline">
            {renderStatusLine(logData.timeline_data, 'DRIVING')}
          </div>
        </div>

        <div className="timeline-row">
          <div className="row-label">4. On Duty (Not Driving)</div>
          <div className="row-timeline">
            {renderStatusLine(logData.timeline_data, 'ON_DUTY')}
          </div>
        </div>

        {/* Hour labels at bottom */}
        <div className="timeline-hours-row bottom">
          <div className="timeline-label-cell"></div>
          <div className="timeline-hours-container">
            {hours.map(hour => (
              <div key={hour} className="hour-label">
                {hour === 0 ? 'M' : hour === 12 ? 'N' : hour}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderStatusLine = (timeline, status) => {
    const statusEntries = timeline.filter(entry => entry.status === status);

    if (statusEntries.length === 0) return null;

    // Create SVG path for connecting line graph
    const segments = [];

    statusEntries.forEach((entry, idx) => {
      const startX = (entry.start_hour / 24) * 100;
      const endX = ((entry.start_hour + entry.duration) / 24) * 100;

      segments.push(
        <g key={idx}>
          {/* Filled rectangle for active period */}
          <rect
            x={`${startX}%`}
            y="0"
            width={`${(entry.duration / 24) * 100}%`}
            height="100%"
            fill={STATUS_COLORS[status]}
            fillOpacity="0.3"
            stroke={STATUS_COLORS[status]}
            strokeWidth="2"
          />
          {/* Bold line at middle of active period */}
          <line
            x1={`${startX}%`}
            y1="50%"
            x2={`${endX}%`}
            y2="50%"
            stroke={STATUS_COLORS[status]}
            strokeWidth="3"
          />
          {/* Tooltip text */}
          <title>{entry.description} ({entry.duration.toFixed(1)}hrs)</title>
        </g>
      );
    });

    return (
      <svg className="status-line-svg" width="100%" height="100%" preserveAspectRatio="none">
        {segments}
      </svg>
    );
  };

  return (
    <div className="log-sheet">
      <div className="log-header">
        <div className="log-title">
          <h3>Day {logData.day_number} - {new Date(logData.date).toLocaleDateString()}</h3>
        </div>
        <div className="log-info">
          <div className="info-row">
            <span><strong>Driver:</strong> {logData.driver_name}</span>
            <span><strong>Carrier:</strong> {logData.carrier_name}</span>
          </div>
          <div className="info-row">
            <span><strong>Vehicle:</strong> {logData.vehicle_number || 'N/A'}</span>
            <span><strong>Total Miles:</strong> {logData.total_miles?.toFixed(1) || 0} miles</span>
          </div>
        </div>
      </div>

      {/* Timeline Graph */}
      <div className="log-graph">
        {renderTimeline()}
      </div>

      {/* Daily Totals */}
      <div className="log-totals">
        <div className="total-item">
          <span className="total-label">Off Duty:</span>
          <span className="total-value">{logData.total_off_duty_hours?.toFixed(1)} hrs</span>
        </div>
        <div className="total-item">
          <span className="total-label">Sleeper Berth:</span>
          <span className="total-value">{logData.total_sleeper_berth_hours?.toFixed(1)} hrs</span>
        </div>
        <div className="total-item">
          <span className="total-label">Driving:</span>
          <span className="total-value">{logData.total_driving_hours?.toFixed(1)} hrs</span>
        </div>
        <div className="total-item">
          <span className="total-label">On Duty:</span>
          <span className="total-value">{logData.total_on_duty_hours?.toFixed(1)} hrs</span>
        </div>
      </div>

      {/* Remarks */}
      {logData.remarks && (
        <div className="log-remarks">
          <strong>Remarks:</strong> {logData.remarks}
        </div>
      )}
    </div>
  );
};

export default LogSheets;
