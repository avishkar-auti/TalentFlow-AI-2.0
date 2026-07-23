from typing import Any, Dict
from pydantic import BaseModel
from .base import BaseTool, ToolResult

class PDFGenerateInput(BaseModel):
    template_name: str
    data: Dict[str, Any]

class PDFGenerateOutput(BaseModel):
    pdf_bytes: str # base64
    filename: str

class PDFGenerateTool(BaseTool):
    name = "pdf_generate"
    description = "Generate PDF from Jinja2 HTML template + data"
    input_schema = PDFGenerateInput
    output_schema = PDFGenerateOutput

    async def execute(self, input_data: PDFGenerateInput) -> ToolResult:
        return ToolResult(success=True, data={
            "pdf_bytes": "mock_base64_pdf_data",
            "filename": f"{input_data.template_name}.pdf"
        })
