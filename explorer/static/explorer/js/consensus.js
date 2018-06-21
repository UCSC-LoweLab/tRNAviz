// d3 data load with promise
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory(require('d3-request')) :
  typeof define === 'function' && define.amd ? define(['d3-request'], factory) :
  (global.d3 = global.d3 || {}, global.d3.promise = factory(global.d3));
} (this, (function (d3) { 'use strict';
  function promisify(caller, fn) {
    return function () {
      for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }
      return new Promise(function (resolve, reject) {
        var callback = function callback(error, data) {
          if (error) {
            reject(Error(error));
            return;
          }
          resolve(data);
        };
        fn.apply(caller, args.concat(callback));
      });
    };
  }
  var module$1 = {};
  ['csv', 'tsv', 'json', 'xml', 'text', 'html'].forEach(function (fnName) {
    module$1[fnName] = promisify(d3, d3[fnName]);
  });
  return module$1;
})));

var feature_code = {
	'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U', '-': '-', 'N': 'N',
	'Purine': 'R', 'Pyrimidine': 'Y', 'G / C': 'S', 'A / U': 'W', 'A / C': 'M', 'G / U': 'K',
	'C / G / U': 'B', 'A / C / U': 'H', 'A / G / U': 'D', 'A / C / G': 'V',
	'Paired': ':'
}

var draw_cloverleaf = function(cloverleaf_data) {
  cloverleaf_data = JSON.parse(cloverleaf_data)
  var window_scale_factor = 2;
  var svg_width = 1200;
  var svg_height = 1200;

  var cloverleaf_margin = 50,
      cloverleaf_width = 500,
      cloverleaf_height = 525,
      tilemap_width = 1200,
      tilemap_height = 700;

  d3.select('#svg-area')
    .append('svg')
    .attr('width', svg_width)
    .attr('height', svg_height)
    .attr('class', 'cloverleaf-svg')
    .append('g')
    .attr('id', 'cloverleaf')
    .attr('width', cloverleaf_width + cloverleaf_margin * 2)
    .attr('height', cloverleaf_height + cloverleaf_margin * 2)
    .append('g')
    .attr('id', 'base_distro')
    .attr('width', cloverleaf_width + cloverleaf_margin * 2)
    .attr('height', cloverleaf_height + cloverleaf_margin * 2)
    .attr('transform', 'translate(' + (cloverleaf_margin * 2 + cloverleaf_width) + ', ' + (cloverleaf_height / 4 + cloverleaf_margin) + ')');

  d3.select('body')
    .append('div')
    .attr('class', 'tooltip')  
    .style('opacity', 0);

  var coords_loaded = d3.promise.json(coords_path);
  coords_loaded.then(function(coords) {
	  
	  var circles = d3.select('#cloverleaf').selectAll('circle')
	    .data(coords, d => 'circle' + d['position'])
	    .enter()
	    .append('circle')
      .attr('class', 'cloverleaf-circle')
	    .attr('id', d => 'circle' + d['position'])
	    .attr('cx', d => d['x'])
	    .attr('cy', d => d['y'])
	    .attr('r', d => d['radius'])

    var circle_text = d3.select('#cloverleaf').selectAll('text')
      .data(coords, d => 'consensus' + d['position'])
      .enter()
      .append('text');
  }).then(function() {
  	update_cloverleaf(cloverleaf_data)
  });

};

var update_cloverleaf = function(cloverleaf_data) {
	new Promise(function(resolve, reject) {
	  var coords = d3.select('#cloverleaf').selectAll('circle').data();
	  for (var index in coords) {
	  	coords[index]['consensus'] = cloverleaf_data[coords[index]['position']]['consensus'];
	  	coords[index]['freqs'] = cloverleaf_data[coords[index]['position']]['freqs'];
	  }
	  resolve(coords);
  }).then(function(updated_coords) {
  	set_cloverleaf_circle_attributes(updated_coords);
    set_cloverleaf_text_attributes(updated_coords);
  })
};

