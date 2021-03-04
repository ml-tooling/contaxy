from fastapi import APIRouter, Depends

from ..dependencies import get_authenticated_user
from ..models.users import User, UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me")
def hello(user: User = Depends(get_authenticated_user)) -> UserOut:
    return UserOut(**user.dict())
