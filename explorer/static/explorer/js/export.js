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

var download_png = function(id) {
  selector = $('#' + id);
  svg_selector = selector.clone();
  svg_selector.find('*').each(function() {
    if (this.id != '') {
      styles = $('#' + this.id).getStyleObject()
      not_allowed_styles = ['filter', 'mask', 'maskType']
      filtered_styles = Object.keys(styles)
        .filter(key => !not_allowed_styles.includes(key))
        .reduce((obj, key) => {
          obj[key] = styles[key];
          return obj;
        }, {});
      $(this).css(filtered_styles);
    }
  })
  
  svg_str = new XMLSerializer().serializeToString(svg_selector[0]);
  canvas = document.createElement('canvas');
  canvas.width = selector.width() * 2
  canvas.height = selector.height() * 2
  canvg(canvas, svg_str, {scaleWidth: selector.width() * 2, scaleHeight: selector.height() * 2, ignoreDimensions: true});
  download(canvas.toDataURL("image/png"), id + ".png", "image/png");
}
var download_json = function(json) {
  download(JSON.stringify(json, null, 2), "data.json", 2);
}