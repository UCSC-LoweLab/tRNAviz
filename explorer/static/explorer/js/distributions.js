var all_features = ['A', 'C', 'G', 'U', '-', 'A:U', 'U:A', 'G:C', 'C:G', 'G:U', 'U:G', 'A:A', 'A:C', 'A:G', 'C:A', 'C:C', 'C:U', 'G:A', 'G:G', 'U:C', 'U:U', '-:A', '-:C', '-:G', '-:U']
var sorted_positions = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '8', '9', '10:25', '11:24', '12:23', '13:22', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '26', '27:43', '28:42', '29:41', '30:40', '31:39', '32', '33', '34', '35', '36', '37', '38', '44', '45', '46', '47', '48', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', 'V1', 'V2', 'V3', 'V4', 'V5', '49:65', '50:64', '51:63', '52:62', '53:61', '54', '55', '56', '57', '58', '59', '60', '73']

var draw_distribution = function(plot_data) {
  d3.select('#distribution-area .loading-overlay').style('display', 'none');

  var isotypes = Object.keys(plot_data).sort();
  var positions = Object.keys(plot_data[isotypes[0]]).sort((position1, position2) => sorted_positions.indexOf(position1) - sorted_positions.indexOf(position2));
  var features = Object.keys(plot_data[isotypes[0]][positions[0]][0]).filter(d => all_features.includes(d))
  var num_groups = plot_data[isotypes[0]][positions[0]].length;

  var plot_width = 60 * isotypes.length;
  var plot_height = 65 * positions.length;
  var plot_margin = 100; // extra for placing axes and tooltips
  var facet_width = (plot_width - 30) / isotypes.length - 5;
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
    .rangeRound([10, plot_width - 30])
    .padding(0.1);

  var isotype_axis = d3.axisTop(isotype_scale);

  var position_scale = d3.scaleBand()
    .domain(positions)
    .rangeRound([10, plot_height - 30])
    .paddingInner(0.1);

  var position_axis = d3.axisLeft(position_scale);

  var feature_scale = d3.scaleOrdinal()
    .domain(['A', 'C', 'G', 'U', '-', 'A:A', 'A:C', 'A:G', 'A:U', 'C:A', 'C:C', 'C:G', 'C:U', 'G:A', 'G:C', 'G:G', 'G:U', 'U:A', 'U:C', 'U:G', 'U:U'])
    .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#cccccc'].concat(d3.schemeCategory20));

  var svg = d3.select('#distribution-svg');

  svg.append('g')
    .attr('class', 'xaxis')
    .attr('transform', 'translate(60, 20)')
    .call(isotype_axis);

  svg.append('g')
    .attr('class', 'yaxis')
    .attr('transform', 'translate(60, 20)')
    .call(position_axis);

  svg.selectAll('.xaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + isotypes[d])

  svg.selectAll('.yaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + positions[d])

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
        x = isotype_scale(isotype) + 60;
        y = position_scale(position) + 20;
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
        tooltip_feature.html(d.key);
        tooltip_feature.style('text-color', feature_scale(d.key));
        // tooltip_count.html(plot_data)
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
      .attr("stroke", "black")
      .on('mouseover', function(d, i) {
        tooltip_position.html(position);
        tooltip_isotype.html(isotype);
        tooltip_group.html(d.data.group);
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        tooltip_count.html(plot_data[isotype][position].filter(x => x['group'] == d.data.group)[0][d3.select('#tooltip-feature').html()]);
        tooltip.transition()
          .duration(100)
          .style('opacity', .9)
          .style('left', d3.event.pageX + 'px')
          .style('top', d3.event.pageY + 'px');
        d3.select(this)
          .transition()
          .duration(100)
          .attr('class', 'distro-rect-highlight');
      })
      .on('mousemove', function(d, i) {  
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        tooltip_count.html(plot_data[isotype][position].filter(x => x['group'] == d.data.group)[0][d3.select('#tooltip-feature').html()]);
        tooltip.style('left', d3.event.pageX + 'px')
          .style('top', d3.event.pageY + 'px');
        })
      .on('mouseout', function(d) {   
        tooltip.transition()    
          .duration(100)    
          .style('opacity', 0); 
        d3.select(this)
          .transition()
          .duration(100)
          .attr('class', 'distro-rect');
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
  var assembly_groups = []
  for (focus of foci) {
    assembly_groups = assembly_groups.concat(plot_data[focus].map(d => [d['assembly'], d['group']]))
  }
  assembly_groups = Array.from(new Set(assembly_groups.map(x => JSON.stringify(x)))).map(x => JSON.parse(x))
  var assemblies = assembly_groups.map(x => x[0])
  var groups = Array.from(new Set(assembly_groups.map(x => x[1])))

  var group_sizes = Array.from(assembly_groups.map(x => x[1])
    .sort()
    .reduce((acc, val) => acc.set(val, 1 + (acc.get(val) || 0)), new Map())
    .values())

  var plot_width = 250 * foci.length + 400;
  var plot_height = 20 * assemblies.length + 10 * groups.length;
  var plot_margin = 100; 
  var facet_width = 250;
  var y_axis_offset = 50 + 7 * assemblies.reduce(function (a, b) { return a.length > b.length ? a : b; }).length;

  d3.select('#distribution-area')
    .append('svg')
    .attr('id', 'distribution-svg')
    .attr('width', plot_width + plot_margin)
    .attr('height', plot_height + plot_margin)
    .append('g')
    .attr('id', 'distribution-plots');

  var focus_scale = d3.scaleBand()
    .domain(foci)
    .range([10, foci.length * facet_width])
    .padding(0.1);

  var focus_axis = d3.axisTop(focus_scale);

  // generate y axis and put spacers in between groups
  var assemblies_sorted = assembly_groups.sort((a, b) => parseInt(a[1]) - parseInt(b[1])).map(d => d[0]);
  var y_axis_labels = [];
  for (i in group_sizes) {
    y_axis_labels = y_axis_labels.concat(assemblies_sorted.splice(0, group_sizes[i]));
    if (i != groups.length - 1) y_axis_labels.push('spacer' + i);
  }

  var assembly_group_scale = d3.scaleBand()
    .domain(y_axis_labels)
    .range([10, 20 * assemblies.length])
    .paddingInner(0.1)

  var assembly_group_axis = d3.axisLeft(assembly_group_scale);

  var feature_scale = d3.scaleOrdinal()
    .domain(['A', 'C', 'G', 'U', '-', 'A:A', 'A:C', 'A:G', 'A:U', 'C:A', 'C:C', 'C:G', 'C:U', 'G:A', 'G:C', 'G:G', 'G:U', 'U:A', 'U:C', 'U:G', 'U:U'])
    .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#cccccc'].concat(d3.schemeCategory20));

  var svg = d3.select('#distribution-svg');

    
  svg.append('g')
    .attr('class', 'xaxis')
    .attr('transform', 'translate(' + y_axis_offset + ', 35)')
    .call(focus_axis);

  svg.selectAll('.xaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + foci[d])

  svg.append('g')
    .attr('class', 'yaxis')
    .attr('transform', 'translate(' + y_axis_offset + ', 40)')
    .call(assembly_group_axis);

  svg.selectAll('.yaxis text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + y_axis_labels[d])

  svg.selectAll('.yaxis .tick')
    .attr('opacity', d => {
      if (d.substring(0, 6) == 'spacer') return 0;
      return 1;
    })

  var draw_facet = function(focus, group, data) {

    var current_facet = focus + '-' + group;
    var stacked = d3.stack().keys(all_features)
      .offset(d3.stackOffsetExpand)(data); 


    var facet = d3.select('#distribution-plots')
      .append('g')
      .attr('class', 'facet')
      .attr('id', current_facet)
      .attr('focus', focus)
      .attr('group', group)
      .attr('transform', d => {
        x = focus_scale(focus) + y_axis_offset - 10;
        return "translate(" + x + ",40)";
      })

    function stackMin(stacked) {
      return d3.min(stacked, function(d) { return d[0]; });
    };

    function stackMax(stacked) {
      return d3.max(stacked, function(d) { return d[1]; });
    };

    var bar_x_scale = d3.scaleLinear()
      .domain([d3.min(stacked, stackMin), d3.max(stacked, stackMax)])
      .range([0, facet_width - 20]);

    var bars = facet.append('g')
      .selectAll('g')
      .data(stacked)
      .enter()
      .append('g')
      .attr("fill", d => feature_scale(d.key))
      .on('mouseover', d => {
        tooltip_feature.html(d.key);
        tooltip_feature.style('text-color', feature_scale(d.key));
        // tooltip_count.html(plot_data)
      })
      .selectAll('rect')
      .data(d => d)
      .enter()
      .append('rect')
      .attr('class', 'distro-rect')
      .attr("x", d => bar_x_scale(d[0]))
      .attr("y", d => assembly_group_scale(d.data.assembly))
      .attr("width", d => {
        adata = d;
        return bar_x_scale(d[1] - d[0]) })
      .attr("height", assembly_group_scale.bandwidth)
      .attr("stroke-width", 1)
      .attr("stroke", "black")
      .on('mouseover', function(d, i) {
        tooltip_position.html(d.data.focus.split('-')[1]);
        tooltip_isotype.html(d.data.focus.split('-')[0]);
        tooltip_group.html(d.data.group);
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        tooltip_count.html(plot_data[d.data.focus].filter(x => x['group'] == d.data.group && x['assembly'] == d.data.assembly)[0][d3.select('#tooltip-feature').html()]);
        tooltip.transition()
          .duration(100)
          .style('opacity', .9)
          .style('left', d3.event.pageX + 'px')
          .style('top', d3.event.pageY + 'px');
        d3.select(this)
          .transition()
          .duration(100)
          .attr('class', 'distro-rect-highlight');
      })
      .on('mousemove', function(d, i) {  
        tooltip_freq.html(Math.round((d[1] - d[0]) * 100) / 100)
        var feature = d3.select('#tooltip-feature').html()
        tooltip_count.html(plot_data[d.data.focus].filter(x => x['group'] == d.data.group && x['assembly'] == d.data.assembly)[0][d3.select('#tooltip-feature').html()]);
        tooltip.style('left', d3.event.pageX + 'px')
          .style('top', d3.event.pageY + 'px');
        })
      .on('mouseout', function(d) {   
        tooltip.transition()    
          .duration(100)    
          .style('opacity', 0); 
        d3.select(this)
          .transition()
          .duration(100)
          .attr('class', 'distro-rect');
      });

  };

  for (focus of foci) {
    for (group of groups) {
      draw_facet(focus, group, plot_data[focus].filter(x => x['group'] == group));
      console.log(plot_data[focus].filter(x => x['group'] == group).length)
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