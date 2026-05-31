import { useState } from 'react';
import Navbar from './components/Navbar';
import BottomNavigationBar from './components/BottomNavigationBar';
import MapView from './views/MapView';
import BuildingList from './views/BuildingList';

function getNavbarView(screen) {
  if (screen === 5) return 'back';
  if (screen >= 3) return 'profile';
  return 'default';
}

export default function App() {
  const [currentScreen, setCurrentScreen] = useState(1);

  return (
    <div className="flex justify-center items-start min-h-screen bg-gray-200">
      <div className="relative w-full max-w-[430px] h-screen flex flex-col bg-white overflow-hidden shadow-2xl">
        <Navbar
          view={getNavbarView(currentScreen)}
          onBack={() => setCurrentScreen(1)}
        />

        <main className="flex-1 flex flex-col overflow-hidden pb-16">
          {currentScreen <= 4 ? (
            <MapView
              currentScreen={currentScreen}
              setCurrentScreen={setCurrentScreen}
            />
          ) : (
            <BuildingList />
          )}
        </main>

        <BottomNavigationBar
          currentScreen={currentScreen}
          setCurrentScreen={setCurrentScreen}
        />
      </div>
    </div>
  );
}
