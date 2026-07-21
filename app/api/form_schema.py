from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional, Any, Union, Literal
from enum import Enum


class FieldType(str, Enum):
    """Canonical field types — kept in sync with the frontend `FieldType` enum
    (libs/models/src/field.model.ts). Naming is camelCase, matching the frontend."""
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multiSelect"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    TOGGLE_SWITCH = "toggleSwitch"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    TEXT_AREA = "textArea"
    FILE_UPLOAD = "fileUpload"
    RICH_TEXT = "richText"
    COLOR_PICKER = "colorPicker"
    LIKERT_SCALE = "likertScale"
    URL = "url"
    PASSWORD = "password"


# Legacy field-type spellings persisted by earlier versions of the API.
# Keys are lowercased with separators stripped, so both "textarea" and
# "TEXT_AREA" normalize to the canonical "textArea".
_LEGACY_FIELD_TYPES = {
    "tel": FieldType.PHONE.value,
    "textarea": FieldType.TEXT_AREA.value,
    "multiselect": FieldType.MULTI_SELECT.value,
    "toggleswitch": FieldType.TOGGLE_SWITCH.value,
    "fileupload": FieldType.FILE_UPLOAD.value,
    "richtext": FieldType.RICH_TEXT.value,
    "colorpicker": FieldType.COLOR_PICKER.value,
    "likertscale": FieldType.LIKERT_SCALE.value,
}


def normalize_field_type(value: Any) -> Any:
    """Map legacy/loosely-cased field types onto canonical ones.

    Unknown values pass through untouched so enum validation still reports them.
    """
    if not isinstance(value, str):
        return value
    key = value.lower().replace("_", "").replace("-", "")
    return _LEGACY_FIELD_TYPES.get(key, value)


class ColorFormat(str, Enum):
    HEX = "hex"
    RGB = "rgb"
    RGBA = "rgba"
    HSL = "hsl"
    HSLA = "hsla"


class RuleConditionOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "notEquals"
    GREATER_THAN = "greaterThan"
    GREATER_THAN_OR_EQUAL = "greaterThanOrEqual"
    LESS_THAN = "lessThan"
    LESS_THAN_OR_EQUAL = "lessThanOrEqual"
    BETWEEN = "between"
    CONTAINS = "contains"
    NOT_CONTAINS = "notContains"
    STARTS_WITH = "startsWith"
    ENDS_WITH = "endsWith"
    REGEX = "regex"
    IS_EMPTY = "isEmpty"
    IS_NOT_EMPTY = "isNotEmpty"
    IN = "in"
    NOT_IN = "notIn"


class RuleActionType(str, Enum):
    SHOW = "show"
    HIDE = "hide"
    ENABLE = "enable"
    DISABLE = "disable"
    SET_REQUIRED = "setRequired"
    SET_VALUE = "setValue"
    CLEAR_VALUE = "clearValue"


class FieldOption(BaseModel):
    label: str
    value: Any


class RuleCondition(BaseModel):
    fieldId: str
    operator: RuleConditionOperator
    value: Any


class RuleConditionGroup(BaseModel):
    operator: Literal["and", "or"]
    conditions: List[Union[RuleCondition, RuleConditionGroup]]


class RuleAction(BaseModel):
    targetFieldId: str
    type: RuleActionType
    value: Optional[Any] = None


class FormRule(BaseModel):
    id: str
    description: Optional[str] = None
    conditionLogic: Optional[Literal["and", "or"]] = "and"
    conditions: List[Union[RuleCondition, RuleConditionGroup]]
    actions: List[RuleAction]


class ThemeSettings(BaseModel):
    primaryColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    textColor: Optional[str] = None
    fontFamily: Optional[str] = None
    borderRadius: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class FormField(BaseModel):
    id: str
    type: FieldType
    label: str
    placeholder: Optional[str] = None
    required: Optional[bool] = False
    options: Optional[List[FieldOption]] = []
    validations: Optional[List[Any]] = []
    rules: Optional[List[FormRule]] = []
    theme: Optional[ThemeSettings] = None

    # Number field
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None

    # Color picker field
    colorFormat: Optional[ColorFormat] = None

    # Phone field
    defaultCountry: Optional[str] = None
    showCountrySelector: Optional[bool] = None

    @field_validator("type", mode="before")
    @classmethod
    def _normalize_type(cls, value: Any) -> Any:
        return normalize_field_type(value)


class FormSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    submitMessage: Optional[str] = None
    fields: List[FormField]
    rules: Optional[List[FormRule]] = []
    theme: Optional[ThemeSettings] = None

    model_config = ConfigDict(from_attributes=True)


class FormSchemaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    submitMessage: Optional[str] = None
    fields: List[FormField]
    rules: Optional[List[FormRule]] = None
    theme: Optional[ThemeSettings] = None

    model_config = ConfigDict(from_attributes=True)


class FormSchemaResponse(FormSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)
