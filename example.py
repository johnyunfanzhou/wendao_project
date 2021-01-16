import argparse
import pandas as pd

import utils
from structure import People


def batch_new_people(filename, **kwargs):
	"""
	file format: csv
	name	parent	incash	outcash
	"""
	df = pd.read_csv(filename, dtype={'name': str, 'parent': str, 'incash': float, 'outcash': float})
	df['name'] = df['name'].fillna('')
	df['parent'] = df['parent'].fillna('')
	df.loc[df['parent'] == '', 'parent'] = None
	df['incash'] = df['incash'].fillna(0.)
	df['outcash'] = df['outcash'].fillna(0.)
	update_queue = []

	for idx, row in df.iterrows():
		row_dict = row.to_dict()
		node = People(**row_dict)

		if utils.ID_MAP.get(node.name, None) is not None:
				raise ValueError('Duplicated username found in id: {}, name: {}'.format(i, utils.ID_MAP[node.name]))

		pname = row_dict.get('parent', None)
		if pname is None:
			utils.add_root(node.id)
		else:
			node.parent = utils.ID_MAP[pname]
			pnode = utils.load_people_node(pname, is_id=False)
			pnode.children.append(node.id)
			pnode.active_children.append(node.id)
			pnode.dump()

		node.dump()
		utils.ID_MAP[node.name] = node.id
		update_queue.append(node.id)

		print('{} added.'.format(row_dict))

	# update metadata
	print('Updating metadata ...')
	for nid in update_queue:
		node = utils.load_people_node(nid)
		node.update_upward()
		node.dump()


def batch_deactivate_people(name_list, **kwargs):
	update_queue = []
	for name in name_list:
		node = utils.load_people_node(name, is_id=False)
		old_status = node.active
		node.active = False

		if node.parent is not None:
			pnode = utils.load_people_node(node.parent)
			pnode.active_children = [cid for cid in pnode.active_children if cid != node.id]
			pnode.dump()

		node.dump()
		update_queue.append(node.id)
		print('id: {}, name: {} was {}, now deactive.'.format(node.id, node.name, 'active' if old_status else 'deactive'))

	# update metadata
	print('Updating metadata ...')
	for nid in update_queue:
		node = utils.load_people_node(nid)
		node.update_upward()
		node.dump()


def batch_activate_people(name_list, **kwargs):
	update_queue = []
	for name in name_list:
		node = utils.load_people_node(name, is_id=False)
		old_status = node.active
		node.active = True

		if node.parent is not None:
			pnode = utils.load_people_node(node.parent)
			if node.id not in pnode.active_children:
				pnode.active_children.append(node.id)
			pnode.dump()

		node.dump()
		update_queue.append(node.id)
		print('id: {}, name: {} was {}, now active.'.format(node.id, node.name, 'active' if old_status else 'deactive'))

	# update metadata
	print('Updating metadata ...')
	for nid in update_queue:
		node = utils.load_people_node(nid)
		node.update_upward()
		node.dump()


def _payment(payer, amount, ptype):
	payer_node = utils.load_people_node(payer, is_id=False)
	pb = utils.PERCENTAGE[ptype]
	payer_node._expense_cache += amount

	def recurse_payback(node, pbamount, _expense=True):
		if not _expense:
			node._outcash_cache += (pb['l1'] + pb['l2']) * pbamount
			node.dump()
		if node.parent is not None:
			l1_node = utils.load_people_node(node.parent)
			l1_node._incash_cache += pb['l1'] * pbamount

			if l1_node.parent is not None:
				l2_node = utils.load_people_node(l1_node.parent)
				if len(l2_node.active_children) >= utils.L2_THRESHOLD_NUM_PEOPLE:
					l2_node._incash_cache += pb['l2'] * pbamount
					l2_node.dump()

			l1_node.dump()
			recurse_payback(l1_node, l1_node._incash_cache, _expense=False)

	recurse_payback(payer_node, amount)

	def recurse_cleanup(node):
		node.expense_cache += node._expense_cache
		node.incash_cache += node._incash_cache
		node.outcash_cache += node._outcash_cache
		node._expense_cache = 0
		node._incash_cache = 0
		node._outcash_cache = 0
		node.dump()
		if node.parent is not None:
			pnode = utils.load_people_node(node.parent)
			recurse_cleanup(pnode)

	recurse_cleanup(payer_node)


