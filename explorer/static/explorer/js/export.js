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

});
// $('#cloverleaf-download-png').click(() => download_png('cloverleaf'));


var download_pdf = function(id) {
  selector = $('#' + id)
  svg_selector = selector.clone()
  svg_selector.find('*').each(function() {
    if (this.id != '') $(this).css($('#' + this.id).getStyleObject())
  })
  svg = svg_selector[0]
  pdf = new jsPDF('l', 'pt', [selector.width(), selector.height()]);
  svg2pdf(svg, pdf, {xOffset: 5, yOffset: 5, scale: 0.98})
  pdf.save(id + '.pdf')
}
