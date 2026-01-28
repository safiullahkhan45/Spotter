import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './RouteMap.css';

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const RouteMap = ({ routeData }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current || !routeData?.locations) return;

    // Initialize map if not already done
    if (!mapInstanceRef.current) {
      mapInstanceRef.current = L.map(mapRef.current).setView([39.8283, -98.5795], 5); // Center of USA

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstanceRef.current);
    }

    const map = mapInstanceRef.current;

    // Clear existing layers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        map.removeLayer(layer);
      }
    });

    const { current, pickup, dropoff } = routeData.locations;

    // Add markers if coordinates are available
    const markers = [];
    if (current?.coordinates) {
      const marker = L.marker(current.coordinates)
        .bindPopup(`<b>Current Location</b><br/>${current.name}`)
        .addTo(map);
      markers.push(marker);
    }

    if (pickup?.coordinates) {
      const marker = L.marker(pickup.coordinates)
        .bindPopup(`<b>Pickup</b><br/>${pickup.name}`)
        .addTo(map);
      markers.push(marker);
    }

    if (dropoff?.coordinates) {
      const marker = L.marker(dropoff.coordinates)
        .bindPopup(`<b>Dropoff</b><br/>${dropoff.name}`)
        .addTo(map);
      markers.push(marker);
    }

    // Draw route if geometry is available
    if (routeData.geometry?.coordinates) {
      const coords = routeData.geometry.coordinates.map(coord => [coord[1], coord[0]]);
      L.polyline(coords, { color: '#1a73e8', weight: 4 }).addTo(map);
    }

    // Fit bounds to show all markers
    if (markers.length > 0) {
      const group = L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.1));
    }

  }, [routeData]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div className="route-map-container">
      <div ref={mapRef} className="route-map" />
      <div className="route-info">
        <p><strong>📍 Current:</strong> {routeData.locations?.current?.name}</p>
        <p><strong>📦 Pickup:</strong> {routeData.locations?.pickup?.name}</p>
        <p><strong>🎯 Dropoff:</strong> {routeData.locations?.dropoff?.name}</p>
        {routeData.estimated && (
          <p className="estimated-notice">
            ⚠️ Route coordinates unavailable - using estimated distance
          </p>
        )}
      </div>
    </div>
  );
};

export default RouteMap;
