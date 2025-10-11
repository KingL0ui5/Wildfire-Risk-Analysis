    const map = new maplibregl.Map({
        container: 'map', // container id
        style: 'https://api.maptiler.com/maps/streets-v2/style.json?key=5Vd1Ny9BxtDQJ9GTpLcX',
        center: [-120.5, 43.8], // starting position [lng, lat]
        zoom: 7, // starting zoom
        maplibreLogo: true
    });