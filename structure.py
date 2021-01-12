import json

import utils

class People(object):
	"""docstring for People"""
	def __init__(self, **kwargs):
		"""
		:param args.parent: People
		:param args.outflow: float, initialize at 0.0
		:param args.inflow: float, initialize at 0.0
		:param args.percent: dict
		:param args.parent: People
		:param args.children: list[People]
		"""
		self.id = None
		self.parent = None
		self.incash = 0.
		self.outcash = 0.
		self.incash_cache = 0.
		self.outcash_cache = 0.
		self._incash_cache = 0.
		self._outcash_cache = 0.
		self.name = 'new_client'
		self.active = True
		self.children = []
		self.num_children = 0

		self.__dict__.update(kwargs)
		if self.id is None:
			self.assign_id()


	def assign_id(self):
		with open(utils.ID_NUM_FILE, 'r+') as f:
			i = int(f.read())
			f.seek(0)
			f.write(str(i + 1))
		self.id = i


	def dump_people_node(self):
		if self.id is None:
			self.assign_id()
		filename = utils.PEOPLE_NODE_FILENAME.format(self.id)
		with open(filename, 'w+') as f:
			json.dump(self.__dict__, f, indent=4)


	def _get_num_children(self):
		result = len(self.children)
		for cid in self.children:
			cnode = utils.load_people_node(cid)
			result += cnode._get_num_children()
		return result


	def update_upward(self):
		self.num_children = self._get_num_children()
		self.dump_people_node()
		if self.parent is not None:
			pnode = utils.load_people_node(self.parent)
			pnode.update_upward()
