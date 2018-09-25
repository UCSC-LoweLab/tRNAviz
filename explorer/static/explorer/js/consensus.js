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
	'Paired': ':', 'Mismatched': '÷'
}

var feature_scale = d3.scaleOrdinal()
  .domain(['', 'A', 'C', 'G', 'U', '-', 'Purine', 'Pyrimidine', 'Weak', 'Strong','Amino','Keto','B','D','H','V','N','Absent','Mismatched','Paired','High mismatch rate'])
  .range(['#ffffff', '#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#dddddd', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd','#e5c494','#ccebd5','#ffa79d','#a6cdea','white','#ffffff','#cccccc','#ffffcc','#222222']);

var draw_cloverleaf = function(cloverleaf_data) {
  var cloverleaf_area_width = 525,
      cloverleaf_area_height = 550;

  d3.select('#cloverleaf-area')
    .append('svg')
    .attr('width', cloverleaf_area_width)
    .attr('height', cloverleaf_area_height)
    .attr('class', 'cloverleaf-svg')
    .append('g')
    .attr('transform', 'translate(5, 0)') // Otherwise, position 18 outline is cut off
    .attr('id', 'cloverleaf')
    .attr('width', cloverleaf_area_width)
    .attr('height', cloverleaf_area_height)

  d3.select('body')
    .append('div')
    .attr('class', 'tooltip tooltip-cloverleaf')  
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
  var tooltip = d3.select('.tooltip-cloverleaf');
  var tooltip_position = tooltip.append('div')
  var tooltip_consensus = tooltip.append('div')

  d3.select('#cloverleaf').selectAll('circle')
    .data(coords)
    .attr('id', d => 'circle' + d['position'])
    .attr('cx', d => d['x'])
    .attr('cy', d => d['y'])
    .attr('r', d => d['radius'])
    .attr('fill', d => feature_scale(d['consensus']))
    .on('mouseover', function(d) {
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
      update_base_distro(d, 'cloverleaf', '');
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
      if (d['position'].search('V') == -1) return d['y'] + 5;
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

var update_base_distro;
var adata;
var draw_base_distro = function(freq_data, plot_type) {
  var base_distro_area_width = 750,
      base_distro_area_height = 375,    
      base_distro_width = 700,
      base_distro_height = 325;

  var base_distro = d3.select('#' + plot_type + '-base-distro-area')
    .append('svg')
    .attr('width', base_distro_area_width)
    .attr('height', base_distro_area_height)
    .attr('class', plot_type + '-base-distro-svg')
    .append('g')
    .attr('id', plot_type + '-base-distro')
    .attr('width', base_distro_area_width)
    .attr('height', base_distro_area_height);

  // initialize x and y axes (for initial UI)
  if (plot_type == 'cloverleaf') {
    var max_freq = d3.max(Object.values(freq_data).map(d => d3.sum(Object.values(d['freqs']))));
    var base_freq_scale = d3.scaleLinear()
      .domain([0, max_freq])
      .range([base_distro_height, 0]);
    var base_freq_axis = d3.axisLeft(base_freq_scale);
    base_distro.append('g')
      .attr('class', 'base_yaxis')
      .attr('transform', 'translate(35, 10)')
      .call(base_freq_axis);
  } else {
    var isotype_max_freq = d3.max(Object.values(freq_data).map(d => d3.sum(Object.values(d['freqs']))));
    var isotype_base_freq_scale = d3.scaleLinear()
      .domain([0, isotype_max_freq])
      .range([base_distro_height, 0]);
    var isotype_base_freq_axis = d3.axisLeft(isotype_base_freq_scale);
    base_distro.append('g')
      .attr('class', 'base_yaxis')
      .attr('transform', 'translate(35, 10)')
      .call(isotype_base_freq_axis);
  }

  
  var base_feature_scale = d3.scaleBand()
    .domain(['A', 'C', 'G', 'U', 'absent'])
    .range([0, base_distro_width / 2])
    .paddingInner(0.2);

  var base_feature_axis = d3.axisBottom(base_feature_scale);

  d3.axisBottom(base_feature_scale);

  base_distro.append('g')
    .attr('class', 'base_xaxis')
    .attr('transform', 'translate(42, ' + (base_distro_height + 15) + ')')
    .call(base_feature_axis);

  update_base_distro = (coord, plot_type, isotype) => {
    var base_distro_width = 700,
        base_distro_height = 325;
      
    var base_distro = d3.select('#' + plot_type + '-base-distro');

    base_distro.selectAll('g.base_xaxis, g.base_yaxis, g.rects').remove();

    // update features for x axis
    var current_features = Array.from(Object.keys(coord['freqs'])).sort();

    var base_feature_scale = d3.scaleBand()
      .domain(current_features)
      .range([0, current_features.length > 10 ? base_distro_width : base_distro_width / 2])
      .paddingInner(0.2);

    var base_feature_axis = d3.axisBottom(base_feature_scale);

    base_distro.append('g')
      .attr('class', 'base_xaxis')
      .attr('transform', 'translate(42, ' + (base_distro_height + 15) + ')')
      .call(base_feature_axis);

    // update freqs for y axis
    if (plot_type == 'tilemap') {
      var isotype_max_freq = d3.max(Object.values(freq_data)
        .filter(d => d['isotype'] == isotype)
        .map(d => d3.sum(Object.values(d['freqs'])))
        );
      var isotype_base_freq_scale = d3.scaleLinear()
        .domain([0, isotype_max_freq])
        .range([base_distro_height, 0]);
      var base_freq_axis = d3.axisLeft(isotype_base_freq_scale);
    } else {
      var max_freq = d3.sum(d3.nest()
        .key(d => d['isotype'])
        .rollup(d => d3.max(Object.values(d).map(value => d3.max(Object.values(value['freqs'])))))
        .entries(freq_data)
        .map(d => d['value']))
      var base_freq_scale = d3.scaleLinear()
        .domain([0, max_freq])
        .range([base_distro_height, 0]);
      var base_freq_axis = d3.axisLeft(base_freq_scale);
    }

    base_distro.append('g')
      .attr('class', 'base_yaxis')
      .attr('transform', 'translate(35, 10)')
      .call(base_freq_axis);


    // update features for fill scale
    var base_fill_scale = d3.scaleOrdinal()
      .domain(['A', 'C', 'G', 'U', '-', 'A:A', 'A:C', 'A:G', 'A:U', 'C:A', 'C:C', 'C:G', 'C:U', 'G:A', 'G:C', 'G:G', 'G:U', 'U:A', 'U:C', 'U:G', 'U:U'])
      .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8'].concat(d3.schemeCategory20));

    base_distro.selectAll('.base_xaxis .tick text, .base_yaxis .tick text')  // select all the text elements for the xaxis
      .attr('text-anchor', 'center')
      .attr('class', 'axis-text');

    var rects = base_distro.append('g')
      .attr('class', 'rects')
      .attr('transform', 'translate(42, 10)')
      .selectAll('rect')
      .data(d3.entries(coord['freqs']))
      .enter()
      .append('rect')
      .attr('x', function(d) { return base_feature_scale(d['key']) }) //+ base_distro_width / Object.keys(coord['freqs']).length / 10; })
      .attr('y', function(d) { return plot_type == 'cloverleaf' ? base_freq_scale(d['value']) : isotype_base_freq_scale(d['value']); })
      .attr('id', function(d) {return d['key'] + ' : ' + d['value'];})
      .attr('height', function(d) { return base_distro_height - (plot_type == 'cloverleaf' ? base_freq_scale(d['value']) : isotype_base_freq_scale(d['value'])); })
      .attr('width', function() { return base_feature_scale.bandwidth(); })
      .attr('stroke', '#666666')
      .attr('stroke-width', '1')
      .style('fill', function(d) { return base_fill_scale(d['key']); })
      .style('fill-opacity', 0.7);
  }
};




var draw_tilemap = function(tilemap_data) {
  d3.select('#tilemap-area .loading-overlay').style('display', 'none')
  var tilemap_area_width = 1220,
      tilemap_area_height = 450,
      tile_width = 15;

  var isotypes = Array.from(new Set(tilemap_data.map(d => d['isotype']))).sort();
  var positions = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '8', '9', '10:25', '11:24', '12:23', '13:22', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '26', '27:43', '28:42', '29:41', '30:40', '31:39', '32', '33', '34', '35', '36', '37', '38', '44', '45', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', 'V1', 'V2', 'V3', 'V4', 'V5', '46', '47', '48', '49:65', '50:64', '51:63', '52:62', '53:61', '54', '55', '56', '57', '58', '59', '60', '73'];

  var tilemap = d3.select('#tilemap-area')
    .append('svg')
    .attr('width', tilemap_area_width)
    .attr('height', tilemap_area_height)
    .attr('class', 'tilemap-svg')
    .append('g')
    .attr('id', 'tilemap')
    .attr('width', tilemap_area_width)
    .attr('height', tilemap_area_height);

  // build scales and axes
  var position_scale = d3.scaleLinear()
    .domain([0, positions.length - 1])
    .range([50, 1200]);

  var position_axis = d3.axisBottom(position_scale)
    .ticks(positions.length)
    .tickFormat(d => positions[d]);

  var isotype_scale = d3.scaleLinear()
    .domain([0, isotypes.length - 1])
    .range([10, 360]);

  var isotype_axis = d3.axisLeft(isotype_scale)
    .ticks(isotypes.length)
    .tickFormat(d => isotypes[d]);

  var feature_scale = d3.scaleOrdinal()
    // .domain(['A', 'C', 'G', 'U', '-', 'A:A', 'A:C', 'A:G', 'A:U', 'C:A', 'C:C', 'C:G', 'C:U', 'G:A', 'G:C', 'G:G', 'G:U', 'U:A', 'U:C', 'U:G', 'U:U'])
    .domain(['A', 'C', 'G', 'U', '-', 'Purine','Pyrimidine','Weak','Strong','Amino','Keto','B','D','H','V','N','Absent','Mismatched','Paired','High mismatch rate'])
    .range(['#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#dddddd', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd','#e5c494','#ccebd5','#ffa79d','#a6cdea','white','#ffffff','#cccccc','#ffffcc','#222222']);

  tilemap.append('g')
    .attr('class', 'xaxis')
    .attr('transform', 'translate(7, 380)')
    .call(position_axis);

  tilemap.append('g')
    .attr('class', 'yaxis')
    .attr('transform', 'translate(45, 7)')
    // .attr('text-anchor', 'right')
    .call(isotype_axis);

  tilemap.selectAll('.xaxis text')  // select all the text elements for the xaxis
    .attr('text-anchor', 'end')
    .attr('transform', function(d) { return 'translate(-' + this.getBBox().height + ', ' + (this.getBBox().height) + ') rotate(-90)'; });

  // Give each tick a unique identifier for bolding on mouseover
  tilemap.selectAll('.xaxis .tick text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + positions[d].replace(':', '-'));

  tilemap.selectAll('.yaxis .tick text')
    .attr('class', 'axis-text')
    .attr('id', d => 'tick-' + isotypes[d].replace(':', '-'));

  var tiles = tilemap.selectAll('rect')
    .data(tilemap_data)
    .enter()
    .append('rect')
    .attr('id', d => d['isotype'] + ' ' + d['position'])
    .attr('x', d => { 
        var x = position_scale(positions.findIndex(position => position == d['position']));
        if (d['type'] == 'right') { return x + tile_width / 2; } 
        else if (['left', 'single', 'block'].includes(d['type'])) { return x; }
      })
    .attr('y', d => isotype_scale(isotypes.findIndex(isotype => isotype == d['isotype'])))
    .attr('width', d => {
      if (d['type'] == 'single' || d['type'] == 'block') {
        return tile_width;
      } else if (d['type'] == 'left' || d['type'] == 'right') {
        return tile_width / 2;
      }
    })
    .attr('height', tile_width)
    .attr('stroke', '#666666')
    .attr('stroke-width', '1.5')
    .attr('data-consensus', d => d['consensus'])
    .style('fill', d => {
      if (d['consensus'] != '') {
        return feature_scale(d['consensus']);
      } else {
        return '#ffffff';
      }
    }).style('fill-opacity', d => {
      if (d['type'] == 'block') return 0;
      else return 0.7;
    }).on('mouseover', function(d) {
      d3.select(this)
        .attr('stroke', '#ff0000')
        .attr('stroke-width', '2.5');
      d3.select('#tick-' + d['isotype'].replace(':', '-'))
        .attr('class', 'axis-focus');
      d3.select('#tick-' + d['position'].replace(':', '-'))
        .attr('class', 'axis-focus');
      update_base_distro(d, 'tilemap', d['isotype']);
    }).on('mouseout', function(d) {
      d3.select(this)
        .attr('stroke', '#666666')
        .attr('stroke-width', '1.5');
      d3.select('#tick-' + d['isotype'].replace(':', '-'))
        .attr('class', 'axis-text');
      d3.select('#tick-' + d['position'].replace(':', '-'))
        .attr('class', 'axis-text');
    });
};