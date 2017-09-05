import mysql.connector
from mysql.connector import errorcode
import settings as s



def create_question_template(xblock_id, question_template, image_url, resolver_selection, variables, answer_template):
    """
    Inserts a new question template into the database
        question template
        variables
    """
    connection = mysql.connector.connect(**s.database)
    
    # clean_up_variables_and_expressions(fe_xblock, connection)
    
    insert_question_template(xblock_id, connection, question_template, image_url, resolver_selection, answer_template)
    
    create_variables(xblock_id, connection, variables)
    
    connection.commit()
    connection.close()


def update_question_template(xblock_id, question_template, image_url, resolver, updated_variables, answer_template):
    """
    Updates an existing question template in the database
    """
        
    connection = mysql.connector.connect(**s.database)
    
    clean_up_variables_and_expressions(xblock_id, connection)
    
    update_question_template_content(xblock_id, connection, question_template, image_url, resolver, answer_template)
    
    create_variables(xblock_id, connection, updated_variables)
    
    connection.commit()
    connection.close()


def fetch_question_template_data(xblock_id):
    """
    Fetches question template data from the database:
        question_template
        variables
        _answer_template_string
    """
    connection = mysql.connector.connect(**s.database)
    
    question_template = ""
    url_image = ""
    resolver= ""
    answer_template = ""
    variables = {}
    
    # query question_template
    question_template_query = "SELECT template, url_image, resolver, _answer_template_string FROM edxapp.qgb_question_template where xblock_id = '" + xblock_id + "'"
    print question_template_query
    question_template_cursor = connection.cursor()
    question_template_cursor.execute(question_template_query)
    row = question_template_cursor.fetchone()
    
    if row is not None:
        question_template = row[0]
        url_image = row[1]
        resolver = row[2]
        answer_template = row[3]
    question_template_cursor.close()
    
    
    # query variables
    variable_query = "SELECT name, type, min_value, max_value, type, decimal_places FROM edxapp.qgb_variable WHERE xblock_id = '" + xblock_id + "'"
    variable_query_cursor = connection.cursor()
    variable_query_cursor.execute(variable_query)
    row = variable_query_cursor.fetchone()
    
    
    # fetch variables from the result set
    while row is not None:
        variable = {}
        variable['name'] = row[0]
        variable['type'] = row[1]
        variable['min_value'] = row[2]
        variable['max_value'] = row[3]
        variable['type'] = row[4]
        variable['decimal_places'] = row[5]
        
        variables[variable['name']] = variable
        row = variable_query_cursor.fetchone()
        
    variable_query_cursor.close()
    
    
    connection.close()
    return question_template, url_image, resolver, variables, answer_template


def clean_up_variables_and_expressions(xblock_id, connection):
    """
    Removes variables of the question template
    """
    
    cursor = connection.cursor()
    
    # remove variables
    VARIABLES_REMOVE_QUERY = ("DELETE FROM edxapp.qgb_variable WHERE xblock_id = '" + xblock_id + "'")
    cursor.execute(VARIABLES_REMOVE_QUERY)
    
    cursor.close()


def insert_question_template(xblock_id, connection, question_template, image_url, resolver, answer_template):
    cursor = connection.cursor()
    query = "INSERT INTO edxapp.qgb_question_template (xblock_id, template, url_image, resolver, _answer_template_string) VALUES ('" + xblock_id + "', '" + question_template + "', '"  + image_url + "', '" + resolver + "', '" +  answer_template + "')"
    print query
    cursor.execute(query)
    cursor.close()


def update_question_template_content(xblock_id, connection, question_template, image_url, resolver, answer_template):
    """
    Updates question template
    """
    
    cursor = connection.cursor()
    query = "UPDATE edxapp.qgb_question_template SET template = '" + question_template + "', url_image = '" + image_url + "', resolver = '" + resolver + "', _answer_template_string = '" + answer_template + "' WHERE xblock_id = '" + xblock_id + "'"
    print query
    cursor.execute(query)
    cursor.close()


def create_variables(xblock_id, connection, updated_variables):
    """
    Creates variables for a question template
    """
    
    cursor = connection.cursor()
    query = "INSERT INTO edxapp.qgb_variable (xblock_id, name, type, min_value, max_value, decimal_places) VALUES (%s, %s, %s, %s, %s, %s)"
    print query
    for variable_name, variable in updated_variables.iteritems():
        updated_variable_data = (xblock_id, variable_name, variable['type'], variable['min_value'], variable['max_value'], variable['decimal_places'])
        cursor.execute(query, updated_variable_data)
    
    cursor.close()


def is_block_in_db(xblock_id):
    
    connection = mysql.connector.connect(**s.database)
    
    query = "SELECT id FROM edxapp.qgb_question_template WHERE xblock_id = '" + xblock_id + "'"
    print query
    cursor = connection.cursor()
    cursor.execute(query)
    
    rowcount = cursor.rowcount
    cursor.close()
    connection.close()

    return (rowcount > 0)


def delete_xblock(xblock_id):
    
    connection = mysql.connector.connect(**s.database)
    
    delete_query_str = "DELETE FROM edxapp.qgb_question_template WHERE xblock_id like '%" + xblock_id + "%'"
    cursor = connection.cursor()
    cursor.execute(delete_query_str)
    
    cursor.close()
    connection.commit()
    connection.close()
    
    
def is_xblock_submitted(item_id):
    
    # 1. TABLE submissions_studentitem(id)
    # 2. TABLE submissions_submission(student_item_id)
    """
    SELECT count(*) FROM edxapp.submissions_submission WHERE student_item_id IN (SELECT id FROM edxapp.submissions_studentitem WHERE item_id = item_id )
    """
    
    is_submitted = False
    
    query = "SELECT count(*) FROM edxapp.submissions_submission WHERE student_item_id IN (SELECT id FROM edxapp.submissions_studentitem WHERE item_id = '" + item_id + "')"
    connection = mysql.connector.connect(**s.database)
    cursor = connection.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        is_submitted = row[0] > 0
        
    cursor.close()
    connection.close()

    return is_submitted    
