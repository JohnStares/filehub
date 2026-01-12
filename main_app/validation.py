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