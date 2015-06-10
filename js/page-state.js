var BYPASS_STATE = false;


function syncState(is_update) {
  $('#page-loading').show();

  $.get(url('page'),
    function(c) {
      if (c.error) {

        showError(c.error);

      } else {

        uiRender(c.state);

        if (c.state.render_url) {
          delete c.state.content;
        }

        if (is_update) {
          History.replaceState(c.state, c.state_title, c.state_url);
        } else {
          BYPASS_STATE = true;
          History.pushState(c.state, c.state_title, c.state_url);
          BYPASS_STATE = false;
        }

      }
    }
  );
}


function stateChanged() {
  if (!BYPASS_STATE) {
    $('#page-loading').show();

    var state = History.getState();

    uiRender(state.data);
  }
}



function uiRender(s) {
  if (s.terms != undefined) {
    TERMS.key(s.terms);
    TILDS.key(s.tilds);
    TIMES.key(s.timestamp);

    TERMS.val(s.terms_v);
    TIMES.text(s.timestamp_v);

    clearTilds();
    addTilds(s.tilds_v.split('~'));

    if (s.render_url == undefined) {
      pageRender(s.content);
    } else {
      $.get(
        s.render_url,
        function(c) {
          if (c.error) {

            showError(c.error);

          } else {

            pageRender(c.content);
            
          }
        }
      );
    }
  } else {
    $('#page-loading').hide();
  }
}


function pageRender(content) {
  $('#page-content').html(content);
  $('#page-content span.tilde-link').click(pageClick);
      
  $('#page-loading').hide();
}


function pageClick() {
  TERMS.key($(this).attr('terms'));
  
  syncState();
}


//////////
// INIT //
//////////
function init_page_state() {
  History.Adapter.bind(window, 'statechange', stateChanged);

  syncState(true);
}