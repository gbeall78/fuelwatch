import exceptions
import re

def validateHTMLStyleAttribute(testCase):
    if re.search("^((\w+(-\w+)*:\w+);)+$", testCase) is None:
        raise exceptions.invalidStyleParameter(f'{testCase} - Invalid style attribute given. Format should contain at least one set of "word:word;"')

def validateHTMLClassAttribute(testCase):
    if re.search("^[_\-a-zA-Z]{1}\w+$", testCase) is None:
        raise exceptions.invalidClassParameter(f'{testCase} - Invalid class attribute given. Format should contain at least one set of "word"')

def validateHTMLTableHeader(testCase, data):
    if testCase == '':
        raise noTableHeaderException(f'The table must contain a header row.')
    if leng(testCase) != len(data):
        raise tableHeaderDataSizeMismatchException(f'Different number of columns between the header and data')