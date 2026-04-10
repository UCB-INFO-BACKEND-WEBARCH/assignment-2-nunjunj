from flask import request, jsonify 
from app.models import db, CategoryModel
from app.schemas import CategoryCreateSchema
 
 
def category_routes(app):
 
    @app.route('/categories', methods=['GET'])
    def get_categories():
        ret = []
        for c in CategoryModel.query.all():
            item = c.to_dict()
            item['task_count'] = len(c.tasks)
            ret.append(item)
        return jsonify({"categories": ret}), 200
        
    @app.route('/categories/<int:cat_id>', methods=['GET'])
    def get_category(cat_id):
        cat = db.get_or_404(CategoryModel, cat_id)
        ret =  cat.to_dict()
        ret['tasks'] = [task.to_dict() for task in cat.tasks]
        return jsonify(ret), 200

    @app.route('/categories', methods=['POST'])
    def create_category():
        data = request.get_json()
        
        try: 
            data_validated = CategoryCreateSchema().load(data)
        except Exception as e:
            return jsonify({"errors": e.messages}), 400
        
        if CategoryModel.query.filter_by(name=data_validated['name']).first() is not None:
            return jsonify({"error": {
        "name": ["Category with this name already exists."]
    }}), 400
            
        else: 
            cat = CategoryModel()
            cat.name = data_validated.get('name')
            cat.color = data_validated.get('color')
            db.session.add(cat)
            db.session.commit()
            return jsonify(cat.to_dict()), 201
        
    @app.route('/categories/<int:cat_id>', methods=['DELETE'])
    def delete_category(cat_id):
        cat = db.get_or_404(CategoryModel, cat_id)
        
        if len(cat.tasks) > 0:
            return jsonify({"error": "Cannot delete category with existing tasks. Move or delete tasks first."
                            }), 400
            
        db.session.delete(cat)
        db.session.commit()
        return jsonify({"message": "Category deleted"}), 200
