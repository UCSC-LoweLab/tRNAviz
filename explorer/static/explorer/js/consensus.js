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
	'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U', 'Absent': '-', 'N': 'N',
	'Purine': 'R', 'Pyrimidine': 'Y', 'C / G': 'S', 'A / U': 'W', 'A / C': 'M', 'G / U': 'K',
	'C / G / U': 'B', 'A / C / U': 'H', 'A / G / U': 'D', 'A / C / G': 'V',
	'Paired': ':', 'Mismatched': '÷'
}
var provenance = {'A': ['A'], 'C': ['C'], 'G': ['G'], 'U': ['U'], 
  'Purine': ['A', 'G', 'Purine'], 'Pyrimidine': ['C', 'U', 'Pyrimidine'], 
  'C / G': ['C', 'G', 'C / G'], 'A / U': ['A', 'U', 'A / U'], 'G / U': ['G', 'U', 'G / U'], 'A / C': ['A', 'C', 'Amino'],
  'C / G / U': ['C', 'G', 'U', 'C / G', 'G / U', 'Pyrimidine'], 
  'A / C / U': ['A', 'C', 'U', 'A / C', 'Pyrimidine', 'A / U'], 
  'A / G / U': ['A', 'G', 'U', 'Purine', 'A / U', 'G / U'], 
  'A / C / G': ['A', 'C', 'G', 'A / C', 'Purine', 'C / G'], 
  'Paired': ['C:G', 'G:C', 'A:U', 'U:A', 'G:U', 'U:G', 'G:U / U:G', 'C:G / G:C', 'A:U / U:A', 'A:U / C:G', 'G:C / U:A', 'Purine:Pyrimidine', 'Pyrimidine:Purine', 'N:N', 'Paired'], 
  'Absent': ['-', '-:-'], 'Mismatched': ['Mismatched', 'A:G', 'G:A', 'C:U', 'U:C', 'A:C', 'C:A', 'A:A', 'C:C', 'G:G', 'U:U'], '': [''], 
  'Malformed': ['A:-', '-:A', 'C:-', '-:C', 'G:-', '-:G', 'U:-', '-:U'],
  'A:U': ['A:U'], 'U:A': ['U:A'], 'G:C': ['G:C'], 'C:G': ['C:G'], 'G:U': ['G:U'], 'U:G': ['U:G'], 
  'Purine:Pyrimidine': ['G:C', 'A:U', 'Purine:Pyrimidine'], 'Pyrimidine:Purine': ['C:G', 'U:A', 'Pyrimidine:Purine'], 'G:U / U:G': ['G:U', 'U:G'], 'C:G / G:C': ['G:C', 'C:G'], 'A:U / U:A': ['A:U', 'U:A'], 'A:U / C:G': ['A:U', 'C:G'], 'G:C / U:A': ['G:C', 'U:A']}

var feature_scale = d3.scaleOrdinal()
  .domain(['', 'A', 'C', 'G', 'U', '-', 'Purine', 'Pyrimidine', 'Weak', 'Strong', 'Amino', 'Keto', 'B', 'D', 'H', 'V', 'N', 'Absent', 'Mismatched', 'Paired', 'High mismatch rate',
    'A / U', 'C / G', 'A / C', 'G / U', 'C / G / U', 'A / G / U', 'A / C / U', 'A / C / G',
    'A:U', 'U:A', 'G:C', 'C:G', 'G:U', 'U:G', 'A:G', 'G:A', 'C:U', 'U:C', 'A:C', 'C:A', 'A:A', 'C:C', 'G:G', 'U:U', 
    'Malformed', 'A:-', '-:A', 'C:-', '-:C', 'G:-', '-:G', 'U:-', '-:U', '-:-'])
  .range(['#ffffff', '#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#7f7f7f', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd', '#e5c494','#ccebd5','#ffa79d','#a6cdea','#ffffff', '#7f7f7f','#333333','#ffffcc','#b3b3b3',
    '#b3de69', '#fb72b2', '#c1764a', '#b26cbd', '#e5c494', '#ccebd5', '#ffa79d', '#a6cdea',
    '#17b3cf', '#9ed0e5', '#ff7f0e', '#ffbb78', '#a067bc', '#ceafd5', '#2fc69e', '#8be4cf', '#e377c2', '#f7b6d2', '#c47b70', '#f0a994', '#e7cb94', '#cedb9c', '#e7969c', '#9ca8de',
    '#333333', '#333333', '#333333', '#333333', '#333333', '#333333', '#333333', '#333333', '#333333', '#7f7f7f']);

