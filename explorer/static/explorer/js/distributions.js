var all_features = ['A', 'C', 'G', 'U', '-', 'A:U', 'U:A', 'G:C', 'C:G', 'G:U', 'U:G', 'A:A', 'A:C', 'A:G', 'C:A', 'C:C', 'C:U', 'G:A', 'G:G', 'U:C', 'U:U', '-:A', '-:C', '-:G', '-:U', '-:-']
var sorted_positions = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '8', '8:14', '9', '9:23', '10:25', '10:45', '11:24', '12:23', '13:22', '14', '15', '15:48', '16', '17', '17a', '18', '18:55', '19', '19:56', '20', '20a', '20b', '21', '22:46', '26', '26:44', '27:43', '28:42', '29:41', '30:40', '31:39', '32', '33', '34', '35', '36', '37', '38', '44', '45', '46', '47', '48', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', 'V1', 'V2', 'V3', 'V4', 'V5', '49:65', '50:64', '51:63', '52:62', '53:61', '54', '54:58', '55', '56', '57', '58', '59', '60', '73']
var feature_scale = d3.scaleOrdinal()
  .domain(['', 'A', 'C', 'G', 'U', '-', 'Purine', 'Pyrimidine', 'Weak', 'Strong', 'Amino', 'Keto', 'B', 'D', 'H', 'V', 'N', 'Absent', 'Mismatched', 'Paired', 'High mismatch rate',
    'A / U', 'G / C', 'A / C', 'G / U', 'C / G / U', 'A / G / U', 'A / C / U', 'A / C / G',
    'A:U', 'U:A', 'G:C', 'C:G', 'G:U', 'U:G', 'A:G', 'G:A', 'C:U', 'U:C', 'A:C', 'C:A', 'A:A', 'C:C', 'G:G', 'U:U', 
    'Missing', 'A:-', '-:A', 'C:-', '-:C', 'G:-', '-:G', 'U:-', '-:U'])
  .range(['#ffffff', '#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#7f7f7f', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd', '#e5c494','#ccebd5','#ffa79d','#a6cdea','#ffffff', '#7f7f7f','#333333','#ffffcc','#b3b3b3',
    '#b3de69', '#fb72b2', '#c1764a', '#b26cbd', '#e5c494', '#ccebd5', '#ffa79d', '#a6cdea',
    '#17b3cf', '#9ed0e5', '#ff7f0e', '#ffbb78', '#a067bc', '#ceafd5', '#2fc69e', '#8be4cf', '#e377c2', '#f7b6d2', '#c47b70', '#f0a994', '#e7cb94', '#cedb9c', '#e7969c', '#9ca8de',
    '#333333', '#333333', '#333333', '#333333', '#333333', '#333333', '#333333', '#333333', '#333333']);

var feature_legend_scale = d3.scaleOrdinal()
  .domain(['A', 'C', 'G', 'U', 
    'A:U', 'U:A', 'G:C', 'C:G', 'G:U', 'U:G', 'A:G', 'G:A', 'C:U', 'U:C', 'A:C', 'C:A', 'A:A', 'C:C', 'G:G', 'U:U', 
    'Absent (- or -:-)', 'Malformed (N:- or -:N)'])
  .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', 
    '#17b3cf', '#9ed0e5', '#ff7f0e', '#ffbb78', '#a067bc', '#ceafd5', '#2fc69e', '#8be4cf', '#e377c2', '#f7b6d2', '#c47b70', '#f0a994', '#e7cb94', '#cedb9c', '#e7969c', '#9ca8de',
    '#7f7f7f', '#333333'])

