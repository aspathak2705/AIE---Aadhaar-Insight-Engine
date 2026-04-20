import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import Plotly from 'plotly.js-dist-min';
import createPlotlyComponent from 'react-plotly.js/factory';

const plotFactory = createPlotlyComponent.default || createPlotlyComponent;
const Plot = plotFactory(Plotly);

const STATE_NAME_ALIASES = {
  'andaman & nicobar island': 'andaman and nicobar',
  'andaman and nicobar island': 'andaman and nicobar',
  chhatisgarh: 'chhattisgarh',
  odisha: 'orissa',
  pondicherry: 'puducherry',
  uttarakhand: 'uttaranchal',
  westbengal: 'west bengal',
  telangana: 'andhra pradesh',
  ladakh: 'jammu and kashmir',
};

function normalizeStateName(name) {
  const normalized = String(name || '').toLowerCase().trim();
  return STATE_NAME_ALIASES[normalized] || normalized;
}

function normalizeDistrictName(name) {
  return String(name || '').toLowerCase().trim();
}

function formatLabel(name) {
  return String(name || '')
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function prepareStateGeojson(json) {
  if (!json?.features) {
    return json;
  }

  json.features.forEach((feature, index) => {
    if (!feature.properties) {
      feature.properties = {};
    }

    const stateName = feature.properties.ST_NM || feature.properties.NAME_1 || `state-${index}`;
    feature.properties.state_name = stateName;
    feature.properties.state_key = normalizeStateName(stateName);
    feature.properties.feature_uid = String(index);
  });

  return json;
}

function prepareDistrictGeojson(json) {
  if (!json?.features) {
    return json;
  }

  json.features.forEach((feature, index) => {
    if (!feature.properties) {
      feature.properties = {};
    }

    const stateName = feature.properties.ST_NM || feature.properties.NAME_1 || '';
    const districtName = feature.properties.DISTRICT || feature.properties.NAME_2 || `district-${index}`;

    feature.properties.state_name = stateName;
    feature.properties.district_name = districtName;
    feature.properties.state_key = normalizeStateName(stateName);
    feature.properties.district_key = normalizeDistrictName(districtName);
    feature.properties.feature_uid = `${feature.properties.state_key}::${feature.properties.district_key}::${index}`;
  });

  return json;
}

export default function GeoIntelligencePage() {
  const [stateGeojson, setStateGeojson] = useState(null);
  const [districtGeojson, setDistrictGeojson] = useState(null);
  const [data, setData] = useState([]);
  const [metricOption, setMetricOption] = useState('anomaly_score');
  const [selectedState, setSelectedState] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/india_states_datameet.geojson').then((res) => res.json()),
      fetch('/india_districts_datameet.geojson').then((res) => res.json()),
    ])
      .then(([stateJson, districtJson]) => {
        setStateGeojson(prepareStateGeojson(stateJson));
        setDistrictGeojson(prepareDistrictGeojson(districtJson));
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);

    const params = new URLSearchParams({ metric: metricOption });
    if (selectedState) {
      params.set('state', selectedState);
    }

    axios
      .get(`http://127.0.0.1:8000/api/geo?${params.toString()}`)
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setLoading(false);
      });
  }, [metricOption, selectedState]);

  const mapConfig = useMemo(() => {
    if (!stateGeojson || !districtGeojson) {
      return null;
    }

    if (!selectedState) {
      const stateValueMap = new Map(
        data.map((item) => [normalizeStateName(item.state), item.value]),
      );

      const matchedFeatures = stateGeojson.features.filter((feature) =>
        stateValueMap.has(feature.properties.state_key),
      );

      const stateLookup = new Map(
        matchedFeatures.map((feature) => [feature.properties.feature_uid, feature.properties]),
      );

      return {
        geojson: stateGeojson,
        locations: matchedFeatures.map((feature) => feature.properties.feature_uid),
        z: matchedFeatures.map((feature) => stateValueMap.get(feature.properties.state_key)),
        text: matchedFeatures.map((feature) => feature.properties.state_name),
        featureidkey: 'properties.feature_uid',
        lookup: stateLookup,
        title: 'Click a state to open its district map.',
        subtitle: 'India-wide view',
      };
    }

    const districtValueMap = new Map(
      data.map((item) => [normalizeDistrictName(item.district), item.value]),
    );

    const selectedDistrictFeatures = districtGeojson.features.filter(
      (feature) => feature.properties.state_key === selectedState,
    );

    return {
      geojson: {
        ...districtGeojson,
        features: selectedDistrictFeatures,
      },
      locations: selectedDistrictFeatures.map((feature) => feature.properties.feature_uid),
      z: selectedDistrictFeatures.map(
        (feature) => districtValueMap.get(feature.properties.district_key) ?? null,
      ),
      text: selectedDistrictFeatures.map((feature) => feature.properties.district_name),
      featureidkey: 'properties.feature_uid',
      lookup: null,
      title: 'District view for the selected state.',
      subtitle: formatLabel(selectedState),
    };
  }, [data, districtGeojson, selectedState, stateGeojson]);

  if (!stateGeojson || !districtGeojson || loading || !mapConfig) {
    return <div className="body-md">Mapping territories...</div>;
  }

  const colorscale = [
    [0, '#f8fafb'],
    [0.5, '#ffdad6'],
    [1, '#d32f2f'],
  ];

  const handlePlotClick = (event) => {
    if (selectedState) {
      return;
    }

    const featureId = event?.points?.[0]?.location;
    if (!featureId) {
      return;
    }

    const feature = mapConfig.lookup?.get(String(featureId));
    if (feature?.state_key) {
      setSelectedState(feature.state_key);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h3 className="headline-md">
            {selectedState ? `${formatLabel(selectedState)} District Risk Map` : 'Geospatial Risk Topography'}
          </h3>
          <p className="body-md" style={{ marginTop: '8px', color: 'var(--on-surface-variant)' }}>
            {mapConfig.title} Activity shows Aadhaar-related transaction intensity, while anomaly score highlights unusual patterns.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {selectedState && (
            <button className="btn-primary" type="button" onClick={() => setSelectedState(null)}>
              Back to India Map
            </button>
          )}
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
      </div>

      <div
        className="body-md"
        style={{
          marginBottom: '24px',
          padding: '14px 16px',
          borderRadius: '8px',
          backgroundColor: 'var(--surface-container-low)',
          color: 'var(--on-surface-variant)',
        }}
      >
        <strong style={{ color: 'var(--on-surface)' }}>{mapConfig.subtitle}:</strong>{' '}
        {selectedState
          ? 'Each district is shaded using the selected metric for that district within this state.'
          : 'Each state is shaded using the selected metric averaged across that state. Click any state to inspect its districts.'}
      </div>

      <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
        <Plot
          key={selectedState ? `district-${selectedState}-${metricOption}` : `india-${metricOption}`}
          data={[
            {
              type: 'choropleth',
              geojson: mapConfig.geojson,
              locations: mapConfig.locations,
              z: mapConfig.z,
              text: mapConfig.text,
              featureidkey: mapConfig.featureidkey,
              colorscale,
              marker: { line: { width: 0.6, color: '#ffffff' } },
              colorbar: { title: metricOption === 'anomaly_score' ? 'Risk' : 'Activity' },
              hovertemplate:
                metricOption === 'anomaly_score'
                  ? '%{text}<br>Anomaly Score: %{z:.4f}<extra></extra>'
                  : '%{text}<br>Activity Ratio: %{z:.4f}<extra></extra>',
            },
          ]}
          layout={{
            geo: {
              fitbounds: 'locations',
              visible: false,
              showframe: false,
              showcoastlines: false,
              projection: {
                type: 'mercator',
              },
            },
            width: 1000,
            height: 650,
            margin: { t: 0, b: 0, l: 0, r: 0 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
          }}
          config={{ responsive: true }}
          onClick={handlePlotClick}
        />
      </div>
    </div>
  );
}
