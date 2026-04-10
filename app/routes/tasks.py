from flask import request, jsonify 
from app.models import db, TaskModel, CategoryModel
from app.schemas import TaskCreateSchema, TaskUpdateSchema
from app.jobs import send_due_soon_reminder
from datetime import timezone, timedelta
import datetime
from redis import Redis
from rq import Queue
import os

def task_routes(app):
    
    @app.route('/tasks', methods=['GET'])
    def get_tasks():
        completed = request.args.get('completed')
        if completed == 'true':
            tasks = TaskModel.query.filter_by(completed=True).all()
        elif completed == 'false':
            tasks = TaskModel.query.filter_by(completed=False).all()
        else:
            tasks = TaskModel.query.all()
        
        
        return jsonify({"tasks": [task.to_full_dict() for task in tasks]}), 200
         
        
    @app.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        task = TaskModel.query.get(task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task.to_full_dict()), 200

    @app.route('/tasks', methods=['POST'])
    def create_task():
        data = request.get_json()
        
        try: 
            data_validated = TaskCreateSchema().load(data)
        except Exception as e:
            return jsonify({"errors": e.messages}), 400
            
        category_id = data_validated.get('category_id')
        if category_id is not None:
            category = CategoryModel.query.get(category_id)
            if category is None:
                return jsonify({"errors": {"category_id": ["Category not found."]}}), 400

        task = TaskModel()
        task.title = data_validated.get('title')
        task.description = data_validated.get('description')
        task.due_date = data_validated.get('due_date')
        task.category_id = data_validated.get('category_id')
        
        db.session.add(task)
        db.session.commit()
    

        if due_soon(task.due_date):
            redis_conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
            queue = Queue(connection=redis_conn)
            queue.enqueue(send_due_soon_reminder, task.title)
            q = True
            
        else:
            q = False
        
        return jsonify({
            "task": task.to_full_dict(),
            "notification_queued": q
        }), 201
    
    def due_soon(due_date):
        
        if due_date is None:
            return False
        
        now = datetime.datetime.now(timezone.utc)
        
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
            
        if now < due_date <= now + timedelta(hours=24):
            return True
        
        else:
            return False
        
    @app.route('/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        task = TaskModel.query.get(task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        
        data = request.get_json()
        try: 
            data_validated = TaskUpdateSchema().load(data)
        except Exception as e:
            return jsonify({"errors": e.messages}), 400
        if 'title' in data_validated:
            task.title = data_validated['title']
        if 'description' in data_validated:
            task.description = data_validated['description']
        if 'completed' in data_validated:
            task.completed = data_validated['completed']
        if 'due_date' in data_validated:
            task.due_date = data_validated['due_date']
        if 'category_id' in data_validated:
            task.category_id = data_validated['category_id']

        db.session.commit()
        return jsonify(task.to_full_dict()), 200

        
    @app.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        task = TaskModel.query.get(task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted"}), 200