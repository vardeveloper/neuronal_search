from typing import Any, List

from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from api import deps

def endpoints(app):
    @app.get("/customer", response_model=List[schemas.Customer], tags=["customers"])
    def read_customers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),
    ) -> Any:
        """
        Retrieve customers.
        """
        customers = crud.customer.get_multi(db, skip=skip, limit=limit)
        return customers

    @app.post("/customer", response_model=schemas.Customer, tags=["customers"])
    def create_customer(
        *,
        db: Session = Depends(deps.get_db),
        customer_in: schemas.CustomerBase,
        current_user: models.User = Depends(deps.get_current_active_superuser),
    ) -> Any:
        """
        Create new customer.
        """
        customer = crud.customer.get_by_code(db, code=customer_in.code)
        if customer:
            raise HTTPException(
                status_code=400,
                detail="The customer with this code already exists in the system.",
            )
        customer = crud.customer.create(db, obj_in=customer_in)
        return customer

    @app.get("/customer/{customer_id}", response_model=schemas.Customer, tags=["customers"])
    def read_customer_by_id(
        customer_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db),
    ) -> Any:
        """
        Get a specific customer by id.
        """
        customer = crud.customer.get(db, id=customer_id)
        if not crud.user.is_superuser(current_user):
            raise HTTPException(
                status_code=400, detail="The user doesn't have enough privileges"
            )
        return customer

    return app
