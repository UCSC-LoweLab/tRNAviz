var isotypes, positions, parent;
var stacked;
var adata, idata, isotype_scale, position_scale, distro_data;
var isotype_axis, position_axis, svg;
var features = ['A', 'C', 'G', 'U', '-', 'A:U', 'U:A', 'G:C', 'C:G', 'G:U', 'U:G', 'A:A', 'A:C', 'A:G', 'C:A', 'C:C', 'C:U', 'G:A', 'G:G', 'U:C', 'U:U', '-:A', '-:C', '-:G', '-:U']
var sorted_positions = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '8', '9', '10:25', '11:24', '12:23', '13:22', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '26', '27:43', '28:42', '29:41', '30:40', '31:39', '32', '33', '34', '35', '36', '37', '38', '44', '45', '46', '47', '48', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', 'V1', 'V2', 'V3', 'V4', 'V5', '49:65', '50:64', '51:63', '52:62', '53:61', '54', '55', '56', '57', '58', '59', '60', '73']

var draw_distribution = function(plot_data) {
  distro_data = JSON.parse(plot_data);
  d3.select('#distribution-area .loading-overlay').style('display', 'none');

  var isotypes = Object.keys(distro_data).sort();
  var positions = Object.keys(distro_data[isotypes[0]]).sort((position1, position2) => sorted_positions.indexOf(position1) - sorted_positions.indexOf(position2));

  var plot_width = 60 * isotypes.length;
  var plot_height = 2400;
  var plot_margin = 100; // extra for placing axes
  var facet_width = plot_width / isotypes.length - 5;
  var facet_height = plot_height / positions.length - 10; 

  d3.select('#distribution-area')
    .append('svg')
    .attr('id', 'distribution-svg')
    .attr('width', plot_width + plot_margin)
    .attr('height', plot_height + plot_margin)
    .append('g')
    .attr('id', 'distribution-plots');

  var isotype_scale = d3.scaleBand()
    .domain(isotypes)
    .rangeRound([10, plot_width - 10])
    .padding(0);

  var isotype_axis = d3.axisTop(isotype_scale);

  var position_scale = d3.scaleLinear()
    .domain([0, positions.length - 1])
    .range([0, plot_height - 20]);

  var position_axis = d3.axisLeft(position_scale)
    .ticks(positions.length)
    .tickFormat(d => positions[d]);

  var svg = d3.select('#distribution-svg');

  svg.append('g')
    .attr('class', 'xaxis')
    .attr('transform', 'translate(40, 20)')
    .call(isotype_axis);

  svg.append('g')
    .attr('class', 'yaxis')
    .attr('transform', 'translate(40, 50)')
    .call(position_axis);

  svg.selectAll('.xaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + isotypes[d])

  svg.selectAll('.yaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + positions[d])

  var draw_facet = function(isotype, position, data) {

    var current_facet = isotype + '-' + position;
    stacked = d3.stack().keys(['A', 'C', 'G', 'U', '-'])
      .offset(d3.stackOffsetExpand)(data);    

    var feature_scale = d3.scaleOrdinal()
      .domain(['A', 'C', 'G', 'U', '-', 'Purine','Pyrimidine','Weak','Strong','Amino','Keto','B','D','H','V','N','Absent','Mismatched','Paired','High mismatch rate'])
      .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#dddddd', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd','#e5c494','#ccebd5','#ffa79d','#a6cdea','white','#ffffff','#cccccc','#ffffcc','#222222']);

    var position_scale = d3.scaleLinear()
      .domain([0, positions.length - 1])
      .range([10, plot_height - 10]);

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
        x = isotype_scale(isotype) + 40;
        y = position_scale(positions.indexOf(position)) + 20;
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
      .on('mouseover', d => {
        idata = d;
        tooltip_feature.html(d.key);
        tooltip_feature.style('text-color', feature_scale(d.key));
        // tooltip_count.html(distro_data)
      })
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
      .on('mouseover', function(d, i) {
        tooltip_position.html(d.data.position);
        tooltip_isotype.html(d.data.isotype);
        tooltip_group.html(d.data.group);
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        // feature = d3.select('#tooltip-feature').html()
        // tooltip_count.html(distro_data[d.data.isotype][d.data.position].map(x => x['group'] == d.data.group)[feature])
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

  var tooltip = d3.select('.tooltip')
  var tooltip_position = tooltip.select('#tooltip-position');
  var tooltip_isotype = tooltip.select('#tooltip-isotype');
  var tooltip_group = tooltip.select('#tooltip-group');
  var tooltip_feature = tooltip.select('#tooltip-feature');
  var tooltip_freq = tooltip.select('#tooltip-freq');

  for (isotype of isotypes) {
    for (position of positions) {
      draw_facet(isotype, position, distro_data[isotype][position]);
    };
  };
  

};


var draw_position_distribution = function(plot_data) {
  d3.select('#distribution-svg').html(JSON.parse(plot_data));
}