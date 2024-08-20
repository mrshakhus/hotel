import re


def format_query(query):
    query = query.lower()
    query = re.sub(r'[^\w\s]', '', query)
    
    tokens = query.split()
    formatted_query = ' & '.join(tokens)

    return formatted_query