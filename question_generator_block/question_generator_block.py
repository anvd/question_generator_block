"""TO-DO: Write a description of what this XBlock is."""

import sys
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

try:
    # Python 3
    import cElementTree as ET
except ImportError:
  try:
    # Python 2 need to import a different module
    import xml.etree.cElementTree as ET
  except ImportError:
    sys.exit("Failed to import cElementTree from any known place")

loader = ResourceLoader(__name__)


@XBlock.needs("i18n")
class QuestionGeneratorXBlock(XBlock, SubmittingXBlockMixin, StudioEditableXBlockMixin):
    """
    Question Generator XBlock
    """

    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="Question Generator Block"
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

    _solver = String(
        display_name = "Problem Solver",
        help = "Select a solver for this problem",
        default = 'matlab',
        scope = Scope.settings,
        values = [
                    {"display_name": "MatLab", "value": "matlab"},
                    {"display_name": "None", "value": "none"},
                ]
    )

    _question_template = String (
        display_name = "Question Template",
        help = "",
        default = "Given a = [a] and b = [b]. Calculate the sum, difference of a and b.",
        scope = Scope.settings)

    # _answer_template = String (
    #     display_name = "Answer Template",
    #     help = "Teacher has to fill the answer here!!!",
    #     default = "x =<a> + <b>",
    #     scope = Scope.settings)

    _answer_template = Dict(
        display_name="Answer Template",
        help="Teacher has to fill the answer here!!!",
        default=
            {
                "sum": "[a] + [b]",
                "difference": "[a] - [b]"
            },
        scope=Scope.settings
    )

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

    xblock_id = None

    component_location_id = String(
        display_name="Component Location ID",
        help="",
        default=xblock_id,  # TODO: get xblock_id
        scope=Scope.settings
    )

    raw_data = '''<problem>
        <description>Given a = [a] and b = [b]. Calculate the sum, difference of a and b. </description>
        <image_group>
                <image_url link="http://example.com/image1">Image 1</image_url>
        </image_group>
        <variable_group>
                <variable name="a" type="integer" min_value="1" max_value="200"/>
                <variable name="b" type="float" min_value="1.0" max_value="200.5" decimal_places="2"/>
        </variable_group>
        <solution_group>
                <solution sum = "[a] + [b]" difference = "[a] - [b]">Answer 1</solution>
        </solution_group>
</problem>
    '''

    _problem_raw_data = String(
        display_name="Problem raw data",
        help="Raw data passed to XML editor",
        default=raw_data,
        scope=Scope.content
    )

    enable_template = False # False for Editor mode, True for Template mode.

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


    editable_fields = ('display_name',
                       '_solver',
                       'max_attempts',
                       'max_points',
                       'show_points_earned',
                       'show_submission_times',
                       'show_answer',
                       'component_location_id',
                       '_problem_raw_data'
                       )

    has_score = True
    show_in_read_only_mode = True
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
        print("## Calling FUNCTION student_view() ##")
        context = context

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))

        should_disbled = ''

        # generate question from template if necessary
        # self.generated_question, self.generated_variables = qgb_question_service.generate_question(self._question_template, self._variables)
        self.generated_question, self.generated_variables = qgb_question_service.generate_question_edit(
            self._question_template, self._variables)

        print("## START DEBUG INFO ##")
        print("context = {}".format(context))
        print("self.generated_question = {}".format(self.generated_question))
        print("self.generated_variables = {}".format(self.generated_variables))
        print("## END DEBUG INFO ##")

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
        # Add below fields to context
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
        print("## End FUNCTION student_view() ##")

        return frag


    def studio_view(self, context):
        """
        Render a form for editing this XBlock (override the StudioEditableXBlockMixin's method)
        """
        print("## Calling FUNCTION studio_view() ##")

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
        context['enable_template'] = self.enable_template

        # problem data to display to xml editor
        context['problem_raw_data'] = self._problem_raw_data

        print("## START DEBUG INFO ##")
        print("context = {}".format(context))
        print("## End DEBUG INFO ##")

        # fragment.content = loader.render_template('static/html/question_generator_studio_edit.html', context)
        fragment.content = loader.render_template('static/html/studio_raw_edit.html', context)

        fragment.add_css(self.resource_string("static/css/question_generator_block_studio_edit.css"))

        # fragment.add_javascript(loader.load_unicode('static/js/src/question_generator_studio_edit.js'))
        fragment.add_javascript(loader.load_unicode('static/js/src/studio_raw_edit.js'))
        fragment.initialize_js('StudioEditableXBlockMixin')

        print("## End FUNCTION studio_view() ##")

        return fragment


    def serialize_data_to_context(self, context):
        """
        Save data to context to re-use later to avoid re-accessing the DBMS
        """
        print("## CALLING FUNCTION serialize_data_to_context() ##")
        print("## START DEBUG INFO ##")
        print("self._question_template = {}".format(self._question_template))
        print("self._image_url = {}".format(self._image_url))
        print("self._variables= {}".format(self._variables))
        print("self.generated_variables= {}".format(self.generated_variables))
        print("self._answer_template= {}".format(self._answer_template))
        print("## END DEBUG INFO ##")

        context['saved_question_template'] = self._question_template
        context['saved_url_image'] = self._image_url
        context['serialized_variables'] = json.dumps(self._variables)
        context['serialized_generated_variables'] = json.dumps(self.generated_variables)
        context['saved_answer_template'] = self._answer_template
        # context['saved_resolver_selection'] = self._resolver_selection # Old
        context['saved_resolver_selection'] = self._solver  # use _solver from editable_fields

        print("context = {}".format(context))
        print("## End FUNCTION serialize_data_to_context() ##")


    def deserialize_data_from_context(self, context):
        """
        De-serialize data previously saved to context
        """
        print("## CALLING FUNCTION deserialize_data_from_context() ##")

        self.question_template = context['saved_question_template']
        self.image_url = context['saved_url_image']
        self.answer_template = context['saved_answer_template']
        self.variables = json.loads(context['serialized_variables'])
        self.generated_variables = json.loads(context['serialized_generated_variables'])
        self.resolver_selection = context['saved_resolver_selection']   # TODO: update this to new field in Settings tab

        print("## START DEBUG INFO ##")
        print("self._question_template = {}".format(self.question_template))
        print("self.image_url = {}".format(self.image_url))
        print("self.answer_template = {}".format(self.answer_template))
        print("self.variables = {}".format(self.variables))
        print("self.generated_variables = {}".format(self.generated_variables))
        print("self.resolver_selection = {}".format(self.resolver_selection))
        print("## End DEBUG INFO ##")
        print("## End FUNCTION deserialize_data_from_context() ##")


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

        print("## CALLING FUNCTION student_submit() ##")
        print("## START DEBUG INFO ##")
        print("data = {}".format(data))

        self.deserialize_data_from_context(data)

        points_earned = 0

        # TODO generate the teacher's answer
        # Generate answer for this submission
        generated_answer = qgb_question_service.generate_answer(self.generated_variables, self._answer_template)

        student_answer = data['student_answer']
        # save the submission
        submission_data = {
            'generated_question': data['saved_generated_question'],
            'student_answer': student_answer,
            'generated_answer': generated_answer,
            'variable_values': data['serialized_generated_variables']
        }
        print("submission_data = {}".format(submission_data))

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

        print("## End FUNCTION student_submit() ##")

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

    @XBlock.json_handler
    def fe_submit_studio_raw_edits(self, data, suffix=''):
        """
        AJAX handler for studio edit submission
        """

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))

        print("## Calling FUNCTION fe_submit_studio_raw_edits() ###")
        print("## DEBUG INFO ###")
        print("All POST fields: {}".format(data))
        print("### xml_data: ###")
        print(data['problem_raw_data'])
        print("## End DEBUG INFO ###")

        # Process raw edit
        updated_xml_string = data['problem_raw_data']

        # Extract data fields from xml string
        # TODO: Process XML data using XML parser cElementTree,
        raw_edit_data = self.read_data_from_xml_string(updated_xml_string)

        # TODO: then save to DB model?
        # qgb_db_service.update_question_template(self.xblock_id, updated_question_template, updated_url_image, updated_resolver_selection, updated_variables, updated_answer_template)

        updated_question_template = raw_edit_data['question_template']
        updated_url_image = raw_edit_data['image_url']
        updated_variables = raw_edit_data['variables']
        updated_answer_template = raw_edit_data['solutions'][1]  # get only one firt answer for now. TODO: update to support multi-answers attributes for multiple solutions
        # updated_resolver_selection = data['_solver']

        # "refresh" XBlock's values
        # update values to global variables
        self.question_template = updated_question_template
        self.image_url = updated_url_image
        self.variables = updated_variables
        self.answer_template = updated_answer_template
        # self.resolver_selection = updated_resolver_selection

        # update values to global fields
        setattr(self, '_question_template', updated_question_template)
        setattr(self, '_image_url', updated_url_image)
        setattr(self, '_answer_template', updated_answer_template)
        setattr(self, '_variables', updated_variables)
        # setattr(self, '_resolver_selection', updated_resolver_selection)

        # update problem fields
        self.raw_data = updated_xml_string
        setattr(self, '_problem_raw_data', updated_xml_string)

        # HANDLE FIELDS IN editable_fields
        #
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

            print("## End FUNCTION fe_submit_studio_raw_edits() ###")
            return {'result': 'success'}
        else:
            raise JsonHandlerError(400, validation.to_json())

    def read_data_from_xml_string(self, xml_data):
        '''
        Process raw edit for problem data fields in Editor tab:

            1. problem description
            2. Image url
            3. variables (name, min_value, max_value, type, decimal_places)
            4. answer_template


        <problem>
            <description>Given a = [a] and b = [b], c = [c]. Calculate the [sum], [difference] of a and b. </description>
            <image_group>
                <image_url link="http://example.com/image1">Image 1</image_url>
                <image_url link="http://example.com/image2">Image 2</image_url>
            </image_group>
            <variable_group>
                <variable name="a" min="1" max="200" type="integer"/>
                <variable name="b" min="1.0" max="20.5" type="float" decimal_places="2"/>
                <variable name="c" min="1" max="200"  type="string"/>
            </variable_group>
            <solution_group>
                <solution sum = "[a] + [b] + [c]" difference = "[a] - [b] - [c]">Answer 2</solution>
                <solution sum = "[b] + [c] + [a]" difference = "[c] - [b] - [a]">Answer 3</solution>
            </solution_group>
        </problem>

        :param xml_data:
        :return:
        '''
        print("## CALLING FUNCTION read_data_from_xml_string() ##")

        # Reading the xml data from a string:
        # fromstring() parses XML from a string directly into an Element, which is the root element of the parsed tree.
        problem = ET.fromstring(xml_data)
        problem_childs = problem.getchildren()
        # print(problem_childs)

        # init a dict to store problem field values extracted from the xml string
        problem_data_fields = {}

        for field in problem_childs:
            # print("field.tag: " + field.tag)
            # print("field.attrib: ", field.attrib)
            if field.tag == "description":
                # extract the question template
                problem_data_fields["question_template"] = field.text
            elif field.tag == "image_group":
                # Extract image url
                #
                # A problem can have many images
                # only get first image_url for now
                # TODO: support multiple images
                image_urls = field.findall('image_url')  # find all direct children only for this field.
                # get first image_url
                problem_data_fields["image_url"] = image_urls[0].get('link')  # get its link attrib
            elif field.tag == "variable_group":
                # Extract variables info
                problem_data_fields["variables"] = {}  # initialize the variables dict
                # find all direct childs of element 'variable_group'
                variable_list = field.findall("variable")
                for variable in variable_list:
                    variable_attributes = variable.attrib
                    var_name = variable_attributes["name"]
                    # if var_type == "float":
                    #     var_decimal_places = variable_attributes["decimal_places"]

                    # add each variable into the variable dict
                    problem_data_fields["variables"][var_name] = variable_attributes

            elif field.tag == "solution_group":
                # Extract the solutions
                problem_data_fields["solutions"] = {}  # initialize the solutions dict
                # find all direct childs of element 'solver_group'
                solver_list = field.findall("solution")
                i = 0
                for solver in solver_list:
                    i = i + 1
                    solver_attributes = solver.attrib
                    # add each solution into the problem data
                    problem_data_fields["solutions"][i] = solver_attributes

            print("## End FUNCTION read_data_from_xml_string() ##")

        return problem_data_fields


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
        print("## CALLING FUNCTION show_answer_handler() ##")
        print("## START DEBUG INFO ##")
        print("data = {}".format(data))

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
