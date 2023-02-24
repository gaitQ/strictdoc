import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC07_T20_AddComment(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "document.sdoc"),
            os.path.join(path_to_sandbox, "document.sdoc"),
        )

        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("Document 1")
        self.assert_text("PROJECT INDEX")

        self.click_link("DOC")

        self.assert_text("Hello world!")

        self.hover_and_click(
            hover_selector="(//sdoc-node)[2]",
            click_selector=(
                '(//sdoc-node)[2]//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

        # There should be no open comment fields, only an add comment button.
        self.assert_element_not_present("(//*[@id='requirement[COMMENT]'])")

        self.click_xpath('//*[@data-testid="form-add-comment-field-action"]')
        self.type(
            "(//*[@id='requirement[COMMENT]'])", "Comment #1", by=By.XPATH
        )

        self.click_xpath('//*[@data-testid="form-add-comment-field-action"]')
        self.type(
            "(//*[@id='requirement[COMMENT]'])[2]", "Comment #2", by=By.XPATH
        )

        self.click_xpath('//*[@data-testid="form-add-comment-field-action"]')
        self.type(
            "(//*[@id='requirement[COMMENT]'])[3]", "Comment #3", by=By.XPATH
        )

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        self.assert_text("Comment #1")
        self.assert_text("Comment #2")
        self.assert_text("Comment #3")

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
