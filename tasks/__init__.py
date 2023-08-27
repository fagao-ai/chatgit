from invoke import Collection

from tasks import db, misc

ns = Collection.from_module(misc)
for module in [db]:
    ns.add_collection(Collection.from_module(module))
