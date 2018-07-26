var isotypes, positions;
var stacked;
var adata, isotype_scale, position_scale, distro_data;
var draw_distribution = function(plot_data) {
  // d3.select('#distribution-area').html(plot_data)
  distro_data = JSON.parse(plot_data);
  // dict is { isotype : { position : { base: freq, base2: freq}}}
  // example: 'Thr': {'20': {'U': 57.0, 'G': 0.0, 'A': 0.0, 'C': 0.0, '-': 0.0}
  d3.select('#distribution-area .loading-overlay').style('display', 'none');

  // get number of isotypes and positions
  // isotypes = new Set();
  // positions = new Set();
  // for (row of distro_data) {
  // 	isotypes.add(row['isotype']);
  // 	positions.add(row['position']);
  // }
  isotypes = Object.keys(distro_data)
  positions = Object.keys(distro_data[isotypes[0]])

  var plot_width = 1200;
  var plot_height = 2000;
  var facet_width = plot_width / (isotypes.length + 1);
  var facet_height = plot_height / (positions.length + 1);

	d3.select('#distribution-area')
	  .append('svg')
	  .attr('id', 'distribution-svg')
	  .attr('width', plot_width)
	  .attr('height', plot_height)
	  .append('g')
	  .attr('id', 'distribution-plots');

	var draw_facet = function(isotype, position, data) {
		adata = data  
    var current_facet = isotype + '-' + position;

	  var feature_scale = d3.scaleOrdinal()
	    .domain(['A', 'C', 'G', 'U', '-', 'Purine','Pyrimidine','Weak','Strong','Amino','Keto','B','D','H','V','N','Absent','Mismatched','Paired','High mismatch rate'])
	    .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#dddddd', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd','#e5c494','#ccebd5','#ffa79d','#a6cdea','white','#ffffff','#cccccc','#ffffcc','#222222']);

	  var isotype_scale = d3.scaleLinear()
	    .domain([0, isotypes.length - 1])
	    .range([10, plot_width]);

	  var position_scale = d3.scaleLinear()
	    .domain([0, positions.length - 1])
	    .range([10, plot_height]);

	  var height_scale = d3.scaleLinear()
			.domain([0, 1])
			.range([0, facet_height]);


		var stack = d3.stack().keys(['A', 'C', 'G', 'U', '-']);
	  stacked = stack(data);

	  var facet = d3.select('#distribution-plots')
	    .append('g')
	    .attr('class', 'facet')
	    .attr('id', current_facet)
	    .attr('transform', d => {
	    	x = isotype_scale(isotypes.indexOf(isotype));
	    	y = position_scale(positions.indexOf(position));
	    	return "translate(" + x + "," + y + ")";
	    })
	    // .attr('width', plot_width)
	    // .attr('height', plot_height);

	  var bars = facet.selectAll('rect')
	  	.data(stacked)
	  	.enter()
	  	.append('rect')
	  	.attr("y", (d, i) => {
	  		g = 0;
	  		return height_scale(d[g][0]);
	  	})
			.attr("height", (d, i) => {
				g = 0;
				return height_scale(d[g][1] - d[g][0]);
			})
      .attr("width", 10)
	    .style("fill", function(d, i) {
					return feature_scale(i);
			});

	};

	for (isotype of isotypes) {
		for (position of positions) {
			draw_facet(isotype, position, distro_data[isotype][position]);
		};
	};
	

};


