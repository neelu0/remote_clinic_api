from remote_clinic_api import app, db
from flask import jsonify, request
from remote_clinic_api.models import *
import json

from flask import Response
from markupsafe import escape
from datetime import datetime
from mongoengine import ValidationError, FieldDoesNotExist, NotUniqueError

@app.route('/')
def hello():
    return jsonify({'hello':'world'})

@app.route('/patients', methods = ['GET','POST'])
def patients():
    if request.method == 'GET':    
        patient_objects = Patient.objects.exclude('password')
        patient_schema = PatientSchema()
        p_list_json = []
        if request.args.get('limit') is not None:
            limit = request.args.get('limit')
            for i in patient_objects[:int(limit)]:
                p_list_json.append(patient_schema.dump(i))
        else:
            for j in patient_objects:
                p_list_json.append(patient_schema.dump(j))
        return jsonify(p_list_json)
    
    elif request.method == 'POST':
        patient_json = request.json
        patient_schema = PatientSchema()
        patient = patient_schema.load(patient_json)
        patient.save()
        new_patient = patient_schema.dump(patient)
        return jsonify(new_patient)

@app.route('/patients/<string:patient_id>', methods=['GET','PATCH','PUT'])
def get_patient(patient_id):
    if request.method == 'GET':
        patient_object = Patient.objects.exclude('password').get_or_404(id=str(patient_id))
        patient_schema = PatientSchema()
        return jsonify(patient_schema.dump(patient_object))

    elif request.method == 'PATCH' or request.method == 'PUT':
        updated_fields = request.json
        patient_dic = PatientSchema().dump(Patient.objects.get_or_404(id=str(patient_id)))
        patient_dic.update(updated_fields)
        updated_patient = PatientSchema().load(patient_dic)
        updated_patient.save()
        return jsonify(PatientSchema().dump(updated_patient))
@app.route('/doctors', methods=['GET', 'POST'])
def doctor():
    if request.method == 'GET': ## Return All Doctors List.
        limit = request.args.get('limit')
        offset = request.args.get('offset')
        try:
            if limit is not None: limit = int(limit)
            if offset is not None: offset = int(offset)

            if offset is None: end = limit
            elif limit is None: end = None 
            else: end = limit + offset

        except TypeError as ve:
            end = None
            offset = None
        result = Doctor.objects[offset:end]
        jsonData = result.to_json()
        return jsonData
    elif request.method == 'POST': ## Add Doctor Record.
        body = request.json
        try: # Try to store doctor info. 
            doctor = Doctor(**body)
            doctor.save()
            return jsonify({'id': str(doctor.id) })
        except ValidationError as error:
            return error.message
    else:
        res = Response()
        res.status_code = 402
        return res

@app.route('/doctors/<id>', methods=['GET','PUT', 'DELETE'])
def doctors(id):
    if request.method == 'GET': ## Return Single Doctor.
        try: # Try to get doctor info with the given id. 
            result = Doctor.objects(id = id)
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT': ## Update Doctor.
        try:
            body = request.json
            result = Doctor.objects(id = id)
            result[0].update(**body)
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message        
    elif request.method == 'DELETE': ## Delete Doctor.
        try:
            result = Doctor.objects(id = id)
            result[0].delete()
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 402
        return res

@app.route('/doctors/<doctorId>/documents', methods=['GET', 'POST'])
def ddocument(doctorId):
    if request.method == 'GET':
        try:
            result = DDocuments.objects(owner = doctorId)  
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{doctorId}` is NOT FOUND!!!'            
        except ValidationError as err:
            return err.message
    elif request.method == 'POST':
        body = request.json
        try: # Try to store info. 
            ddocument = DDocuments(**body)
            ddocument.save()
            return jsonify({"id": str(ddocument.id)})
        except FieldDoesNotExist as atterr:
            return f"INCORRECT STRUCTURE: {str(atterr)}"
        except ValidationError as error:
            return error.message
    else:
        res = Response()
        res.status_code = 402
        return res

@app.route('/doctors/<doctorId>/documents/<documentId>', methods=['GET','PUT', 'DELETE'])
def ddocuments(doctorId,documentId):
    if request.method == 'GET':
        try:
            result = DDocuments.objects(id = documentId, owner = doctorId)  
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with given id: `{documentId}` is NOT FOUND!!!'                        
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT':
        try:
            body = request.json
            result = DDocuments.objects(id = documentId, owner = doctorId)
            result[0].update(**body)
            return jsonify({"id": documentId, "owner": doctorId})
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message        
    elif request.method == 'DELETE':
        try:
            result = DDocuments.objects(id = documentId, owner = doctorId)  
            result[0].delete()
            return jsonify({"documentId":documentId,"ownerId":doctorId})
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 402
        return res

@app.route('/doctors/<doctorId>/reviews', methods=['GET','POST'])
def docreviews(doctorId):
    if request.method == 'GET':
        try:
            result = Reviews.objects(review_for = doctorId)  
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{doctorId}` is NOT FOUND!!!'            
        except ValidationError as err:
            return err.message
    elif request.method == 'POST':
        body = request.json
        try: # Try to store info. 
            review = Reviews(**body)
            review.save()
            return jsonify({"id": str(review.id)})
        except FieldDoesNotExist as atterr:
            return f"INCORRECT STRUCTURE: {str(atterr)}"
        except ValidationError as error:
            return error.message

