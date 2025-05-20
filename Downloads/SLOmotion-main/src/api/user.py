from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)


class Customer(BaseModel):
    customer_name: str


class UserCreateResponse(BaseModel):
    user_id: int


@router.post("/", response_model=UserCreateResponse)
def create_user(new_cart: Customer):
    # probably just insert into users and return an id
    # maybe also insert into watchlist? to create a user's watchlist and just default set status to public

    try:
        with db.engine.begin() as connection:  # creates a new user
            result = connection.execute(
                sqlalchemy.text(
                    """
                        INSERT INTO users (name)
                        VALUES (:customer_name)
                        RETURNING id
                    """
                ),
                {"customer_name": new_cart.customer_name},
            )
            user_id = result.scalar_one()

            if user_id is None:
                raise HTTPException(status_code=500, detail="Failed to create user")

            # creates a new watchlist for the user
            connection.execute(
                sqlalchemy.text(
                    """
                        INSERT INTO watchlists (user_id, public)
                        VALUES (:user_id, :public)
                    """
                ),
                {"user_id": user_id, "public": True},
            )

            return UserCreateResponse(user_id=int(user_id))

    except sqlalchemy.exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
