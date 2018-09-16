# coding: utf-8


def orm_iter(_class, start=0, limit=1000):
    count = limit

    while count <= limit:
        os = _class.select().where(_class.id > start).order_by(_class.id).limit(limit)
        count = len(os)
        if os:
            for o in os:
                yield o
            start = os[count-1].id
        else:
            break
