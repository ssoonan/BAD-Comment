from google.cloud import firestore
from app.db.base import DatabaseModel

import datetime


class FirestoreModel(DatabaseModel):
    def __init__(self, collection_name):
        self.db = firestore.Client()
        self.collection_name = collection_name

    def create(self, document_id, data):
        doc_ref = self.db.collection(self.collection_name).document(document_id)
        data['created_at'] = datetime.datetime.now(datetime.UTC)
        doc_ref.set(data)
        print(f'{self.collection_name} {document_id} created.')

    def update(self, document_id, data):
        doc_ref = self.db.collection(self.collection_name).document(document_id)
        data['updated_at'] = datetime.datetime.now(datetime.UTC)
        doc_ref.update(data)
        print(f'{self.collection_name} {document_id} updated.')

    def get(self, document_id):
        doc_ref = self.db.collection(self.collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            print(f'{self.collection_name} data: {doc.to_dict()}')
            return doc.to_dict()
        else:
            print(f'No such {self.collection_name} {document_id}!')
            return None
