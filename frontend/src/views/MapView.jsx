import CampusMap from '../components/CampusMap';
import ItineraryPanel from '../components/ItineraryPanel';

export default function MapView({ currentScreen, setCurrentScreen }) {
  return (
    <div className="relative flex-1 overflow-hidden">
      <div className="absolute inset-0">
        <CampusMap currentScreen={currentScreen} />
      </div>

      {currentScreen === 1 && (
        <div className="absolute top-4 left-4 right-4 z-[400] flex gap-2 pointer-events-auto">
          <button
            onClick={() => setCurrentScreen(2)}
            className="flex-1 flex items-center gap-2 bg-white rounded-2xl shadow-md px-4 py-3 text-sm text-gray-500 hover:shadow-lg transition"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0088fe" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
            <span className="text-gray-600 font-medium">Chercher</span>
            <span className="ml-auto text-[#0088fe]">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
              </svg>
            </span>
          </button>

          <button className="bg-[#0088fe] text-white rounded-2xl shadow-md px-4 py-3 text-sm font-semibold hover:bg-blue-600 transition whitespace-nowrap flex items-center gap-1">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="4" y1="6" x2="20" y2="6" />
              <line x1="8" y1="12" x2="16" y2="12" />
              <line x1="11" y1="18" x2="13" y2="18" />
            </svg>
            Filtre
          </button>
        </div>
      )}

      {(currentScreen === 3 || currentScreen === 4) && (
        <ItineraryPanel />
      )}

      {(currentScreen === 1 || currentScreen === 2) && (
        <div className="absolute top-20 left-0 right-0 text-center z-[300] pointer-events-none">
          <h2 className="text-lg font-bold text-gray-800 drop-shadow-sm">Carte du Campus</h2>
          <p className="text-xs text-gray-500">Vue interactive</p>
        </div>
      )}

      <button
        onClick={() => setCurrentScreen((s) => Math.min(s + 1, 5))}
        className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[400] bg-white/90 rounded-full p-2 shadow-md hover:shadow-lg transition pointer-events-auto"
        aria-label="Écran suivant"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0088fe" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>
    </div>
  );
}
