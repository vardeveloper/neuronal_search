from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models import Customer
from schemas import CustomerCreate, CustomerUpdate


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_by_code(self, db: Session, *, code: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.code == code).first()

    def create(self, db: Session, *, obj_in: CustomerCreate) -> Customer:
        db_obj = Customer(
            name=obj_in.name,
            code=obj_in.code,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Customer, obj_in: Union[CustomerUpdate, Dict[str, Any]]
    ) -> Customer:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def is_active(self, customer: Customer) -> bool:
        return customer.is_active


customer = CRUDCustomer(Customer)
