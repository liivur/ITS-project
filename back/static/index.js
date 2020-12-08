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

var map;
$(document).ready(function() {
	let from = '';
	let to = '';
	const pairPaths = [];
	
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 14,
		center: { lat: 58.38, lng: 26.73 },
		mapTypeId: 'terrain',
	});
	let markers = {
		from: new google.maps.Marker({
		    title:'From'
		}),
		to: new google.maps.Marker({
		    title:'To'
		}),
	};

	let geocoder = new google.maps.Geocoder();
	let directionsService = new google.maps.DirectionsService();
	let directionsDisplay = new google.maps.DirectionsRenderer();
	directionsDisplay.setMap(map);

	function resetFromTo() {
		from = '';
		to = '';
		$('.js-address-from').val('');
		$('.js-address-to').val('');
		markers.from.setMap(null);
		markers.to.setMap(null);
	}

	function setMarker(marker, location) {
		marker.setPosition(location);
		marker.setMap(map);
	}

	function updateMap(path, pairs) {
		if (path.length < 2) {
			return;
		}
		while (pairPaths.length) {
			pairPaths.pop().setMap(null);
		}
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

		if (pairs && pairs.length) {
			let icons = [
				{
					icon: {
						path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
					},
					offset: "100%",
				},
			];
			for (var i = pairs.length - 1; i >= 0; i--) {
				flightPath = new google.maps.Polyline({
					path: pairs[i].map(function(item) {
						return {
							lat: item[0],
							lng: item[1],
						};
					}),
					icons: icons,
					geodesic: true,
					strokeColor: '#FF0000',
					strokeOpacity: 1.0,
					strokeWeight: 2,
				});
				flightPath.setMap(map);
				pairPaths.push(flightPath);
			}
		}
	}
	
	function getPath(from = '', to = '') {
		$.ajax({
			// url: apiUrl + 'path',
			// url: apiUrl + 'path_coord_nn_dep',
			url: apiUrl + 'path_google',
			type: 'GET',
			dataType: 'json',
			data: {
				from: from,
				to: to,
			},
			crossDomain: true,
		})
		.done(function(response) {
			// let path = response.path.map(function(elem, index) {
			// 	return {
			// 		location: {
			// 			// lat: elem.coords[0],
			// 			// lng: elem.coords[1],
			// 			lat: elem.location.lat,
			// 			lng: elem.location.lng,
			// 		},
			// 	}
			// });
			updateMap(response.path, response.pairs);
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

		getPath(from, to);
	});

	$('.js-save-path').on('click', function(e) {
		e.preventDefault();

		savePath(from, to);
		resetFromTo();
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
		}, 
		function(results, status) {
			console.log(results, status);
			if (status == google.maps.GeocoderStatus.OK && results[0]) {
				let coords = event.latLng.lat() + ',' + event.latLng.lng();
				if (isFrom) {
					from = coords;
					setMarker(markers.from, event.latLng);
					$('.js-address-from').val(results[0].formatted_address)
				} else {
					to = coords;
					setMarker(markers.to, event.latLng);
					$('.js-address-to').val(results[0].formatted_address)
				}
			}
		});
		console.log('map click', event);
	});

	// points = ['Mõisavahe 2, Tartu, Estonia', 'Näituse 3, Tartu, Estonia', 'Turu 8, Tartu, Estonia', 'Riia 120, Tartu, Estonia']

	
});