from pydantic import BaseModel
from typing import List, Optional, Any, Union
from enum import Enum
import uuid


class FieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DATE = "date"

class RuleConditionOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "notEquals"
    GREATER_THAN = "greaterThan"
    LESS_THAN = "lessThan"
    CONTAINS = "contains"

class RuleActionType(str, Enum):
    SHOW = "show"
    HIDE = "hide"
    ENABLE = "enable"
    DISABLE = "disable"
    SET_REQUIRED = "setRequired"


class FieldOption(BaseModel):
    label: str
    value: Any


class RuleConditionGroup(BaseModel):
    pass

class RuleCondition(BaseModel):
    fieldId: str
    operator: RuleConditionOperator
    value: Any

RuleConditionGroup.model_rebuild(force=True)
RuleConditionGroup.model_fields.update({
    'operator': str, # 'and' or 'or'
    'conditions': List[Union[RuleCondition, RuleConditionGroup]]
})


class RuleAction(BaseModel):
    targetFieldId: str
    type: RuleActionType
    value: Optional[Any] = None

class FormRule(BaseModel):
    id: str
    description: Optional[str] = None
    conditions: List[Union[RuleCondition, RuleConditionGroup]]
    actions: List[RuleAction]

class FormField(BaseModel):
    id: str
    type: FieldType
    label: str
    placeholder: Optional[str] = None
    options: Optional[List[FieldOption]] = []
    validations: Optional[List[Any]] = []
    rules: Optional[List[FormRule]] = []

class FormSchema(BaseModel):
    id: str = str(uuid.uuid4())
    name: str
    description: Optional[str] = None
    fields: List[FormField]
    rules: Optional[List[FormRule]] = []

class FormSchemaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    fields: List[FormField]
    rules: Optional[List[FormRule]] = None
