"""
naming @ utilities

utilities to work with names and strings
"""


def remove_suffix(name):
    
    """
    Remove suffix from given name string
    
    @param name: given name string to process
    @return: str, name without suffix
    """
    
    edits = name.split( '_' )
    
    if len(edits) < 2:
        return name
    
    suffix = '_' + edits[-2] + '_' + edits[-1]
    name_without_suffix = name[ :-len(suffix)]
    
    return name_without_suffix

def remove_prefix(name):
    
    """
    Remove prefix from given name string
    
    @param name: given name string to process
    @return: str, name without prefix
    """
    
    edits = name.split( '_' )
    
    if len(edits) < 2:
        return name
    
    prefix = edits[0] + '_'
    name_without_prefix = name[ len(prefix): ]
    
    return name_without_prefix


def renumber(name):
    
    """
    Attempt to reset numerical ending of given 'name' string to "01"
    
    @param name: given name string to process
    @return: str, name without prefix
    """
    
    edits = name.split( '_' )
    
    if len(edits) < 2:
        return name
    
    numerical_suffix = '_' + edits[-1]
    name_without_suffix = name[ :-len(numerical_suffix)]
    
    new_name = name_without_suffix + '_01'
    return new_name











