from fastapi import APIRouter, status

from schemas.health import HealthResponse

router = APIRouter()


@router.get(
    path='/health',
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse
)
async def health():
    return HealthResponse(status="ok")
