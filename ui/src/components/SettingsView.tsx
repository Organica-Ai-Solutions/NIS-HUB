import React, { useState } from 'react';
import { 
  CogIcon, 
  ServerIcon, 
  ShieldCheckIcon, 
  BellIcon,
  ChartBarIcon,
  WifiIcon,
  CheckIcon 
} from '@heroicons/react/24/outline';

export const SettingsView: React.FC = () => {
  const [settings, setSettings] = useState({
    system: {
      heartbeatInterval: 30,
      maxNodes: 100,
      memoryRetention: 30,
      autoBackup: true,
      debugMode: false,
    },
    security: {
      requireAuth: true,
      tokenExpiry: 24,
      maxFailedAttempts: 5,
      encryptMemory: true,
    },
    notifications: {
      nodeDisconnect: true,
      memoryFull: true,
      missionComplete: true,
      criticalErrors: true,
    },
    performance: {
      maxConcurrentTasks: 10,
      memoryBufferSize: 1000,
      networkTimeout: 30,
      compressionEnabled: true,
    }
  });

  const handleSettingChange = (category: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value
      }
    }));
  };

  const handleSave = () => {
    // Here you would typically send the settings to your backend
    console.log('Saving settings:', settings);
    // Show success message
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Settings</h1>
          <p className="text-slate-400">Configure your NIS HUB system preferences</p>
        </div>
        <button onClick={handleSave} className="button-primary flex items-center space-x-2">
          <CheckIcon className="h-4 w-4" />
          <span>Save Changes</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <CogIcon className="h-5 w-5 text-nis-blue-400" />
              <h3 className="text-lg font-semibold text-white">System Configuration</h3>
            </div>
          </div>
          <div className="card-content space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Heartbeat Interval (seconds)
              </label>
              <input
                type="number"
                value={settings.system.heartbeatInterval}
                onChange={(e) => handleSettingChange('system', 'heartbeatInterval', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                min="10"
                max="300"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Maximum Nodes
              </label>
              <input
                type="number"
                value={settings.system.maxNodes}
                onChange={(e) => handleSettingChange('system', 'maxNodes', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                min="1"
                max="1000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Memory Retention (days)
              </label>
              <input
                type="number"
                value={settings.system.memoryRetention}
                onChange={(e) => handleSettingChange('system', 'memoryRetention', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                min="1"
                max="365"
              />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">Auto Backup</span>
              <button
                onClick={() => handleSettingChange('system', 'autoBackup', !settings.system.autoBackup)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                  settings.system.autoBackup ? 'bg-nis-blue-600' : 'bg-slate-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    settings.system.autoBackup ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">Debug Mode</span>
              <button
                onClick={() => handleSettingChange('system', 'debugMode', !settings.system.debugMode)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                  settings.system.debugMode ? 'bg-nis-blue-600' : 'bg-slate-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    settings.system.debugMode ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <ShieldCheckIcon className="h-5 w-5 text-emerald-400" />
              <h3 className="text-lg font-semibold text-white">Security & Authentication</h3>
            </div>
          </div>
          <div className="card-content space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">Require Authentication</span>
              <button
                onClick={() => handleSettingChange('security', 'requireAuth', !settings.security.requireAuth)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                  settings.security.requireAuth ? 'bg-emerald-600' : 'bg-slate-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    settings.security.requireAuth ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Token Expiry (hours)
              </label>
              <input
                type="number"
                value={settings.security.tokenExpiry}
                onChange={(e) => handleSettingChange('security', 'tokenExpiry', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                min="1"
                max="168"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Max Failed Attempts
              </label>
              <input
                type="number"
                value={settings.security.maxFailedAttempts}
                onChange={(e) => handleSettingChange('security', 'maxFailedAttempts', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                min="1"
                max="10"
              />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">Encrypt Memory</span>
              <button
                onClick={() => handleSettingChange('security', 'encryptMemory', !settings.security.encryptMemory)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                  settings.security.encryptMemory ? 'bg-emerald-600' : 'bg-slate-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    settings.security.encryptMemory ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <BellIcon className="h-5 w-5 text-yellow-400" />
              <h3 className="text-lg font-semibold text-white">Notifications</h3>
            </div>
          </div>
          <div className="card-content space-y-4">
            {Object.entries(settings.notifications).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-300 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </span>
                <button
                  onClick={() => handleSettingChange('notifications', key, !value)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                    value ? 'bg-yellow-600' : 'bg-slate-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                      value ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="h-5 w-5 text-nis-purple-400" />
              <h3 className="text-lg font-semibold text-white">Performance</h3>
            </div>
          </div>
          <div className="card-content space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Max Concurrent Tasks
              </label>
              <input
                type="number"
                value={settings.performance.maxConcurrentTasks}
                onChange={(e) => handleSettingChange('performance', 'maxConcurrentTasks', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                min="1"
                max="100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Memory Buffer Size
              </label>
              <input
                type="number"
                value={settings.performance.memoryBufferSize}
                onChange={(e) => handleSettingChange('performance', 'memoryBufferSize', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                min="100"
                max="10000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Network Timeout (seconds)
              </label>
              <input
                type="number"
                value={settings.performance.networkTimeout}
                onChange={(e) => handleSettingChange('performance', 'networkTimeout', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                min="5"
                max="300"
              />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">Compression Enabled</span>
              <button
                onClick={() => handleSettingChange('performance', 'compressionEnabled', !settings.performance.compressionEnabled)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                  settings.performance.compressionEnabled ? 'bg-nis-purple-600' : 'bg-slate-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    settings.performance.compressionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center space-x-2">
            <ServerIcon className="h-5 w-5 text-slate-400" />
            <h3 className="text-lg font-semibold text-white">System Information</h3>
          </div>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium text-slate-300 mb-2">Version</h4>
              <p className="text-slate-400">NIS HUB v1.0.0</p>
            </div>
            <div>
              <h4 className="font-medium text-slate-300 mb-2">Uptime</h4>
              <p className="text-slate-400">2 days, 4 hours</p>
            </div>
            <div>
              <h4 className="font-medium text-slate-300 mb-2">Memory Usage</h4>
              <p className="text-slate-400">1.2 GB / 8.0 GB</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 