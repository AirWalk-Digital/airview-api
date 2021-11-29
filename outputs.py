from junitparser import TestCase, Attr, JUnitXml

class StaticAnalysisTestCase(TestCase):
    file = Attr()



xml = JUnitXml.fromfile('static-analysis.xml')
for suite in xml:
    # handle suites
    for case in suite:
        # handle cases
        #print(case)
        # handle suites
    
        error_case = StaticAnalysisTestCase.fromelem(case)

        #file=error_case.file
        #line=error_case..line
        #check_name=error_case.name

        print(error_case.file)