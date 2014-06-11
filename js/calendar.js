var timeline;


//////////////////
// PRESENTATION //
//////////////////
function markSeen() {
  var t = $(this);
  
  t.toggleClass('fa-check fa-times');

  $('#timeline-loading').setLoading(true);

  $.post(
    '/seen/' + t.attr('tag'),
    function() {
      t.closest('.timeline-event').toggleClass('complete');
      
      $('#timeline-loading').setLoading(false);
    });
}


function updateTimelineData() {
  $('#timeline-loading').setLoading(true);

  $.get(
    '/timeline/' + $('.tild').text(),
    function(o) {
      var dt = new google.visualization.DataTable(o.data, 0.6);

      $('.btn-seen').unbind('click', markSeen);

      timeline.draw(dt);

      if (o.custom) {
        timeline.setVisibleChartRange(new Date(o.min), new Date(o.max));
        timeline.setCustomTime(new Date(o.custom));

        timeline.redraw();
      }

      $('.btn-seen').click(markSeen);

      $('#timeline-loading').setLoading(false);
    }
  );
}


////////////
// EVENTS //
////////////
function timelineChange(e) {
  var d = e.time;

  $('#timeline-loading').setLoading(true);
  $.post(
    '/seen/' + $('.tild:first').text() + '/' + d.getFullYear() + '/' + (d.getMonth() + 1) + '/' + (d.getDay() + 1),
    function() {
      updateTimelineData();

      $('#timeline-loading').setLoading(false);
    });
}


function timelineSelected() {
  var e = timeline.getSelection();

  $('#timeline-loading').setLoading(true);
  if (e.length) {
    if (e[0].row != undefined) {
      var id = timeline.getItem(e[0].row).content.split('"')[1];

      $.get(
        '/derive/' + id,
        function(o) {
          clearTilds(); // TODO: ***************** TENUOUS LINK

          addTilds(o.tilds);  // TODO: ***************** TENUOUS LINK

          updateTimelineData();

          $('#timeline-loading').setLoading(false);
      });
    }
  }
}


/////////////
// LOADING //
/////////////
function initTimeline() {
  var tl = document.getElementById('timeline');
  var options = {
    'showCustomTime'    : true,
    'showCurrentTime'   : false,
    'axisOnTop'         : true,
    'animate'           : true,
    'animateZoom'       : true,
    'groupsOrder'       : false,
    'stackEvents'       : false
  };

  timeline = new links.Timeline(tl, options);

  google.visualization.events.addListener(
    timeline,
    'timechanged',
    timelineChange
  );

  google.visualization.events.addListener(
    timeline,
    'select',
    timelineSelected
  );

  $('.timeline-frame').addClass('drop-shadow');
}

google.load("visualization", "1");
google.setOnLoadCallback(initTimeline);


///////////
// READY //
///////////
$(document).ready(function() {
  window.onresize = function() {
    timeline.checkResize();
  };
});