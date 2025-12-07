import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Retailers from './pages/Retailers';
import Orders from './pages/Orders';
import Reports from './pages/Reports';
import Sync from './pages/Sync';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
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