var draw_cloverleaf = function(cloverleaf_data, isotype) {
  var cloverleaf_area_width = 525,
      cloverleaf_area_height = 550;

  var cloverleaf = d3.select('#cloverleaf-area')
    .append('svg')
    .attr('width', cloverleaf_area_width)
    .attr('height', cloverleaf_area_height)
    .attr('class', 'cloverleaf-svg')
    .attr('id', 'cloverleaf')
    .append('g')
    .attr('width', cloverleaf_area_width)
    .attr('height', cloverleaf_area_height)

  // append dummy rect to listen for click events, for unlocking selections
  cloverleaf.append('rect')
    .attr('width', cloverleaf_area_width)
    .attr('height', cloverleaf_area_height)
    .attr('fill', 'white')
    .on('click', function() {
    if (d3.select('#cloverleaf').attr('locked')) {
      dehighlight();
      d3.select('#cloverleaf').attr('locked', null);
    }
  });

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
  	update_cloverleaf(cloverleaf_data);
  });

  var update_cloverleaf = function(cloverleaf_data) {
  	new Promise(function(resolve, reject) {
  	  var coords = d3.select('#cloverleaf').selectAll('circle').data();
  	  for (var index in coords) {
  	  	coords[index]['feature'] = cloverleaf_data[coords[index]['position']]['feature'];
        coords[index]['datatype'] = cloverleaf_data[coords[index]['position']]['datatype'];
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
    var tooltip_position = tooltip.append('div').attr('class', 'tooltip-position')
    var tooltip_consensus = tooltip.append('div').attr('class', 'tooltip-consensus')
    var tooltip_datatype = tooltip.append('div').attr('class', 'tooltip-datatype')

    d3.select('#cloverleaf').selectAll('circle')
      .data(coords)
      .attr('id', d => 'circle' + d['position'])
      .attr('cx', d => d['x'])
      .attr('cy', d => d['y'])
      .attr('r', d => d['radius'])
      .classed('cloverleaf-near-consensus', d => d['datatype'] == 'Near-consensus')
      .attr('fill', d => feature_scale(d['feature']))
      .on('mouseover',  function(d) {
        if (!d3.select('#cloverleaf').attr('locked')) {
          dehighlight();
          highlight(d);
        }
      })
      .on('mousemove', function(d) {
        if (!d3.select('#cloverleaf').attr('locked')) {
          tooltip.style('left', d3.event.pageX + 'px').style('top', d3.event.pageY + 'px')
        }
      })
      .on('mouseout', d => d3.select('#cloverleaf').attr('locked') ? '' : dehighlight())
      .on('click', function(d) {
        if (!d3.select('#cloverleaf').attr('locked')) {
          d3.select('#cloverleaf').attr('locked', true);
          d3.select('.tooltip-cloverleaf').transition()    
            .duration(100)    
            .style('opacity', 0); 
        } else {
          dehighlight();
          d3.select('#cloverleaf').attr('locked', null);
          highlight(d);
        }
      });
  };

  function highlight(d) {
    d3.select('.tooltip-position').html('Position ' + d['position'])
    if (d['feature'] != '') {
      d3.select('.tooltip-consensus').html(d['feature'])
      d3.select('.tooltip-datatype').html(d['datatype'])
    }
    else {
      d3.select('.tooltip-consensus').html('')
      d3.select('.tooltip-datatype').html('')
    }
    d3.select('.tooltip-cloverleaf').transition()
      .duration(100)
      .style('opacity', .95)
      .style('left', d3.event.pageX + 'px')
      .style('top', d3.event.pageY + 'px');
    d3.select('#circle' + d['position'])
      .classed('cloverleaf-highlight', true);
    update_base_distro(d, 'cloverleaf', isotype);
  }
  function dehighlight() { 
    d3.select('.tooltip-cloverleaf')
      .style('opacity', 0); 
    d3.select('.cloverleaf-highlight')
      .classed('cloverleaf-highlight', false);
  }
  var set_cloverleaf_text_attributes = function(coords) {

    d3.select('#cloverleaf').selectAll('text')
      .data(coords)
      .attr('id', d => 'consensus' + d['position'])
      .attr('x', d => d['x'])
      .attr('y', d => { 
        if (d['position'].search('V') == -1) return d['y'] + 5;
        else return d['y'] + 4;
      })
      .attr('opacity', d => d['datatype'] == 'Near-consensus' ? 0.3 : 1)
      .attr('text-anchor', 'middle')
      .attr('font-size', d => {
        if (d['position'].search('V') == -1) return '15px';
        else return '10px';
      })
      .text(d => feature_code[d['feature']])
      .style('pointer-events', 'none');
  };
};

var update_base_distro;
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
    .attr('id', plot_type + '-base-distro')
    .append('g')
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
      .attr('id', plot_type + '-base-yaxis')
      .attr('class', 'base-yaxis')
      .attr('transform', 'translate(46, 10)')
      .call(base_freq_axis);
  } else {
    var isotype_max_freq = d3.max(Object.values(freq_data).map(d => d3.sum(Object.values(d['freqs']))));
    var isotype_base_freq_scale = d3.scaleLinear()
      .domain([0, isotype_max_freq])
      .range([base_distro_height, 0]);
    var isotype_base_freq_axis = d3.axisLeft(isotype_base_freq_scale);
    base_distro.append('g')
      .attr('id', plot_type + 'base-yaxis')
      .attr('class', 'base-yaxis')
      .attr('transform', 'translate(46, 10)')
      .call(isotype_base_freq_axis);
  }
  
  var base_feature_scale = d3.scaleBand()
    .domain(['A', 'C', 'G', 'U', 'Absent'])
    .range([0, base_distro_width / 2])
    .paddingInner(0.2);

  var base_feature_axis = d3.axisBottom(base_feature_scale);

  d3.axisBottom(base_feature_scale);

  base_distro.append('g')
    .attr('id', plot_type + '-base-xaxis')
    .attr('class', 'base-xaxis')
    .attr('transform', 'translate(53, ' + (base_distro_height + 15) + ')')
    .call(base_feature_axis);

  base_distro.selectAll('.base-xaxis .tick text, .base-yaxis .tick text')  // select all the text elements for the xaxis
    .attr('class', 'axis-text');

  update_base_distro = (coord, plot_type, isotype) => {
    var base_distro_width = 700,
        base_distro_height = 325;
      
    var base_distro = d3.select('#' + plot_type + '-base-distro');

    base_distro.selectAll('g.base-xaxis, g.base-yaxis, g.rects').remove();

    // update features for x axis
    var current_features = Array.from(Object.keys(coord['freqs'])).sort(function(a, b) {
      if (a == 'Absent') return 1;
      if (b == 'Absent') return -1;
      return a < b ? -1 : 1;
    });

    var base_feature_scale = d3.scaleBand()
      .domain(current_features)
      .range([0, current_features.length > 10 ? base_distro_width - 10 : base_distro_width / 2])
      .paddingInner(0.2);

    var base_feature_axis = d3.axisBottom(base_feature_scale);

    base_distro.append('g')
      .attr('id', plot_type + '-base-xaxis')
      .attr('class', 'base-xaxis')
      .attr('transform', 'translate(53, ' + (base_distro_height + 15) + ')')
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
      var max_freq = d3.sum(Object.values(coord['freqs']));
      var base_freq_scale = d3.scaleLinear()
        .domain([0, max_freq])
        .range([base_distro_height, 0]);
      var base_freq_axis = d3.axisLeft(base_freq_scale);
    }

    base_distro.append('g')
      .attr('class', 'base-yaxis')
      .attr('id', plot_type + '-base-yaxis')
      .attr('transform', 'translate(46, 10)')
      .call(base_freq_axis);

    base_distro.selectAll('.base-xaxis .tick text, .base-yaxis .tick text')  // select all the text elements for the xaxis
      .attr('class', 'axis-text');

    var rects = base_distro.append('g')
      .attr('class', 'rects')
      .attr('transform', 'translate(53, 10)')
      .selectAll('rect')
      .data(d3.entries(coord['freqs']))
      .enter()
      .append('rect')
      .attr('x', function(d) { return base_feature_scale(d['key']) }) //+ base_distro_width / Object.keys(coord['freqs']).length / 10; })
      .attr('y', function(d) { return plot_type == 'cloverleaf' ? base_freq_scale(d['value']) : isotype_base_freq_scale(d['value']); })
      .attr('id', function(d) {return 'cloverleaf-rect-' + d['key'].replace(':', '-') + '-' + d['value'];})
      .attr('height', function(d) { return base_distro_height - (plot_type == 'cloverleaf' ? base_freq_scale(d['value']) : isotype_base_freq_scale(d['value'])); })
      .attr('width', function() { return base_feature_scale.bandwidth(); })
      .attr('stroke', '#666666')
      .attr('stroke-width', '1')
      .style('fill', function(d) { return feature_scale(d['key']); })
      .style('fill-opacity', 0.7);
  }
};




