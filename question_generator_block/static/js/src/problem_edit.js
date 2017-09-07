/* Javascript for StudioEditableXBlockMixin. */
function StudioEditableXBlockMixin(runtime, xblockElement) {
    "use strict";
    
    var fields = [];
    var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined'); // Studio includes a copy of tinyMCE and its jQuery plugin
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin

    var csxColor = ["#009FE6", "black"];
    var studio_buttons = {
        "question_template-tab": "TEMPLATE",
        "editor-tab": "EDITOR",
        "general_information-tab": "SETTINGS",
    };

    // define tab id mapping of current tab to target tab
    var target_tabId_map = {
        'question_template-tab' : "editor-tab",
        'editor-tab' : "question_template-tab"
    }

    // define tab id mapping of current tab to target tab
    var target_tabName_map = {
        'question_template-tab' : "Simple Template",
        'editor-tab' : "Advanced Editor"
    }

    var error_message_element = $(xblockElement).find('div[name=error-message]');
    var question_template_textarea_element = $(xblockElement).find('textarea[name=question_template]');
    var url_image_input = $(xblockElement).find('input[name=image_url]');
    var variables_table_element = $(xblockElement).find('table[name=variables_table]');
    var add_variable_button_element = $(xblockElement).find('li[name=add_variable]');
    var answer_template_textarea_element =  $(xblockElement).find('textarea[name=answer_template]');
    // for editor mode toggle
    var enable_advanced_editor_element = $(xblockElement).find('input[name=enable_advanced_editor]');
    var enable_advanced_editor = enable_advanced_editor_element.val();
    var editor_mode_name_element = $(xblockElement).find('input[name=current_editor_mode_name]');
    var editor_mode_name = editor_mode_name_element.val();

    // DOM object for xml editor
    var xml_editor_element = $(xblockElement).find('textarea[name=raw_editor_xml_data]');
    var my_XML_Box = '.xml-box';

    // WORKING
    var xml_editor = CodeMirror.fromTextArea($(my_XML_Box)[0], {
        mode: 'xml',
        lineNumbers: true,
        lineWrapping: true
    });


    $(function($) {
        // append tab action bar

//        for (var b in studio_buttons) {
//            $('.editor-modes')
//                .append(
//                    $('<li>', {class: "action-item"}).append(
//                        $('<a />', {class: "action-primary", id: b, text: studio_buttons[b]})
//                    )
//                );
//        }

        $('.editor-modes')
                .append(
                    $('<li>', {class: "action-item"}).append(
                        $('<a />', {class: "action-primary", id: 'question_template-tab', text: studio_buttons['question_template-tab']})
                    )
                );

        $('.editor-modes')
                .append(
                    $('<li>', {class: "action-item"}).append(
                        $('<a />', {class: "action-primary", id: 'general_information-tab', text: studio_buttons['general_information-tab']})
                    )
                );

        // Set default tab
        tab_switch("question_template-tab");

        $('#question_template-tab').click(function() {
            tab_switch("question_template-tab");
        });

        $('#editor-tab').click(function() {
            tab_switch("editor-tab");
        });

        $('#general_information-tab').click(function() {
            tab_switch("general_information-tab");
        });

        $('#btn_switch_editor_mode').click(function() {
            // get current tab
            var current_tab = $(this).attr('tab-name');

            console.log('previous tab id:' + current_tab);
            console.log('targeted tab id:' + target_tabId_map[current_tab]);
            console.log('targeted tab name:' + studio_buttons[target_tabId_map[current_tab]]);
            console.log('next editor mode:' + target_tabName_map[current_tab]);
            console.log('enable_advanced_editor:' + enable_advanced_editor);

            if(enable_advanced_editor == 'False') {
                if(! confirmConversionToXml())
                    return;
                // if confirmed, proceed
                // update editor mode
                enable_advanced_editor = 'True'; // update JS global variable
                enable_advanced_editor_element.val(enable_advanced_editor); // update value to hidden element enable_advanced_editor
            } else {
                if(! confirmConversionToTemplate())
                    return;
                // if confirmed, proceed
                // update editor mode
                enable_advanced_editor = 'False'; // update global variable
                enable_advanced_editor_element.val(enable_advanced_editor); // update value to hidden input element
            }
            // Already removed button 'Add Variable' in tab switching function

            // update attributes for the current tab <li> tag
            // update text
            $("#"+current_tab).text(studio_buttons[target_tabId_map[current_tab]]);
            // update attribute
            $("#"+current_tab).attr('id',target_tabId_map[current_tab]);

            // update attributes for the switching editor button
            // update text
            $('#btn_switch_editor_mode').text(target_tabName_map[current_tab]);
            // update attribute
            $('#btn_switch_editor_mode').attr('tab-name',target_tabId_map[current_tab]);

            // targeted editor_mode_name
//            TODO: Check why this cause JS error ???
//            editor_mode_name = target_tabName_map[current_tab]); // update targeted editor_mode_name
////            editor_mode_name = 'Advanced Editor'; // update targeted editor_mode_name
//            editor_mode_name_element.val(editor_mode_name); // update value for hidden element editor_mode_name
//            // update title attribute for the editor mode toggle button
////            $('#btn_switch_editor_mode').attr('title', 'Switch to ' + editor_mode_name + ' mode'); // update title for the Editor mode button
//            $('#btn_switch_editor_mode').title('Switch to ' + editor_mode_name + ' mode'); // update title for the Editor mode button

            // switch to the targeted tab
            tab_switch(target_tabId_map[current_tab]);

            // TODO: update enable_advanced_editor_element.val() and xblock global variable 'enable_advanced_editor'
        });

        // listeners for "Remove" buttons of "Variables"
        variables_table_element.find('input[type=button][class=remove_button]').bind('click', function(e) {
        	var removeButton = $(this);
        	var parentRow = removeButton.closest('tr');
        	parentRow.remove();
        });

    });


    /*
     Have the user confirm the one-way conversion to XML.
     Returns true if the user clicked OK, else false.
     */
    function confirmConversionToXml() {
        return confirm(gettext('If you use the Advanced Editor, this problem template will be converted to XML for raw edit. The default interface is still Simple Template. You can toggle between them\n\nProceed to the Advanced Editor?')); // eslint-disable-line max-len, no-alert
    };

    /*
     Have the user confirm the one-way conversion to XML.
     Returns true if the user clicked OK, else false.
     */
    function confirmConversionToTemplate() {
        return confirm(gettext('Are you sure you want to switch back to Simple Template interface.\n\nProceed ?')); // eslint-disable-line max-len, no-alert
    };


   function fillErrorMessage(errorMessage) {
		error_message_element.empty();

		if (errorMessage != null) {
			var errorLabelNode = "<label class='validation_error'>" + errorMessage + "</label>";
			error_message_element.append(errorLabelNode);
		}
    }

    $(xblockElement).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var type = $wrapper.data('cast');
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return tinyMceAvailable && $field.tinymce(); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (type == 'boolean')
                    return (val == 'true' || val == '1');
                if (type == "integer")
                    return parseInt(val, 10);
                if (type == "float")
                    return parseFloat(val);
                if (type == "generic" || type == "list" || type == "set") {
                    val = val.trim();
                    if (val === "")
                        val = null;
                    else
                        val = JSON.parse(val); // TODO: handle parse errors
                }
                return val;
            },
            removeEditor: function() {
                $field.tinymce().remove();
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        
        $field.bind("change input paste", fieldChanged);
        $resetButton.click(function() {
            $field.val($wrapper.attr('data-default')); // Use attr instead of data to force treating the default value as a string
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });

        if (type == 'datepicker' && datepickerAvailable) { // TODO remove?
            $field.datepicker('destroy');
            $field.datepicker({dateFormat: "m/d/yy"});
        }
    });


    $(xblockElement).find('.wrapper-list-settings .list-set').each(function() {
        var $optionList = $(this);
        var $checkboxes = $(this).find('input');
        var $wrapper = $optionList.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');

        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return false; },
            val: function() {
                var val = [];
                $checkboxes.each(function() {
                    if ($(this).is(':checked')) {
                        val.push(JSON.parse($(this).val()));
                    }
                });
                return val;
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        $checkboxes.bind("change input", fieldChanged);

        $resetButton.click(function() {
            var defaults = JSON.parse($wrapper.attr('data-default'));
            $checkboxes.each(function() {
                var val = JSON.parse($(this).val());
                $(this).prop('checked', defaults.indexOf(val) > -1);
            });
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });
    });

    var studioSubmit = function(data) {
        var handlerUrl = runtime.handlerUrl(xblockElement, 'fe_submit_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext("Saving")});
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: "json",
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext("This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.");
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === "object" && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext("Unable to update settings"), message: message});
        });
    };

    // Save action
    $(xblockElement).find('a[name=save_button]').bind('click', function(e) {
    	console.log("Save button clicked");
    	
    	error_message_element.empty();
    	
    	// "General information" tab
        e.preventDefault();
        var fieldValues = {};
        var fieldValuesNotSet = []; // List of field names that should be set to default values
        for (var i in fields) {
            var field = fields[i];
            if (field.isSet()) {
                fieldValues[field.name] = field.val();
            } else {
                fieldValuesNotSet.push(field.name);
            }
            // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
            // when loading editor for another block:
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }

        // 1. xml_editor_element
        var raw_editor_xml_data = xml_editor.getValue();
        console.log('raw_editor_xml_data: ' + raw_editor_xml_data);
        
        
        // "Template" tab
        /*
			1. question_template
			2. variables (name, min_valua, max_value, type, decimal_places)
			3. answer_template
        */
        // 1. question_template_textarea_element
        var question_template = question_template_textarea_element.val();
        console.log('question_template: ' + question_template);

        // image
        var image_url = url_image_input.val();
        console.log('image_url: ' + image_url);

//        var resolver_element = $(xblockElement).find('input[name=Resolver]:checked');
//        var resolver_selection = resolver_element.val();
//        console.log('resolver_selection: ' + resolver_selection);
        
        // 2. variables_table_element
        var variables = {};
    	variables_table_element.find('tr').each(function(row_index) {
    		if (row_index > 0) { // first row is the header
    			var variable = {}
    			
    			var columns = $(this).find('td');
    			
    			// 2nd column: "variable name"
    			var variable_name = columns.eq(1).children().eq(0).val();

    			if (variable_name.length == 0) { // empty variable name
    				fillErrorMessage('Variable name can not be empty');
    				return false;
    			}
    			
    			if (variables.hasOwnProperty(variable_name)) { // duplicate verification
    				fillErrorMessage('Variable names can not be duplicated');
    				return false;
    			}
    			
    			variable['name'] = variable_name;

    			
    			// 3rd column: "min_value"
    			var min_value = columns.eq(2).children().eq(0).val();
    			
    			if (min_value.length == 0) { // empty min_value
    				fillErrorMessage('min_value can not be empty');
    				return false;
    			}
    			
    			variable['min_value'] = min_value;

    			
    			// 4th column: "max_value"
    			var max_value = columns.eq(3).children().eq(0).val();

    			if (max_value.length == 0) { // empty max_value
    				fillErrorMessage('max_value can not be empty');
    				return false;
    			}
    			
    			var min_value_numer = Number(min_value);
    			var max_value_number = Number(max_value);
    			if (min_value_numer > max_value_number) {
    				fillErrorMessage('min_value can not be bigger than max_value');
    				return false;
    			}
    			
    			variable['max_value'] = max_value;
    			

    			// 5th column: "type"
    			var type = columns.eq(4).children().eq(0).val();
    			variable['type'] = type;

    			
    			// 6th column: "decimal_places"
    			var decimal_places = columns.eq(5).children().eq(0).val();
    			variable['decimal_places'] = decimal_places;
    			
    			variables[variable_name] = variable;
    			console.log('Row ' + row_index + ': variable_name: ' + variable_name + ', min: ' + min_value + ', max: ' + max_value + ', type: ' + type + ', decimal_places: ' + decimal_places);
    		}
    	});
    	
    	
    	// 3. answer_template 
        var answer_template = answer_template_textarea_element.val();
        console.log('answer_template: ' + answer_template);
        
        
        // client-side validation error
        if (error_message_element.children().length > 0) { 
        	return;
        }

//        debugger;
        // server side validation
        // perform studio submit and update default editor mode
        var submit_data = {enable_advanced_editor: enable_advanced_editor, values: fieldValues, defaults: fieldValuesNotSet, question_template: question_template, image_url: image_url, variables: variables, answer_template: answer_template, raw_editor_xml_data: raw_editor_xml_data};
	    studioSubmit(submit_data);
    });


    $(xblockElement).find('.cancel-button').bind('click', function(e) {
        // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
        // when loading editor for another block:
        for (var i in fields) {
            var field = fields[i];
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }
        e.preventDefault();
        runtime.notify('cancel', {});
    });
    
    
    $(xblockElement).find('a[name=add_variable_button]').bind('click', function(e) {
    	// console.log("Add VARIABLE button clicked");
    	
    	
    	var new_row = $('<tr></tr>');
    	new_row.attr("class", "formula_edit_table_row");
    	
    	 // first column (empty space)
    	var first_column = $('<td></td>');
    	new_row.append(first_column);
    	
    	
    	// second column: variable name
    	var second_column = $('<td></td>');
    	second_column.attr("class", "table_cell_alignment");
    	
    	var variable_name_element = $('<input />');
    	variable_name_element.attr("type", "text");
    	variable_name_element.attr("class", "formula_input_text");
    	variable_name_element.attr("value", "");
    	second_column.append(variable_name_element);
    	new_row.append(second_column);
    	

    	// third column: min value
    	var third_column  = $('<td></td>');
    	third_column.attr("class", "table_cell_alignment number_input_cell");
    	
    	var variable_min_value_element = $('<input />');
    	variable_min_value_element.attr("type", "number");
    	variable_min_value_element.attr("class", "formula_input_text");
    	variable_min_value_element.attr("value", "1");
    	third_column.append(variable_min_value_element);
    	new_row.append(third_column);

    	
    	// fourth column: max value
    	var fourth_column  = $('<td></td>');
    	fourth_column.attr("class", "table_cell_alignment number_input_cell");
    	
    	var variable_max_value_element = $('<input />');
    	variable_max_value_element.attr("type", "number");
    	variable_max_value_element.attr("class", "formula_input_text");
    	variable_max_value_element.attr("value", "10");
    	fourth_column.append(variable_max_value_element);
    	new_row.append(fourth_column);

    	
    	// fifth column: type
    	var fifth_column  = $('<td></td>');
    	fifth_column.attr("class", "table_cell_alignment");
    	
    	var variable_type_element = $('<select></select>');
    	variable_type_element.attr("class", "formula_input_text");
    	
    	var int_option_element = $("<option></option>");
    	int_option_element.attr("value", "int");
    	int_option_element.text("int");
    	int_option_element.attr("selected", "selected");
    	variable_type_element.append(int_option_element);
    	
    	var float_option_element = $("<option></option>");
    	float_option_element.attr("value", "float");
    	float_option_element.text("float");
    	variable_type_element.append(float_option_element);
    	
    	fifth_column.append(variable_type_element);
    	new_row.append(fifth_column);

    	
    	// sixth column: decimal_places
    	var sixth_column  = $('<td></td>');
    	sixth_column.attr("class", "table_cell_alignment number_input_cell");
    	
    	var variable_decimal_places_element = $('<input>');
    	variable_decimal_places_element.attr("type", "number");
    	variable_decimal_places_element.attr("min", "0");
    	variable_decimal_places_element.attr("max", "7");
    	variable_decimal_places_element.attr("class", "formula_input_text");
    	variable_decimal_places_element.attr("value", "0");
    	sixth_column.append(variable_decimal_places_element);
    	new_row.append(sixth_column);


    	// seventh column: Remove button
    	var seventh_column  = $('<td></td>');
    	seventh_column.attr("class", "table_cell_alignment");

    	var remove_variable_button = $('<input>');
    	remove_variable_button.attr("type", "button");
    	remove_variable_button.attr("class", "remove_button");
    	remove_variable_button.attr("value", "Remove");
    	seventh_column.append(remove_variable_button);
    	new_row.append(seventh_column);
    	
    	// add event handler
    	remove_variable_button.click(function() {
    		new_row.remove();
    		// console.log("REMOVE BUTTON CLICKED");
    	});

    	
    	// eighth column: empty column
//    	TODO: not neccessary, remove this empty column ???
//    	var eighth_column  = $('<td></td>');
//    	new_row.append(eighth_column);
    	
    	
    	// append the new row to variables table
    	variables_table_element.append(new_row);
    });
    


    function tab_highlight(toHighlight) {
        for (var b in studio_buttons) {
            if (b != toHighlight) $("a[id=" + b + "]").css({"color": csxColor[0]});
        }
        $("a[id=" + toHighlight + "]").css({"color": csxColor[1]});
    }
    
    
    function update_buttons(toShow) {
    	if (toShow == 'question_template-tab') {
    	    // show "Add variable" and "Add expression" buttons
    		$("li[name=add_variable]").show()
    	} else {
    	    // hide "Add variable" and "Add expression" buttons
    		$("li[name=add_variable]").hide()
    	}
    }


    // Hide all panes except toShow
    function tab_switch(toShow) {
        tab_highlight(toShow);
        for (var b in studio_buttons) $("div[name=" + b + "]").hide();
        $("div[name=" + toShow + "]").show();
        
        update_buttons(toShow);
    }




}
