from flask import Flask
from flask_restful import Resource, Api, abort, reqparse

app = Flask(__name__)
api = Api(app)

todos = {}


parser = reqparse.RequestParser()
parser.add_argument('task', type=str, help='Task to do')


def handle_no_todo(todo_id):
    if todo_id not in todos:
        abort(404, message='ToDo {} doesn\'t exists'.format(todo_id))


class Todo(Resource):
    def get(self, todo_id):
        handle_no_todo(todo_id)
        return {todo_id: todos[todo_id]}

    def put(self, todo_id):
        args = parser.parse_args(strict=True)
        task = {'task': args['task']}
        todos[todo_id] = task

        return task, 201

    def delete(self, todo_id):
        handle_no_todo(todo_id)
        del todos[todo_id]
        return '', 204


class TodoList(Resource):
    def get(self):
        return todos, 200

    def post(self):
        args = parser.parse_args(strict=True)

        if todos:
            todo_id = int(max(todos.keys()).lstrip('todo')) + 1
        else:
            todo_id = 0

        todo_id = 'todo{}'.format(todo_id)

        todos[todo_id] = {'task': args['task']}
        return todos[todo_id], 201


api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')


if __name__ == '__main__':
    app.run(debug=True)

