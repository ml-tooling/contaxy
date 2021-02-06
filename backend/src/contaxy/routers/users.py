from fastapi import APIRouter, Depends

from contaxy.dependencies import get_authenticated_user
from contaxy.user import User, UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me")
def hello(user: User = Depends(get_authenticated_user)) -> UserOut:
    return UserOut(**user.dict())
