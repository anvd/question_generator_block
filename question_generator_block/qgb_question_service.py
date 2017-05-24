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

DECIMAL_PLACES = [ ONE_PLACE, TWO_PLACES, THREE_PLACES, FOUR_PLACES, FIVE_PLACES, SIX_PLACES, SEVEN_PLACES ]



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


def generate_question(question_template, variables):
    
    compiled_variable_patterns = {}
    generated_variables = {}
    
    
    # generate variables' value
    for var_name, variable in variables.iteritems():
        compiled_variable_patterns[var_name] = re.compile('<' + var_name + '>')
        var_type = variable['type']
        var_decimal_places_int = int(variable['decimal_places'])
        
        var_value = ""
        if var_type == 'int':
            var_value = str(randint(int(variable['min_value']), int(variable['max_value'])))
        else: # float
            var_value = str(uniform(float(variable['min_value']), float(variable['max_value'])))
            var_decimal_places = get_decimal_places(var_decimal_places_int)
            var_value = str(Decimal(var_value).quantize(var_decimal_places))

        generated_variables[var_name] = var_value
        
    
    # generate the question and answer
    generated_question = question_template
    for var_name, var_value in generated_variables.iteritems():
        generated_question = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]), generated_question)
    
    
    return generated_question, generated_variables


def generate_answer(generated_variables, answer_template):
    
    compiled_variable_patterns = {}
    for var_name, var_value in generated_variables.iteritems():
        compiled_variable_patterns[var_name] = re.compile('<' + var_name + '>')
    
    generated_answer = answer_template
    for var_name, var_value in generated_variables.iteritems():
        generated_answer = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]), generated_answer)
    
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
    print('generated question: ' +  generated_question)
    print 'Generated n: ' + generated_variables['n']
    print 'Generated m: ' + generated_variables['m']
    
    
    generated_answer = generate_answer(generated_variables, answer_template)
    print('generated answer: ' +  generated_answer)
    
