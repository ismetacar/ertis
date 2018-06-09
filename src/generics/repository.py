from bson import ObjectId
from pymongo.errors import OperationFailure, DuplicateKeyError

from src.utils.errors import ErtisError


class RecordNotExistsError(ErtisError):
    def __init__(self, record_type, record_id):
        super().__init__(status_code=404, err_code="errors.resourceNotFound", err_msg='Resource not found')
        self.record_type = record_type
        self.record_id = record_id


class IDMismatchError(ErtisError):
    def __init__(self, given_id, data_id):
        super().__init__(err_msg="errors.idMismatchError", err_code="errors.idMismatchError", status_code=400)
        self.given_id = given_id
        self.data_id = data_id


class ErtisDuplicateKeyError(ErtisError):
    def __init__(self, collection_name, key, pymongo_exc=None):
        super().__init__(status_code=409,
                         err_msg="There is already existing record at <{}> collection"
                                 "with given <{}>key ".format(collection_name, key),
                         err_code="errors.resourceAlreadyExists",
                         reason=pymongo_exc)
        self.collection_name = collection_name
        self.key = key


def raise_resource_not_found_err(collection_name, key):
    raise ErtisError(
        err_code="errors.resourceNotFound",
        status_code=404,
        err_msg="Not found any resource in collection<{}> with given key <{}>".format(collection_name, key),
        context={
            'collection_name': collection_name,
            'key': key
        }
    )


def maybe_object_id(maybe_id):
    if isinstance(maybe_id, ObjectId):
        return maybe_id
    elif not ObjectId.is_valid(maybe_id):
        return maybe_id
    else:
        return ObjectId(maybe_id)


def normalize_ids(where):
    if not where:
        return

    if '_id' in where:
        if type(where['_id']) == dict and "$in" in where['_id']:
            _ids = [
                maybe_object_id(_id)
                for _id in where['_id']['$in']
            ]
            where['_id']['$in'] = _ids
            return where
        elif type(where['_id']) == str:
            where['_id'] = maybe_object_id(where['_id'])
            return where
    return where


def _pre_process_where(where):
    normalized_where = normalize_ids(where)
    return normalized_where


def create_id():
    return ObjectId()


class ErtisGenericRepository(object):

    def __init__(self, db):
        self.db = db

    def save(self, document, collection, force=False):
        if "_id" not in document:
            document["_id"] = create_id()
        else:
            document['_id'] = maybe_object_id(document['_id'])
        try:
            if force:
                self.db[collection].replace_one(
                    {'_id': document['_id']},
                    document,
                    upsert=True
                )
            else:
                self.db[collection].save(document)

        except DuplicateKeyError as e:
            raise ErtisError(
                err_code="errors.duplicateKeyError",
                status_code=409,
                err_msg="There is already existing record in collection<{}>.".format(collection),
                context={
                    'collection': collection,
                    'error_message': e.details['errmsg']
                }
            )

        return document

    def replace(self, document, collection):
        if "_id" not in document:
            raise ErtisError(
                err_code="errors.invalidResource",
                status_code=400,
                err_msg="Document is invalid for this operation<{}>".format('UPDATE'),
                context={
                    "document": document,
                    "collection": collection}
            )

        where = {
            '_id': maybe_object_id(document.get('_id'))
        }

        return self.db[collection].replace_one(where, normalize_ids(document))

    def update_one_by(self, where, command, collection):
        where = _pre_process_where(where)

        update_result = self.db[collection].update_one(where, command)

        if update_result.modified_count == 0:
            raise_resource_not_found_err(collection, where)

    def find_one_by(self, where=None, select=None, raise_exec=True, collection=None):
        where = _pre_process_where(where)

        founded = self.db[collection].find_one(where, select)

        if not founded and raise_exec:
            raise_resource_not_found_err(collection, where)

        return founded

    def find_one_by_id(self, _id, collection, raise_exec=True):
        founded = self.find_one_by(
            where={
                "_id": maybe_object_id(_id)
            },
            raise_exec=raise_exec,
            collection=collection
        )

        return founded

    def remove_one_by(self, where=None, collection=None, raise_exec=True):
        where = _pre_process_where(where)

        result = self.db[collection].remove(where)

        if result["n"] == 0 and raise_exec:
            raise_resource_not_found_err(collection, where)

        return result

    def remove_many(self, where=None, collection=None):
        where = _pre_process_where(where)
        result = self.db[collection].delete_many(where)
        return result

    def remove_one_by_id(self, _id, collection):
        return self.remove_one_by(
            where={
                "_id": maybe_object_id(_id)
            },
            collection=collection
        )

    def query(self, where=None, select=None, limit=None, skip=None, sort=None, collection=None):

        try:
            where = _pre_process_where(where)

            if not select:
                select = None

            if not limit or limit > 500:
                limit = 500

            cur = self.db[collection].find(where, select)

            total_count = cur.explain()

            if skip:
                cur.skip(int(skip))

            if limit:
                cur.limit(int(limit))

            if sort:
                cur.sort(sort)

            items = list(cur)

            return items, total_count["executionStats"]["nReturned"]

        except OperationFailure as e:
            if e.code in [2, 4]:
                raise ErtisError(
                    context=e.details,
                    err_msg='Please provide valid query...',
                    err_code='errors.badQuery',
                    status_code=400
                )

            raise

    def distinct(self, field=None, where=None, collection=None):
        where = _pre_process_where(where)
        result = self.db[collection].distinct(field, where)
        return result
