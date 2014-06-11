var timeline;

function tild_hover() {
  $(this).find('.fa').toggleClass('hide');
  $(this).find('span').toggleClass('hide');
}

function tild_click(e) {
  $(e.target).closest('.tild').remove();

  load();
  $('#terms').focus();
}

jQuery.fn.hookupTild = function() {
  $(this).hover(tild_hover, tild_hover);
  $(this).click(tild_click);
};

jQuery.fn.toggleLoading = function() {
  $(this[0]).toggleClass('fa-refresh fa-spin');
};




function seen() {
  var t = $(this);

  t.toggleLoading();

  $.post(
    '/seen',
    'key=' + t.attr('tag') + (t.hasClass('fa-check') ? '&seen=1' : ''),
    function() {
      t.toggleClass('fa-check fa-times');
      t.closest('.timeline-event').toggleClass('complete');
      t.toggleLoading();
    });
}


var timelineOptions = {
    width             : '100%',
    showCurrentTime   : 'false',
    axisOnTop         : 'true',
    animate           : 'true',
    animateZoom       : 'true'
}

function load() {
  $('.fetching-tilds').toggleLoading();
  $.get(
    '/load_timeline',
    'ts=' + $('.tild.added').text(),
    function(o) {

      $('.btn-seen').unbind('click', seen);

      timeline.draw(new google.visualization.DataTable(o.data, 0.6), timelineOptions);
      timeline.setVisibleChartRangeAuto();

      $('.btn-seen').click(seen);
      $('.fetching-tilds').toggleLoading();

      $('#terms').focus();
    });
}

function select() {
  var e = timeline.getSelection();
  
  if (e.length) {
    if (e[0].row != undefined) {
      var r = timeline.getItem(e[0].row).content.split('"')[1];

      $(".tild.added").remove();

      $.get(
        '/derive_tilds',
        'key=' + r,
        function(o) {

          for (var i = o.tilds.length - 1; i >= 0 ; i--) {
            var t = $('<span class="tild added appender"><span class="tilde">~</span><i class="fa fa-times hide"></i>' + o.tilds[i] + '</span>');
            t.hookupTild();

            $('#tildes').before(t);
          }
        });
    }
  }
}

function terms_key_down(e) {
  if (e.which == 13) {
    $('.fetching-terms').toggleLoading();
    // GET RESULTS FROM WIKIPEDIA
    $.get(
      '/results',
      'qry=' + $('#terms').val() + '&k=' + 4642138092470272,
      function(o) {
        $('#results').html('');
        for (var i = 0; i < o.results.length; i++) { 
          $('#results').append('<a href="' + o.results[i].url + '">' + o.results[i].text + '</a><br/>');
        }
        $('.fetching-terms').toggleLoading();
      });

  } else if (e.which == 222 || e.which == 163) {
    $('#tildes').fadeIn();
    $('#tilds').focus().typeahead('val', '');
    return false;
  } else if (e.which == 46 && $(this).val() == '') {
    if ($('.tild.added').length == 0) {
      load();
      $('#tildes').fadeOut();
    } else {

      if ($('.tild.added.focus').length == 0) {
        $('.tild.added:first').addClass('focus');
      } else {
        $('.tild.added.focus').remove();
      }
    }

    return false;
  }
}

function tilds_key_down(e) {
  if (e.which == 13 || e.which == 222 || e.which == 163) {
    if ($(this).val() != '') {
      var t = $('<span class="tild added appender"><span class="tilde">~</span><i class="fa fa-times hide"></i>' + $(this).val().split('~')[0] + '</span>');

      t.hookupTild();

      $('#tildes').before(t);
      $('#tilds').typeahead('val', '');
    }

    if (e.which == 13) {
      load();
      $('#tildes').fadeOut();
    }
    
    return false;

  } else if (e.which == 8 && $(this).val() == '') {
    if ($('.tild.added').length == 0) {
      load();
      $('#tildes').fadeOut();
    } else {

      if ($('.tild.added.focus').length == 0) {
        $('.tild.added:last').addClass('focus');
      } else {
        $('.tild.added.focus').remove();
      }
    }

    return false;
  }
    
  $('.tild.added').removeClass('focus');
}


var substringMatcher = function(xs) {
    return function findMatches(input, ret) {
      var matches;
      var r = new RegExp(input, 'i');
   
      matches = [];

      $.each(xs, function(i, x) {
        if (r.test(x)) {
          matches.push({ value: x });
        }
      });
   
      ret(matches);
    };
  };

var options = {
    hint: true,
    highlight: true,
    minLength: 1
  };


$(document).ready(function() {
  $('#terms').keydown(terms_key_down);
  $('#terms').typeahead(options, {
      source: substringMatcher(['John Locke', 'Jack Shepherd'])
    });

  $('#tilds').keydown(tilds_key_down);
  $('#tilds').typeahead(options, {
      source: substringMatcher(['Lost', 'S#', 'E#'])
    });

  $('#tildes').hide();

  $('.tild.added').hookupTild();

  $('.tild.added').keydown(function(e) {
    if (e.which == 8) {
      e.target.remove();
    }
  });

  $('.tild.added').click(function(e) {
    e.target.remove();
  });

  google.load('visualization', '1',
    { callback : function() {
      timeline = new links.Timeline(document.getElementById('timeline'));
      google.visualization.events.addListener(timeline, 'select', select);

      timeline.draw(new google.visualization.DataTable([], 0.6), timelineOptions);
      timeline.setVisibleChartRangeAuto();

      $('.timeline-frame').addClass('drop-shadow');

      load();
    }
  });

  window.onresize = function() {
    timeline.checkResize();
  };

  $('.tt-hint').addClass('form-control');
});