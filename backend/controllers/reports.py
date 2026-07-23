from fastapi import APIRouter
from fastapi.responses import Response
from backend.services.report_service import ReportService
from backend.shared.response import APIResponse

router = APIRouter()

@router.get("/{candidate_id}", response_model=APIResponse)
async def get_report(candidate_id: str):
    service = ReportService()
    report = await service.generate_json_report(candidate_id)
    return APIResponse(success=True, data=report)

@router.get("/{candidate_id}/pdf")
async def download_pdf_report(candidate_id: str):
    service = ReportService()
    pdf_bytes = await service.generate_pdf_report(candidate_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{candidate_id}.pdf"}
    )
