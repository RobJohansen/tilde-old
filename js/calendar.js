var timeline;


////////////////
// LINE STYLE //
////////////////
var ItemLine = function (data, options) {
  links.Timeline.Item.call(this, data, options);
};

ItemLine.prototype = new links.Timeline.Item();

ItemLine.prototype.createDOM = function () {
    var _this = this;
    var divLine = document.createElement("DIV");
    divLine.style.position = "absolute";
    divLine.style.width = "0px";

    this.dom = divLine;
    this.updateDOM();

    return divLine;
};

ItemLine.prototype.showDOM = function (container) {
    var dom = this.dom;
    if (!dom) {
        dom = this.createDOM();
    }

    if (dom.parentNode != container) {
        if (dom.parentNode) {
            this.hideDOM();
        }

        container.insertBefore(dom, container.firstChild);
        this.rendered = true;
    }
};

ItemLine.prototype.hideDOM = function () {
    var dom = this.dom;
    if (dom) {
        var parent = dom.parentNode;
        if (parent) {
            parent.removeChild(dom);
            this.rendered = false;
        }
    }
};

ItemLine.prototype.updateDOM = function () {
    var divLine = this.dom;
    if (divLine) {
        divLine.className = "timeline-event item-line";

        if (this.isCluster) {
            links.Timeline.addClassName(divLine, 'timeline-event-cluster');
        }

        if (this.className) {
            links.Timeline.addClassName(divLine, this.className);
        }
    }
};

ItemLine.prototype.updatePosition = function (timeline) {
    var dom = this.dom;
    if (dom) {
        var left = timeline.timeToScreen(this.start),
            axisOnTop = timeline.options.axisOnTop,
            axisTop = timeline.size.axis.top,
            axisHeight = timeline.size.axis.height

        dom.style.left = (left - this.lineWidth / 2) + "px";
        dom.style.top = "0px";
        dom.style.height = axisHeight + "px";
    }
};

ItemLine.prototype.isVisible = function (start, end) {
    if (this.cluster) return false;

    return (this.start > start)
        && (this.start < end);
};

ItemLine.prototype.setPosition = function (left, right) {
    this.dom.style.left = (left - this.lineWidth / 2) + "px";
};

ItemLine.prototype.getRight = function (timeline) {
    return timeline.timeToScreen(this.start);
};


///////////////
// TRAVERSAL //
///////////////
jQuery.fn.isComplete = function() {
    return $(this).closest('.timeline-event').find('.fa').hasClass('fa-times');
};


jQuery.fn.timelineLevel = function() {
    return $(this).find('a').attr('level');
};


jQuery.fn.timelineParent = function() {
    var nLevel = $(this).closest('.timeline-event').timelineLevel();

    return $('.timeline-event').filter(function(i) {
        return $(this).timelineLevel() == nLevel - 1;
    });
};

jQuery.fn.timelineSiblings = function() {
    var n = $(this).closest('.timeline-event');

    var nLevel = n.timelineLevel();
    var nPos = n.position();

    return $('.timeline-event').filter(function(i) {
        var t = $(this);

        var tLevel = t.timelineLevel();
        var tPos = t.position();

        return tLevel == nLevel &&
               tPos.left != nPos.left;
    });
};


jQuery.fn.timelineDescendants = function() {
    var n = $(this).closest('.timeline-event');

    var nLevel = n.timelineLevel();
    var nPos = n.position();

    return $('.timeline-event').filter(function(i) {
        var t = $(this);

        var tLevel = t.timelineLevel();
        var tPos = t.position();

        return tLevel > nLevel &&
               tPos.left >= nPos.left &&
               tPos.left + t.width() <= nPos.left + n.width() + 5;
    });
};


/////////////
// HELPERS //
/////////////

//     // Parent
//     var p = $(this).timelineParent();

//     while (p.length > 0) {
//         var children = p.timelineChildren();

//         var percentage = children.filter(function(index) {
//             return $(this).isComplete();
//         }).length / children.length * 100;
        
//         p.markCompletion(percentage);

//         p = p.timelineParent();


function percentRGB(p, c) {
    var g = p > 50 ? 255 - c : Math.round(p * 5.12 - c);
    var b = p <= 50 ? 99 - c : Math.round(100 - c - (p - 50) * 2);

    return 'rgb(0, ' + Math.max(g, 0) + ',' + Math.max(b, 0) + ')';         
}


jQuery.fn.processCompletion = function() {
    var n = $(this);
    var ns = n.timelineSiblings();

    while (ns.length > 0 && ns.filter(function() { return $(this).isComplete() }).length == ns.length) {
        n = n.timelineParent();
        ns = n.timelineSiblings();
    }

    n.markCompletion(100);
    n.timelineDescendants().markCompletion(100);
};

