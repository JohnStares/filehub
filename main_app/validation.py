import re

def is_username_validated(username: str) -> bool:
    """
    Validates a username against a predefined regex pattern 
    
    :param username: User's Username
    :type username: str
    :rtype: bool
    """
    pattern = re.compile(
		r"^(?:[A-Z][a-z]*\.\s+)?[A-Z][a-z']+(?:\s*[-_.]?\s*[A-Z][a-z']*)*(?:\s+[A-Z][a-z']+)?\d*$", 
		re.IGNORECASE
	)
    
    return bool(pattern.match(username))


def free_from_special_characters(texts: str | list[str], allowed_pattern=None) -> bool:
    """
    Scans a text and ensure it is free from special character. you can pass in a list and it will scan through everything.
    
    :param texts: Either a username, name, email or text in general
    :type texts: str | list[str]
    :param allowed_pattern: A pattern that can be compile to regex containing things you want to allow

    :rtype: bool
    
    """
    if not isinstance(texts, list):
        if not isinstance(texts, str):
            return False
        return False
    
    if allowed_pattern:
        pattern = re.compile(allowed_pattern)
    else:
        pattern = re.compile(r'^(?!.*[!<>#\\/&%$]).*$')

    for text in texts:
        if text == "" or not text.strip(" "):
            return False
        
        if pattern.fullmatch(text) is None:
            return False
        
    return True


def is_email_valid(email: str) -> bool:
    """
    Ensures that the email being provided is valid
    
    :param email: A valid email
    :type email: str
    :return: Either True or False
    :rtype: bool
    """
    pattern = re.compile(r'^(?!\.)(?!.*\.\.)(?!.*\.$)[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+'
        r'@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*'
        r'\.[a-zA-Z]{2,}$'
    )

    if not isinstance(email, str):
        return False
    
    return bool(pattern.fullmatch(email.strip()))