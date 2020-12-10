"""

MongoDB - A type of NoSQL database
------------------------------------------------------------------------------------------------------------------------
- NoSQL databases are way of storing data. It doesnt require a predefined data model.

#Structure for MongoDB
- Database
    - Collections
        - Documents

# Database
-> SQL equivalent is Database
# Collection
- > SQL equivalent is Table
# Document
-> SQL equivalent is a row of data in the table


# Document Notes
- A document can be represented by a JSON / dictionary
- The SQL table rows below:
index | Name | Age | Address |
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
1     |John  | 83  | 1 High Street
2     |James | 29  | 12 Main Street

- Can be represented by the following documents:
{
    'id': 1,
    'Name': 'John'
    'Age': 83,
    'Address': '1 High Street'
}

and

{
    'id': 2,
    'Name': 'James'
    'Age': 29,
    'Address': '10 Main Street'
}



pymongo - the library we are using to connect to our cloud MongoDB database
------------------------------------------------------------------------------------------------------------------------
More info:
- pymongo: https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-for-more-than-one-document
- advanced mongodb queries: https://docs.mongodb.com/manual/reference/operator/query/

# Basics
These notes make use of the unfinished class below 'EventsDB'

Database object
- db = MongoClient(<connection_str>)[<database_name>]

For the EventsDB class, the database object is the class variable: self._db

A collection object --> self._db[<collection_name>]
List all collections --> self._db.list_collection_names(), note this returns the name of the collections as strings,
not the objects themselves.

# document query
- A collection can be queried to retrieve relevant documents.
- nomenclature -> the keys for documents are generally referred to as fields
{
    'field1': 'field1 value'
    'field2': {
        'field3': 'field3 value'
        'field4': 'field4 value'
    }
- Unlike tables, we can have nested fields. E.g. field 3 and field 4 are nested in field 2.

- self._db['collection1'].find() --> equivalent to SELECT*
- self._db['collection1'].find({}) --> also equivalent to SELECT*

.find(<search_query>)
--> first argument can be used to specify search parameters.
    e.g. {'field1': {'$exist': True}} --> returns an iterable of all documents that contain the field 'field1'.
--> works on nested fields as well
    e.g. {'field2.field3': {'$exist': True}} --> returns all documents that contain the nested field 'field3'
    that is nested inside of a 'field2'.
--> multiple conditions:
   e.g. {'$and': [{'field1': {'$exist': True}}, {'field2': {'$exist': True}}]} --> returns all documents that contain
   both the 'field1' and 'field2'

e.g. if i want to print all documents that contain the field 'name':
for document in self._db[<collection_name>].find({'name': {'$exists': True}}):
    print(document)

--> second argument can be used to define what fields I want to return using 1 for needed and 0 for not needed
e.g. .find({}, {'_id': 0}) --> Returns all documents in collection, but without the field '_id' which is auto generated
by MongoDB when the document is added.


Event Store - current design (probably needs work)
------------------------------------------------------------------------------------------------------------------------

# Collections
- Current all collections will just hold event documents (see more info below). Each collection will group events for
  a particular type of event e.g. 'football'.

# Documents
- Our event documents will represent a the bets on a single event for a single bookmaker. An example document is:

{
    'bookmaker': 'betway'
    'odds': {
        'england': 2.5
        'germany': 1.5
        'draw': 2.0
    }
}
- An id will be assign to these documents when they are added to MongoDB
- This event document represents the betting odds from the bookmaker 'betway', for a football match between
  'england' and 'germany'. In football, games can end in a 'draw', so this outcome is also represented as a team.
  If 'england' win and you bet on them, you will receive 2.5 times your initial bet.

- The odds in the document should cover all possible outcomes, e.g. 'england' wins, 'germany' wins, both teams draw,
  but this is equally represented by 'draw' wins.


TODO: See method docstrings for more info

NB:
- names is being defined as the collection of participants in a betting event. For the example event document above,
  this would lead to names = ['england', 'germany', 'draw']
- names is probably the best way to identify two event documents as being related to the same real life event.
  e.g. if two event documents share the same names, then they are betting on the same real life event. (could be flawed
  logic)

methods:
- .retrieve_events()
- .list_all_event_name_groups()
- maybe others????

Testing:

- I've added a bunch of fake events to a collection named 'test_collection'. Can view them in examples.py or by running:
- events_db = EventsDB()
- for doc in events_db._db['test_collection'].find({}, {'_id': 0}):
-     print(doc)
"""

import pymongo


class EventsDB:
    _username = 'magellan310'
    _password = 'RhRgSiKUDImIlMhf'
    _db_name = 'events_db'
    _connection_str = f'mongodb+srv://{_username}:{_password}@cluster0.mnlhv.mongodb.net/{_db_name}?retryWrites=true&w=majority'
    _placeholder_col = 'placeholder'

    def __init__(self):
        self._client = pymongo.MongoClient(self._connection_str)
        self._db = self._client[self._db_name]

    def store_event(self, event_doc: dict, event_type: str):
        """
        This method inserts a single event document into the collection named <event_type>. If this collection
        doesn't already exist, the collection will be created.
        """
        collection = self._db[event_type]
        collection.insert_one(event_doc)

    def store_events(self, event_docs: [dict], event_type: str):
        """
        This method inserts a list of event documents into the collection named <event_type>. If this collection
        doesn't already exist, the collection will be created.
        """
        collection = self._db[event_type]
        collection.insert_many(event_docs)

    def retrieve_events(self, names: list, event_type: str):
        """
        Given a group of names, e.g. ['name1', 'name2'] find all documents that contain those names. Note these names
        are nested in the field 'odds', so the search query argument would probably use 'odds.name1' etc instead.

        --> returns of list of event documents, without the '_id' field added.
        """

    def list_all_event_name_groups(self, event_type):
        """
        For a particular event type e.g. collection, want to retrieve name groups within that collection.
        --> this gives as a proxy for how many unique events are captured by the collection


        Returns -> List of names, wheres names is a list or set of names.
        """

    def clear_events(self):
        """
        This method deletes all collections in the database apart from the placeholder collection which is required,
        as the database requires at least one collection at all times.
        """
        event_cols = [col for col in self._db.list_collection_names() if col != self._placeholder_col]

        for event_col in event_cols:
            self._db[event_col].drop()
