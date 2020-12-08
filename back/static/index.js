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
	getAlgorithms();
	getSlots();
	let from = '';
	let to = '';
	const pairPaths = [];
	const directionsRenderers = [];
	
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

	function updateMap(paths, pairs) {
		while (pairPaths.length) {
			pairPaths.pop().setMap(null);
		}
		while (directionsRenderers.length) {
			directionsRenderers.pop().setMap(null);
		}
		

    	for (var i = paths.length - 1; i >= 0; i--) {
    		let path = paths[i];
    		if (path.length < 2) {
				continue;
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
					let directionsRenderer = new google.maps.DirectionsRenderer();
					directionsRenderer.setDirections(response);
					directionsRenderer.setMap(map);
					directionsRenderers.push(directionsRenderer);
				} else {
					console.log('Directions request failed due to ' + status);
				}
			});
    	}

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
	
	function getPaths(path, slot, from = '', to = '') {
		$.ajax({
			url: apiUrl + path,
			// url: apiUrl + 'path_coord_nn_dep',
			// url: apiUrl + 'path_brute_axe',
			// url: apiUrl + 'path_google',
			type: 'GET',
			dataType: 'json',
			data: {
				from: from,
				to: to,
				slot: slot,
			},
			crossDomain: true,
		})
		.done(function(response) {
			updateMap(response.paths, response.pairs);
			console.log('success', response);

			$('.js-travel-time').html(response.distance);
			$('.js-calculation-time').html(response.time);
		})
		.fail(function(e) {
			console.log('error', e);
		})
		.always(function() {
			console.log('complete');
		});
	}

	function savePath(from, to, slot) {
		$.ajax({
			url: apiUrl + 'path',
			type: 'POST',
			dataType: 'json',
			data: {
				from: from,
				to: to,
				slot: slot,
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

		$slot = $('input[name="slot"]:checked');
		$algo = $('.js-algorithm-select');
		getPaths($algo.val(), $slot.val(), from, to);
	});

	$('.js-save-path').on('click', function(e) {
		e.preventDefault();

		$button = $('input[name="slot"]:checked');
		savePath(from, to, $button.val());
		resetFromTo();
	});

	let isFrom = true;
	function toggleFromTo() {
		isFrom = !isFrom;
		$button = $('.js-toggle-from-to');
		if (isFrom) {
			$button.text('Select from');
		} else {
			$button.text('Select to');
		}
	}
	$('.js-toggle-from-to').on('click', function(e) {
		e.preventDefault();
		toggleFromTo();
	});

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
				toggleFromTo();
			}
		});
		console.log('map click', event);
	});

	// points = ['Mõisavahe 2, Tartu, Estonia', 'Näituse 3, Tartu, Estonia', 'Turu 8, Tartu, Estonia', 'Riia 120, Tartu, Estonia']

	function getSlots() {
		$.ajax({
			url: apiUrl + 'slots',
			type: 'GET',
			dataType: 'json',
			crossDomain: true,
		}).done(function(response) {
			console.log('success', response);
			$('.data-container').html(response.map(function(item) {
				return '<label>' + item + '<input type="radio" name="slot" value="' + item + '"></label>';
			}).join('<br>'));
			$('input[name="slot"]').first().prop('checked', true);
		});
	}

	function getAlgorithms() {
		$.ajax({
			url: apiUrl + 'algorithms',
			type: 'GET',
			dataType: 'json',
			crossDomain: true,
		}).done(function(response) {
			console.log('success', response);
			$('.js-algorithm-select').html(response.map(function(item) {
				return '<option value="' + item.path + '">' + item.name + '</option>';
			}).join('<br>'));
			$('.js-algorithm-select option').first().prop('selected', true);
		});
	}
});