var set_cloverleaf_circle_attributes = function(coords) {
  var tooltip = d3.select('.tooltip');
  var tooltip_position = tooltip.append('div')
  var tooltip_consensus = tooltip.append('div')
  var feature_scale = d3.scaleOrdinal()
    .domain(['', 'A', 'C', 'G', 'U', '-', 'Purine', 'Pyrimidine', 'Weak', 'Strong','Amino','Keto','B','D','H','V','N','Absent','Mismatched','Paired','High mismatch rate'])
    .range(['#ffffff', '#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#dddddd', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd','#e5c494','#ccebd5','#ffa79d','#a6cdea','white','#ffffff','#cccccc','#ffffcc','#222222']);

  d3.select('#cloverleaf').selectAll('circle')
    .data(coords)
    .attr('id', d => 'circle' + d['position'])
    .attr('cx', d => d['x'])
    .attr('cy', d => d['y'])
    .attr('r', d => d['radius'])
    .attr('fill', d => feature_scale(d['consensus']))
    .on('mouseover', function(d) {
      // tooltip.html()
      tooltip_position.html('Position ' + d['position'])
      tooltip_consensus.html(d['consensus'])
      tooltip.transition()
        .duration(100)
        .style('opacity', .9)
        .style('left', d3.event.pageX + 'px')
        .style('top', d3.event.pageY + 'px');
      d3.select(this)
        .transition()
        .duration(100)
        .attr('class', 'cloverleaf-highlight');

      d3.selectAll('#base_distro g').remove();
      draw_base_distro(d);
    })
    .on('mousemove', function() {  
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
        .attr('class', 'cloverleaf-circle');
    });
};

var set_cloverleaf_text_attributes = function(coords) {

  d3.select('#cloverleaf').selectAll('text')
    .data(coords)
    .attr('id', d => 'consensus' + d['position'])
    .attr('x', d => d['x'])
    .attr('y', d => { 
      if (d['position'].search('V') == -1) return d['y'] + 6;
      else return d['y'] + 4;
    })
    .attr('text-anchor', 'middle')
    .attr('font-size', d => {
      if (d['position'].search('V') == -1) return '15px';
      else return '10px';
    })
    .text(d => feature_code[d['consensus']])
    .style('pointer-events', 'none');
};

var draw_base_distro = function(coord) {

	var base_distro = d3.select('#base_distro');
	var current_features = Object.keys(coord['freqs']);
	var base_distro_plot_height = 200,
	  base_distro_plot_width = 400;

	var base_feature_scale = d3.scaleBand()
	  .domain(current_features)
	  .range([10, 490]);

	var base_feature_axis = d3.axisBottom(base_feature_scale);

	var base_freq_scale = d3.scaleLinear()
	  .domain([0, d3.max(Object.values(coord['freqs']))])
	  .range([200, 0]);

	var base_freq_axis = d3.axisLeft(base_freq_scale);

	var base_fill_scale = d3.scaleOrdinal()
	  .domain(['A', 'C', 'G', 'U', '-', 'A:A', 'A:C', 'A:G', 'A:U', 'C:A', 'C:C', 'C:G', 'C:U', 'G:A', 'G:C', 'G:G', 'G:U', 'U:A', 'U:C', 'U:G', 'U:U'])
	  .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8'].concat(d3.schemeCategory20));
	  // .domain(['A', 'C', 'G', 'U', '-', 'Purine','Pyrimidine','Weak','Strong','Amino','Keto','B','D','H','V','N','Absent','Mismatched','Paired','High mismatch rate'])
	  // .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#dddddd', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd','#e5c494','#ccebd5','#ffa79d','#a6cdea','white','#ffffff','#cccccc','#ffffcc','#222222']);

	base_distro.append('g')
	  .attr('class', 'base_xaxis')
	  .attr('transform', 'translate(0, 210)')
	  .call(base_feature_axis);

	base_distro.append('g')
	  .attr('class', 'base_yaxis')
	  .call(base_freq_axis);

	base_distro.selectAll('.base_xaxis text')  // select all the text elements for the xaxis
	  .attr('text-anchor', 'center');

	var rects = base_distro.append('g')
	  .attr('class', 'rects')
	  .selectAll('rect')
	  .data(d3.entries(coord['freqs']))
	  .enter()
	  .append('rect')
	  .attr('x', function(d) { return base_feature_scale(d['key']) + base_distro_plot_width / Object.keys(coord['freqs']).length / 10; })
	  .attr('y', function(d) { return base_freq_scale(d['value']); })
	  .attr('id', function(d) {return d['key'] + ' : ' + d['value'];})
	  .attr('height', function(d) { return base_distro_plot_height - base_freq_scale(d['value']); })
	  .attr('width', function() { return base_distro_plot_width / Object.keys(coord['freqs']).length; })
	  .attr('stroke', '#666666')
	  .attr('stroke-width', '1')
	  .style('fill', function(d) { return base_fill_scale(d['key']); })
	  .style('fill-opacity', 0.7);
};


var draw_tilemap = function() {
  
}