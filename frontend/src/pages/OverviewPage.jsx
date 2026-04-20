import React, { useEffect, useState } from 'react';
import { AlertTriangle, Activity, MapPin } from 'lucide-react';
import { api } from '../lib/api';

export default function OverviewPage() {
  const [data, setData] = useState({ stats: null, top_regions: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/api/overview')
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(console.error);
  }, []);

  if (loading) return <div className="body-md">Loading intelligence...</div>;

  const { stats, top_regions } = data;

  return (
    <>
      <div className="grid-4">
        <div className="card">
          <h3 className="title-lg kpi-title">Global Regions</h3>
          <div className="headline-md kpi-value">{stats.regions}</div>
          <div className="kpi-trend positive">Active Surveillance</div>
        </div>
        
        <div className="card">
          <h3 className="title-lg kpi-title">Avg Risk Score</h3>
          <div className="headline-md kpi-value">{parseFloat(stats.avg_risk).toFixed(3)}</div>
          <div className="kpi-trend negative">Threshold: 0.70</div>
        </div>
        
        <div className="card">
          <h3 className="title-lg kpi-title">Critical Anomalies</h3>
          <div className="headline-md kpi-value" style={{ color: 'var(--error)' }}>
            {stats.high_risk}
          </div>
          <div className="kpi-trend negative"><AlertTriangle size={14} /> High Risk</div>
        </div>
        
        <div className="card">
          <h3 className="title-lg kpi-title">Max Activity Ratio</h3>
          <div className="headline-md kpi-value">{parseFloat(stats.max_activity).toFixed(1)}x</div>
          <div className="kpi-trend positive"><Activity size={14}/> Baseline Multiplier</div>
        </div>
      </div>

      <div className="card">
        <h3 className="headline-md" style={{ marginBottom: '24px' }}>Top Risk Regions</h3>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>STATE</th>
                <th>DISTRICT</th>
                <th>PINCODE</th>
                <th>ANOMALY SCORE</th>
              </tr>
            </thead>
            <tbody>
              {top_regions.map((region, idx) => (
                <tr key={idx}>
                  <td className="body-md">{region.state}</td>
                  <td className="body-md">{region.district}</td>
                  <td className="body-md" style={{ fontFamily: 'monospace' }}>{region.pincode}</td>
                  <td className="body-md">
                    <span style={{ 
                      color: region.anomaly_score > 0.8 ? 'var(--error)' : 'var(--warning)',
                      fontWeight: 600 
                    }}>
                      {parseFloat(region.anomaly_score).toFixed(4)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
