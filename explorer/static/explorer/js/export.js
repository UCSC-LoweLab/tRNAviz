(function($){
    $.fn.getStyleObject = function(){
        var dom = this.get(0);
        var style;
        var returns = {};
        if(window.getComputedStyle){
            var camelize = function(a,b){
                return b.toUpperCase();
            }
            style = window.getComputedStyle(dom, null);
            for(var i=0;i<style.length;i++){
                var prop = style[i];
                var camel = prop.replace(/\-([a-z])/g, camelize);
                var val = style.getPropertyValue(prop);
                returns[camel] = val;
            }
            return returns;
        }
        if(dom.currentStyle){
            style = dom.currentStyle;
            for(var prop in style){
                returns[prop] = style[prop];
            }
            return returns;
        }
        return this.css();
    }
})(jQuery);

var make_filename = function(name, ext) {
  var now = new Date();
  var stamp = now.getFullYear()
    + ('0' + (now.getMonth() + 1)).slice(-2)
    + ('0' + now.getDate()).slice(-2)
    + '-' + ('0' + now.getHours()).slice(-2)
    + ('0' + now.getMinutes()).slice(-2)
    + ('0' + now.getSeconds()).slice(-2);
  return name + '_' + stamp + '.' + ext;
}

var download_pdf = function(id, name) {
  name = name || id;
  selector = $('#' + id);
  svg_selector = selector.clone();
  svg_selector.children().each(function() {
    if (this.id != '') $(this).css($('#' + this.id).getStyleObject());
    $(this).find('*').each(function() {
      if (this.id != '') $(this).css($('#' + this.id).getStyleObject());
    })
  })
  svg = svg_selector[0];
  if (selector.width() > selector.height()) {
    pdf = new jsPDF('l', 'pt', [selector.width(), selector.height()]);
  }
  else {
    pdf = new jsPDF('p', 'pt', [selector.width(), selector.height()]);
  }
  svg2pdf(svg, pdf, {xOffset: 5, yOffset: 5, scale: 0.98});
  pdf.save(make_filename(name, 'pdf'));
}

var download_png = function(id, name) {
  name = name || id;
  var selector = $('#' + id);
  var svg_selector = selector.clone();

  // SVG presentation properties that canvg needs as XML attributes (not CSS)
  var svg_properties = [
    'fill', 'fill-opacity', 'fill-rule',
    'stroke', 'stroke-width', 'stroke-opacity', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin',
    'opacity', 'display', 'visibility',
    'font-size', 'font-family', 'font-weight', 'font-style',
    'text-anchor', 'text-decoration', 'dominant-baseline'
  ];

  // Use index-based matching to avoid duplicate ID issues and handle elements without IDs
  var original_elements = selector.find('*').toArray();
  var clone_elements = svg_selector.find('*').toArray();

  for (var i = 0; i < original_elements.length; i++) {
    var computed = window.getComputedStyle(original_elements[i]);
    // Set as SVG attributes (not CSS) so canvg can read them
    for (var j = 0; j < svg_properties.length; j++) {
      var val = computed.getPropertyValue(svg_properties[j]);
      if (val) clone_elements[i].setAttribute(svg_properties[j], val);
    }
  }

  var svg_str = new XMLSerializer().serializeToString(svg_selector[0]);
  var canvas = document.createElement('canvas');
  canvas.width = selector.width() * 2;
  canvas.height = selector.height() * 2;
  var ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  canvg(canvas, svg_str, {scaleWidth: selector.width() * 2, scaleHeight: selector.height() * 2, ignoreDimensions: true, ignoreClear: true});
  download(canvas.toDataURL("image/png"), make_filename(name, 'png'), "image/png");
}

var download_svg = function(id, name) {
  name = name || id;
  var selector = $('#' + id);
  var svg_selector = selector.clone();

  var svg_properties = [
    'fill', 'fill-opacity', 'fill-rule',
    'stroke', 'stroke-width', 'stroke-opacity', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin',
    'opacity', 'display', 'visibility',
    'font-size', 'font-family', 'font-weight', 'font-style',
    'text-anchor', 'text-decoration', 'dominant-baseline'
  ];

  var original_elements = selector.find('*').toArray();
  var clone_elements = svg_selector.find('*').toArray();

  for (var i = 0; i < original_elements.length; i++) {
    var computed = window.getComputedStyle(original_elements[i]);
    for (var j = 0; j < svg_properties.length; j++) {
      var val = computed.getPropertyValue(svg_properties[j]);
      if (val) clone_elements[i].setAttribute(svg_properties[j], val);
    }
  }

  svg_selector[0].setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  var svg_str = new XMLSerializer().serializeToString(svg_selector[0]);
  download("data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg_str), make_filename(name, 'svg'), "image/svg+xml");
}

var download_json = function(json) {
  download(JSON.stringify(json, null, 2), "data.json", 2);
}
