from flask_restful import Resource, Api, reqparse
from app import app
from models import Category, db, Service

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

##############################################################
class ResourceService(Resource):
    def get(self, id=None):
        if id:
            # Fetch specific service
            service = Service.query.get(id)
            if not service:
                return {'message': 'Service not found'}, 404
            return {
                'id': service.id,
                'name': service.name,
                'type': service.type,
                'description': service.description,
                'price': service.price,
                'location': service.location,
                'duration': service.duration,
                'category': {
                    'id': service.category.id,
                    'name': service.category.name
                }
            }
        # Fetch all services
        services = Service.query.all()
        return {
            'services': [
                {
                    'id': service.id,
                    'name': service.name,
                    'type': service.type,
                    'description': service.description,
                    'price': service.price,
                    'location': service.location,
                    'duration': service.duration,
                    'category': {
                        'id': service.category.id,
                        'name': service.category.name
                    }
                }
                for service in services
            ]
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank.")
        parser.add_argument('category_id', type=int, required=True, help="Category ID cannot be blank.")
        parser.add_argument('type', type=str, required=True, help="Type cannot be blank.")
        parser.add_argument('description', type=str, required=True, help="Description cannot be blank.")
        parser.add_argument('price', type=float, required=True, help="Price must be a number.")
        parser.add_argument('location', type=str, required=True, help="Location cannot be blank.")
        parser.add_argument('duration', type=str, required=True, help="Duration cannot be blank.")
        args = parser.parse_args()

        category = Category.query.get(args['category_id'])
        if not category:
            return {'message': 'Category does not exist'}, 400

        if args['price'] <= 0:
            return {'message': 'Price must be positive'}, 400

        new_service = Service(
            name=args['name'],
            category=category,
            type=args['type'],
            description=args['description'],
            price=args['price'],
            location=args['location'],
            duration=args['duration']
        )
        db.session.add(new_service)
        db.session.commit()

        return {'message': 'Service added successfully', 'service': {
            'id': new_service.id,
            'name': new_service.name,
            'type': new_service.type,
            'description': new_service.description,
            'price': new_service.price,
            'location': new_service.location,
            'duration': new_service.duration,
            'category': {
                'id': category.id,
                'name': category.name
            }
        }}, 201

    def put(self, id):
        service = Service.query.get(id)
        if not service:
            return {'message': 'Service not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank.")
        parser.add_argument('category_id', type=int, required=True, help="Category ID cannot be blank.")
        parser.add_argument('type', type=str, required=True, help="Type cannot be blank.")
        parser.add_argument('description', type=str, required=True, help="Description cannot be blank.")
        parser.add_argument('price', type=float, required=True, help="Price must be a number.")
        parser.add_argument('location', type=str, required=True, help="Location cannot be blank.")
        parser.add_argument('duration', type=str, required=True, help="Duration cannot be blank.")
        args = parser.parse_args()

        category = Category.query.get(args['category_id'])
        if not category:
            return {'message': 'Category does not exist'}, 400

        if args['price'] <= 0:
            return {'message': 'Price must be positive'}, 400

        service.name = args['name']
        service.category = category
        service.type = args['type']
        service.description = args['description']
        service.price = args['price']
        service.location = args['location']
        service.duration = args['duration']
        db.session.commit()

        return {'message': 'Service updated successfully', 'service': {
            'id': service.id,
            'name': service.name,
            'type': service.type,
            'description': service.description,
            'price': service.price,
            'location': service.location,
            'duration': service.duration,
            'category': {
                'id': category.id,
                'name': category.name
            }
        }}, 200

    def delete(self, id):
        service = Service.query.get(id)
        if not service:
            return {'message': 'Service not found'}, 404

        db.session.delete(service)
        db.session.commit()

        return {'message': 'Service deleted successfully'}, 200

# Add resource to API
api.add_resource(ResourceService, '/api/service', '/api/service/<int:id>')
##############################################################

