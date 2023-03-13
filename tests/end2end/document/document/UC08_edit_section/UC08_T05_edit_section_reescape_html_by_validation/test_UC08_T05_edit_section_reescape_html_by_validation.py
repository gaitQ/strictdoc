from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.constants import RST_STRING_THAT_NEEDS_HTML_ESCAPING
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC08_T05_EditSectionReescapeHTMLByValidation(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen()
            screen_document.assert_header_document_title("Document 1")

            screen_document.assert_text("Hello world!")

            form_edit_section: Form_EditSection = (
                screen_document.do_open_form_edit_section()
            )
            form_edit_section.do_fill_in_text(
                RST_STRING_THAT_NEEDS_HTML_ESCAPING
            )
            form_edit_section.do_form_submit_and_catch_error(
                "RST markup syntax error on line 2: "
                "Bullet list ends without a blank line; unexpected unindent."
            )
            form_edit_section.assert_contenteditable_contains(
                RST_STRING_THAT_NEEDS_HTML_ESCAPING
            )

        assert test_setup.compare_sandbox_and_expected_output()