var draw_distribution = function(plot_data) {
  var isotypes = Object.keys(plot_data).sort();
  var positions = Object.keys(plot_data[isotypes[0]]).sort((position1, position2) => sorted_positions.indexOf(position1) - sorted_positions.indexOf(position2));
  var features = Object.keys(plot_data[isotypes[0]][positions[0]][0]).filter(d => all_features.includes(d))
  var num_groups = plot_data[isotypes[0]][positions[0]].length;

  var facet_width = 30 + 5 * num_groups;
  var facet_height = 40; 
  var legend_height = 80;
  var legend_width = 400;
  var x_axis_buffer = 40;
  var y_axis_buffer = 60;
  var plot_width = Math.max(450, y_axis_buffer + (facet_width * isotypes.length) + 20);
  var plot_height = x_axis_buffer + (facet_height * positions.length) + legend_height;

  var svg = d3.select('#distribution-area')
    .append('svg')
    .attr('id', 'distribution')
    .attr('width', plot_width)
    .attr('height', plot_height)

  var isotype_scale = d3.scaleBand()
    .domain(isotypes)
    .rangeRound([0, facet_width * isotypes.length])
    .paddingInner(0.1);

  var isotype_axis = d3.axisTop(isotype_scale);

  var position_scale = d3.scaleBand()
    .domain(positions)
    .rangeRound([0, facet_height * positions.length])
    .paddingInner(0.1);

  var position_axis = d3.axisLeft(position_scale);

  svg.append('g')
    .attr('class', 'xaxis')
    .attr('transform', 'translate(' + y_axis_buffer + ', 20)')
    .call(isotype_axis);

  svg.append('g')
    .attr('class', 'yaxis')
    .attr('transform', 'translate(' + y_axis_buffer + ', 20)')
    .call(position_axis);

  svg.selectAll('.xaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + d)

  svg.selectAll('.yaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + d.replace(':', '-'))

  // create legend
  var legend = svg.append('g')
    .attr('id', 'legend')
    .attr('transform', 'translate(' + (y_axis_buffer / 2 + (plot_width - legend_width) / 2) + ', ' + (plot_height - legend_height) + ')')
  
  legend.selectAll('rect')
    .data(feature_legend_scale.domain())
    .enter()
    .append('rect')
    .attr('class', 'legend-rect')
    .attr('id', d => 'legend-rect-' + d.replace(/[^a-zA-Z0-9\-]/g, '_'))
    .attr('x', (d, i) => 50 * Math.floor(i / 4))
    .attr('y', (d, i) => (18 * i) % 72 + 2 * (i % 4))
    .attr("width", 18)
    .attr("height", 18)
    .style('fill', d => feature_legend_scale(d));
  
  legend.selectAll('text')
    .data(feature_legend_scale.domain())
    .enter()
    .append('text')
    .attr('class', 'legend-label')
    .attr('id', d => 'legend-label-' + d.replace(/[^a-zA-Z0-9\-]/g, '_'))
    .attr('x', (d, i) => 50 * Math.floor(i / 4) + 22)
    .attr('y', (d, i) => (18 * i) % 72 + 2 * (i % 4) + 13)
    .text(d => d);


  var draw_facet = function(isotype, position, data) {

    var current_facet = isotype + '-' + position;
    var stacked = d3.stack().keys(features)
      .offset(d3.stackOffsetExpand)(data);    

    var bar_x_scale = d3.scaleBand()
      .domain(data.map(function(d) { return d.group; }).sort())
      .rangeRound([0, facet_width])
      .padding(0.1);

    var bar_y_scale = d3.scaleLinear()
      .domain([d3.min(stacked, stackMin), d3.max(stacked, stackMax)])
      .range([0, facet_height - 5]);

    function stackMin(stacked) {
      return d3.min(stacked, function(d) { return d[0]; });
    }

    function stackMax(stacked) {
      return d3.max(stacked, function(d) { return d[1]; });
    }

    var facet = d3.select('#distribution')
      .append('g')
      .attr('class', 'facet')
      .attr('id', current_facet.replace(':', '-'))
      .attr('isotype', isotype)
      .attr('position', position)
      .attr('transform', d => {
        x = isotype_scale(isotype) + y_axis_buffer;
        y = position_scale(position) + 22;
        return "translate(" + x + "," + y + ")";
      })

    var bars = facet.append('g')
      .selectAll('g')
      .data(stacked)
      .enter()
      .append('g')
      .attr("fill", d => feature_scale(d.key))
      .on('mouseover', d => {
        tooltip_feature.html(d.key);
        tooltip_feature.style('text-color', feature_scale(d.key));
      })
      .selectAll('rect')
      .data(d => d)
      .enter()
      .append('rect')
      .attr('class', 'distro-rect')
      .attr("x", d => bar_x_scale(d.data.group))
      .attr("y", d => bar_y_scale(d[0]))
      .attr("height", d => bar_y_scale(d[1] - d[0]))
      .attr("width", bar_x_scale.bandwidth)
      .attr("stroke-width", 1)
      .attr("stroke", "#333333")
      .attr('data-toggle', 'tooltip')
      .on('mouseover', function(d, i) {
        tooltip_position.html(position);
        tooltip_isotype.html(isotype);
        tooltip_group.html(d.data.group);
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        tooltip_count.html(plot_data[isotype][position].filter(x => x['group'] == d.data.group)[0][d3.select('#tooltip-feature').html()]);
        $('.tooltip-distribution').css({
          opacity: 0.9,
        }).position({
          my: "left top",
          of: d3.event,
          collision: "flip"
        });
        highlight_cloverleaf_tooltip(position);
        d3.select(this)
          .transition()
          .duration(100)
          .attr('class', 'distro-rect-highlight');
      })
      .on('mousemove', function(d, i) {  
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        tooltip_count.html(plot_data[isotype][position].filter(x => x['group'] == d.data.group)[0][d3.select('#tooltip-feature').html()]);
        $('.tooltip-distribution').css({
          opacity: 0.9,
        }).position({
          my: "left top",
          of: d3.event,
          collision: "flip"
        });
      })
      .on('mouseout', function(d) {   
        tooltip.transition()    
          .duration(100)    
          .style('opacity', 0); 
        d3.select(this)
          .transition()
          .duration(100)
          .attr('class', 'distro-rect');
        d3.selectAll('circle').attr('class', 'tooltip-cloverleaf-circle');
      });

  };

  for (isotype of isotypes) {
    for (position of positions) {
      draw_facet(isotype, position, plot_data[isotype][position]);
    };
  };

  var tooltip = d3.select('.tooltip')
  var tooltip_position = tooltip.select('#tooltip-position');
  var tooltip_isotype = tooltip.select('#tooltip-isotype');
  var tooltip_group = tooltip.select('#tooltip-group');
  var tooltip_feature = tooltip.select('#tooltip-feature');
  var tooltip_freq = tooltip.select('#tooltip-freq');
  var tooltip_count = tooltip.select('#tooltip-count');

};

var draw_species_distribution = function(plot_data) {
  d3.select('#distribution-area .loading-overlay').style('display', 'none');
  var foci = Object.keys(plot_data).sort();
  var assembly_groups = Array.from(new Set([].concat.apply([], Object.keys(plot_data).map(focus => plot_data[focus].map(d => [d['assembly'], d['group']]).map(group => JSON.stringify(group)))))).map(group => JSON.parse(group)).sort((a, b) => parseInt(a[1]) - parseInt(b[1]));
  var assemblies = assembly_groups.map(x => x[0])
  var groups = Array.from(new Set(assembly_groups.map(x => x[1])))

  var group_sizes = Array.from(assembly_groups.map(x => x[1])
    .sort()
    .reduce((acc, val) => acc.set(val, 1 + (acc.get(val) || 0)), new Map())
    .values())
  
  var facet_height = 100 - 10 * foci.length;
  var x_axis_buffer = 7 * assemblies.reduce(function (a, b) { return a.length > b.length ? a : b; }).length;
  var legend_height = 80;
  var legend_width = 400;
  var y_axis_buffer = 140;
  var plot_width = Math.max(600, y_axis_buffer + 15 * assemblies.length + 15 * (groups.length - 1) + 20);
  var plot_height = legend_height + x_axis_buffer + facet_height * foci.length;
  
  var svg = d3.select('#distribution-area')
    .append('svg')
    .attr('id', 'distribution')
    .attr('width', plot_width)
    .attr('height', plot_height)

  // Set up scales and axes
  var focus_scale = d3.scaleBand()
    .domain(foci)
    .range([0, foci.length * facet_height])
    .padding(0.1);

  var focus_format = function(d, i) {
    var datapoint = plot_data[foci[i]][0];
    var focus_str = datapoint['position'].includes(':') ? datapoint['position'] : 'Position ' + datapoint['position'];
    if (datapoint['isotype'] != 'All' || datapoint['anticodon'] != 'All') {
      focus_str += ' / ' + datapoint['isotype']
      if (datapoint['anticodon'] != 'All') focus_str += '-' + datapoint['anticodon']
    }
    focus_str += datapoint['score'] != $('#id_focus-0-score').attr('score-range') ? '<br>' + datapoint['score'] : '';
    return focus_str;
  }

  var focus_axis = d3.axisLeft(focus_scale)
    .ticks(foci.length)
    .tickFormat(focus_format);


  function wrapAxisText(text) {
    text.each(function() {
      var text = d3.select(this);
      var lines = text.text().split('<br>');
      if (lines.length == 1) {
        text.text(null)
          .append("tspan")
          .text(lines[0])
          .attr("x", -10)
          .attr("y", text.attr("y"))
      }
      else {
        text.text(null)
          .append("tspan")
          .text(lines[0])
          .attr("x", -10)
          .attr("y", -5)
        text.append('tspan')
          .text(lines[1])
          .attr("x", -10)
          .attr("y", 0)
          .attr("dy", "1.1em")
      }

    })
  };

  // generate x axis and put spacers in between groups
  var x_axis_labels = [].concat.apply([], group_sizes
    .map((d, i) => assembly_groups
      .filter(assembly => assembly[1] == i + 1)
      .map(assembly => assembly[0])
      .sort()) // recreate assembly groups without indexes
    .map((d, i) => i != group_sizes.length - 1 ? d.concat(['spacer' + i]) : d) // add spacer
  )
  
  // use unique label ids
  var x_axis_label_ids = [].concat.apply([], group_sizes
    .map((d, i) => assembly_groups
      .filter(assembly => assembly[1] == i + 1)
      .map(assembly => (assembly[0] + '-' + assembly[1]).replace(/[^a-zA-Z0-9\-]/g, '_'))
      .sort()
    )
    .map((d, i) => i != group_sizes.length - 1 ? d.concat(['spacer' + i]) : d) // add spacer
  )

  var assembly_group_format = function(d, i) { return x_axis_labels[i]; }

  var assembly_group_scale = d3.scaleBand()
    .domain(Object.values(x_axis_label_ids))
    .range([10, Math.max(15 * x_axis_labels.length, 30)])
    .paddingInner(0.1)

  var assembly_group_axis = d3.axisBottom(assembly_group_scale)
    .ticks(x_axis_labels.length)
    .tickFormat(assembly_group_format)

  svg.append('g')
    .attr('class', 'xaxis')
    .attr('transform', 'translate(' + y_axis_buffer + ', ' + (plot_height - legend_height - x_axis_buffer) + ')')
    .call(assembly_group_axis);

  svg.selectAll('.xaxis text')
    .attr('class', 'axis-text')
    .attr('text-anchor', 'end')
    .attr('transform', function(d) { return 'translate(-' + this.getBBox().height + ', ' + (this.getBBox().height) + ') rotate(-90)'; });


  svg.selectAll('.xaxis .tick')
    .attr('opacity', d => {
      if (d.substring(0, 6) == 'spacer') return 0;
      return 1;
    })

  svg.append('g')
    .attr('class', 'yaxis')
    .attr('transform', 'translate(' + y_axis_buffer + ', 0)')
    .call(focus_axis)
    .selectAll('.tick text')
    .call(wrapAxisText);

  svg.selectAll('.yaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + d.replace(':', '-'))

  // create legend
  var legend = svg.append('g')
    .attr('id', 'legend')
    .attr('transform', 'translate(' + (y_axis_buffer / 2 + (plot_width - legend_width) / 2) + ', ' + (plot_height - legend_height) + ')')
  
  legend.selectAll('rect')
    .data(feature_legend_scale.domain())
    .enter()
    .append('rect')
    .attr('class', 'legend-rect')
    .attr('id', d => 'legend-rect-' + d.replace(/[^a-zA-Z0-9\-]/g, '-'))
    .attr('x', (d, i) => 50 * Math.floor(i / 4))
    .attr('y', (d, i) => (18 * i) % 72 + 2 * (i % 4))
    .attr("width", 18)
    .attr("height", 18)
    .style('fill', d => feature_legend_scale(d))
  
  legend.selectAll('text')
    .data(feature_legend_scale.domain())
    .enter()
    .append('text')
    .attr('class', 'legend-label')
    .attr('id', d => 'legend-label-' + d.replace(/[^a-zA-Z0-9\-]/g, '_'))
    .attr('x', (d, i) => 50 * Math.floor(i / 4) + 22)
    .attr('y', (d, i) => (18 * i) % 72 + 2 * (i % 4) + 13)
    .text(d => d);

  var draw_facet = function(focus, group, data) {

    var current_facet = focus + '-' + group;
    var stacked = d3.stack().keys(all_features)
      .offset(d3.stackOffsetExpand)(data);

    var facet = d3.select('#distribution')
      .append('g')
      .attr('class', 'facet')
      .attr('id', current_facet.replace(':', '-'))
      .attr('focus', focus)
      .attr('group', group)
      .attr('transform', d => {
        return 'translate(' + y_axis_buffer + ', ' + focus_scale(focus) + ')';
      })

    function stackMin(stacked) {
      return d3.min(stacked, function(d) { return d[0]; });
    };

    function stackMax(stacked) {
      return d3.max(stacked, function(d) { return d[1]; });
    };

    var bar_y_scale = d3.scaleLinear()
      .domain([d3.min(stacked, stackMin), d3.max(stacked, stackMax)])
      .range([0, facet_height - 10]);

    var bars = facet.append('g')
      .selectAll('g')
      .data(stacked)
      .enter()
      .append('g')
      .attr("fill", d => feature_scale(d.key))
      .on('mouseover', d => {
        tooltip_feature.html(d.key);
        tooltip_feature.style('text-color', feature_scale(d.key));
      })
      .selectAll('rect')
      .data(d => d)
      .enter()
      .append('rect')
      .attr('class', 'distro-rect')
      .attr("x", function(d, i) {
        return assembly_group_scale((d.data.assembly + '-' + d.data.group).replace(/[^a-zA-Z0-9\-]/g, '_')) // reconstruct label id based on group
      })
      .attr("y", d => bar_y_scale(d[0]))
      .attr("width", assembly_group_scale.bandwidth)
      .attr("height", d => {
        if (isNaN(d[1]) || isNaN(d[0])) return 0;
        else return bar_y_scale(d[1] - d[0]);
      })
      .attr("stroke-width", 1)
      .attr("stroke", "#333333")
      .attr('data-toggle', 'tooltip')
      .on('mouseover', function(d, i) {
        tooltip_position.html(d.data.position);
        tooltip_isotype.html(d.data.isotype);
        tooltip_group.html(d.data.assembly);
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        tooltip_count.html(plot_data[d.data.focus].filter(x => x['assembly'] == d.data.assembly)[0][d3.select('#tooltip-feature').html()]);
        $('.tooltip-distribution').css({
          opacity: 0.9,
        }).position({
          my: "left top",
          of: d3.event,
          collision: "flip"
        });
        highlight_cloverleaf_tooltip(d.data.position);
      })
      .on('mousemove', function(d, i) {  
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        var feature = d3.select('#tooltip-feature').html()
        tooltip_count.html(plot_data[d.data.focus].filter(x => x['assembly'] == d.data.assembly)[0][d3.select('#tooltip-feature').html()]);
        $('.tooltip-distribution').css({
          opacity: 0.9,
        }).position({
          my: "left top",
          of: d3.event,
          collision: "flip"
        });
      })
      .on('mouseout', function(d) {   
        tooltip.transition()    
          .duration(100)    
          .style('opacity', 0); 
        d3.select(this)
          .transition()
          .duration(100)
          .attr('class', 'distro-rect');
        d3.selectAll('circle').attr('class', 'tooltip-cloverleaf-circle');
      });

  };

  for (focus of foci) {
    for (group of groups) {
      draw_facet(focus, group, plot_data[focus]);
    };
  };

  var tooltip = d3.select('.tooltip')
  var tooltip_position = tooltip.select('#tooltip-position');
  var tooltip_isotype = tooltip.select('#tooltip-isotype');
  var tooltip_group = tooltip.select('#tooltip-group');
  var tooltip_feature = tooltip.select('#tooltip-feature');
  var tooltip_freq = tooltip.select('#tooltip-freq');
  var tooltip_count = tooltip.select('#tooltip-count');
};