from fastapi import APIRouter

router = APIRouter(tags=["inventory"])


@router.get("")
def list_inventory():
    return []
