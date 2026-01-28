import { useState } from 'react';
import './App.css';
import TripForm from './components/TripForm';
import RouteMap from './components/RouteMap';
import LogSheets from './components/LogSheets';

function App() {
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTripCalculated = (data) => {
    setTripData(data);
    setError(null);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setTripData(null);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚛 FMCSA ELD Trip Planner</h1>
        <p>Hours of Service Compliant Route Planning & Electronic Logging</p>
      </header>

      <main className="app-main">
        <div className="container">
          {/* Trip Input Form */}
          <section className="section">
            <TripForm
              onTripCalculated={handleTripCalculated}
              onError={handleError}
              onLoading={handleLoading}
            />
          </section>

          {/* Error Display */}
          {error && (
            <section className="section error-section">
              <div className="error-message">
                <strong>⚠️ Error:</strong> {error}
              </div>
            </section>
          )}

          {/* Loading State */}
          {loading && (
            <section className="section">
              <div className="loading">
                <div className="spinner"></div>
                <p>Calculating route and HOS compliance...</p>
              </div>
            </section>
          )}

          {/* Results */}
          {tripData && !loading && (
            <>
              {/* Trip Summary */}
              <section className="section">
                <h2>📊 Trip Summary</h2>
                <div className="trip-summary">
                  <div className="summary-card">
                    <div className="summary-label">Total Distance</div>
                    <div className="summary-value">
                      {tripData.total_distance_miles?.toFixed(1)} miles
                    </div>
                  </div>
                  <div className="summary-card">
                    <div className="summary-label">Driving Hours</div>
                    <div className="summary-value">
                      {tripData.total_driving_hours?.toFixed(1)} hrs
                    </div>
                  </div>
                  <div className="summary-card">
                    <div className="summary-label">Total On-Duty</div>
                    <div className="summary-value">
                      {tripData.total_on_duty_hours?.toFixed(1)} hrs
                    </div>
                  </div>
                  <div className="summary-card">
                    <div className="summary-label">Days Required</div>
                    <div className="summary-value">
                      {tripData.num_days_required} day{tripData.num_days_required > 1 ? 's' : ''}
                    </div>
                  </div>
                </div>

                {/* Compliance Status */}
                <div className={`compliance-status ${tripData.is_compliant ? 'compliant' : 'non-compliant'}`}>
                  <strong>{tripData.is_compliant ? '✅' : '❌'}</strong>
                  {tripData.compliance_notes}
                </div>
              </section>

              {/* Route Map */}
              {tripData.route_data && (
                <section className="section">
                  <h2>🗺️ Route Map</h2>
                  <RouteMap routeData={tripData.route_data} />
                </section>
              )}

              {/* ELD Log Sheets */}
              {tripData.log_sheets && tripData.log_sheets.length > 0 && (
                <section className="section">
                  <h2>📋 ELD Log Sheets</h2>
                  <LogSheets logSheets={tripData.log_sheets} />
                </section>
              )}
            </>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>
          Built for FMCSA Hours of Service Compliance | 70hrs/8days Property Carrier
        </p>
      </footer>
    </div>
  );
}

export default App;
