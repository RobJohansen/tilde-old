var timeline;
var data;

function select(e) {
  alert(e);
}

function go() {
  $.get(
    '/load',
    'ts=' + $('#terms'),
    function(o) {
      data = new google.visualization.DataTable(o.data, 0.6);
      refresh();
    });
}

function refresh() {
  timeline.draw(data, { width : '100%' });
}

$(document).ready(function() {
  $('#go').click(go);

  $('#terms').keydown(function(e) {
    if (e.which == 13) {
      go();
    } else if (e.which == 222) {
      $('#tilds').focus();

      return false;
    }
  });

  $('#tilds').keydown(function(e) {
    if (e.which == 13) {
      go();
    } else if (e.which == 8 && $(this).val() == '') {
      $('#terms').focus();
    }
  });

  google.load('visualization', '1', 
    { callback : function() {
      timeline = new links.Timeline(document.getElementById('timeline'));
      google.visualization.events.addListener(timeline, 'select', select);

      go();
    }
  });

  window.onresize = refresh;
});