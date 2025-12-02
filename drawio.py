import random
import time



DEFAULT_DRAWIO_XML = """
<mxfile host="app.diagrams.net" version="29.2.1">
  <diagram name="JavaToCodeScheme" id="jtcsid">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="500" pageHeight="500" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
{0}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

OPERATION_XML = """
        <mxCell id="{0}" parent="{1}" value="{2}" vertex="1">
          {3}
        </mxCell>\n"""
PROCEDURE_XML = """
        <mxCell id="{0}" parent="{1}" style="ellipse;" value="{2}" vertex="1">
          {3}
        </mxCell>\n"""
FOR_XML = """
        <mxCell id="{0}" parent="{1}" style="hexagon" value="{2}" vertex="1">
          {3}
        </mxCell>\n"""
IF_XML = """
        <mxCell id="{0}" parent="{1}" style="rhombus" value="{2}" vertex="1">
          {3}
        </mxCell>\n"""
IO_XML = """
        <mxCell id="{0}" parent="{1}" style="shape=parallelogram;perimeter=parallelogramPerimeter" value="{2}" vertex="1">
          {3}
        </mxCell>\n"""
CALL_XML = """
        <mxCell id="{0}" parent="{1}" style="shape=process" value="{2}" vertex="1">
          {3}
        </mxCell>\n"""

ARROW_XML = """
        <mxCell id="{0}" parent="{1}" edge="1" style="edgeStyle=orthogonalEdgeStyle;" source="{2}" target="{3}" >
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
ARROW_TXT_XML = """
        <mxCell id="{0}" parent="{1}" style="edgeLabel;resizable=0;" value="{2}" vertex="1" connectable="0">
          <mxGeometry relative="1" x="0" y="0" as="geometry">
            <mxPoint x="0" y="0" as="offset" />
          </mxGeometry>
        </mxCell>
"""

POS_XML = """<mxGeometry height="80" width="160" x="{0}" y="{1}" as="geometry" />"""

class DrawIO:
    def __init__(self, name: str = "myScheme.png"):
        self.name = name
        self.scheme = ""
        self.block_list = []
        self.arrow_list = []

    def __iter__(self) -> str:
        return self.compile_scheme()

    def compile_scheme(self) -> str:
        return DEFAULT_DRAWIO_XML.format(self.scheme)

    def add_operation(self, text: str, x: int, y: int) -> str:
        return self.add_text_block(OPERATION_XML,  text, x, y)

    def add_procedure(self, text: str, x: int, y: int) -> str:
        return self.add_text_block(PROCEDURE_XML,  text, x, y)

    def add_for(self, text: str, x: int, y: int) -> str:
        return self.add_text_block(FOR_XML,  text, x, y)

    def add_if(self, text: str, x: int, y: int) -> str:
        return self.add_text_block(IF_XML,  text, x, y)

    def add_io(self, text: str, x: int, y: int) -> str:
        return self.add_text_block(IO_XML,  text, x, y)

    def add_call(self, text: str, x: int, y: int) -> str:
        return self.add_text_block(CALL_XML,  text, x, y)

    def add_text_block(self, text_block: str, text: str, x: int, y: int) -> str:
        text = self.xml_str(text)
        block_id = self.generate_id()
        self.scheme += text_block.format(block_id, "1", text, POS_XML.format(x, y))
        self.block_list.append(block_id)
        return block_id

    def add_arrow(self, source: str, target: str) -> str:
        if source != "" and target != "":
            arrow_id = self.generate_id()
            self.scheme += ARROW_XML.format(arrow_id, "1", source, target)
            self.arrow_list.append(arrow_id)
            return arrow_id
        else:
            return ""

    def add_arrow_txt(self, arrow: str, text: str) -> str:
        if arrow != "":
            text = self.xml_str(text)
            text_id = self.generate_id()
            self.scheme += ARROW_TXT_XML.format(text_id, arrow, text)
            self.arrow_list.append(text_id)
            return text_id
        else:
            return ""

    def reset(self) -> None:
        self.scheme = ""

    @staticmethod
    def generate_id() -> str:
        return f"{int(time.time() * 1000)}{random.randint(10 ** 6, 10 ** 7)}"

    @staticmethod
    def xml_str(input_str: str) -> str:
        input_str = input_str.replace("'", "&quot;")
        input_str = input_str.replace('"', "&quot;")
        return input_str

    def save_xml(self, path) -> None:
        with open(path, "w", encoding="UTF-8") as file:
            file.write(self.compile_scheme())