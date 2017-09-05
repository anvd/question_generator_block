import re
from random import randint, uniform

from decimal import *

ONE_PLACE = Decimal(10) ** -1
TWO_PLACES = Decimal(10) ** -2
THREE_PLACES = Decimal(10) ** -3
FOUR_PLACES = Decimal(10) ** -4
FIVE_PLACES = Decimal(10) ** -5
SIX_PLACES = Decimal(10) ** -6
SEVEN_PLACES = Decimal(10) ** -7

DECIMAL_PLACES = [ONE_PLACE, TWO_PLACES, THREE_PLACES, FOUR_PLACES, FIVE_PLACES, SIX_PLACES, SEVEN_PLACES]


def generate_question_template():
    """
    Generates data for a newly created question template
    """
    sample_question_template = "Given a = <a> and b = <b>. Calculate the sum, difference of a and b."

    a_variable = {
        'name': 'a',
        'min_value': 0,
        'max_value': 10,
        'type': 'int',
        'decimal_places': 2
    }

    b_variable = {
        'name': 'b',
        'min_value': 10,
        'max_value': 20,
        'type': 'int',
        'decimal_places': 2
    }

    variables = {
        'a': a_variable,
        'b': b_variable,
    }

    sample_answer_template = ""

    return sample_question_template, variables, sample_answer_template


def get_decimal_places(var_decimal_places_int):
    if (var_decimal_places_int < 1):
        return ONE_PLACE
    elif (var_decimal_places_int > 7):
        return SEVEN_PLACES

    return DECIMAL_PLACES[var_decimal_places_int - 1]


def generate_question_old(question_template, variables):
    compiled_variable_patterns = {}
    generated_variables = {}

    # generate variables' value
    for var_name, variable in variables.iteritems():
        compiled_variable_patterns[var_name] = re.compile('<' + var_name + '>')
        var_type = variable['type']

        var_value = ""
        if var_type == 'int':
            var_value = str(randint(int(variable['min_value']), int(variable['max_value'])))
        else:  # float
            var_decimal_places_int = int(variable['decimal_places'])
            var_value = str(uniform(float(variable['min_value']), float(variable['max_value'])))
            var_decimal_places = get_decimal_places(var_decimal_places_int)
            var_value = str(Decimal(var_value).quantize(var_decimal_places))

        generated_variables[var_name] = var_value

    # generate the question and answer
    generated_question = question_template
    for var_name, var_value in generated_variables.iteritems():
        generated_question = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]),
                                                                      generated_question)

    return generated_question, generated_variables


def generate_question(question_template, variables):
    compiled_variable_patterns = {}
    generated_variables = {}

    print("## CALLING FUNCTION generate_question() ##")
    print("## START DEBUG INFO ##")
    print("question_template = {}".format(question_template))
    print("variables= {}".format(variables))

    # generate variables' value
    for var_name, variable in variables.iteritems():
        #
        compiled_variable_patterns[var_name] = re.compile('\[' + var_name + '\]')
        var_type = variable['type']

        var_value = ""
        if var_type == 'int' or var_type == 'integer':
            var_value = str(randint(int(variable['min_value']), int(variable['max_value'])))
        elif var_type == 'float' or var_type == 'double' or var_type == 'real':  # number is not integer
            var_decimal_places_int = int(variable['decimal_places'])
            var_value = str(uniform(float(variable['min_value']), float(variable['max_value'])))
            var_decimal_places = get_decimal_places(var_decimal_places_int)
            var_value = str(Decimal(var_value).quantize(var_decimal_places))
        else:  # string?
            pass

        generated_variables[var_name] = var_value

    print("generated_variables= {}".format(generated_variables))
    print("compiled_variable_patterns= {}".format(compiled_variable_patterns))

    # generate the question and answer
    generated_question = question_template
    # replace values into varibales
    for var_name, var_value in generated_variables.iteritems():
        generated_question = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]),
                                                                      generated_question)

    print("generated_question= {}".format(generated_question))
    print("## END DEBUG INFO ##")
    print("## End FUNCTION generate_question() ##")

    return generated_question, generated_variables


# TODO: remove this function
def generate_answer_string(generated_variables, answer_template_string):

    print("## CALLING FUNCTION generate_answer_string() ##")
    print("## START DEBUG INFO ##")
    print("BEFORE, generated_variables = {}".format(generated_variables))
    print "BEFORE, _answer_template_string = ", answer_template_string

    compiled_variable_patterns = {}
    for var_name, var_value in generated_variables.iteritems():
        # compiled_variable_patterns[var_name] = re.compile('<' + var_name + '>')
        compiled_variable_patterns[var_name] = re.compile('\[' + var_name + '\]')

    generated_answer = answer_template_string  # string
    for var_name, var_value in generated_variables.iteritems():
        generated_answer = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]),
                                                                    generated_answer)

    print "AFTER, generated_answer = ", generated_answer
    print("## END DEBUG INFO ##")
    print("## End FUNCTION generate_answer_string() ##")

    return generated_answer


def generate_answer(generated_variables, answer_template):
    '''
    Generate solutions for given problem. Each answer may have many key attributes

    :param generated_variables:
    :param answer_template:
    :return: a dict of answers for given attributes
    '''

    print("## CALLING FUNCTION generate_answer() ##")
    print("## START DEBUG INFO ##")
    print("BEFORE, generated_variables = {}".format(generated_variables))
    print("BEFORE, _answer_template_string = {}".format(answer_template))

    # compile regular expression pattern object to search for given variables in the answer template
    compiled_variable_patterns = {}
    for var_name, var_value in generated_variables.iteritems():
        compiled_variable_patterns[var_name] = re.compile('\[' + var_name + '\]')
    # print("compiled_variable_patterns = {}".format(compiled_variable_patterns))

    # prepare answer dict
    generated_answer = {}

    # generate answers by key
    for key, value in answer_template.iteritems():
        print("key = {}".format(key))
        print("value = {}".format(value))
        generated_answer[key] = answer_template[key]  # get answer template by key
        for var_name, var_value in generated_variables.iteritems():
            print("var_name = {}".format(var_name))
            print("var_value = {}".format(var_value))
            # replace values into variables for the answer template
            generated_answer[key] = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]),
                                                                             generated_answer[key])

    print("AFTER, generated_answer = {}".format(generated_answer))
    print("## END DEBUG INFO ##")
    print("## End FUNCTION generate_answer() ##")

    return generated_answer


if __name__ == "__main__":
    question_template1 = "What is the energy to raise <n> apples to <m> meters?"
    n_variable = {
        'name': 'n',
        'type': 'int',
        'min_value': 1,
        'max_value': 10,
        'decimal_places': 2
    }

    m_variable = {
        'name': 'm',
        'type': 'int',
        'min_value': 5,
        'max_value': 20,
        'decimal_places': 2
    }

    variables = {
        'n': n_variable,
        'm': m_variable
    }

    answer_template = "<n> apples and <m> meters is the answer"

    generated_question, generated_variables = generate_question(question_template1, variables)

    print('test_template1: ' + question_template1)
    print('generated question: ' + generated_question)
    print 'Generated n: ' + generated_variables['n']
    print 'Generated m: ' + generated_variables['m']

    generated_answer = generate_answer(generated_variables, answer_template)
    print('generated answer: ' + generated_answer)

