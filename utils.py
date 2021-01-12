import json
from structure import People

L2_THRESHOLD_NUM_PEOPLE = 3
PERCENTAGE = {
	'1': {'l1': 0.2, 'l2': 0.1}, 
	'0': {'l1': 0.0, 'l2': 0.0}
}

ID_NUM_FILE = './data/id.txt'
ROOT_ID_FILE = './data/root.txt'
PEOPLE_NODE_FILENAME = './data/{}.json'

def _id_map():
	res = {}
	with open(ID_NUM_FILE, 'r') as f:
		last = int(f.read())
	for i in range(0, last):
		with open(PEOPLE_NODE_FILENAME.format(i), 'r') as f:
			node_dict = json.load(f)
			if res.get(node_dict['name'], None) is not None:
				raise ValueError('Duplicated username found in id: {}, name: {}'.format(i, node_dict['name']))
			res[node_dict['name']] = node_dict['id']
	return res

ID_MAP = _id_map()


def add_root(nid):
	with open(ROOT_ID_FILE, 'a+') as f:
		f.write(str(nid) + '\n')


def load_people_node(nid, is_id=True):
	"""name: str of username"""
	if not is_id:
		nid = ID_MAP[nid]
	nid = int(nid)
	filename = PEOPLE_NODE_FILENAME.format(nid)
	with open(filename, 'r') as f:
		node_dict = json.load(f)
	node = People(**node_dict)
	return node


def patch():
	with open(ID_NUM_FILE, 'r') as f:
		last = int(f.read())
	for i in range(0, last):
		with open(PEOPLE_NODE_FILENAME.format(i), 'r') as f:
			node_dict = json.load(f)
			node_dict['active'] = True
			node_dict['active_children'] = node_dict['children']
		with open(PEOPLE_NODE_FILENAME.format(i), 'w') as f:
			json.dump(node_dict, f, indent=4)
