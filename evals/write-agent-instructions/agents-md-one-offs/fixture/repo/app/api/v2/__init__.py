from fastapi import APIRouter

router = APIRouter(prefix="/v2")


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int) -> dict:
    return {"id": invoice_id, "lines": []}
