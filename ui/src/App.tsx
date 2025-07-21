import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { NodesView } from './components/NodesView';
import { MemoryView } from './components/MemoryView';
import { MissionsView } from './components/MissionsView';
import { SettingsView } from './components/SettingsView';
import { WebSocketProvider } from './contexts/WebSocketContext';
import './App.css';

export type ViewType = 'dashboard' | 'nodes' | 'memory' | 'missions' | 'settings';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'nodes':
        return <NodesView />;
      case 'memory':
        return <MemoryView />;
      case 'missions':
        return <MissionsView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <WebSocketProvider>
      <div className="flex h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Sidebar */}
        <Sidebar 
          currentView={currentView}
          onViewChange={setCurrentView}
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header 
            currentView={currentView}
            onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
          />
          
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-mesh">
            <div className="container mx-auto px-6 py-8">
              {renderView()}
            </div>
          </main>
        </div>
      </div>
    </WebSocketProvider>
  );
}

export default App;
