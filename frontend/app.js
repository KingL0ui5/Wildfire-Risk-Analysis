const map = new maplibregl.Map({
    container: 'map', // container id
    style: 'https://api.maptiler.com/maps/streets-v2/style.json?key=5Vd1Ny9BxtDQJ9GTpLcX',
    center: [-120.5, 43.8], // starting position [lng, lat]
    zoom: 6, // starting zoom
    maplibreLogo: true
});

map.on('load', () => {
  map.addSource('riskPoints', {
    type: 'geojson',
    data: './test.geojson'
  });

  map.addLayer({
    id: 'risk-heatmap',
    type: 'heatmap',
    source: 'riskPoints',
    paint: {
      'heatmap-weight': ['interpolate', ['linear'], ['get','risk'], 0, 0, 100, 1],
      'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 1, 1, 12, 2],
      'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 5, 30, 12, 15],
      'heatmap-color': [
        'interpolate', ['linear'], ['heatmap-density'],
        0.0, 'rgb(0, 0, 0, 0)',
        0.1, 'hsl(120,90%,45%)',
        0.2, 'hsl(60,90%,50%)',
        0.3, 'hsl(20,90%,50%)',
        1.0, 'hsl(0,90%,45%)'
      ],
      'heatmap-opacity': 0.85
    }
  });
});

