from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.execute import ExecuteRequest, ExecuteResponse
from app.services.judge0_executor import judge0_executor

router = APIRouter()


@router.post("", response_model=ExecuteResponse)
async def execute_code(
    payload: ExecuteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> ExecuteResponse:
    return await judge0_executor.execute(payload)
