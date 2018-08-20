var bitchart_data;
var draw_bitchart = function(plot_data) {
	bitchart_data = JSON.parse(plot_data);



	var plot_width = 1200,
			plot_height = 800,
			plot_margin = 100;

	// d3.select('#plot-area')
	// 	.append('svg')
	// 	.attr('id', 'plot-svg')
	// 	.attr('width', plot_width + plot_margin)
	// 	.attr('height', plot_height + plot_margin)
	// 	.append('g')
	// 	.attr('id', 'bitchart-plot')

	// var position_scale = d3.scaleBand();
	// 	.domain(positions)
	// 	.range([50, 1180]);

 //  var position_axis = d3.axisBottom(position_scale)
 //    .ticks(positions.length)
 //    .tickFormat(d => positions[d]);

 //  var isotype_scale = d3.scaleLinear()
 //    .domain([0, isotypes.length - 1])
 //    .range([10, 375]);

 //  var isotype_axis = d3.axisLeft(isotype_scale)
 //    .ticks(isotypes.length)
 //    .tickFormat(d => isotypes[d]);


}