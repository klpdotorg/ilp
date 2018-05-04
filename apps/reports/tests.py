from io import StringIO
from django.core.management import call_command
from django.test import TestCase
import tempfile
import os.path
from reports.reports import ReportOne 

#class ReportGenerateTest(TestCase):
    # def test_command_output(self):
    #     with open('/tmp/testout', 'w') as out_file:
    #         #StringIO()
    #         # args = ('sndfs', 'adfadf', 'report_one','pdf', 'test')
    #         call_command('reportgen','sndfs', 'adfadf', 'report_one','pdf', 'test', stdout=out_file)
    #         self.assertIn('success', out_file.read())
    
            
class GeneratedOutputTest(TestCase):
    def test_html_output(self):
        r = ReportOne('from_date','to_date')
        r.get_html('test_run')
        self.assertTrue(os.path.exists('apps/reports/output/test_run.html'))

    def test_pdf_output(self):
        r = ReportOne('from_date','to_date')
        r.get_pdf('test_run')
        self.assertTrue(os.path.exists('apps/reports/reports_pdf/test_run.pdf'))
