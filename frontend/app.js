const map = new maplibregl.Map({
  container: 'map',
  style: 'https://api.maptiler.com/maps/streets-v2/style.json?key=5Vd1Ny9BxtDQJ9GTpLcX',
  center: [-120.5, 43.8],
  zoom: 6,
  maplibreLogo: true
});

// Popup
const popup = new maplibregl.Popup({
  closeButton: true,
  closeOnClick: true
});

// click -> coords
map.on('click', (e) => {
  const { lng, lat } = e.lngLat;
  popup
    .setLngLat([lng, lat])
    .setHTML(`<strong>Longitude:</strong> ${lng.toFixed(5)}<br><strong>Latitude:</strong> ${lat.toFixed(5)}`)
    .addTo(map);
});

// format date
function fmtDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (isNaN(d)) return String(value);
  return d.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
}

// navbar time
function updateNavbarTime(isoString) {
  const el = document.getElementById('time');
  if (!el) return;
  el.textContent = fmtDate(isoString);
}

// top 5 list
function renderTop5(features) {
  const ul = document.getElementById('top5');
  if (!ul) return;
  const top5 = [...features]
    .sort((a, b) => (Number(b.properties?.risk) || 0) - (Number(a.properties?.risk) || 0))
    .slice(0, 5);
  ul.innerHTML = top5.map(f => {
    const [lon, lat] = f.geometry?.coordinates || [NaN, NaN];
    const risk = Number(f.properties?.risk) || 0;
    const date = f.properties?.date ? ` • ${fmtDate(f.properties.date)}` : '';
    const cause = f.properties?.cause ? ` • ${f.properties.cause}` : '';
    return `<li class="list-group-item">${lon.toFixed(3)}, ${lat.toFixed(3)} <span class="text-muted">— risk ${risk}${date}${cause}</span></li>`;
  }).join('');
}

// dataset time from FC.properties.generated_at or max feature date
function getDatasetTime(geojson) {
  const fcTime = geojson?.properties?.generated_at;
  if (fcTime) return fcTime;
  let latest = null;
  for (const f of geojson?.features || []) {
    const t = f?.properties?.date;
    if (!t) continue;
    const ms = new Date(t).getTime();
    if (!isNaN(ms) && (latest == null || ms > latest)) latest = ms;
  }
  return latest != null ? new Date(latest).toISOString() : null;
}

map.on('load', () => {
  // source
  map.addSource('riskPoints', {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] }
  });

  // layers
  const heatCommon = {
    'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 4, 0.6, 8, 1.5, 12, 2.5],
    'heatmap-radius':    ['interpolate', ['linear'], ['zoom'], 4, 12, 8, 28, 12, 60],
    'heatmap-opacity':   ['interpolate', ['linear'], ['zoom'], 5, 0.8, 10, 0.7, 13, 0.5]
  };

  map.addLayer({
    id: 'risk-heat-low',
    type: 'heatmap',
    source: 'riskPoints',
    filter: ['<', ['get', 'risk'], 50],
    paint: {
      'heatmap-weight': 1,
      ...heatCommon,
      'heatmap-color': [
        'interpolate', ['linear'], ['heatmap-density'],
        0.0, 'rgba(0, 0, 0, 0)',
        0.15, 'rgba(0, 255, 0, 0.15)',
        0.4, 'rgba(0, 255, 0, 0.35)',
        0.8, 'rgba(0, 255, 0, 0.6)'
      ]
    }
  });

  map.addLayer({
    id: 'risk-heat-mid',
    type: 'heatmap',
    source: 'riskPoints',
    filter: ['all', ['>=', ['get', 'risk'], 50], ['<=', ['get', 'risk'], 75]],
    paint: {
      'heatmap-weight': 1,
      ...heatCommon,
      'heatmap-color': [
        'interpolate', ['linear'], ['heatmap-density'],
        0.0, 'rgba(0, 0, 0, 0)',
        0.15, 'rgba(255, 165, 0, 0.25)',
        0.4, 'rgba(255, 165, 0, 0.55)',
        0.8, 'rgba(255, 140, 0, 0.85)'
      ]
    }
  });

  map.addLayer({
    id: 'risk-heat-high',
    type: 'heatmap',
    source: 'riskPoints',
    filter: ['>', ['get', 'risk'], 75],
    paint: {
      'heatmap-weight': 1.2,
      ...heatCommon,
      'heatmap-color': [
        'interpolate', ['linear'], ['heatmap-density'],
        0.0, 'rgba(0, 0, 0, 0)',
        0.1, 'rgba(255, 50, 50, 0.4)',
        0.3, 'rgba(255, 0, 0, 0.75)',
        0.6, 'rgba(230, 0, 0, 0.9)',
        1.0, 'rgba(200, 0, 0, 1.0)'
      ]
    }
  });

  map.addLayer({
    id: 'risk-points-outline',
    type: 'circle',
    source: 'riskPoints',
    minzoom: 7,
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 7, 2, 12, 6],
      'circle-color': [
        'case',
        ['<', ['get', 'risk'], 50], 'rgba(0, 255, 0, 0.3)',
        ['<=', ['get', 'risk'], 75], 'rgba(255, 165, 0, 0.5)',
        'rgba(255, 0, 0, 0.8)'
      ],
      'circle-stroke-color': 'rgba(255,255,255,0.7)',
      'circle-stroke-width': 0.6
    }
  });

  // initial file load
  fetch('./points.geojson')
    .then(r => r.json())
    .then(gj => {
      const src = map.getSource('riskPoints');
      if (src) src.setData(gj);
      const features = gj.features || [];
      renderTop5(features);
      updateNavbarTime(getDatasetTime(gj));
    })
    .catch(err => console.error('Failed to load points.geojson:', err));

  // backend polling
  const DATA_URL = 'http://localhost:5000/predict';
  function pollAndUpdate() {
    fetch(DATA_URL, { cache: 'no-store' })
      .then(r => r.json())
      .then(gj => {
        const src = map.getSource('riskPoints');
        if (src) src.setData(gj);
        const features = gj.features || [];
        renderTop5(features);
        updateNavbarTime(getDatasetTime(gj));
      })
      .catch(err => console.warn('Update failed:', err));
  }
  pollAndUpdate();
  setInterval(pollAndUpdate, 10_000);
});