def batch_payment(filename: str, papply=False, **kwargs):
	"""
	file format: csv
	payer	amount	ptype
	"""
	df = pd.read_csv(filename, dtype={'payer': str, 'amount': float, 'ptype': str})
	df['payer'] = df['payer'].fillna('')
	df['amount'] = df['amount'].fillna(0.)
	df['ptype'] = df['ptype'].fillna('')
	for idx, row in df.iterrows():
		row_dict = row.to_dict()
		_payment(**row_dict)
		print('{} processed.'.format(row_dict))
	export_all(cache=True)


def apply():
	with open(utils.ID_NUM_FILE, 'r') as f:
		last = int(f.read())
	for i in range(0, last):
		node = utils.load_people_node(i)
		node.expense += node.expense_cache
		node.incash += node.incash_cache
		node.outcash += node.outcash_cache
		node.expense_cache = 0
		node.incash_cache = 0
		node.outcash_cache = 0
		node.dump()
		if node.parent is not None:
			pnode = utils.load_people_node(node.parent)
			recurse_apply(pnode)

	recurse_apply(payer_node)


def export_all(cache=False):
	with open(utils.ID_NUM_FILE, 'r') as f:
		i = int(f.read())
	df_dict = {'id': [], 'name': [], 'expense': [], 'incash': [], 'outcash': [], 'netcash': []}
	for nid in range(i):
		node = utils.load_people_node(nid)
		if node.active:
			if cache:
				df_dict['id'].append(nid)
				df_dict['name'].append(node.name)
				df_dict['expense'].append(node.expense_cache)
				df_dict['incash'].append(node.incash_cache)
				df_dict['outcash'].append(node.outcash_cache)
				df_dict['netcash'].append(node.incash_cache- node.outcash_cache)
			else:
				df_dict['id'].append(nid)
				df_dict['name'].append(node.name)
				df_dict['expense'].append(node.expense_cache)
				df_dict['incash'].append(node.incash)
				df_dict['outcash'].append(node.outcash)
				df_dict['netcash'].append(node.incash - node.outcash)
	df = pd.DataFrame(df_dict)
	filename = 'output_cache.csv' if cache else 'output.csv'
	with open(filename, 'w') as f:
		df.to_csv(f, index=False, line_terminator='\n')


def reset_all(cache=False):
	with open(utils.ID_NUM_FILE, 'r') as f:
		i = int(f.read())
	for nid in range(i):
		node = utils.load_people_node(nid)
		if not cache:
			node.incash = 0.
			node.outcash = 0.
		node.incash_cache = 0.
		node.outcash_cache = 0.
		node._incash_cache = 0.
		node._outcash_cache = 0.
		node.dump()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('func', choices=['people', 'activate', 'deactivate', 'payment', 'apply', 'reset', 'reset_cache'])
	parser.add_argument('--file', type=str)
	parser.add_argument('--name', type=str, nargs='+')
	args = parser.parse_args()
	if args.func in ['people', 'payment'] and args.file is None:
		parser.error('Function {} required --file.'.format(args.func))
	if args.func in ['activate', 'deactivate'] and args.name is None:
		parser.error('Function {} required --name.'.format(args.func))

	if args.func == 'people':
		batch_new_people(args.file)
	if args.func == 'activate':
		batch_activate_people(args.name)
	if args.func == 'deactivate':
		batch_deactivate_people(args.name)
	if args.func == 'payment':
		batch_payment(args.file)
	if args.func == 'apply':
		apply()
	if args.func == 'reset_cache':
		reset_all(cache=True)
	if args.func == 'reset':
		reset_all()