@app.route('/doctors/<doctorId>/reviews/<reviewId>', methods=['GET','PUT', 'DELETE'])
def mod_docreviews(doctorId,reviewId):
    if request.method == 'GET':
        try:
            result = Reviews.objects(id = reviewId, review_for = doctorId)  
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with given id: `{reviewId}` is NOT FOUND!!!'                        
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT':
        try:
            body = request.json
            result = Reviews.objects(id = reviewId, review_for = doctorId)
            result[0].update(**body)
            return jsonify({"id": reviewId, "review_for": doctorId})
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message        
    elif request.method == 'DELETE':
        try:
            result = Reviews.objects(id = reviewId, review_for = doctorId)  
            result[0].delete()
            return jsonify({"documentId":reviewId,"ownerId":doctorId})
        except ValidationError as err:
            return err.message


@app.route('/operators', methods=['GET','POST'])
def operator():
    if request.method == 'GET':
        limit = request.args.get('limit')
        offset = request.args.get('offset')
        try:
            if limit is not None: limit = int(limit)
            if offset is not None: offset = int(offset)

            if offset is None: end = limit
            elif limit is None: end = None 
            else: end = limit + offset

        except TypeError as ve:
            end = None
            offset = None
        result = Operator.objects[offset:end]
        jsonData = result.to_json()
        return jsonData
    elif request.method == 'POST':
        body = request.json
        try: 
            operator = Operator(**body)
            operator.save()
            return jsonify({'id': str(operator.id) })
        except NotUniqueError as emailAlreadyReg:
            return "ERROR: Account already registered with the given email Address."
        except FieldDoesNotExist as atterr:
            return f"INCORRECT STRUCTURE: {str(atterr)}"
        except ValidationError as error:
            return error.message
    else:
        res = Response()
        res.status_code = 401
        return res

@app.route('/operators/<id>', methods=['GET','PUT','DELETE'])
def get_operator(id):
    if request.method == 'GET':
        try: 
            result = Operator.objects(id = id)
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT':
        try:
            body = request.json
            result = Operator.objects(id = id)
            result[0].update(**body)
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message        
    elif request.method == 'DELETE':
        try:
            result = Operator.objects(id = id)
            result[0].delete()
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 401
        return res

@app.route('/operators/<operatorId>/roles', methods=['GET','POST'])
def operator_roles(operatorId):
    if request.method == 'GET':
        try:
            result = OperatorRoles.objects(operator = operatorId)  
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{operatorId}` is NOT FOUND!!!'            
        except ValidationError as err:
            return err.message
    elif request.method == 'POST':
        body = request.json
        try: # Try to store info. 
            opRole = OperatorRoles(**body)
            opRole.save()
            return jsonify({"id": str(opRole.id)})
        except FieldDoesNotExist as atterr:
            return f"INCORRECT STRUCTURE: {str(atterr)}"
        except ValidationError as error:
            return error.message
    else:
        res = Response()
        res.status_code = 401
        return res

@app.route('/operators/<operatorId>/roles/<roleId>', methods=['GET','PUT','DELETE'])
def get_operator_roles(operatorId, roleId):
    if request.method == 'GET':
        try:
            result = OperatorRoles.objects(operator = operatorId, id = roleId)  
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with given id: `{roleId}` is NOT FOUND!!!'                        
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT':
        try:
            body = request.json
            result = OperatorRoles.objects(operator = operatorId, id = roleId)  
            result[0].update(**body)
            return jsonify({"id": roleId, "operatorId": operatorId})
        except IndexError as notFound:
            return f'Record with the id: `{roleId}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message        
    elif request.method == 'DELETE':
        try:
            result = OperatorRoles.objects(operator = operatorId, id = roleId)  
            result[0].delete()
            return jsonify({"roleId":roleId, "operatorId":operatorId})
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 401
        return res

@app.route('/operators/<operatorId>/permissions', methods=['GET'])
def operator_permission(operatorId):
    if request.method == 'GET':
        try:
            permissions = [] # Create empty permisstion List.
            roles = OperatorRoles.objects(operator = operatorId) 
            for role in roles:
                r_ = Roles.objects(id = role.id)
                permissions.append([p for p in r_.permissions])
            return jsonify(permissions)
        except AttributeError as atterr:
            return f"ERROR: {str(atterr)}"
        except IndexError as notFound:
            return f'Record with given id: `{operatorId}` is NOT FOUND!!!'                        
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 401
        return res

@app.route('/roles', methods=['GET','POST'])
def roles():
    if request.method == 'GET':
        limit = request.args.get('limit')
        offset = request.args.get('offset')
        try:
            if limit is not None: limit = int(limit)
            if offset is not None: offset = int(offset)

            if offset is None: end = limit
            elif limit is None: end = None 
            else: end = limit + offset

        except TypeError as ve:
            end = None
            offset = None
        result = Roles.objects[offset:end]
        jsonData = result.to_json()
        return jsonData
    elif request.method == 'POST':
        body = request.json
        try: 
            role = Roles(**body)
            role.save()
            return jsonify({'id': str(role.id) })
        except ValidationError as error:
            return error.message
    else:
        res = Response()
        res.status_code = 401
        return res  
@app.route('/roles/<id>', methods=['GET','PUT','DELETE'])
def get_roles(id):
    if request.method == 'GET':
        try: 
            result = Roles.objects(id = id)
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT':
        try:
            body = request.json
            result = Roles.objects(id = id)
            result[0].update(**body)
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message   
    elif request.method == 'DELETE':
        try:
            result = Roles.objects(id = id)
            result[0].delete()
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 401
        return res