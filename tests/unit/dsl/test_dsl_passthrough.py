from strictdoc.backend.dsl.models import Document, Requirement
from strictdoc.backend.dsl.reader import SDReader
from strictdoc.backend.dsl.writer import SDWriter


def test_100_basic_test():
    input = """
[DOCUMENT]
NAME: Test Doc

[SECTION]
LEVEL: 0
TITLE: Test Section

[REQUIREMENT]
TAGS: Tag 1, Tag 2, Tag 3
REFS:
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
STATEMENT: System shall do X
BODY: >>>
This is an optional body of the requirement.
This is an optional body of the requirement.
<<<
COMMENT: This requirement is very important

[REQUIREMENT]
UID: REQ-001
STATUS: Draft
TITLE: Optional title B
STATEMENT: System shall do Y
COMMENT: This requirement is very important

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    assert isinstance(document.section_contents[0].section_contents[0], Requirement)
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.tags[0] == 'Tag 1'
    assert requirement_1.tags[1] == 'Tag 2'
    assert requirement_1.tags[2] == 'Tag 3'

    writer = SDWriter()
    output = writer.write(document)

    print(output)
    assert input == output
