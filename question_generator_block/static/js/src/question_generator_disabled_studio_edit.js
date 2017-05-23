/* Javascript for studio_view when the XBlock has already been submitted. */
function StudioDisabledEditXBlock(runtime, xblockElement) {
    "use strict";
    
    $(xblockElement).find('.cancel-button').bind('click', function(e) {
        runtime.notify('cancel', {});
    });
    
}