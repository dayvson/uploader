from uploader import TestHTTPClientApplicationsRoutesSuite
from uploader_webdriver import TestAcceptanceUploaderSuite
import unittest

def run():
    unit_suite = TestHTTPClientApplicationsRoutesSuite()
    webdriver_acceptance = TestAcceptanceUploaderSuite()
    alltests = unittest.TestSuite((unit_suite, webdriver_acceptance))
    runner = unittest.TextTestRunner()
    runner.run(alltests)

    
if __name__ == "__main__":
    run()