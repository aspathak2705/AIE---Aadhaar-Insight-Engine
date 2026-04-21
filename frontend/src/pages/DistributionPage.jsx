import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';

export default function DistributionPage() {
  const [data, setData] = useState({ histogram: [], quantiles: {}, district_breakdown: [] });
  
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/api/states')
      .then(res => setStates(res.data))
      .catch(console.error);
      
    fetchDistributionData('', '');
  }, []);

  const fetchDistributionData = (state = '', district = '') => {
    setLoading(true);
    let url = '/api/distribution';
    const params = [];
    if (state) params.push(`state=${encodeURIComponent(state)}`);
    if (district) params.push(`district=${encodeURIComponent(district)}`);
    
    if (params.length > 0) {
      url += '?' + params.join('&');
    }
      
    api.get(url)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(console.error);
  };

  const handleStateChange = (e) => {
    const s = e.target.value;
    setSelectedState(s);
    setSelectedDistrict('');
    fetchDistributionData(s, '');
    
    if (s) {
      api.get(`/api/districts?state=${encodeURIComponent(s)}`)
        .then(res => setDistricts(res.data))
        .catch(console.error);
    } else {
      setDistricts([]);
    }
  };

  const handleDistrictChange = (e) => {
    const d = e.target.value;
    setSelectedDistrict(d);
    fetchDistributionData(selectedState, d);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <div className="card mobile-stack-card" style={{ padding: '24px' }}>
        <h3 className="headline-md" style={{ margin: 0 }}>Distribution Filters</h3>
        <div className="page-controls">
          <select 
            className="input-field responsive-select"
            value={selectedState}
            onChange={handleStateChange}
          >
            <option value="">National Average (All States)</option>
            {states.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          
          <select 
            className="input-field responsive-select"
            value={selectedDistrict}
            onChange={handleDistrictChange}
            disabled={!selectedState}
          >
            <option value="">All Districts</option>
            {districts.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="body-md">Computing distributions...</div>
      ) : (
        <>
          <div className="grid-2">
            <div className="card">
              <h3 className="title-lg" style={{ marginBottom: '24px' }}>Activity Ratio Distribution</h3>
              <div className="chart-frame chart-frame-md chart-scroll-x">
                <div className="chart-min-width" style={{ width: '100%', height: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.histogram}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--outline-grid)" vertical={false} />
                    <XAxis dataKey="name" stroke="var(--on-surface-variant)" tick={{ fontSize: 12 }} />
                    <YAxis stroke="var(--on-surface-variant)" />
                    <Tooltip 
                      cursor={{ fill: 'var(--surface-container-low)' }} 
                      contentStyle={{ borderRadius: 8, border: 'none', backgroundColor: 'var(--surface-container-highest)' }} 
                      itemStyle={{ color: 'var(--primary)' }}
                    />
                    <Bar dataKey="count" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="title-lg" style={{ marginBottom: '12px' }}>Activity Range Summary</h3>
              <p
                className="body-md"
                style={{ marginBottom: '24px', color: 'var(--on-surface-variant)' }}
              >
                This summary shows what low, typical, and high activity looks like in
                the selected area. Here, activity means the level of Aadhaar-related
                updates or transactions recorded for a region compared with its
                enrolment volume.
              </p>
              
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ACTIVITY LEVEL</th>
                    <th>ACTIVITY RATIO</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Lowest observed activity</td>
                    <td>{parseFloat(data.quantiles['0.0'] || 0).toFixed(4)}</td>
                  </tr>
                  <tr>
                    <td>Lower-range activity</td>
                    <td>{parseFloat(data.quantiles['0.25'] || 0).toFixed(4)}</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Typical activity</td>
                    <td style={{ fontWeight: 600 }}>{parseFloat(data.quantiles['0.5'] || 0).toFixed(4)}</td>
                  </tr>
                  <tr>
                    <td>Higher-range activity</td>
                    <td>{parseFloat(data.quantiles['0.75'] || 0).toFixed(4)}</td>
                  </tr>
                  <tr>
                    <td style={{ color: 'var(--error)', fontWeight: 600 }}>Highest observed activity</td>
                    <td style={{ color: 'var(--error)', fontWeight: 600 }}>{parseFloat(data.quantiles['1.0'] || 0).toFixed(4)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          {selectedState && !selectedDistrict && data.district_breakdown && data.district_breakdown.length > 0 && (
            <div className="card" style={{ minHeight: '500px' }}>
              <h3 className="title-lg" style={{ marginBottom: '24px' }}>District Distribution Breakdown</h3>
              <div className="chart-frame chart-scroll-x" style={{ height: Math.max(340, data.district_breakdown.length * 30) }}>
                <div className="chart-min-width" style={{ width: '100%', height: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.district_breakdown} layout="vertical" margin={{ left: 100, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--outline-grid)" horizontal={false} />
                    <XAxis type="number" stroke="var(--on-surface-variant)" />
                    <YAxis dataKey="district" type="category" stroke="var(--on-surface-variant)" tick={{ fontSize: 12 }} width={120} />
                    <Tooltip 
                      cursor={{ fill: 'var(--surface-container-low)' }} 
                      contentStyle={{ borderRadius: 8, border: 'none', backgroundColor: 'var(--surface-container-highest)' }} 
                      itemStyle={{ color: 'var(--primary)' }}
                      formatter={(value) => typeof value === 'number' ? value.toFixed(4) : value}
                    />
                    <Bar dataKey="activity_ratio" name="Avg Activity" fill="var(--primary-container)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
