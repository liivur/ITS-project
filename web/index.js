// This example creates a 2-pixel-wide red polyline showing the path of
// the first trans-Pacific flight between Oakland, CA, and Brisbane,
// Australia which was made by Charles Kingsford Smith.
var map;

// const apiUrl = 'https://135eq1ocxffj-496ff2e9c6d22116-5000-colab.googleusercontent.com/';
const apiUrl = 'http://localhost:5000/';

// src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCg2zb5Hlx6LNU0zaJw9vg98WvUv7JoZCw&callback=initMap&libraries=&v=weekly"
// function initMap() {
	// const flightPlanCoordinates = [
	// 	{ lat: 37.772, lng: -122.214 },
	// 	{ lat: 21.291, lng: -157.821 },
	// 	{ lat: -18.142, lng: 178.431 },
	// 	{ lat: -27.467, lng: 153.027 },
	// ];
// }

function updateMap(path) {
	console.log('updateMap', path);
	const flightPath = new google.maps.Polyline({
		path: path,
		geodesic: true,
		strokeColor: "#FF0000",
		strokeOpacity: 1.0,
		strokeWeight: 2,
	});
	flightPath.setMap(map);
}

$(document).ready(function() {
	map = new google.maps.Map(document.getElementById("map"), {
		zoom: 3,
		center: { lat: 0, lng: -180 },
		mapTypeId: "terrain",
	});
	
	function getPath(address = '') {
		$.ajax({
			url: apiUrl + 'path',
			type: 'GET',
			dataType: 'json',
			data: {address: address},
			crossDomain: true,
		})
		.done(function(response) {
			let path = response.path.map(function(elem, index) {
				return {
					lat: elem.coords[0],
					lng: elem.coords[1],
				}
			});
			updateMap(path);
			console.log("success", response);
		})
		.fail(function(e) {
			console.log("error", e);
		})
		.always(function() {
			console.log("complete");
		});
	}

	function savePath(address) {
		$.ajax({
			url: apiUrl + 'path',
			type: 'POST',
			dataType: 'json',
			data: {address: address},
			crossDomain: true,
		})
		.done(function(response) {
			console.log("path saved", response);
		})
		.fail(function(e) {
			console.log("error", e);
		})
		.always(function() {
			console.log("complete");
		});
	}
	
	$('.js-check-path').on('click', function(e) {
		e.preventDefault();

		getPath($('.js-address').val());
	});

	$('.js-save-path').on('click', function(e) {
		e.preventDefault();

		savePath($('.js-address').val());
	});

	// points = ['Mõisavahe 2, Tartu, Estonia', 'Näituse 3, Tartu, Estonia', 'Turu 8, Tartu, Estonia', 'Riia 120, Tartu, Estonia']
});