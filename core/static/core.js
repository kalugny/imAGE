$(document).ready(function(){

    $('.popup').popup();

    var pics = d3.select('.container').selectAll('.image.segment')
        .data(PICTURES)
        .enter()
        .append('div')
            .attr('class', 'ui centered big image segment');

    pics.append('img')
        .attr('src', function(d) { return '/static/' + d.path; })
        .on('load', function(d){
            var img_width = this.width;
            var svg = d3.select(this.parentNode)
                .append('svg')
                    .attr('class', 'overlay');

            var x_factor = (parseInt(svg.style('width')) - parseInt(svg.style('padding-right')) - parseInt(svg.style('padding-left'))) / this.naturalWidth;
            var y_factor = (parseInt(svg.style('height')) - parseInt(svg.style('padding-top')) - parseInt(svg.style('padding-bottom')))  / this.naturalHeight;

            d.faces.forEach(function(f){
                var rect = svg.append('rect')
                    .attr('x', f.rect.left * x_factor)
                    .attr('y', f.rect.top * y_factor)
                    .attr('width', f.rect.width * x_factor)
                    .attr('height', f.rect.height * x_factor)
                    .attr('class', 'rect ' + f.gender)
                    .each(function(){
                        $(this).popup({
                            popup: $('.choose_person.popup'),
                            movePopup: false,
                            exclusive: true,
                            position: 'right center',
                            on: 'click',
                            distanceAway: f.rect.width * x_factor,
                            offset: f.rect.height * y_factor / 2,
                            onShow: function(){
                                var $select = this.find('select');
                                $select.val(f.person);
                                $select.off('change').on('change', function(){
                                    var val = $(this).val();
                                    $.post('/update_face/', $.param({face_id: f.face_id, person: val}), function(){
                                        f.person = val;
                                        t.text(f.person + ', ' + f.age);
                                    });
                                });
                            }
                        });
                    });

                var t = svg.append('text')
                    .attr('x', f.rect.left * x_factor)
                    .attr('y', f.rect.top * y_factor)
                    .attr('dy', '-0.35em')
                    .text(f.person != '' ? f.person + ", " + f.age : f.age);
            });
        });

});