import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Select


class Operator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    LIKE = "like"
    ILIKE = "ilike"
    BETWEEN = "between"
    IN = "in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"



class FilterCondition(BaseModel):
    column: str
    operator: Operator = Operator.EQ
    value: Any = None
    value2: Any = None  # second value for BETWEEN

def apply_filter(query: Select, model, condition: FilterCondition) -> Select:
    """Apply a single filter condition to a query."""
    col = getattr(model, condition.column, None)
    if col is None:
        raise ValueError(f"Unknown column '{condition.column}' on {model.__name__}")

    match condition.operator:
        case Operator.EQ:
            query = query.where(col == condition.value)
        case Operator.NEQ:
            query = query.where(col != condition.value)
        case Operator.GT:
            query = query.where(col > condition.value)
        case Operator.GTE:
            query = query.where(col >= condition.value)
        case Operator.LT:
            query = query.where(col < condition.value)
        case Operator.LTE:
            query = query.where(col <= condition.value)
        case Operator.LIKE:
            query = query.where(col.like(condition.value))
        case Operator.ILIKE:
            query = query.where(col.ilike(condition.value))
        case Operator.BETWEEN:
            if condition.value2 is None:
                raise ValueError("BETWEEN requires value and value2")
            query = query.where(col.between(condition.value, condition.value2))
        case Operator.IN:
            if not isinstance(condition.value, list):
                raise ValueError("IN requires value to be a list")
            query = query.where(col.in_(condition.value))
        case Operator.IS_NULL:
            query = query.where(col.is_(None))
        case Operator.IS_NOT_NULL:
            query = query.where(col.isnot(None))

    return query


def apply_filters(query: Select, model, conditions: list[FilterCondition]) -> Select:
    """Apply multiple filter conditions (AND)."""
    for condition in conditions:
        query = apply_filter(query, model, condition)
    return query