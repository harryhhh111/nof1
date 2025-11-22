import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Settings, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

export default function ConfigPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                Configuration
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <Settings className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {user?.username}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Trading Configuration
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Configure your trading preferences and exchange settings.
          </p>
        </div>

        {/* Configuration Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Exchange Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Exchange Settings</CardTitle>
              <CardDescription>
                Configure your exchange connections and API settings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Exchange configuration interface will be implemented here</p>
                <p className="text-sm">This will include:</p>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Hyperliquid API configuration</li>
                  <li>• Binance API settings</li>
                  <li>• Agent Wallet management</li>
                  <li>• Security settings</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Trading Strategy Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Trading Strategy</CardTitle>
              <CardDescription>
                Set up your trading strategies and risk management
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Trading strategy configuration will be implemented here</p>
                <p className="text-sm">This will include:</p>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• LLM model selection</li>
                  <li>• Risk parameters</li>
                  <li>• Position sizing rules</li>
                  <li>• Stop-loss settings</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Notification Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>
                Configure alerts and notifications for your trading activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Notification settings will be implemented here</p>
                <p className="text-sm">This will include:</p>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Trade execution alerts</li>
                  <li>• Price notifications</li>
                  <li>• Risk warnings</li>
                  <li>• Email/SMS settings</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* System Preferences */}
          <Card>
            <CardHeader>
              <CardTitle>System Preferences</CardTitle>
              <CardDescription>
                Customize your dashboard and user experience
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>System preferences will be implemented here</p>
                <p className="text-sm">This will include:</p>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Dashboard customization</li>
                  <li>• Theme settings</li>
                  <li>• Language preferences</li>
                  <li>• Timezone settings</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Save Button */}
        <div className="mt-8 flex justify-center">
          <Button size="lg" disabled className="opacity-50">
            Save Configuration (Coming Soon)
          </Button>
        </div>
      </main>
    </div>
  );
}