import json

from structure import People

L2_THRESHOLD_NUM_PEOPLE = 3
PERCENTAGE = {
	'tuition': {'l1': 0.2, 'l2': 0.1}, 
	'other': {'l1': 0.0, 'l2': 0.0}
}

ID_NUM_FILE = './data/id.txt'
ROOT_ID_FILE = './data/root.txt'
PEOPLE_NODE_FILENAME = './data/{}.json'


def add_root(nid):
	with open(ROOT_ID_FILE, 'a+') as f:
		f.write(str(nid) + '\n')


def load_people_node(nid):
	filename = PEOPLE_NODE_FILENAME.format(nid)
	with open(filename, 'r') as f:
		node_dict = json.load(f)
	node = People(**node_dict)
	return node