jQuery.fn.processUncompletion = function() {
    var n = $(this);

    n.markCompletion(0);
    n.timelineDescendants().markCompletion(0);

    n = n.timelineParent();

    while (n.length > 0 && n.isComplete()) {
        n.markCompletion(0);
        n = n.timelineParent();
    }
};


jQuery.fn.markCompletion = function(percentage) {
    $(this).find('.timeline-event-progress')
        .css('width', percentage + "%")
        .css('background-color', percentRGB(percentage, 0))
        .css('border-right-color', percentRGB(percentage, 30));

    $(this).find('.fa')
        .addClass(percentage == 100 ? 'fa-times' : 'fa-check')
        .removeClass(percentage == 100 ? 'fa-check' : 'fa-times');

    $(this).each(function() {
        timeline.updateData(timeline.getItemIndex(this), {'content' : this.innerHTML });
    })
};


//////////////////
// PRESENTATION //
//////////////////
function refreshTimeline(options) {
    $('.timeline-event-button').unbind('click', timelineEventMarked);
    $('.timeline-event-title').unbind('click', timelineEventSelected);

    if (options.custom) {
        timeline.setCustomTime(new Date(options.custom));
    }

    if (options.min && options.max) {
        timeline.setVisibleChartRange(new Date(options.min), new Date(options.max));
    } else {
        timeline.setVisibleChartRangeAuto();
    }

    timeline.redraw();

    $('.timeline-event-button').click(timelineEventMarked);
    $('.timeline-event-title').click(timelineEventSelected);
}


function updateTimeline() {
    $('#tilds-loading').setLoading(true);

    $.get(
        '/timeline/' + $('.tild').text(),

        function(ret) {
            timeline.draw(new google.visualization.DataTable(ret.data, 0.6));

            refreshTimeline(ret);

            $('#tilds-loading').setLoading(false);
        }
    );
}


////////////
// EVENTS //
////////////
function timelineEventSelected() {
    var t = $(this);

    $.get(
        '/derive/' + t.attr('tag'),

        function(ret) {
            if (ret.success) {
                clearTilds(); // TODO: ***************** TENUOUS LINK
                addTilds(ret.tilds);  // TODO: ***************** TENUOUS LINK

                updateTimeline(); // TODO: ONLY UPDATED PARTS

                refreshTimeline(ret);
            }
        }
    );
}


function timelineEventMarked() {
    var t = $(this);

    $('#tilds-loading').setLoading(true);

    $.post(
        '/seen/' + t.attr('tag'),

        function(ret) {
            if (ret.success) {
                refreshTimeline(ret);
            }

            $('#tilds-loading').setLoading(false);
        }
    );

    var n = t.closest('.timeline-event');

    if (t.isComplete()) {
        n.processUncompletion();
    } else {
        n.processCompletion();
    }
}


function timelineChanged(e) {
    var d = e.time;

    $('#tilds-loading').setLoading(true);

    $.post('/seen/' +
        (d.getFullYear()) + '/' + 
        (d.getMonth() + 1) + '/' + 
        (d.getDay() + 1) + '/' + 
        $('.tild:first').text(),

        function(ret) {
            if (ret.success) {
                refreshTimeline(ret);
            }

            $('#tilds-loading').setLoading(false);
        }
    );
}


function timelineChange(e) {    
    var d = $('.timeline-customtime').position().left;

    $('.timeline-event').each(function() {
        var n = $(this);
        var percentage = (d - n.position().left) / n.width() * 100;

        // Math.max(0, Math.min(100, percentage)) TODO: Change to Percentages
        n.markCompletion(percentage < 100 ? 0 : 100);
    });
}


/////////////
// LOADING //
/////////////
function initTimeline() {
    var tl = document.getElementById('timeline');
    var options = {
        'showCurrentTime'   : false,
        'showCustomTime'    : true,
        'animate'           : true,
        'animateZoom'       : true,
        'stackEvents'       : false,
        'groupsOrder'       : false,
        'axisOnTop'         : true,
        'style'             : 'line'
    };

    timeline = new links.Timeline(tl, options);

    timeline.addItemType('line', ItemLine);

    google.visualization.events.addListener(
        timeline,
        'timechanged',
        timelineChanged
    );

    google.visualization.events.addListener(
        timeline,
        'timechange',
        timelineChange
    );

    $('.timeline-frame').addClass('drop-shadow');

    $('.tild').hookupTild();

    if ($('.tild').length > 0) updateTimeline();
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