"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, JSONField, Integer, String, Boolean, Dict
from xblock.fragment import Fragment

from xblock.exceptions import JsonHandlerError, NoSuchViewError
from xblock.validation import Validation

from submissions import api as sub_api
from sub_api_util import SubmittingXBlockMixin

from xblockutils.studio_editable import StudioEditableXBlockMixin, FutureFields
from xblockutils.resources import ResourceLoader

import matlab_service
import qgb_question_service
import qgb_db_service
import json
from resolver_machine import resolver_machine

# import xblock_deletion_handler

loader = ResourceLoader(__name__)


@XBlock.needs("i18n")
class QuestionGeneratorXBlock(XBlock, SubmittingXBlockMixin, StudioEditableXBlockMixin):
    """
    Question Generator XBlock
    """

    display_name = String(
        display_name="Question Generator XBlock",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="Question Generator XBlock"
    )

    max_attempts = Integer(
        display_name="Maximum Attempts",
        help="Defines the number of times a student can try to answer this problem.",
        default=1,
        values={"min": 1}, scope=Scope.settings)
    
    max_points = Integer(
        display_name="Possible points",
        help="Defines the maximum points that the learner can earn.",
        default=1,
        scope=Scope.settings)
    
    show_points_earned = Boolean(
        display_name="Shows points earned",
        help="Shows points earned",
        default=True,
        scope=Scope.settings)
    
    show_submission_times = Boolean(
        display_name="Shows submission times",
        help="Shows submission times",
        default=True,
        scope=Scope.settings)
    
    show_answer = Boolean(
        display_name="Show Answer",
        help="Defines when to show the 'Show/Hide Answer' button",
        default=True,
        scope=Scope.settings)

    #TODO: add comments about scope of these new variables. Why these variables?
    #
    _image_url = String (
        display_name ="image",
        help ="",
        default="",
        scope = Scope.settings)
    
    _resolver_selection = String(
        display_name = "Resolver Machine",
        help ="",
        default = 'none',
        scope = Scope.content)
    
    _question_template = String (
        display_name = "Question Template",
        help = "",
        default = "Given a = <a> and b = <b>. Calculate the sum, difference of a and b.",
        scope = Scope.settings)

    _answer_template = String (
        display_name = "Answer Template",
        help = "Teacher has to fill the answer here!!!",
        default = "x =<a> + <b>",
        scope = Scope.settings)

    _variables = Dict (
        display_name = "Variable List",
        help = "",
        default = 
            {
                'a': {'name': 'a',
                'min_value': 0,
                'max_value': 10,
                'type': 'int',
                'decimal_places': 2
                } , 
                'b' :{'name': 'b',
                'min_value': 10,
                'max_value': 20,
                'type': 'int',
                'decimal_places': 2
                }
            },
        scope = Scope.settings)

    raw_editor = String(
        display_name="Editor",
        default="",
        scope=Scope.settings,
        multiline_editor=True, resettable_editor=False
    )

    raw_html_editor = String(
        display_name="Editor",
        default="",
        scope=Scope.settings,
        multiline_editor="html", resettable_editor=False
    )
    
    xblock_id = None
    newly_created_block = True
    image_url = ""
    resolver_handling = resolver_machine()
    resolver_selection = resolver_handling.getDefaultResolver()
    question_template = ""
    variables = {}
    answer_template = ""
    
    
    generated_question = ""
    generated_variables = {}
    
    student_answer = ""
    
    attempt_number = 0
    

    editable_fields = ('display_name', 'max_attempts', 'max_points', 'show_points_earned', 
                       'show_submission_times', 'show_answer', 
                       '_image_url', '_resolver_selection',
                       '_question_template', '_answer_template', '_variables', "raw_editor", "raw_html_editor")

    has_score = True 
    matlab_server_url = resolver_handling.getDefaultAddress()
    matlab_solver_url = resolver_handling.getDefaultURL()
    
    #matlab_server_url = "172.18.10.33:8080" # TODO allows user to config MATLAB URL in studio
    #matlab_solver_url = "/check"  # TODO allows user to config MATLAB URL in studio

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context):
        """
        The primary view of the QuestionGeneratorXBlock, shown to students when viewing courses.
        """

        context = context
        
        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
        should_disbled = ''

        
        # generate question from template if necessary
        self.generated_question, self.generated_variables = qgb_question_service.generate_question(self._question_template, self._variables)
        
        # load submission data to display the previously submitted result
        submissions = sub_api.get_submissions(self.student_item_key, 1)
        if submissions:
            latest_submission = submissions[0]

            # parse the answer
            answer = latest_submission['answer'] # saved "answer information"
            self.generated_question = answer['generated_question']
            self.generated_answer = answer['generated_answer']  # teacher's generated answer
            self.student_answer = answer['student_answer'] # student's submitted answer
            
            if ('variable_values' in answer): # backward compatibility
                saved_generated_variables = json.loads(answer['variable_values'])
                for var_name, var_value in saved_generated_variables.iteritems():
                    self.generated_variables[var_name] = var_value
                
            self.attempt_number = latest_submission['attempt_number']
            if (self.attempt_number >= self.max_attempts):
                should_disbled = 'disabled'

        
        self.serialize_data_to_context(context)   
        context['disabled'] = should_disbled         
        context['student_answer'] = self.student_answer
        context['image_url'] = self._image_url
        context['attempt_number'] = self.attempt_number_string
        context['point_string'] = self.point_string
        context['question'] = self.generated_question
        context['xblock_id'] = self.xblock_id
        context['show_answer'] = self.show_answer

        
        frag = Fragment()
        frag.content = loader.render_template('static/html/question_generator_block.html', context)
        frag.add_css(self.resource_string("static/css/question_generator_block.css"))
        frag.add_javascript(self.resource_string("static/js/src/question_generator_block.js"))
        frag.initialize_js('QuestionGeneratorXBlock')
        return frag
    
    
    def studio_view(self, context):
        """
        Render a form for editing this XBlock (override the StudioEditableXBlockMixin's method)
        """
        
        # if the XBlock has been submitted already then disable the studio_edit screen
        location = self.location.replace(branch=None, version=None)  # Standardize the key in case it isn't already
        item_id=unicode(location)

        
        # Student not yet submit then we can edit the XBlock
        fragment = Fragment()
        context = {'fields': []}
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)
                

        # self.serialize_data_to_context(context) ??? REMOVE not necessary, remove 
        context['image_url'] = self._image_url
        context['resolver_selection'] = self._resolver_selection
        context['question_template'] = self._question_template
        context["variables"] = self._variables
        context['answer_template'] = self._answer_template
        context['is_submitted'] = 'False'
        
                
        fragment.content = loader.render_template('static/html/question_generator_studio_edit.html', context)
        fragment.add_css(self.resource_string("static/css/question_generator_block_studio_edit.css"))
        fragment.add_javascript(loader.load_unicode('static/js/src/question_generator_studio_edit.js'))
        fragment.initialize_js('StudioEditableXBlockMixin')
        return fragment
    
    
    def serialize_data_to_context(self, context):
        """
        Save data to context to re-use later to avoid re-accessing the DBMS
        """
        context['saved_question_template'] = self._question_template
        context['saved_url_image'] = self._image_url
        context['saved_resolver_selection'] = self._resolver_selection
        context['saved_answer_template'] = self._answer_template
        context['serialized_variables'] = json.dumps(self._variables)
        context['serialized_generated_variables'] = json.dumps(self.generated_variables)
    
    
    def deserialize_data_from_context(self, context):
        """
        De-serialize data previously saved to context
        """
        self.question_template = context['saved_question_template']
        self.image_url = context['saved_url_image']
        self.resolver_selection = context['saved_resolver_selection']
        self.answer_template = context['saved_answer_template']
        self.variables = json.loads(context['serialized_variables'])
        self.generated_variables = json.loads(context['serialized_generated_variables'])
    
    
    def load_data_from_dbms(self):
        """
        Load question template data from MySQL
        """

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
        
        self.question_template, self.image_url, self.resolver_selection, self.variables, self.answer_template = qgb_db_service.fetch_question_template_data(self.xblock_id)


    @XBlock.json_handler
    def student_submit(self, data, suffix=''):
        """
        AJAX handler for Submit button
        """
        
        self.deserialize_data_from_context(data)
        
        points_earned = 0
        
        # TODO generate the teacher's answer
        
        generated_answer = qgb_question_service.generate_answer(self.generated_variables, self.answer_template)
        student_answer = data['student_answer']
        
        # save the submission
        submission_data = {
            'generated_question': data['saved_generated_question'],
            'student_answer': student_answer,
            'generated_answer': generated_answer,
            'variable_values': data['serialized_generated_variables']
        }
        
        # call matlab
        evaluation_result = self.resolver_handling.syncCall(self.resolver_selection, generated_answer, student_answer )
        #evaluation_result = matlab_service.evaluate_matlab_answer(self.matlab_server_url, self.matlab_solver_url, generated_answer, student_answer)
        if evaluation_result == True:
            points_earned = self.max_points
        submission = sub_api.create_submission(self.student_item_key, submission_data)
        sub_api.set_score(submission['uuid'], points_earned, self.max_points)
        
        submit_result = {}
        submit_result['point_string'] = self.point_string

        # disable the "Submit" button once the submission attempts reach max_attemps value
        self.attempt_number = submission['attempt_number']
        submit_result['attempt_number'] = self.attempt_number_string
        if (self.attempt_number >= self.max_attempts):
            submit_result['submit_disabled'] = 'disabled'
        else:
            submit_result['submit_disabled'] = ''

        return submit_result
    
    
    @XBlock.json_handler
    def fe_submit_studio_edits(self, data, suffix=''):
        """
        AJAX handler for studio edit submission
        """
        
        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
            
        updated_question_template = data['question_template']
        updated_url_image = data['image_url']
        updated_resolver_selection = data['resolver_selection']
        updated_variables = data['variables']
        updated_answer_template = data['answer_template']
        
        #qgb_db_service.update_question_template(self.xblock_id, updated_question_template, updated_url_image, updated_resolver_selection, updated_variables, updated_answer_template)
        
    
        # "refresh" XBlock's values
        self.question_template = updated_question_template
        self.image_url = updated_url_image
        self.resolver_selection = updated_resolver_selection
        self.variables = updated_variables
        self.answer_template = updated_answer_template
        setattr(self, '_image_url', updated_url_image)
        setattr(self, '_resolver_selection', updated_resolver_selection)
        setattr(self, '_question_template', updated_question_template)
        setattr(self, '_answer_template', updated_answer_template)
        setattr(self, '_variables', updated_variables)
        
        # call parent method
        # StudioEditableXBlockMixin.submit_studio_edits(self, data, suffix)
        # self.submit_studio_edits(data, suffix)
        # super(FormulaExerciseXBlock, self).submit_studio_edits(data, suffix)
        
        # copy from StudioEditableXBlockMixin (can not call parent method)
        values = {}  # dict of new field values we are updating
        to_reset = []  # list of field names to delete from this XBlock
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            if field_name in data['values']:
                if isinstance(field, JSONField):
                    values[field_name] = field.from_json(data['values'][field_name])
                else:
                    raise JsonHandlerError(400, "Unsupported field type: {}".format(field_name))
            elif field_name in data['defaults'] and field.is_set_on(self):
                to_reset.append(field_name)
        self.clean_studio_edits(values)
        validation = Validation(self.scope_ids.usage_id)
        # We cannot set the fields on self yet, because even if validation fails, studio is going to save any changes we
        # make. So we create a "fake" object that has all the field values we are about to set.
        preview_data = FutureFields(
            new_fields_dict=values,
            newly_removed_fields=to_reset,
            fallback_obj=self
        )
        self.validate_field_data(validation, preview_data)
        if validation:
            for field_name, value in values.iteritems():
                setattr(self, field_name, value)
            for field_name in to_reset:
                self.fields[field_name].delete_from(self)
            return {'result': 'success'}
        else:
            raise JsonHandlerError(400, validation.to_json())
        
    
    
    @property
    def point_string(self):
        if self.show_points_earned:
            score = sub_api.get_score(self.student_item_key)
            if score != None:
                return str(score['points_earned']) + ' / ' + str(score['points_possible']) + ' point(s)'
            
        return str(self.max_points) + ' point(s) possible'
    
    
    @property
    def attempt_number_string(self):
        if (self.show_submission_times):
            return "You have submitted " + str(self.attempt_number) + "/" + str(self.max_attempts) + " time(s)"
        
        return ""
    
    
    @XBlock.json_handler
    def show_answer_handler(self, data, suffix=''):
        """
        AJAX handler for "Show/Hide Answer" button
        """
        
        self.deserialize_data_from_context(data)
        
        generated_answer = qgb_question_service.generate_answer(self.generated_variables, self._answer_template)
        
        return {
            'generated_answer': generated_answer
        }
    
    
    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("QuestionGeneratorXBlock",
             """<question_generator_block/>
             """),
            ("Multiple QuestionGeneratorXBlock",
             """<vertical_demo>
                <question_generator_block/>
                <question_generator_block/>
                <question_generator_block/>
                </vertical_demo>
             """),
        ]
