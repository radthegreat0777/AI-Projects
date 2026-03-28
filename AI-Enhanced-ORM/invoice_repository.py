from sqlalchemy.ext.asyncio import AsyncSession

from db_models import Invoice
from resp_models import InvoiceCreate


class InvoiceRepository:

    def __init__(self, db: AsyncSession):

        self.db = db

    async def create(self, invoice_create: InvoiceCreate) -> Invoice:
        invoice = Invoice(
            user_id=invoice_create.user_id,
            amount=invoice_create.amount,
            description=invoice_create.description
        )
        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice