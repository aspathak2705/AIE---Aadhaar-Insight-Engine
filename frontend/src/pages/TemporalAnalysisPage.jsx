import React, { useEffect, useState } from 'react';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';

export default function TemporalAnalysisPage() {
  const [data, setData] = useState([]);
  
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch states for dropdown
    api.get('/api/states')
      .then(res => setStates(res.data))
      .catch(console.error);
      
    // Fetch initial national data
    fetchTemporalData('', '');
  }, []);

  const fetchTemporalData = (state = '', district = '') => {
    setLoading(true);
    let url = '/api/temporal';
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
    fetchTemporalData(s, '');
    
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
    fetchTemporalData(selectedState, d);
  };

  return (
    <div className="card">
      <div className="page-toolbar" style={{ marginBottom: '32px' }}>
        <h3 className="headline-md">Temporal Analysis</h3>
        
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
        <div className="body-md">Analyzing chronological patterns...</div>
      ) : (
        <div className="chart-frame chart-frame-lg chart-scroll-x">
          <div className="chart-min-width" style={{ width: '100%', height: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--outline-grid)" vertical={false} />
              <XAxis dataKey="month" stroke="var(--on-surface-variant)" />
              <YAxis stroke="var(--on-surface-variant)" />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--surface-container-highest)', border: 'none', borderRadius: '8px' }}
                itemStyle={{ color: 'var(--primary)' }}
                formatter={(value) => typeof value === 'number' ? value.toFixed(4) : value}
              />
              <Legend />
              
              <Bar 
                dataKey="activity_ratio" 
                name="Activity Ratio" 
                fill="var(--primary-container)" 
                barSize={20}
              />
              <Line 
                type="monotone" 
                dataKey="rolling" 
                name="3-Month Trend" 
                stroke="var(--primary)" 
                strokeWidth={3}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
