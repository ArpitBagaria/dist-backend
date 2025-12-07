import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Retailers from './pages/Retailers';
import Orders from './pages/Orders';
import Reports from './pages/Reports';
import Sync from './pages/Sync';

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <nav style={{
        width: '240px',
        backgroundColor: 'var(--color-bg-secondary)',
        borderRight: '1px solid var(--color-border)',
        padding: '24px 0',
        position: 'fixed',
        height: '100vh',
        overflowY: 'auto',
      }}>
        <div style={{ padding: '0 24px', marginBottom: '32px' }}>
          <h1 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--color-primary)' }}>
            Distribution Manager
          </h1>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/orders">Orders</NavLink>
          <NavLink to="/retailers">Retailers</NavLink>
          <NavLink to="/reports">Reports</NavLink>
          <NavLink to="/sync">Sync</NavLink>
        </div>
      </nav>
      <main style={{ marginLeft: '240px', flex: 1, padding: '32px' }}>
        <div className="container">
          {children}
        </div>
      </main>
    </div>
  );
}

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      style={{
        display: 'block',
        padding: '12px 24px',
        color: 'var(--color-text)',
        textDecoration: 'none',
        transition: 'all 0.2s',
        fontWeight: '500',
        fontSize: '14px',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--color-bg)';
        e.currentTarget.style.color = 'var(--color-primary)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent';
        e.currentTarget.style.color = 'var(--color-text)';
      }}
    >
      {children}
    </Link>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/retailers" element={<Retailers />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/sync" element={<Sync />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
