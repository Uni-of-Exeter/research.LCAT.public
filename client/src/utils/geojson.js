/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>. */

const $ = require("jquery")
const L = require("leaflet")
// const colormap = require('colormap')

// Meters/Pixel Zoom Level (1-19)
var m2px = [78271.52,39135.76,19567.88,9783.94,4891.97,2445.98,1222.99,
            611.50,305.75,152.87,76.44,38.22,19.11,9.55,4.78,2.39,1.19,
            0.60,0.30];

function zoom_to_tol(zoom) {
    return m2px[zoom-1];
}

class Geojson {
	constructor(leaflet_map,table,prop,low,high) {
		this.map = leaflet_map
        this.table = table
        this.prop = prop
        this.low = low
        this.high = high
		this.layer_buffer = [L.layerGroup().addTo(this.map),
							 L.layerGroup().addTo(this.map)];
		this.current_layer_buffer=0;
		this.other_layer_buffer=1;

		// this.cols = colormap({
		// 	colormap: 'bathymetry',
		// 	nshades: 100,
		// 	format: 'hex',
		// 	alpha: 0.5
		// })

    }

	swap_buffers(leaflet_map) {
		// double buffer to stop flickering
		leaflet_map.removeLayer(this.layer_buffer[this.other_layer_buffer]);
		this.layer_buffer[this.other_layer_buffer].clearLayers();
     	this.layer_buffer[this.current_layer_buffer].addTo(leaflet_map);
		
		if (this.current_layer_buffer==0) {
			this.current_layer_buffer=1;
			this.other_layer_buffer=0;
		} else {
			this.current_layer_buffer=0;
			this.other_layer_buffer=1;
		}
	}

    squash(v,a,b) {
        return (v-a)/(b-a)
    }
    
	update(leaflet_map,net) {
		let b = leaflet_map.getBounds();
		
		$.getJSON(
			"/api/geojson",
			{
                table: this.table,
				left: b._southWest.lng,
				bottom: b._southWest.lat,
				right: b._northEast.lng,
				top: b._northEast.lat,
				tolerance: zoom_to_tol(leaflet_map.getZoom())
			},
			(data,status) => {
                console.log(data);
				L.geoJSON(data, {
					onEachFeature: (feature,layer) => {						
		                layer.bindPopup(JSON.stringify(feature.properties))
                        let col = "#000"
                        //this.cols[Math.round(this.squash(feature.properties[this.prop],this.low,this.high)*this.cols.length)]
                        layer.setStyle({
				            'fillColor': col,
				            'fillOpacity': 0.75
			            });
					}
				}).addTo(this.layer_buffer[this.current_layer_buffer]);				
				this.swap_buffers(leaflet_map);
			});
	}
}

export { Geojson }
