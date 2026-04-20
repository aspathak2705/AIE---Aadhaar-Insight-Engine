import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Map as MapIcon, TrendingUp, BarChart2, Search, ShieldAlert, CheckCircle } from 'lucide-react';
import OverviewPage from './pages/OverviewPage';
import GeoIntelligencePage from './pages/GeoIntelligencePage';
import TemporalAnalysisPage from './pages/TemporalAnalysisPage';
import DistributionPage from './pages/DistributionPage';
import InvestigationPage from './pages/InvestigationPage';

function Sidebar() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Overview', icon: LayoutDashboard },
    { path: '/geo', label: 'Geo Intelligence', icon: MapIcon },
    { path: '/temporal', label: 'Temporal Analysis', icon: TrendingUp },
    { path: '/distribution', label: 'Distribution', icon: BarChart2 },
    { path: '/investigation', label: 'Investigation', icon: Search },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <h1 className="title-lg" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={28} />
          <span>AIE (Aadhaar Insight Engine)</span>
        </h1>
      </div>
      
      <div className="nav-group">
        <h2 className="nav-header label-md">Intelligence</h2>
        <ul>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path}>
                <Link to={item.path} className={isActive ? 'active' : ''}>
                  <Icon size={20} />
                  <span className="body-md">{item.label}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </div>

      <div style={{ marginTop: 'auto', padding: '16px', background: 'var(--surface-container-low)', borderRadius: '8px' }}>
        <p className="label-sm" style={{ color: 'var(--on-surface-variant)', marginBottom: '4px' }}>SYSTEM STATUS</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="status-indicator status-normal"></span>
          <span className="body-md" style={{ fontWeight: 500 }}>All Systems Nominal</span>
        </div>
      </div>
    </aside>
  );
}

function TopHeader() {
  const location = useLocation();
  const getTitle = () => {
    switch (location.pathname) {
      case '/': return 'System Overview';
      case '/geo': return 'Geo Intelligence';
      case '/temporal': return 'Temporal Analysis';
      case '/distribution': return 'Distribution Analysis';
      case '/investigation': return 'Deep Investigation';
      default: return 'Dashboard';
    }
  };

  return (
    <header className="top-header">
      <div>
        <h2 className="headline-lg">{getTitle()}</h2>
      </div>
      <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        <span className="chip"><CheckCircle size={16} color="var(--primary)" style={{marginRight: 6}}/> Verified</span>
      </div>
    </header>
  );
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <TopHeader />
          <div className="workspace">
            <Routes>
              <Route path="/" element={<OverviewPage />} />
              <Route path="/geo" element={<GeoIntelligencePage />} />
              <Route path="/temporal" element={<TemporalAnalysisPage />} />
              <Route path="/distribution" element={<DistributionPage />} />
              <Route path="/investigation" element={<InvestigationPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
