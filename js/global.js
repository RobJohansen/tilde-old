var SPEED = 200;

jQuery.fn.key = function(value) {
    if (value == undefined) {
        var k = $(this).attr('key');
    
        if (k == undefined) {
          return '';
        } else {
          return k;
        }
    } else {
        $(this).attr('key', value);
    }
};



// function setKey(name, key) {
//   if (key == undefined) {
//     $('#' + name).attr('key', $('#' + name).val());
//   } else {
//     $('#' + name).attr('key', key);
//   }
// }


// function setValKey(name, val, key) {
//   if (name == 'timestamp') {
//     $('#timestamp').text(val);
//   } else {
//     $('#' + name).val(val);
//   }

//   $('#' + name).attr('key', key);
// }



function url(key) {
  switch (key) {
    case 'page'     : return '/page/' + TERMS.key() + TILDS.key() + '?timestamp=' + TIMES.key();
    case 'bh_terms' : return '/get_terms/' + TERMS.val();
    case 'bh_tilds' : return '/get_tilds/' + TILDS.key();
    case 'date'     : return '/date/' + TILDS.key();
    case 'derive'   : return '/derive/';
  }
}


jQuery.fn.setLoading = function(b) {
    if (b) {
        $(this[0]).addClass('fa-refresh fa-spin');
    } else {
        $(this[0]).removeClass('fa-refresh fa-spin');
    }
};


jQuery.fn.getCursorPosition = function() {
    var input = this.get(0);
    if (!input) return;

    if ('selectionStart' in input) {
        return input.selectionStart;

    } else if (document.selection) {
        input.focus();

        var sel = document.selection.createRange();
        var selLen = document.selection.createRange().text.length;

        sel.moveStart('character', -input.value.length);
        return sel.text.length - selLen;
    }
};


function showError(text) {
    alert(text);
}