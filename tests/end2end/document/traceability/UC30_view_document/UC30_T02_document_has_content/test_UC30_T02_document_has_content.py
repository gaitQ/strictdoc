from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC30_T02_document_has_content(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document title")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen()
            screen_document.assert_header_document_title("Document title")
            screen_document.assert_text("Hello world!")

        assert test_setup.compare_sandbox_and_expected_output()
