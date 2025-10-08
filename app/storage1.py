from typing import Dict, List
from uuid import uuid4
from pymongo import MongoClient
from .models import Organization, ComplianceDocument, ValidationRecord
import os
from dotenv import load_dotenv

load_dotenv()

# CHANGE: Use MONGO_URI from environment variables
mongo_uri = os.getenv("MONGO_URI")
print(f"Connecting to MongoDB at {mongo_uri}")
client = MongoClient(mongo_uri)

# # CHANGE: Set up MongoDB client
# client = MongoClient("mongodb://localhost:27017/")
db = client.compliance_db

# CHANGE: Define collections
orgs_collection = db.orgs
documents_collection = db.documents
validations_collection = db.validations

def create_org(data: dict):
    org_id = str(uuid4())
    org = Organization(id=org_id, **data)
    orgs_collection.insert_one(org.dict())  # CHANGE: Insert into MongoDB
    return org.dict()

def list_orgs():
    return list(orgs_collection.find({}, {"_id": 0}))  # CHANGE: Query MongoDB

def list_validations(org_id: str):
    # Query MongoDB for validations with the given orgId
    return list(validations_collection.find({"orgId": org_id}, {"_id": 0}))

def get_org(org_id):
    return orgs_collection.find_one({"id": org_id}, {"_id": 0})  # CHANGE: Query MongoDB

def update_org(org_id, data: dict):
    update_result = orgs_collection.update_one(
        {"id": org_id},
        {"$set": {k: v for k, v in data.items() if v is not None}}
    )  # CHANGE: Update in MongoDB
    if update_result.modified_count > 0:
        return get_org(org_id)
    return None

def delete_org(org_id):
    return orgs_collection.delete_one({"id": org_id}).deleted_count > 0  # CHANGE: Delete from MongoDB

def add_document(org_id, doc: dict):
    doc['orgId'] = org_id
    documents_collection.insert_one(doc)  # CHANGE: Insert into MongoDB
    return doc

def get_document_by_id(doc_id: str):
    # Retrieve the document from the collection using the 'id' field
    document = documents_collection.find_one({"id": doc_id})

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document

def list_documents(org_id):
    return list(documents_collection.find({"orgId": org_id}, {"_id": 0}))  # CHANGE: Query MongoDB

def create_validation(project_name, record: dict):
    record['projectName'] = project_name
    validations_collection.insert_one(record)  # CHANGE: Insert into MongoDB
    return record

def list_validations(org_id: str = None, doc_id: str = None):
    # Build the query based on provided parameters
    query = {}
    if org_id:
        query["orgId"] = org_id
    if doc_id is not None:  # Ensure doc_id is considered only if not None
        query["docId"] = doc_id

    # Query MongoDB for validations with the given orgId and docId
    return list(validations_collection.find(query, {"_id": 0}))

def list_documents_skip_file(org_id: str):
    # Query MongoDB for documents with the given orgId, excluding the 'file' field
    return list(documents_collection.find({"orgId": org_id}, {"_id": 0, "file": 0}))