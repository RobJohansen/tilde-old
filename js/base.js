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


function syncState(is_update, title, url) {
  if (title == undefined) {
    var title = $('title').html();
    var url = $('title').attr('url');
  }

  var state = {
    'terms_k'     : $('#terms').getKey(),
    'terms_v'     : $('#terms').val(),

    'tilds_k'     : $('#tilds').getKey(),
    'tilds_v'     : $('#tilds').val(),

    'timestamp_k' : $('#timestamp').getKey(),
    'timestamp_v' : $('#timestamp').val(),

    'render_url'  : $('#page-content').attr('render')
  }

  if (state.render_url == undefined || state.render_url == "") {
    state.content = $('#page-content').html();
  }

  if (is_update) {
    History.replaceState(state, title, url);
  } else {
    BYPASS_STATE = true;

    History.pushState(state, title, url);

    BYPASS_STATE = false;
  }
}



function stateChanged() {
  if (!BYPASS_STATE) {
    var state = History.getState();

    uiRender(state.data);
  }
}

function getPage() {
  $.get(url('page'),
    function(c) {
      if (c.error) {
        alert(c.error);
      } else {


        uiRender(c.state);

        syncState(false, c.title, c.url);
      }
    });

}

function uiRender(s) {
  setValKey('terms', s.terms_v, s.terms_k);
  setValKey('tilds', s.tilds_v, s.tilds_k);
  setValKey('timestamp', s.timestamp_v, s.timestamp_k);

  if (s.content != undefined) {
    pageRender(s.content);
  } else {
    $('#page-loading').show();

    $.get(s.render_url,
      function(c) {
        if (c.error) {

          alert(c.error);

        } else {

          pageRender(c.content, s.render_url);
          
        }

        $('#page-loading').hide();
      }
    );
  }
}

function pageRender(content, render_url) {
  $('#page-content').html(content);
  $('#page-content').attr('render', render_url);
  $('#page-content span.tilde-link').click(pageClick);
}

function pageClick() {
  setValKey('terms', $(this).attr('termsv'), $(this).attr('terms'));

  getPage();
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

  $('#page-loading').hide();
});