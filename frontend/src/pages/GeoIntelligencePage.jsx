import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Plotly from 'plotly.js-dist-min';
import createPlotlyComponent from 'react-plotly.js/factory';
const plotFactory = createPlotlyComponent.default || createPlotlyComponent;
const Plot = plotFactory(Plotly);
export default function GeoIntelligencePage() {
  const [data, setData] = useState([]);
  const [geojson, setGeojson] = useState(null);
  const [metricOption, setMetricOption] = useState('anomaly_score');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch geojson
    fetch('/india_district.geojson')
      .then(res => res.json())
      .then(json => {
        // Preprocess geojson as in python
        if (json && json.features) {
          json.features.forEach(feature => {
            if(feature && feature.properties && feature.properties.NAME_1) {
              feature.properties.NAME_1 = feature.properties.NAME_1.toLowerCase().trim();
            }
          });
        }
        setGeojson(json);
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);
    axios.get(`http://127.0.0.1:8000/api/geo?metric=${metricOption}`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(console.error);
  }, [metricOption]);

  if (!geojson || loading) return <div className="body-md">Mapping territories...</div>;

  const locations = data.map(d => d.state);
  const z = data.map(d => d.value);

  // Use reds scale or custom from the design system
  // We'll use a deep red to red scale for anomalies
  const colorscale = [
    [0, '#f8fafb'],
    [0.5, '#ffdad6'],
    [1, '#d32f2f']
  ];

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h3 className="headline-md">Geospatial Risk Topography</h3>
        <select 
          className="input-field" 
          style={{ width: '250px' }} 
          value={metricOption}
          onChange={(e) => setMetricOption(e.target.value)}
        >
          <option value="anomaly_score">Anomaly Score</option>
          <option value="activity_ratio">Activity Ratio</option>
        </select>
      </div>

      <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
        <Plot
          data={[
            {
              type: 'choropleth',
              geojson: geojson,
              locations: locations,
              z: z,
              featureidkey: 'properties.NAME_1',
              colorscale: colorscale,
              marker: { line: { width: 0.5, color: 'var(--outline-grid)' } },
              colorbar: { title: metricOption === 'anomaly_score' ? 'Risk' : 'Activity' }
            }
          ]}
          layout={{
            geo: {
              fitbounds: 'locations',
              visible: false
            },
            width: 1000,
            height: 600,
            margin: { t: 0, b: 0, l: 0, r: 0 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
          }}
          config={{ responsive: true }}
        />
      </div>
    </div>
  );
}
