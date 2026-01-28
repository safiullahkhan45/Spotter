import { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import './TripForm.css';

const TripForm = ({ onTripCalculated, onError, onLoading }) => {
  const [formData, setFormData] = useState({
    current_location: '',
    pickup_location: '',
    dropoff_location: '',
    current_cycle_hours: 0,
    driver_name: '',
    carrier_name: '',
    vehicle_number: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'current_cycle_hours' ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    onLoading(true);
    onError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/trips/`, formData);
      onTripCalculated(response.data);
    } catch (error) {
      const errorMessage = error.response?.data?.error ||
                          error.response?.data?.message ||
                          error.message ||
                          'Failed to calculate trip. Please try again.';
      onError(errorMessage);
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="trip-form">
      <h2>🚚 Trip Details</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="current_location">
              Current Location
              <span className="required">*</span>
            </label>
            <input
              type="text"
              id="current_location"
              name="current_location"
              value={formData.current_location}
              onChange={handleChange}
              required
              placeholder="e.g., Richmond, VA"
            />
          </div>

          <div className="form-group">
            <label htmlFor="pickup_location">
              Pickup Location
              <span className="required">*</span>
            </label>
            <input
              type="text"
              id="pickup_location"
              name="pickup_location"
              value={formData.pickup_location}
              onChange={handleChange}
              required
              placeholder="e.g., Baltimore, MD"
            />
          </div>

          <div className="form-group">
            <label htmlFor="dropoff_location">
              Dropoff Location
              <span className="required">*</span>
            </label>
            <input
              type="text"
              id="dropoff_location"
              name="dropoff_location"
              value={formData.dropoff_location}
              onChange={handleChange}
              required
              placeholder="e.g., Newark, NJ"
            />
          </div>

          <div className="form-group">
            <label htmlFor="current_cycle_hours">
              Current Cycle Hours Used (0-70)
              <span className="required">*</span>
            </label>
            <input
              type="number"
              id="current_cycle_hours"
              name="current_cycle_hours"
              value={formData.current_cycle_hours}
              onChange={handleChange}
              required
              min="0"
              max="70"
              step="0.5"
            />
            <small>Hours already used in your 8-day cycle</small>
          </div>

          <div className="form-group">
            <label htmlFor="driver_name">Driver Name</label>
            <input
              type="text"
              id="driver_name"
              name="driver_name"
              value={formData.driver_name}
              onChange={handleChange}
              placeholder="e.g., John Doe"
            />
          </div>

          <div className="form-group">
            <label htmlFor="carrier_name">Carrier Name</label>
            <input
              type="text"
              id="carrier_name"
              name="carrier_name"
              value={formData.carrier_name}
              onChange={handleChange}
              placeholder="e.g., ABC Trucking"
            />
          </div>

          <div className="form-group">
            <label htmlFor="vehicle_number">Vehicle Number</label>
            <input
              type="text"
              id="vehicle_number"
              name="vehicle_number"
              value={formData.vehicle_number}
              onChange={handleChange}
              placeholder="e.g., TRUCK-123"
            />
          </div>
        </div>

        <button type="submit" className="submit-button">
          Calculate Trip & Generate ELD Logs
        </button>
      </form>
    </div>
  );
};

export default TripForm;