var draw_tilemap = function(tilemap_data) {
  d3.select('#tilemap-area .loading-overlay').style('display', 'none')
  var tilemap_area_width = 1150,
      tilemap_area_height = 425,
      tile_width = 14;

  var isotypes = Array.from(new Set(tilemap_data.map(d => d['isotype']))).sort();
  var positions = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '8', '9', '10:25', '11:24', '12:23', '13:22', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '26', '27:43', '28:42', '29:41', '30:40', '31:39', '32', '33', '34', '35', '36', '37', '38', '44', '45', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', 'V1', 'V2', 'V3', 'V4', 'V5', '46', '47', '48', '49:65', '50:64', '51:63', '52:62', '53:61', '54', '55', '56', '57', '58', '59', '60', '73'];

  var tilemap = d3.select('#tilemap-area')
    .append('svg')
    .attr('width', tilemap_area_width)
    .attr('height', tilemap_area_height)
    .attr('class', 'tilemap-svg')
    .attr('id', 'tilemap')
    .append('g')
    .attr('width', tilemap_area_width)
    .attr('height', tilemap_area_height);
  
  // append dummy rect to listen for click events, for unlocking selections
  tilemap.append('rect')
    .attr('width', tilemap_area_width)
    .attr('height', tilemap_area_height)
    .attr('fill', 'white')
    .on('click', function() {
    if (d3.select('#tilemap').attr('locked')) {
      dehighlight();
      d3.select('#tilemap').attr('locked', null);
    }
  });

  // build scales and axes
  var position_scale = d3.scaleLinear()
    .domain([0, positions.length - 1])
    .range([50, 1120]);

  var position_axis = d3.axisBottom(position_scale)
    .ticks(positions.length)
    .tickFormat(d => positions[d]);

  var isotype_scale = d3.scaleLinear()
    .domain([0, isotypes.length - 1])
    .range([10, 350]);

  var isotype_axis = d3.axisLeft(isotype_scale)
    .ticks(isotypes.length)
    .tickFormat(d => isotypes[d]);


  tilemap.append('g')
    .attr('class', 'yaxis')
    .attr('transform', 'translate(45, 7)')
    .call(isotype_axis);

  tilemap.append('g')
    .attr('class', 'xaxis')
    .attr('transform', 'translate(7, 368)')
    .call(position_axis)
    .selectAll('.xaxis text')
    .attr('text-anchor', 'end');

  tilemap.selectAll('.xaxis g')
    .append('g')
    .attr('class', 'xaxis-text')
    .attr('transform', 'rotate(-90) translate(-10, -13)');

  $(d3.selectAll('.xaxis text').nodes()).each(function() {
    this.nextSibling.append(this);
  })

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
    .attr('id', d => 'tile-' + d['isotype'] + '-' + d['position'].replace(':', '-'))
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
    .attr('stroke', d => {
      if (d['datatype'] == 'Consensus') return '#666666';
      else return '#999999';
    })
    .attr('stroke-width', d => {
      if (d['datatype'] == 'Consensus') return 1.5;
      else return 1;
    })
    .attr('data-consensus', d => d['consensus'])
    .style('fill', d => {
      if (d['consensus'] != '') {
        return feature_scale(d['consensus']);
      } else {
        return '#ffffff';
      }
    }).style('fill-opacity', d => {
      if (d['datatype'] == 'Consensus') return 1;
      else return 0.7;
    }).on('mouseover', d => d3.select('#tilemap').attr('locked') ? '' : highlight(d))
    .on('mouseout', d => d3.select('#tilemap').attr('locked') ? '' : dehighlight(d))
    .on('click', function(d) {
      if (!d3.select('#tilemap').attr('locked')) {
        d3.select('#tilemap').attr('locked', true);
      } else {
        dehighlight();
        d3.select('#tilemap').attr('locked', null);
        highlight(d);
      }
    });
  function highlight(d) {
    d3.selectAll('#tile-' + d['isotype'] + '-' + d['position'].replace(':', '-'))
      .classed('tile-focus', true)
      .attr('stroke', '#ff0000')
      .attr('stroke-width', '2.5');
    d3.select('#tick-' + d['isotype'].replace(':', '-'))
      .attr('class', 'axis-focus');
    d3.select('#tick-' + d['position'].replace(':', '-'))
      .attr('class', 'axis-focus');
    update_base_distro(d, 'tilemap', d['isotype']);
  }
  function dehighlight(d) {
    d3.selectAll('.tile-focus')
      .classed('tile-focus', false)
      .attr('stroke', d => {
        if (d['datatype'] == 'Consensus') return '#666666';
        else return '#999999';
      }).attr('stroke-width', d => {
        if (d['datatype'] == 'Consensus') return 1.5;
        else return 1;
      }).style('fill-opacity', d => {
        if (d['datatype'] == 'Consensus') return 1;
        else return 0.7;
      });
    d3.selectAll('.axis-focus')
      .attr('class', 'axis-text');
  }
};

