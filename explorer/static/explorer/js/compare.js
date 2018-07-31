var draw_bitchart = function(plot_data) {
	bitchart_data = JSON.parse(plot_data);
	d3.select('#bitchart-area .loading-overlay').style('display', 'none');
	d3.select('#bitchart-area').html(plot_data)
}