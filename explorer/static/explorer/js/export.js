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


$(document).ready(function() {
  $('#cloverleaf-download-pdf').click(function() {
    download_pdf('cloverleaf');
  })
  $('#cloverleaf-download-png').click(function() {
    download_png('cloverleaf');
  });

});
// 


var download_pdf = function(id) {
  selector = $('#' + id);
  svg_selector = selector.clone();
  svg_selector.find('*').each(function() {
    if (this.id != '') $(this).css($('#' + this.id).getStyleObject())
  })
  svg = svg_selector[0];
  pdf = new jsPDF('l', 'pt', [selector.width(), selector.height()]);
  svg2pdf(svg, pdf, {xOffset: 5, yOffset: 5, scale: 0.96});
  pdf.save(id + '.pdf');
}
var png, canvas;
var download_png = function(id) {
  selector = $('#' + id);
  svg_selector = selector.clone();
  svg_selector.find('*').each(function() {
    if (this.id != '') {
      styles = $('#' + this.id).getStyleObject()
      // filter attributes - canvg does not deal well with fill-opacity
      allowed_styles = ['backgroundColor', 'color', 'cx', 'cy', 'display', 'dominantBaseline', 'fill', 'fillOpacity', 'fillRule', 'float', 'fontFamily', 'fontSize', 'fontStyle', 'fontWeight', 'height', 'lineHeight', 'marginBottom', 'marginLeft', 'marginRight', 'marginTop', 'opacity', 'outlineColor', 'overflowWrap', 'overflowX', 'overflowY', 'r', 'rx', 'ry', 'stroke', 'strokeColor', 'strokeOpacity', 'strokeWidth', 'textAlign', 'top', 'transform', 'verticalAlign', 'width', 'x', 'y', 'zIndex']
      filtered_styles = Object.keys(styles)
        .filter(key => allowed_styles.includes(key))
        .reduce((obj, key) => {
          obj[key] = styles[key];
          return obj;
        }, {});
      $(this).css(filtered_styles);
    }
  })
  
  svg_str = new XMLSerializer().serializeToString(svg_selector[0]);
  // base64 = "data:image/svg+xml;base64," + btoa(encodeURIComponent(svg_str))
  canvas = document.createElement('canvas');
  canvas.width = selector.width() * 2
  canvas.height = selector.height() * 2
  canvg(canvas, svg_str, {scaleWidth: selector.width() * 2, scaleHeight: selector.height() * 2, ignoreDimensions: true});
  download(canvas.toDataURL("image/png"), id + ".png", "image/png");
}
