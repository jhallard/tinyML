# -*- coding: utf-8 -*-
import uuid
import task_lib, json


def deletedb():
    redirect(URL('default', 'deletedb'))

def populate():
    redirect(URL('default', 'populate'))

def index():
	if not auth.user_id :
		redirect(URL('default', 'index'))
	murl = URL('dashboard', 'load_models', user_signature=True)
	turl = URL('dashboard', 'load_transactions', user_signature=True)
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                user_id=auth.user_id if auth.user_id else -1,
				models=[], transactions=[],
				murl=murl, turl=turl)

def model():
	if not auth.user_id :
		redirect(URL('default', 'index'))
	iid = int(request.args(0))
	model = db(db.models.id == iid).select().first()
	mdurl = URL('dashboard', 'load_model', user_signature=True)
	turl = URL('dashboard', 'load_transactions', user_signature=True)
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                    user_id=auth.user_id if auth.user_id else -1, model_id=iid,
                    turl=turl, mdurl=mdurl, model=model, transactions=[])
def models():
	if not auth.user_id :
		redirect(URL('default', 'index'))
	murl = URL('dashboard', 'load_models', user_signature=True)
	turl = URL('dashboard', 'load_transactions', user_signature=True)
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                user_id=auth.user_id if auth.user_id else -1,
                murl=murl, models=[], transactions=[])

def create():
	if not auth.user_id :
		redirect(URL('default', 'index'))
	murl = URL('dashboard', 'load_models', user_signature=True)
	tdurl = URL('dashboard', 'load_transaction', args=[],  user_signature=True)
	mdurl = URL('dashboard', 'load_model', args=[])
	new_url = URL('dashboard', 'add_model', user_signature=True)
	edit_url = URL('dashboard', 'edit_model', user_signature=True)
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                    user_id=auth.user_id if auth.user_id else -1,
                    mdurl=mdurl, murl=murl, new_url=new_url,
		    tdurl=tdurl,  edit_url=edit_url, model={}, transactions=[])

@auth.requires_signature()
def load_models():
    page = int(request.vars.get('page', 1))
    page_size = int(request.vars.get('page_size', 20))
    pb = int(page-1)*(int(page_size))
    pe = int(page)*(int(page_size))
    trs = db(db.models.creator == auth.user_id).select(orderby=~db.models.created_at, limitby=(pb, pe))
    return response.json(dict(models=trs))

def load_model():
    iid = int(request.vars.get('id'))
    # iid = int(request.args(0))
    trs = db(db.models.id == iid).select().first()
    if not auth or not auth.user_id == trs.creator :
        raise HTTP(404,"Prohibited")
    return response.json(dict(model=trs))

@auth.requires_signature()
def add_model():
    name = request.vars.get('name', '');
    mclass = request.vars.get('mclass', '');
    muuid = request.vars.get('uuid', uuid.uuid4());
    arch = request.vars.get('arch');
    if db(db.models.creator == auth.user_id and db.models.name == name).select().first() :
        raise HTTP(400,"Model name exists already.")

    db['models'].insert(
                name=name,
                name_short=name[:9],
                mclass=mclass,
                uuid=muuid,
                arch=arch,
		compiled=False,
                status="compiling",
                creator = auth.user_id)

    model = db(db.models.uuid == muuid).select().first()

    trs = {
            "status": "active",
            "tclass": "create",
            "uuid" : uuid.uuid4(),
            "creator" : auth.user_id,
	    "model_name" : model.name,
	    "model_name_short" : model.name_short,
            "model" : model
            }

    db['transactions'].insert(**trs)

    trs = db(db.transactions.uuid == trs['uuid']).select().first()

    print scheduler.queue_task(task_lib.compile_model, pvars=dict(mid=model.id, tid=str(trs.id)))

    return response.json(dict(model=model, transaction=trs))


@auth.requires_signature()
def edit_model():
    name = request.vars.get('name', '');
    mclass = request.vars.get('mclass', '');
    muuid = request.vars.get('uuid', uuid.uuid4());
    arch = request.vars.get('arch');
    model = db(db.models.uuid == muuid).select().first()
    model.update_record(
                name=name,
                name_short=name[:9],
                mclass=mclass,
                compiled=False,
                uuid=muuid,
                arch=arch,
                status="compiling",
                creator = auth.user_id)

    trs = {
            "status": "active",
            "tclass": "edit",
            "uuid" : uuid.uuid4(),
            "creator" : auth.user_id,
            "model" : model,
	    "model_name" : model.name,
	    "model_name_short" : model.name_short,
            }

    db['transactions'].insert(**trs)

    trs = db(db.transactions.uuid == trs['uuid']).select().first()

    print scheduler.queue_task(task_lib.compile_model, pvars=dict(mid=model.id, tid=str(trs.id)))

    return response.json(dict(model=model, transaction=trs))

@auth.requires_signature()
def load_transactions():
        mid = int(request.vars.get('mid', -1))
	page = int(request.vars.get('page', 1))
	page_size = int(request.vars.get('page_size', 1))
	pb = int(page-1)*(int(page_size))
	pe = int(page)*(int(page_size))

        if mid >= 0 :
            trs = db(db.transactions.creator == auth.user_id and db.transactions.model == mid).select(orderby=~db.transactions.created_at, limitby=(pb, pe))
        else :
            trs = db(db.transactions.creator == auth.user_id).select(orderby=~db.transactions.created_at, limitby=(pb, pe))
	return response.json(dict(transactions=trs))

@auth.requires_signature()
def load_transaction():
        tid = int(request.vars.get('tid', -1))
	if not tid :
	    raise HTTP(404,"Transaction not found or innaccesable.")
		
	tr = db(db.transactions.creator == auth.user_id and db.transactions.id == int(tid)).select().first()
	return response.json(dict(transaction=tr))

def do_logout() :
    redirect(URL('default', 'user', args=['logout']))

def do_login() :
    redirect(URL('default', 'user', args=['login']))

def do_register() :
    redirect(URL('default', 'user', args=['register']))

