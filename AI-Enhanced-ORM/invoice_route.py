from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from database_config import get_db
from invoice_repository import InvoiceRepository
from resp_models import InvoiceCreate, InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
        invoice_data: InvoiceCreate,
        db: AsyncSession = Depends(get_db)
):
    repo = InvoiceRepository(db)

    try:
        invoice = await repo.create(invoice_data)
        return invoice
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An Error occurred - {str(e)}"
        )