var tax_json_to_table = function(table_data) {
  header = '<th scope="col">Rank</th><th scope="col">Clade</th><th scope="col">No. tRNAs</th>'
  body = ''
  table_data.map(d => body += '<tr><td>' + capitalizeFirstLetter(d['rank']) + '</td><td>' + d['clade'] + '</td><td>' + d['count'] + '</td></tr>')
  table = '<table class="table"><thead><tr>' + header + '</tr></thead><tbody>' + body + '</tbody></table>';
  return table;
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

var cons_json_to_table = function(table_data) {
  domain = table_data.filter(d => d['position'] == 'clade')[0]['domain']
  clade = table_data.filter(d => d['position'] == 'clade')[0]['clade']
  header = '<th scope="col">Position</th><th scope="col">' + domain + '</th><th scope="col">' + clade + '</th>'
  body = ''
  table_data.filter(d => d['position'] != 'clade').map(function(d) {
    body += '<tr><td>' + d['position'] + '</td><td>' + d['domain'] + '</td>'
    if (d['clade'] == d['domain']) body += '<td class="cons-match">' + d['clade'] + '</td></tr>'
    else if (provenance[d['domain']].includes(d['clade']) || d['domain'] == '') body += '<td>' + d['clade'] + '</td></tr>'
    else if (d['clade'] == '') body += '<td class="cons-mismatch">N/A</td></tr>'
    else body += '<td class="cons-mismatch">' + d['clade'] + '</td></tr>'
  })

  table = table = '<table class="table"><thead><tr>' + header + '</tr></thead><tbody>' + body + '</tbody></table>';
  return table;
}