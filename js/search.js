///////////
// TILDS //
///////////
jQuery.fn.hookupTild = function() {
  var tild_click = function(e) {
    $(e.target).closest('.tild').remove();
    $('#terms').focus();
  }

  var tild_hover = function() {
    $(this).find('.fa').toggleClass('hide');
    $(this).find('span').toggleClass('hide');
  }

  $(this).hover(tild_hover, tild_hover);
  $(this).click(tild_click);
};


function addTild(value) {
  if (value != '') {
    $('#terms').typeahead('val', '');

    var new_t = '<span class="tild added appender">' +
                  '<span class="tilde">~</span>' +
                  '<i class="fa fa-times hide"></i>' +
                   value.split('~')[0] +
                '</span>';

    new_t = $(new_t);
    new_t.hookupTild();

    $('#tilds-section').before(new_t);
  }
}


function addTilds(tilds) {
  for (var i = 0; i < tilds.length; i++) {
    addTild(tilds[i]);
  }
}


function removeTild(pos) {
  $('#terms').typeahead('val', '');

  if ($('.tild.added').length == 0) {
    $('#tilds-section').fadeOut(SPEED, function() {
      $('#terms').focus();
    });
  } else {
    if ($('.tild.added.focus').length == 0) {
     $('.tild.added:' + pos).addClass('focus');
    } else {
     $('.tild.added.focus').remove();
    }
  }
}


function clearTilds() {
  var c = $('.tild').length;

  for (var i = 0; i < c; i++) {
    removeTild('first');
    removeTild('first');
  }
}


///////////
// PAGES //
///////////
function setPage(e, d) {
  $('#page-loading').setLoading(true);;
  $('#page').attr('src', d.url);
}


function pageLoaded() {
  $('#page-loading').setLoading(false);
}


////////////////
// SEARCH BOX //
////////////////
function terms_key_down(e) {
  switch (e.which) {
    // TILDE KEY
    case KEY_TILDE_FF:
    case KEY_TILDE_IE:
      $('#tilds-section').fadeIn(SPEED, function() {
        $('#tilds').focus(); 
      });

      $('#tilds').typeahead('val', '');
      return false;

    // DELETE KEY
    case KEY_DEL:
      if ($(this).val().length == $(this).getCursorPosition()) {
        return removeTild('first');
      }
  }

  $('.tild.added').removeClass('focus');
}


function tilds_key_down(e) {        
  switch (e.which) {
    // ENTER KEY
    case KEY_ENT:
      $('#tilds-section').fadeOut(SPEED, function() {
        $('#terms').focus();
      });

    // TILDE KEY
    case KEY_TILDE_FF:
    case KEY_TILDE_IE:
      addTild($(this).val());

      updateTimelineData(); // TODO: ***************** TENUOUS LINK
      
      $('#tilds').typeahead('val', '');
      return false;

    // BACKSPACE KEY
    case KEY_BSP:
      if ($(this).val() == '') {
        return removeTild('last');
      }
  }
  
  $('.tild.added').removeClass('focus');
}


///////////////
// TYPEAHEAD //
///////////////
var options = {
  hint: true,
  highlight: true,
  minLength: 1
};


var b_terms = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  remote: {
    url : '/results',
    replace : function() {
      return '/results/' + $('#terms').val() + '/' + $('.tild').text();
    }
  }
});


var b_tilds = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  remote: {
    url : '/tilds',
    replace : function() {
      return '/tilds/' + $('.tild').text();
    }
  }
});

b_terms.initialize();
b_tilds.initialize();


///////////
// READY //
///////////
$(document).ready(function() {
  $('#terms').keydown(terms_key_down);
  $('#terms').typeahead(options, {
      name        : 'terms',
      displayKey  : 'name',
      source      : b_terms.ttAdapter()
    });
  $('#terms').on('typeahead:selected', setPage);

  $('#tilds').keydown(tilds_key_down);
  $('#tilds').typeahead(options, {
      name        : 'tilds',
      displayKey  : 'name',
      source      : b_tilds.ttAdapter()
    });

  $('#tilds-section').hide();

  $('#page').load(pageLoaded);

  $('.tt-hint').addClass('form-control');
});