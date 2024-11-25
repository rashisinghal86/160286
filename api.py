from flask_restful import Resource, Api, reqparse
from app import app
from models import Category, db

api = Api(app)

class ResourceCategory(Resource):
    def get(self):
        categories = Category.query.all()
        return {
            'categories': [
                {'id': category.id, 'name': category.name}
                for category in categories
            ]
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Category name cannot be blank.")
        args = parser.parse_args()

        # Check if the category already exists
        if Category.query.filter_by(name=args['name']).first():
            return {'message': 'Category already exists'}, 400

        # Create a new category
        new_category = Category(name=args['name'])
        db.session.add(new_category)
        db.session.commit()

        return {
            'message': 'Category added successfully',
            'category': {'id': new_category.id, 'name': new_category.name}
        }, 201

    def put(self, id):
        """Edit a category."""
        category = Category.query.get(id)
        if not category:
            return {'message': 'Category not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Category name cannot be blank.")
        args = parser.parse_args()

        category.name = args['name']
        db.session.commit()

        return {
            'message': 'Category updated successfully',
            'category': {'id': category.id, 'name': category.name}
        }, 200

    def delete(self, id):
        """Delete a category."""
        category = Category.query.get(id)
        if not category:
            return {'message': 'Category not found'}, 404

        db.session.delete(category)
        db.session.commit()

        return {'message': 'Category deleted successfully'}, 200
# Add resource to API
api.add_resource(ResourceCategory, '/api/category', '/api/category/<int:id>')



