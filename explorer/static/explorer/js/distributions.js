var isotypes, positions, parent;
var stacked;
var adata, idata, isotype_scale, position_scale, distro_data;

var draw_distribution = function(plot_data) {
  distro_data = JSON.parse(plot_data);
  d3.select('#distribution-area .loading-overlay').style('display', 'none');

  isotypes = Object.keys(distro_data).sort();
  positions = Object.keys(distro_data[isotypes[0]]).sort(position => {
  	return ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '8', '9', '10:25', '11:24', '12:23', '13:22', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '26', '27:43', '28:42', '29:41', '30:40', '31:39', '32', '33', '34', '35', '36', '37', '38', '44', '45', '46', '47', '48', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', 'V1', 'V2', 'V3', 'V4', 'V5', '49:65', '50:64', '51:63', '52:62', '53:61', '54', '55', '56', '57', '58', '59', '60', '73'].indexOf(position);
  })

  var plot_width = 1200;
  var plot_height = 2000;
  var facet_width = plot_width / isotypes.length - 10;
  var facet_height = plot_height / positions.length - 10;

	d3.select('#distribution-area')
	  .append('svg')
	  .attr('id', 'distribution-svg')
	  .attr('width', plot_width)
	  .attr('height', plot_height)
	  .append('g')
	  .attr('id', 'distribution-plots');

  var tooltip = d3.select('body')
    .append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0);
  var tooltip_position = tooltip.append('div')
  var tooltip_isotype = tooltip.append('div')
  var tooltip_group = tooltip.append('div')

	var draw_facet = function(isotype, position, data) {

    var current_facet = isotype + '-' + position;
		var stacked = d3.stack().keys(['A', 'C', 'G', 'U', '-'])
		  .offset(d3.stackOffsetExpand)(data);

	  var feature_scale = d3.scaleOrdinal()
	    .domain(['A', 'C', 'G', 'U', '-', 'Purine','Pyrimidine','Weak','Strong','Amino','Keto','B','D','H','V','N','Absent','Mismatched','Paired','High mismatch rate'])
	    .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#dddddd', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd','#e5c494','#ccebd5','#ffa79d','#a6cdea','white','#ffffff','#cccccc','#ffffcc','#222222']);

	  var isotype_scale = d3.scaleLinear()
	    .domain([0, isotypes.length - 1])
	    .range([10, plot_width]);

	  var position_scale = d3.scaleLinear()
	    .domain([0, positions.length - 1])
	    .range([10, plot_height]);

	  var bar_x_scale = d3.scaleBand()
	  	.domain(data.map(function(d) { return d.group; }))
	  	.rangeRound([0, facet_width])
	  	.padding(0.1);

	  var bar_y_scale = d3.scaleLinear()
    	.domain([d3.min(stacked, stackMin), d3.max(stacked, stackMax)])
    	.range([0, facet_height]);

		function stackMin(stacked) {
		  return d3.min(stacked, function(d) { return d[0]; });
		}

		function stackMax(stacked) {
		  return d3.max(stacked, function(d) { return d[1]; });
		}

	  var facet = d3.select('#distribution-plots')
	    .append('g')
	    .attr('class', 'facet')
	    .attr('id', current_facet)
	    .attr('isotype', isotype)
	    .attr('position', position)
	    .attr('transform', d => {
	    	x = isotype_scale(isotypes.indexOf(isotype));
	    	y = position_scale(positions.indexOf(position));
	    	return "translate(" + x + "," + y + ")";
	    })
	    // .attr('width', plot_width)
	    // .attr('height', plot_height);

	  var bars = facet.append('g')
	  	.selectAll('g')
	  	.data(stacked)
	  	.enter()
	  	.append('g')
      .attr("fill", d => feature_scale(d.key))
	  	.selectAll('rect')
	  	.data(d => d)
	  	.enter()
	  	.append('rect')
	  	.attr("x", d => bar_x_scale(d.data.group))
	  	.attr("y", d => bar_y_scale(d[0]))
			.attr("height", d => bar_y_scale(d[1] - d[0]))
      .attr("width", bar_x_scale.bandwidth)
      .attr("stroke-width", 1)
      .attr("stroke", "black")
			.on('mouseover', function(d) {
	      tooltip_position.html('Isotype: ' + d.data.isotype);
	      tooltip_isotype.html('Position: ' + d.data.position);
	      tooltip_group.html('Group: ' + d.data.group)
	      tooltip.transition()
	        .duration(100)
	        .style('opacity', .9)
	        .style('left', d3.event.pageX + 'px')
	        .style('top', d3.event.pageY + 'px');
	      // d3.select(this)
	      //   .transition()
	      //   .duration(100)
	      //   .attr('class', 'cloverleaf-highlight');
			})
			.on('mousemove', function() {  
      tooltip.style('left', d3.event.pageX + 'px')
        .style('top', d3.event.pageY + 'px');
      })
      .on('mouseout', function(d) {   
	      tooltip.transition()    
	        .duration(100)    
	        .style('opacity', 0); 
	      // d3.select(this)
	      //   .transition()
	      //   .duration(100)
	      //   .attr('class', 'cloverleaf-circle');
    	});

	};

	for (isotype of isotypes) {
		for (position of positions) {
			draw_facet(isotype, position, distro_data[isotype][position]);
		};
	};
	

};


