var TERMS;
var TILDS;
var TIMES;

///////////
// TILDS //
///////////
jQuery.fn.clearAndClose = function() {
    $(this).typeahead('val', '');
};


jQuery.fn.hookupTild = function() {
    var tild_click = function(e) {
        $(e.target).closest('.tild').remove();
        $('#terms').focus();
    }

    var tild_hover = function() {
        $(this).toggleFocusTild();
    }

    $(this).hover(tild_hover, tild_hover);
    $(this).click(tild_click);
};


jQuery.fn.toggleFocusTild = function() {
    $(this).find('.fa').toggleClass('hide');
    $(this).find('span').toggleClass('hide');

    $(this).toggleClass('focus');
};


var tild_click = function(e) {
    $(e.target).closest('.tild').remove();

    TERMS.focus();

    TILDS.key($('.tild').text());

    syncState();
}


var tild_hover = function() {
    $(this).toggleFocusTild();
}


function addTild(value) {
    if (value != '') {
        // TERMS.clearAndClose();

        var new_t = '<span class="tild">' +
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
    // TERMS.clearAndClose();

    if ($('.tild').length == 0) {
        $('#tilds-section').fadeOut(SPEED, function() {
            TERMS.focus();

            TILDS.key($('.tild').text());

            syncState();
        });
    } else {
        if ($('.tild.focus').length == 0) {
            $('.tild' + pos).toggleFocusTild();
        } else {
            $('.tild.focus').remove();
        }
    }
}


function clearTilds() {
    $('.tild').remove();
}



////////////////
// SEARCH BOX //
////////////////

var KEY_DEL       = 46;
var KEY_BSP       = 8;
var KEY_ENT       = 13;
var KEY_TILDE_FF  = 163;
var KEY_TILDE_IE  = 222;


function terms_key_down(e) {
  switch (e.which) {
    // TILDE KEY
    case KEY_TILDE_FF:
    case KEY_TILDE_IE:
        $('#tilds-section').fadeIn(SPEED, function() {
            TILDS.focus(); 
        });

        TILDS.clearAndClose();
      
        return false;

    // DELETE KEY
    case KEY_DEL:
        if ($(this).getCursorPosition() == $(this).val().length) {
            removeTild('');
        }

        return true;

    // ENTER KEY
    case KEY_ENT:
        TERMS.key(TERMS.val());

        syncState();
  }

  $('.tild.focus').toggleFocusTild();
}


function tilds_key_down(e) {        
  switch (e.which) {
    // TILDE KEY
    case KEY_TILDE_FF:
    case KEY_TILDE_IE:
        addTild(TILDS.val());
        
        TILDS.clearAndClose();

        return false;

    // BACKSPACE KEY
    case KEY_BSP:
        if ($(this).getCursorPosition() == 0) {
            removeTild(':last');;
        }

        return true;

    // ENTER KEY
    case KEY_ENT:
        addTild(TILDS.val());
        
        $.get(
            url('date'),
            function(c) {
                $('#tilds-section').fadeOut(SPEED, function() {
                    TIMES.key(c.timestamp);
                    TIMES.text(c.timestamp_v);
                    
                    TERMS.focus();
                    
                    TILDS.key($('.tild').text());

                    syncState();

                    updateTimeline(); // TODO: ***************** TENUOUS LINK
                });
            }
        );
    }
  
    $('.tild.focus').toggleFocusTild();
}


///////////////
// TYPEAHEAD //
///////////////
var bh_options = {
    hint:         true,
    highlight:    true,
    minLength:    1
};

var bh_terms = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url : '/get_terms',
        replace : function() {
            return url('bh_terms');
        }
    }
});

var bh_tilds = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url : '/get_tilds',
        replace : function() {
            return url('bh_tilds');
        }
    }
});


//////////
// INIT //
//////////
function init_search_box() {
    TERMS = $('#terms');
    TILDS = $('#tilds');
    TIMES = $('#timestamp');


    bh_terms.initialize();
    bh_tilds.initialize();

    TERMS.typeahead(bh_options, {
        name        : 'terms',
        displayKey  : 'name',
        source      : bh_terms.ttAdapter()
    });

    TILDS.typeahead(bh_options, {
        name        : 'tilds',
        displayKey  : 'name',
        source      : bh_tilds.ttAdapter()
    });

    TERMS.keydown(terms_key_down);
    // TERMS.on('typeahead:opened', typeaheadOpened);
    // TERMS.on('typeahead:closed', typeaheadClosed);
    // TERMS.on('typeahead:selected', typeaheadSelected);

    TILDS.keydown(tilds_key_down);
    // TILDS.on('typeahead:opened', typeaheadOpened);
    // TILDS.on('typeahead:closed', typeaheadClosed);




    $('#tilds-section').hide();

    if (TILDS.attr('key') != undefined) {
        addTilds(TILDS.attr('valtemp').split('~'));
    }

    TERMS.focus();
}