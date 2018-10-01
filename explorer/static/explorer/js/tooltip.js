$(document).ready(function() {
	$('[data-toggle="tooltip"]').tooltip();
})


var highlight_cloverleaf_tooltip = function(positions) {
  var highlight_positions = positions.split(':');
  d3.select('#circle' + highlight_positions[0]).attr('class', 'tooltip-cloverleaf-highlight')
  if (highlight_positions.length > 1) d3.select('#circle' + highlight_positions[1]).attr('class', 'tooltip-cloverleaf-highlight')
};