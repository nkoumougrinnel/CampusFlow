export default function RoomCard({ name, status, time }) {
  const isOccupied = status === 'occupied';

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 px-4 py-4 flex items-center justify-between">
      <div>
        <p className="font-bold text-gray-800 text-base">{name}</p>
        <p className="text-sm text-gray-500 mt-0.5">{time}</p>
      </div>

      <div className="flex flex-col items-center gap-1">
        <span
          className={`w-4 h-4 rounded-full shadow-sm ${
            isOccupied ? 'bg-red-500' : 'bg-green-500'
          }`}
          title={isOccupied ? 'Occupée' : 'Disponible'}
        />
        <span
          className={`text-[10px] font-semibold ${
            isOccupied ? 'text-red-500' : 'text-green-500'
          }`}
        >
          {isOccupied ? 'Occupée' : 'Libre'}
        </span>
      </div>
    </div>
  );
}
