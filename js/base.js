var BYPASS_STATE = false;

jQuery.fn.getKey = function() {
    var k = $(this).attr('key');
    
    if (k == undefined) {
      return '';
    } else {
      return k;
    }
};


function setKey(name, key) {
  if (key == undefined) {
    $('#' + name).attr('key', $('#' + name).val());
  } else {
    $('#' + name).attr('key', key);
  }
}


function setValKey(name, val, key) {
  if (name == 'timestamp') {
    $('#timestamp').text(val);
  } else {
    $('#' + name).val(val);
  }

  $('#' + name).attr('key', key);
}


function url(name) {
  switch (name) {
    case 'page' : return '/p/' + $('#timestamp').getKey() + '/' + $('#terms').getKey() + $('#tilds').getKey();
    case 'date' : return '/d/' + $('#tilds').getKey();
  }
}


function syncState(is_update) {
  $('#page-loading').show();

  $.get(url('page'),
    function(c) {
      if (c.error) {

        alert(c.error);

      } else {

        uiRender(c.state);

        if (c.state.render_url) {
          delete c.state.content;
        }

        if (is_update) {
          History.replaceState(
            c.state,
            c.state_title,
            c.state_url
          );

        } else {
          BYPASS_STATE = true;

          History.pushState(
            c.state,
            c.state_title,
            c.state_url
          );

          BYPASS_STATE = false;
        }

      }
      
      $('#page-loading').hide();
    }
  );
}

function stateChanged() {
  if (!BYPASS_STATE) {
    var state = History.getState();

    uiRender(state.data);
  }
}

function uiRender(s) {
  setValKey('terms', s.terms_v, s.terms);
  setValKey('tilds', s.tilds_v, s.tilds);
  setValKey('timestamp', s.timestamp_v, s.timestamp);

  if (s.content != undefined) {
    pageRender(s.content);
  } else {
    $('#page-loading').show();

    $.get(s.render_url,
      function(c) {
        if (c.error) {

          alert(c.error);

        } else {

          pageRender(c.content);
          
        }

        $('#page-loading').hide();
      }
    );
  }
}

function pageRender(content) {
  $('#page-content').html(content);
  $('#page-content span.tilde-link').click(pageClick);
}

function pageClick() {
  setValKey('terms', $(this).attr('termsv'), $(this).attr('terms'));
  
  syncState();
}


var KEY_ENT = 13;

function terms_key_down(e) {
  switch (e.which) {
    case KEY_ENT:
      setKey('terms');

      syncState();
  }
}

function tilds_key_down(e) {
  switch (e.which) {
    case KEY_ENT:
      $.get(url('date'),
        function(c) {
          setKey('tilds');
          setValKey('timestamp', c.timestamp_v, c.timestamp);

          syncState();
        }
      );
  }
}

$(document).ready(function() {
  $('#terms').keydown(terms_key_down);
  $('#tilds').keydown(tilds_key_down);

  History.Adapter.bind(window, 'statechange', stateChanged);

  syncState(true);
});