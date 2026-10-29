from fastapi import APIRouter

router = APIRouter(prefix="/v1")


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int):
    return {"id": invoice_id}
