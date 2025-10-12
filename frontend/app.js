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

// Listen for map clicks
map.on('click', (e) => {
  const { lng, lat } = e.lngLat;

  // Show a popup with coordinates
  popup
    .setLngLat([lng, lat])
    .setHTML(`<strong>Longitude:</strong> ${lng.toFixed(5)}<br><strong>Latitude:</strong> ${lat.toFixed(5)}`)
    .addTo(map);

  console.log(`Clicked at: ${lng.toFixed(5)}, ${lat.toFixed(5)}`);
});


map.on('load', () => {
  map.addSource('riskPoints', {
    type: 'geojson',
    data: 'http://localhost/5000/predict'
  });

  const heatCommon = {
    'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 4, 0.6, 8, 1.5, 12, 2.5],
    'heatmap-radius':    ['interpolate', ['linear'], ['zoom'], 4, 12, 8, 28, 12, 60],
    'heatmap-opacity':   ['interpolate', ['linear'], ['zoom'], 5, 0.8, 10, 0.7, 13, 0.5]
  };

  //LOW RISK < 50
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

  //MEDIUM risk 50–75
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

  // HIGH risk > 75
  map.addLayer({
    id: 'risk-heat-high',
    type: 'heatmap',
    source: 'riskPoints',
    filter: ['>', ['get', 'risk'], 75],
    paint: {
      'heatmap-weight': 1.2, // a bit stronger for red areas
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

  fetch('http://localhost:5000/predict')
    .then(r => r.json())
    .then(data => {
      const features = (data && data.features) ? data.features : [];
      const top5 = [...features]
        .sort((a, b) => (Number(b.properties?.risk) || 0) - (Number(a.properties?.risk) || 0))
        .slice(0, 5);

      const ul = document.getElementById('top5');
      if (!ul) return;

      ul.innerHTML = top5.map(f => {
        const [lon, lat] = f.geometry.coordinates || [NaN, NaN];
        const risk = Number(f.properties?.risk) || 0;
        return `<li class="list-group-item">${lon.toFixed(3)}, ${lat.toFixed(3)} <span class="text-muted">— risk ${risk}</span></li>`;
      }).join('');
    })
    .catch(err => console.error('Failed to load points.geojson:', err));

});


