from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from database_config import get_db
from db_agent import query_db_with_natural_language, propose_dml_statement_for_human_approval, approve_and_execute
from resp_models import AgentQueryRequest, AgentQueryResponse, DMLApprovalResponse, DMLProposalRequest, DMLProposalResponse, DMLApprovalRequest

router = APIRouter(prefix="/agent", tags=["Database Agent Routes"])



#Study about - MCP Servers (Model Context protocol)

@router.post("/query", response_model=AgentQueryResponse)
def query_database(request: AgentQueryRequest) -> AgentQueryResponse:

    try:
        thread_id = request.thread_id
        result = query_db_with_natural_language(user_input=request.query, thread_id=thread_id)
        return AgentQueryResponse(query=request.query, result=result, thread_id=thread_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/dml/propose", response_model=DMLProposalResponse)
async def propose_dml_statement(
        request: DMLProposalRequest,
        session: AsyncSession = Depends(get_db)
):
    try:
        proposed_dml = await propose_dml_statement_for_human_approval(request.query
                                                                      , session=session)
        return DMLProposalResponse(
            approval_id=proposed_dml["approval_id"],
            sql=proposed_dml["sql"],
            status="pending"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.post("dml/approve", response_model=DMLApprovalResponse)
async def approve_dml(request: DMLApprovalRequest, session:AsyncSession = Depends(get_db)):
    try:
        result = await approve_and_execute(approval_id=request.approval_id,
                                           approve=request.approve,
                                           session=session)
        approve_status = "approved" if request.approve else "rejected"

        return DMLApprovalResponse(
            approval_id=request.approval_id,
            status=approve_status,
            result=result
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



