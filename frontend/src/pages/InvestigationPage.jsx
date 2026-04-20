import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Search } from 'lucide-react';

export default function InvestigationPage() {
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/states')
      .then(res => {
        setStates(res.data);
      })
      .catch(console.error);
  }, []);

  const handleStateChange = (e) => {
    const s = e.target.value;
    setSelectedState(s);
    setSelectedDistrict('');
    setResults([]);
    
    if (s) {
      axios.get(`http://127.0.0.1:8000/api/investigation?state=${s}`)
        .then(res => setDistricts(res.data.districts))
        .catch(console.error);
    } else {
      setDistricts([]);
    }
  };

  const handleDistrictChange = (e) => {
    const d = e.target.value;
    setSelectedDistrict(d);
    
    if (selectedState && d) {
      setLoading(true);
      axios.get(`http://127.0.0.1:8000/api/investigation?state=${selectedState}&district=${d}`)
        .then(res => {
          setResults(res.data.pincodes);
          setLoading(false);
        })
        .catch(console.error);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', gap: '24px', marginBottom: '32px' }}>
        <div style={{ flex: 1 }}>
          <label className="label-sm" style={{ color: 'var(--on-surface-variant)' }}>STATE FILTER</label>
          <select className="input-field" value={selectedState} onChange={handleStateChange}>
            <option value="">Select State...</option>
            {states.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        
        <div style={{ flex: 1 }}>
          <label className="label-sm" style={{ color: 'var(--on-surface-variant)' }}>DISTRICT FILTER</label>
          <select 
            className="input-field" 
            value={selectedDistrict} 
            onChange={handleDistrictChange}
            disabled={!selectedState}
          >
            <option value="">Select District...</option>
            {districts.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
      </div>

      {loading && <div className="body-md">Investigating...</div>}
      
      {!loading && results.length > 0 && (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>PINCODE</th>
                <th>ANOMALY SCORE (RISK)</th>
                <th>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, idx) => (
                <tr key={idx}>
                  <td className="headline-md" style={{ fontFamily: 'monospace', fontSize: '1.25rem' }}>{r.pincode}</td>
                  <td>
                    <span 
                      className="chip" 
                      style={{ 
                        backgroundColor: r.anomaly_score > 0.8 ? 'var(--error-container)' : 'var(--surface-container-highest)', 
                        color: r.anomaly_score > 0.8 ? 'var(--error)' : 'var(--on-surface)' 
                      }}>
                      {parseFloat(r.anomaly_score).toFixed(4)}
                    </span>
                  </td>
                  <td>
                    <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '0.875rem' }}>
                      <Search size={14} /> Flag
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {!loading && selectedDistrict && results.length === 0 && (
        <div className="body-md">No significant targets found in this district.</div>
      )}
    </div>
  );
}
