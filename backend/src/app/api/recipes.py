from fastapi import APIRouter

router = APIRouter(tags=["recipes"])


@router.get("")
def list_recipes():
    return []
