/* Javascript for QuestionGeneratorXBlock. */
function QuestionGeneratorXBlock(runtime, xblockElement) {
	"use strict";

  		
	var hidden_question_template_element = $(xblockElement).find('input[name=question_template]');
	var hidden_url_image = $(xblockElement).find('input[name=image_url]');
	var hidden_resolver_selection =$(xblockElement).find('input[name=resolver_selection]');
	var hidden_variables_element = $(xblockElement).find('input[name=variables]');
	var hidden_generated_variables_element = $(xblockElement).find('input[name=generated_variables]');
	var hidden_generated_question_element = $(xblockElement).find('input[name=generated_question]');
	var hidden_answer_template_element = $(xblockElement).find('input[name=answer_template]');
    var xblock_id = $(xblockElement).find('input[name=xblock_id]').val();

	var student_answer_textarea_element = $(xblockElement).find('textarea[name=student_answer]');
    var teacher_answer_div_element = $(xblockElement).find('div[name=teacher_answer_div]');
    var show_answer_button = $(xblockElement).find('input[name=show_answer-button]');


	function handleSubmissionResult(results) {
		console.log('handleSubmissionResult INVOKED');
    	$(xblockElement).find('div[name=attempt-number]').text(results['attempt_number']);
    	$(xblockElement).find('div[name=problem-progress]').text(results['point_string']);
    	$(xblockElement).find('input[name=submit-button]').val("Submit")
    	if (results['submit_disabled'] == 'disabled') {
    		$(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
    	}
    	else
    	{
    		$(xblockElement).find('input[name=submit-button]').removeAttr('disabled'); 
    	}
  	}
  	
    // Old version,
    // TODO: remove this
  	function handleShowAnswerResultString(result) {
  		console.log('handleShowAnswerResult INVOKED');

  		var teacher_answer = result['generated_answer'];
  		console.log('teacher_answer: ' + teacher_answer);

  		var answer_title_pre_element = $('<pre></pre>');
  		answer_title_pre_element.text('Answer:');

  		var answer_content_prelement = $('<pre></pre>');
  		answer_content_prelement.text(teacher_answer);

  		teacher_answer_div_element.append(answer_title_pre_element);
  		teacher_answer_div_element.append(answer_content_prelement);

  		show_answer_button.attr('disabled', 'disabled');
  	}

    // new version
    // TODO: support multi answers
    function handleShowAnswerResult(result) {
  		console.log('handleShowAnswerResult INVOKED');

        var answers = result['generated_answer'];
        var answer_title_pre_element = $('<pre></pre>');
  		answer_title_pre_element.text('Answer:');
  		teacher_answer_div_element.append(answer_title_pre_element);

        var key;
        for (key in answers) {
            console.log('answer attribute: ' + key);
            console.log('answer value: ' + answers[key]);
            var answer_content_prelement = $('<pre></pre>');
            var answer_string = key + ' = ' + answers[key];
  		    answer_content_prelement.text(answer_string);
            teacher_answer_div_element.append(answer_content_prelement);
        }

        // disable show answer button
  		show_answer_button.attr('disabled', 'disabled');
  	}


  	$(xblockElement).find('input[name=submit-button]').bind('click', function() {
  		// accumulate student's answer for submission
    	var data = {
      		'saved_question_template': hidden_question_template_element.val(),
      		'saved_url_image': hidden_url_image.val(),
      		'saved_resolver_selection': hidden_resolver_selection.val(),
      		'saved_answer_template': hidden_answer_template_element.val(),
      		'serialized_variables': hidden_variables_element.val(),
      		'serialized_generated_variables': hidden_generated_variables_element.val(),
      		'saved_generated_question': hidden_generated_question_element.val(),
      		'student_answer': student_answer_textarea_element.val()
    	};

    	console.log('data: ' + data);
    	console.log('student_answer: ' + data['student_answer']);
    	console.log('saved_question_template: ' + data['saved_question_template']);
    	console.log('serialized_variables: ' + data['saved_variables']);
    	console.log('serialized_generated_variables: ' + data['saved_generated_variables']);
    	console.log('saved_generated_question: ' + data['saved_generated_question']);
    	console.log('saved_answer_template: ' + data['saved_answer_template']);
    	console.log('saved_url_image: ' + data['saved_url_image']);
    	console.log('saved_resolver_selection: ' + data['saved_resolver_selection']);

        $(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
        $(xblockElement).find('input[name=submit-button]').val("Submitting...")

    	var handlerUrl = runtime.handlerUrl(xblockElement, 'student_submit');
    	$.post(handlerUrl, JSON.stringify(data)).success(handleSubmissionResult);
  	});

  	
    $(function($) {
    	console.log("question_generator_block initialized");
    	if (show_answer_button != null) {
    		show_answer_button.bind('click', function() {
    			console.log("show_answer_button CLICKED");
    			
    			// prepare data
    			var data = {
      				'saved_question_template': hidden_question_template_element.val(),
      				'saved_url_image' : hidden_url_image.val(),
      				'saved_resolver_selection': hidden_resolver_selection.val(),
      				'saved_answer_template': hidden_answer_template_element. val(),
		      		'serialized_variables': hidden_variables_element.val(),
		      		'serialized_generated_variables': hidden_generated_variables_element.val()
    			}
    			
    			var handlerUrl = runtime.handlerUrl(xblockElement, 'show_answer_handler');
//    			$.post(handlerUrl, JSON.stringify(data)).success(handleShowAnswerResult);
    			$.post(handlerUrl, JSON.stringify(data)).success(handleShowAnswerResultString);
    		});
    	}
    });
  	
}
