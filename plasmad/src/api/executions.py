#!/usr/bin/env python3

import werkzeug
# Werkzeug 1.0.0 breaks flask_restplus, need to keep this line in
# till flask restplus patches this
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Namespace, Resource, fields, reqparse, marshal
from xxhash import xxh64_hexdigest
from src.utils.api_utils import *
from src.utils.decorators import *
from src.utils.db_utils import get_plasma_db
from os import path


api = Namespace('execution', description='routes for execution management')


execution_pass = api.model('ExecutionPass', {
    'workflow-id': fields.String(required=True, description='Execution passes'),
    'execution-id': fields.String(required=True, description='Execution passes'),
    'status': fields.Integer(required=True, description='State of execution'),
    'started-at': fields.String(required=True, description='Execution start timestamp'),
    'finished-at': fields.String(required=True, description='Execution end timestamp'),
    'time-taken': fields.String(required=True, description='Time taken by execution pass'),
    #'progress': fields.Wildcard(required=True,secription='Progress of exeuction pass')
})


@api.route('')
class ExecutionList(Resource):
    @api.doc('List all executions')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('workflow-id', type=str, location='args')
        args = parser.parse_args()
        if args['workflow-id']:
            query = {'workflow-id': args['workflow-id']}
        else:
            query = {}
        print(query)
        db = get_plasma_db()
        execution_collection = db.get_collection('executions')
        executions = []
        for item in execution_collection.find(query):
            executions.append(marshal(item, execution_pass))
        response = generate_response(200, executions)
        return response


@api.route('/<execution_id>')
@api.param('execution_id', 'Workflow ID')
class Execution(Resource):
    @api.doc('Get a execution')
    def get(self, execution_id):
        db = get_plasma_db()
        execution_collection = db.get_collection('executions')
        result = execution_collection.find_one({'execution-id': execution_id})
        if result:
            response_data = marshal(result, execution_pass)
            response = generate_response(200, response_data)
        else:
            response = generate_response(404)
        return response

    @api.doc('Update an existing execution')
    def put(self, execution_id):
        parser = reqparse.RequestParser()
        parser.add_argument('update', type=dict, required=True,
                            help='values which need to be updated')
        args = parser.parse_args()
        db = get_plasma_db()
        execution_collection = db.get_collection('executions')
        updated_resource = execution_collection.find_one_and_update(
            {"execution-id": execution_id},
            {"$set": dict(args)['update']}
        )
        if updated_resource:
            response = generate_response(204)
        else:
            response = generate_response(404)
        return response

    @api.doc('Delete a execution')
    def delete(self, execution_id):
        db = get_plasma_db()
        execution_collection = db.get_collection('executions')
        deleted_execution = execution_collection.delete_one(
            {"execution-id": execution_id})
        if deleted_execution.deleted_count == 1:
            response = generate_response(200)
        else:
            response = generate_response(404)
        return response


@api.route('/<execution_id>/logs')
@api.param('execution_id', 'Execution ID')
class ExecutionLogs(Resource):
    @api.doc('Get a execution')
    def get(self, execution_id):
        db = get_plasma_db()
        execution = db.executions.find_one({'execution-id': execution_id})
        if not execution:
            response = generate_response(404)
        else:
            workflow = db.workflows.find_one({'workflow-id': execution['workflow-id']})
            project = db.projects.find_one({'project-id': workflow['project-id']})
            project_path = project['project-path']
            log_path = path.join(project_path,'logs',execution_id+".log")
            if path.exists(log_path):
                with open(log_path,'r') as log_file:
                    log_data = log_file.read()
                response_data = {"logs":log_data}
                response = generate_response(200, response_data)
            else:
                response = generate_response(404)
        return response
