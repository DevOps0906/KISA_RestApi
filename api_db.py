from flask import Flask
from flask_restful import Resource, Api, abort, reqparse
import sqlite3
import json

app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('task', type=str, help='Task to do')


class Todo(Resource):
    select_with_todo_id_sql = 'SELECT * FROM todo WHERE todo_id=?'
    update_sql = 'UPDATE todo SET task = ? WHERE todo_id = ?'
    delete_sql = 'DELETE FROM todo WHERE todo_id = ?'

    def get_todo_with_todo_id(self, todo_id):
        with sqlite3.connect('./db/todo.db') as conn:
            cur = conn.cursor()
            cur.execute(Todo.select_with_todo_id_sql, (todo_id,))

            row = cur.fetchone()
            if not row:
                abort(404, message='ToDo {} doesn\'t exists'.format(todo_id))

            return row

    def get(self, todo_id):
        todo = self.get_todo_with_todo_id(todo_id)

        return {todo_id: todo[2]}

    def put(self, todo_id):
        args = parser.parse_args(strict=True)
        task = {'task': args['task']}

        todo = self.get_todo_with_todo_id(todo_id)

        with sqlite3.connect('./db/todo.db') as conn:
            cur = conn.cursor()
            cur.execute(Todo.update_sql, (args['task'], todo[1]))
            conn.commit()

        return {todo[1]: task}, 201

    def delete(self, todo_id):
        todo = self.get_todo_with_todo_id(todo_id)

        with sqlite3.connect('./db/todo.db') as conn:
            cur = conn.cursor()
            cur.execute(Todo.delete_sql, (todo[1],))
            conn.commit()

        return '', 204


class TodoList(Resource):
    select_sql = 'SELECT * FROM todo'
    select_last_sql = 'SELECT * FROM todo ORDER BY id DESC LIMIT 1'
    insert_sql = 'INSERT INTO todo (todo_id, task) VALUES (?, ?)'

    def get(self):
        with sqlite3.connect('./db/todo.db') as conn:
            cur = conn.cursor()
            cur.execute(TodoList.select_sql)

            rows = cur.fetchall()

            todos = {x[1]: {'task': x[2]} for x in rows}

            return todos, 200

    def post(self):
        args = parser.parse_args(strict=True)

        with sqlite3.connect('./db/todo.db') as conn:
            cur = conn.cursor()
            cur.execute(TodoList.select_last_sql)

            rows = cur.fetchall()
            if not rows:
                todo_id = 0
            else:
                todo_id = int(rows[0][1].lstrip('todo')) + 1

            todo_id = 'todo{}'.format(todo_id)
            cur.execute(TodoList.insert_sql, (todo_id, args['task']))
            conn.commit()

        return {'todo_id': todo_id, 'task': args['task']}, 201


api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')


if __name__ == '__main__':
    app.run(debug=True)

