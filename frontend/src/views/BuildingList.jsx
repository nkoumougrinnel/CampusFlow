// src/views/BuildingList.jsx

import RoomCard from '../components/RoomCard';

const ROOMS = [
  { id: 1, name: 'Salle C17', status: 'occupied', time: 'occupée dans 1h' },
  { id: 2, name: 'Salle C16', status: 'available', time: 'libre maintenant' },
  { id: 3, name: 'Amphi A', status: 'occupied', time: 'occupée dans 1h' },
  { id: 4, name: 'Salle B04', status: 'available', time: "libre jusqu'à 15h" },
  { id: 5, name: 'Salle B12', status: 'occupied', time: 'occupée dans 30 min' },
];

export default function BuildingList() {
  return (
    <div className="flex-1 overflow-y-auto bg-gray-100 px-4 py-5">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Batiments disponibles</h2>

      {/* Liste verticale de RoomCard */}
      <div className="flex flex-col gap-3">
        {ROOMS.map((room) => (
          <RoomCard
            key={room.id}
            name={room.name}
            status={room.status}
            time={room.time}
          />
        ))}
      </div>
    </div>
  );
}
