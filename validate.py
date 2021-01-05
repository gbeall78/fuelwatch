import exceptions as e
import re

def validateHTMLStyleAttribute(testCase):
    if re.search("^((\w+(-\w+)*:\w+);)+$", testCase) is None:
        raise e.invalidStyleParameter(f'{testCase} - Invalid style attribute given. Format should contain at least one set of "word:word;"')

def validateHTMLClassAttribute(testCase):
    if re.search("^[_\-a-zA-Z]{1}\w+$", testCase) is None:
        raise e.invalidClassParameter(f'{testCase} - Invalid class attribute given. Format should contain at least one set of "word"')

def validateHTMLTableHeader(testCase, data):
    if testCase == '':
        raise e.noTableHeaderException(f'The table must contain a header row.')
    if len(testCase) != len(data):
        raise e.tableHeaderDataSizeMismatchException(f'Different number of columns between the header and data')