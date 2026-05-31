import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import { useEffect, useRef } from 'react';
import L from 'leaflet';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const CENTER = [3.8612, 11.5215];
const AMPHI_A_POS = [3.8620, 11.5220];
const ITINERARY_POINTS = [
  [3.8680, 11.5180],
  [3.8660, 11.5195],
  [3.8645, 11.5205],
  [3.8630, 11.5212],
  [3.8620, 11.5220],
];

function AutoOpenMarker({ position, currentScreen }) {
  const markerRef = useRef(null);

  useEffect(() => {
    if (currentScreen === 2 && markerRef.current) {
      markerRef.current.openPopup();
    }
  }, [currentScreen]);

  return (
    <Marker position={position} ref={markerRef}>
      <Popup closeButton={false} className="campus-popup">
        <div className="min-w-[180px] text-sm font-sans">
          <div className="flex items-center justify-between mb-2">
            <span className="font-bold text-gray-800 text-base">Amphi A</span>
            <span className="bg-red-500 text-white text-[10px] font-semibold px-2 py-0.5 rounded-full ml-2">
              Occupée
            </span>
          </div>
          <div className="space-y-1 text-gray-600">
            <div className="flex justify-between">
              <span>Capacité</span>
              <span className="font-medium text-gray-800">200 places</span>
            </div>
            <div className="flex justify-between">
              <span>Flux actuel</span>
              <span className="font-semibold text-red-500">187 étudiants</span>
            </div>
            <div className="flex justify-between">
              <span>Activité</span>
              <span className="font-medium text-gray-800">TP ITT1A</span>
            </div>
          </div>
        </div>
      </Popup>
    </Marker>
  );
}

function TimeBadge({ position }) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;
    const badge = L.marker(position, {
      icon: L.divIcon({
        className: '',
        html: `<div style="
          background:#0088fe;
          color:white;
          font-size:11px;
          font-weight:700;
          padding:3px 8px;
          border-radius:20px;
          white-space:nowrap;
          box-shadow:0 2px 6px rgba(0,136,254,0.5);
          font-family:sans-serif;
        ">14 min</div>`,
        iconAnchor: [24, 12],
      }),
    }).addTo(map);

    return () => map.removeLayer(badge);
  }, [map, position]);

  return null;
}

export default function CampusMap({ currentScreen }) {
  const midPoint = ITINERARY_POINTS[Math.floor(ITINERARY_POINTS.length / 2)];

  return (
    <div className="w-full h-full">
      <MapContainer
        center={CENTER}
        zoom={15}
        scrollWheelZoom={true}
        className="w-full h-full z-0"
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <AutoOpenMarker position={AMPHI_A_POS} currentScreen={currentScreen} />

        {currentScreen === 4 && (
          <>
            <Polyline
              positions={ITINERARY_POINTS}
              pathOptions={{ color: '#0088fe', weight: 5, opacity: 0.85 }}
            />
            <Marker
              position={ITINERARY_POINTS[0]}
              icon={L.divIcon({
                className: '',
                html: `<div style="width:14px;height:14px;background:#ef4444;border:2px solid white;border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>`,
                iconAnchor: [7, 7],
              })}
            />
            <Marker
              position={ITINERARY_POINTS[ITINERARY_POINTS.length - 1]}
              icon={L.divIcon({
                className: '',
                html: `<div style="width:14px;height:14px;background:#0088fe;border:2px solid white;border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>`,
                iconAnchor: [7, 7],
              })}
            />
            <TimeBadge position={midPoint} />
          </>
        )}
      </MapContainer>
    </div>
  );
}
