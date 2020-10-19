import exceptions
import re

def validateHTMLStyleAttribute(testCase):
    if re.search("^((\w+(-\w+)*:\w+);)+$", testCase) is None:
        raise exceptions.invalidStyleParameter(f'{testCase} - Invalid style attribute given. Format should contain at least one set of "word:word;"')


def validateHTMLClassAttribute(testCase):
    if re.search("^[_\-a-zA-Z]{1}\w+$", testCase) is None:
        raise exceptions.invalidClassParameter(f'{testCase} - Invalid class attribute given. Format should contain at least one set of "word"')