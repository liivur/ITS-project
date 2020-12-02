// This example creates a 2-pixel-wide red polyline showing the path of
// the first trans-Pacific flight between Oakland, CA, and Brisbane,
// Australia which was made by Charles Kingsford Smith.
// var map;

// const apiUrl = 'https://135eq1ocxffj-496ff2e9c6d22116-5000-colab.googleusercontent.com/';
const apiUrl = 'http://localhost:5000/';

// src='https://maps.googleapis.com/maps/api/js?key=AIzaSyCg2zb5Hlx6LNU0zaJw9vg98WvUv7JoZCw&callback=initMap&libraries=&v=weekly'
// function initMap() {
	// const flightPlanCoordinates = [
	// 	{ lat: 37.772, lng: -122.214 },
	// 	{ lat: 21.291, lng: -157.821 },
	// 	{ lat: -18.142, lng: 178.431 },
	// 	{ lat: -27.467, lng: 153.027 },
	// ];
// }


$(document).ready(function() {
	let map = new google.maps.Map(document.getElementById('map'), {
		zoom: 14,
		center: { lat: 58.38, lng: 26.73 },
		mapTypeId: 'terrain',
	});

	let geocoder = new google.maps.Geocoder();
	let directionsService = new google.maps.DirectionsService();
	let directionsDisplay = new google.maps.DirectionsRenderer();
	directionsDisplay.setMap(map);

	function updateMap(path) {
		console.log('updateMap', path);
		const origin = path.shift().location;
    	const destination = path.pop().location;

		directionsService.route({
			destination: destination,
			optimizeWaypoints: false,
			origin: origin,
			waypoints: path,
			travelMode: google.maps.TravelMode.DRIVING,
		}, (response, status) => {
			if (status === 'OK') {
				directionsDisplay.setDirections(response);
			} else {
				console.log('Directions request failed due to ' + status);
			}
		});
		// const flightPath = new google.maps.Polyline({
		// 	path: path,
		// 	geodesic: true,
		// 	strokeColor: '#FF0000',
		// 	strokeOpacity: 1.0,
		// 	strokeWeight: 2,
		// });
		// flightPath.setMap(map);
	}
	
	function getPath(from = '', to = '') {
		$.ajax({
			url: apiUrl + 'path',
			type: 'GET',
			dataType: 'json',
			data: {
				from: from,
				to: to,
			},
			crossDomain: true,
		})
		.done(function(response) {
			let path = response.path.map(function(elem, index) {
				return {
					location: {
						lat: elem.coords[0],
						lng: elem.coords[1],
					},
				}
			});
			updateMap(path);
			console.log('success', response);
		})
		.fail(function(e) {
			console.log('error', e);
		})
		.always(function() {
			console.log('complete');
		});
	}

	function savePath(from, to) {
		$.ajax({
			url: apiUrl + 'path',
			type: 'POST',
			dataType: 'json',
			data: {
				from: from,
				to: to,
			},
			crossDomain: true,
		})
		.done(function(response) {
			console.log('path saved', response);
		})
		.fail(function(e) {
			console.log('error', e);
		})
		.always(function() {
			console.log('complete');
		});
	}
	
	$('.js-check-path').on('click', function(e) {
		e.preventDefault();

		getPath($('.js-address-from').val(), $('.js-address-to').val());
	});

	$('.js-save-path').on('click', function(e) {
		e.preventDefault();

		$from = $('.js-address-from');
		$to = $('.js-address-to');
		savePath($from.val(), $to.val());
		$from.val('');
		$to.val('');
	});

	let isFrom = true;
	function toggleFromTo(e) {
		e.preventDefault();
		isFrom = !isFrom;
		$button = $('.js-toggle-from-to');
		if (isFrom) {
			$button.text('Select from');
		} else {
			$button.text('Select to');
		}
	}
	$('.js-toggle-from-to').on('click', toggleFromTo);

	google.maps.event.addListener(map, 'click', function(event){
		geocoder.geocode({
			'latLng': event.latLng
			}, function(results, status) {
				if (status == google.maps.GeocoderStatus.OK && results[0]) {
					if (isFrom) {
						$('.js-address-from').val(results[0].formatted_address)
					} else {
						$('.js-address-to').val(results[0].formatted_address)
					}
				}
			});
		console.log('map click', event);
	});

	// points = ['Mõisavahe 2, Tartu, Estonia', 'Näituse 3, Tartu, Estonia', 'Turu 8, Tartu, Estonia', 'Riia 120, Tartu, Estonia']
});