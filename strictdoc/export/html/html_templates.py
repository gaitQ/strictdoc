import glob
import hashlib
import os.path
import shutil
import tempfile
from pathlib import Path
from typing import Any, List, Optional

from jinja2 import (
    Environment,
    FileSystemLoader,
    ModuleLoader,
    StrictUndefined,
    TemplateRuntimeError,
    nodes,
)
from jinja2.ext import Extension

from strictdoc import environment
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.timing import measure_performance


# https://stackoverflow.com/questions/21778252/how-to-raise-an-exception-in-a-jinja2-macro  # noqa: E501
class AssertExtension(Extension):
    # This is our keyword(s):
    tags = {"assert"}

    def __init__(self, environment):  # pylint: disable=redefined-outer-name
        super().__init__(environment)
        self.current_line = None
        self.current_file = None

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        self.current_line = lineno
        self.current_file = parser.filename

        condition_node = parser.parse_expression()
        if parser.stream.skip_if("comma"):
            context_node = parser.parse_expression()
        else:
            context_node = nodes.Const(None)

        return nodes.CallBlock(
            self.call_method(
                "_assert", [condition_node, context_node], lineno=lineno
            ),
            [],
            [],
            [],
            lineno=lineno,
        )

    def _assert(
        self, condition: bool, context_or_none: Optional[Any], caller
    ):  # pylint: disable=unused-argument
        if not condition:
            error_message = (
                f"Assertion error in the Jinja template: "
                f"{self.current_file}:{self.current_line}."
            )
            if context_or_none:
                error_message += f" Message: {context_or_none}"
            raise TemplateRuntimeError(error_message)
        return ""


class HTMLTemplates:
    PATH_TO_JINJA_CACHE_DIR = os.path.join(
        tempfile.gettempdir(), "strictdoc_cache", "jinja"
    )

    def __init__(self, project_config: ProjectConfig):
        path_to_output_dir_hash = hashlib.md5(
            project_config.export_output_dir.encode("utf-8")
        ).hexdigest()
        self.path_to_jinja_cache_bucket_dir = os.path.join(
            HTMLTemplates.PATH_TO_JINJA_CACHE_DIR, path_to_output_dir_hash
        )
        self._jinja_environment: Optional[Environment] = None

    def compile_jinja_templates(self):
        if os.path.isdir(self.path_to_jinja_cache_bucket_dir):
            return
        jinja_environment = Environment(
            loader=FileSystemLoader(environment.get_path_to_html_templates()),
            undefined=StrictUndefined,
            extensions=[AssertExtension],
        )
        # TODO: Check if this line is still needed (might be some older workaround).
        jinja_environment.globals.update(isinstance=isinstance)
        with measure_performance("Compile Jinja templates"):
            Path(self.path_to_jinja_cache_bucket_dir).mkdir(
                parents=True, exist_ok=True
            )
            jinja_environment.compile_templates(
                self.path_to_jinja_cache_bucket_dir,
                zip=None,
                ignore_errors=False,
            )

    def jinja_environment(self) -> Environment:
        if self._jinja_environment is not None:
            return self._jinja_environment
        assert os.path.isdir(self.path_to_jinja_cache_bucket_dir)
        self._jinja_environment = Environment(
            loader=ModuleLoader(self.path_to_jinja_cache_bucket_dir),
            undefined=StrictUndefined,
            extensions=[AssertExtension],
        )
        return self._jinja_environment

    def reset_jinja_environment_if_outdated(
        self, strictdoc_last_update
    ) -> None:
        if os.path.isdir(self.path_to_jinja_cache_bucket_dir):
            jinja_cache_files: List[str] = list(
                glob.iglob(
                    f"{self.path_to_jinja_cache_bucket_dir}/**/*.py",
                    recursive=True,
                )
            )
            if len(jinja_cache_files) == 0:
                shutil.rmtree(self.path_to_jinja_cache_bucket_dir)
                return

            jinja_cache_mtime = get_file_modification_time(jinja_cache_files[0])

            if strictdoc_last_update > jinja_cache_mtime:
                HTMLTemplates._jinja_environment = None
                shutil.rmtree(self.path_to_jinja_cache_bucket_dir)
