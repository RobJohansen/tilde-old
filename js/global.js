var SPEED = 100;

var KEY_DEL = 46;
var KEY_BSP = 8;
var KEY_ENT = 13;
var KEY_TILDE_FF = 163;
var KEY_TILDE_IE = 222;


////////////
// GLOBAL //
////////////
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