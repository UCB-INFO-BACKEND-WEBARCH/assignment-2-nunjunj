
from marshmallow import fields,validate, Schema


class TaskCreateSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))
    due_date = fields.DateTime(required=False,allow_none=True)
    category_id = fields.Integer(required=False, allow_none=True)

class TaskUpdateSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))
    completed = fields.Boolean(required=False)
    due_date = fields.DateTime(required=False, allow_none=True)
    category_id = fields.Integer(required=False, allow_none=True)

class CategoryCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    color = fields.String(required=False, allow_none=True, validate=validate.Regexp(r"^#[0-9A-Fa-f]{6}$"))