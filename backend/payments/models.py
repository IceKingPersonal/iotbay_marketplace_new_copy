from dataclasses import dataclass


@dataclass
class Payment:
    payment_id: int
    order_id: int
    payment_method_id: int
    customer_id: int
    amount: float
    payment_date: str

    @staticmethod
    def validate_order_status(status: str) -> bool:
        return status == "Saved"

    @staticmethod
    def validate_amount(amount) -> bool:
        return isinstance(amount, (int, float)) and amount > 0

    @classmethod
    def from_row(cls, row) -> "Payment":
        return cls(
            payment_id=row["payment_id"],
            order_id=row["order_id"],
            payment_method_id=row["payment_method_id"],
            customer_id=row["customer_id"],
            amount=row["amount"],
            payment_date=row["payment_date"],
        )
