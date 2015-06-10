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






