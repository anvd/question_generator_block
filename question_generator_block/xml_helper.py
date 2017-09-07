import sys
from xblock.exceptions import JsonHandlerError, NoSuchViewError

try:
    # Python 3
    import cElementTree as ET
except ImportError:
  try:
    # Python 2 need to import a different module
    import xml.etree.cElementTree as ET
  except ImportError:
    sys.exit("Failed to import cElementTree from any known place")


def convert_problem_data_to_xml(data):
    '''
    Process raw edit for problem data fields in Editor tab:

        1. problem description
        2. Image url
        3. variables (name, min_value, max_value, type, decimal_places)
        4. _answer_template_string

    :param data: dictionary
    :return:
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
    '''
    print("## CALLING FUNCTION convert_problem_data_to_xml() ##")
    print("Input data dict: {}".format(data))

    xml_string = ''
    problem = ET.Element('problem')

    # convert question template
    field_question_template = data['question_template']
    description = ET.SubElement(problem, 'description')
    description.text = field_question_template


    # convert image
    field_image_url = data['image_url']
    # xml elements
    image_group = ET.SubElement(problem, 'image_group')
    image_url = ET.SubElement(image_group, 'image_url')
    # Set attribute
    image_url.set('link', field_image_url)

    # convert variables
    variables = data['variables']
    # xml elements
    variable_group = ET.SubElement(problem, 'variable_group')
    for var_name, attributes in variables.iteritems():
        var_name = ET.SubElement(variable_group, 'variable')
        for attribute, value in attributes.iteritems():
            # Set attribute
            var_name.set(attribute, value)

    # Convert answer template tring to dictionary, then build xml data
    field_answer_template = data['answer_template']
    # Check for empty input
    if not field_answer_template:
        raise JsonHandlerError(400, "Answer template must not be empty")


    # Parse and convert answer template string to dict first
    answer_template_dict = {}
    answer_template_list = field_answer_template.split('\n')
    print("data type of answer_template_list: {}".format(type(answer_template_list)))
    print "answer_template_list = "
    print(answer_template_list)
    print "field_answer_template = "
    print(field_answer_template)

    for answer in answer_template_list:
        # only process if not empty, ignore empty answer template
        if answer:
            # answer template must contains '=' character
            if (answer.find('=') != -1):    # found '=' at lowest index of string
                answer_attrib_list = answer.split('=')
                print "answer_attrib_list = "
                print(answer_attrib_list)

                answer_attrib_key = answer_attrib_list[0]
                answer_attrib_value = answer_attrib_list[1]
                print "answer_attrib_key = "
                print(answer_attrib_key)
                print "answer_attrib_value = "
                print(answer_attrib_value)

                # Remove unexpected white spaces
                answer_attrib_key = answer_attrib_key.lstrip()  # all leading whitespaces are removed from the string.
                answer_attrib_key = answer_attrib_key.rstrip()  # all ending whitespaces are removed from the string.
                answer_attrib_value = answer_attrib_value.lstrip()  # all leading whitespaces are removed from the string.
                answer_attrib_value = answer_attrib_value.rstrip()  # all ending whitespaces are removed from the string.

                print "REMOVED SPACES, answer_attrib_key = "
                print(answer_attrib_key)
                print "REMOVED SPACES,answer_attrib_value = "
                print(answer_attrib_value)

                # Add answer attribute to dict
                answer_template_dict[answer_attrib_key] = answer_attrib_value
            else:
                raise JsonHandlerError(400, "Unsupported answer format. Answer template must contains '=' character: {}".format(answer))

    print("Resulted answer_template_dict: {}".format(answer_template_dict))

    # xml elements
    solution_group = ET.SubElement(problem, 'solution_group')
    solution = ET.SubElement(solution_group, 'solution')
    # Add the converted dict data to xml elements
    for attrib_key, attrib_value in answer_template_dict.iteritems():
        solution.set(attrib_key, attrib_value)
        solution.text = 'Answer template'

    print "Problem elem dum = ", ET.dump(problem)

    indented_problem = indent(problem)
    print "after indent ,Problem elem dum = ", ET.dump(indented_problem)

    xml_string = ET.tostring(indented_problem)

    print "Output xml string = ", xml_string
    print("## End FUNCTION convert_problem_data_to_xml() ##")

    return xml_string

def read_data_from_xml_string(xml_data):
    '''
    Process raw edit for problem data fields in Editor tab:

        1. problem description
        2. Image url
        3. variables (name, min_value, max_value, type, decimal_places)
        4. _answer_template_string


    <problem>
        <description>Given a = [a] and b = [b], c = [c]. Calculate the [sum], [difference] of a and b. </description>
        <image_group>
            <image_url link="http://example.com/image1">Image 1</image_url>
            <image_url link="http://example.com/image2">Image 2</image_url>
        </image_group>
        <variable_group>
            <variable name="a" min="1" max="200" type="integer"/>
            <variable name="b" min="1.0" max="20.5" type="float" decimal_places="2"/>
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

def dict_to_string(dict, sep = '\n'):

    result = ""
    for key, value in dict.iteritems():
        result = result + key + '=' + value
        result = result + sep

    return result

# TODO: check why this function has problem? Only return the last child tag of elem.
# in-place prettyprint formatter
# def indent(elem, level=0):
#     i = "\n" + level*"  "
#     if len(elem):
#         if not elem.text or not elem.text.strip():
#             elem.text = i + "  "
#         if not elem.tail or not elem.tail.strip():
#             elem.tail = i
#         for elem in elem:
#             indent(elem, level+1)
#         if not elem.tail or not elem.tail.strip():
#             elem.tail = i
#     else:
#         if level and (not elem.tail or not elem.tail.strip()):
#             elem.tail = i
#     return elem

# Follow https://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem
