import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

type Role = 'FOS' | 'Admin' | 'Delivery';

interface MenuItemProps {
  label: string;
  path: string;
}

const roleMenus: Record<Role, MenuItemProps[]> = {
  FOS: [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Orders', path: '/orders' },
    { label: 'Retailers', path: '/retailers' },
    { label: 'Reports', path: '/reports' },
  ],
  Admin: [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Orders', path: '/orders' },
    { label: 'Retailers', path: '/retailers' },
    { label: 'Reports', path: '/reports' },
    { label: 'Sync', path: '/sync' },
  ],
  Delivery: [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Orders', path: '/orders' },
  ],
};

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [currentRole, setCurrentRole] = useState<Role | null>(null);
  const location = useLocation();

  const menuItems = currentRole ? roleMenus[currentRole] : [];

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Distribution ERP</h1>
        </div>

        <nav className="flex-1 overflow-y-auto p-4">
          {currentRole ? (
            <div className="space-y-1">
              {menuItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`block px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="text-sm text-gray-500 text-center py-8">
              Select a role to view menu
            </div>
          )}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-lg font-semibold text-gray-900">
                {currentRole ? `${currentRole} Portal` : 'Distribution Manager'}
              </h2>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 mr-2">Role:</span>
              {(['FOS', 'Admin', 'Delivery'] as Role[]).map((role) => (
                <button
                  key={role}
                  onClick={() => setCurrentRole(role)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    currentRole === role
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
