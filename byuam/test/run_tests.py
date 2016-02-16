import getpass
import os
import shutil
import unittest

from byuam.body import Asset, Shot
from byuam.environment import Department, Status
from byuam.element import Element
from byuam.project import Project

class TestAssetManager(unittest.TestCase):

	def setUp(self):
		self.project = Project()
		self.assets_dir = self.project.get_assets_dir()
		if not os.path.exists(self.assets_dir):
			os.mkdir(self.assets_dir)
		self.shots_dir = self.project.get_shots_dir()
		if not os.path.exists(self.shots_dir):
			os.mkdir(self.shots_dir)
		self.users_dir = self.project.get_users_dir()
		if not os.path.exists(self.users_dir):
			os.mkdir(self.users_dir)

	def tearDown(self):
		shutil.rmtree(self.assets_dir)
		shutil.rmtree(self.shots_dir)
		shutil.rmtree(self.users_dir)

class TestBody(TestAssetManager):

	def setUp(self):
		TestAssetManager.setUp(self)

		self.create_count = 10
		self.shot_names = []
		for i in xrange(self.create_count):
			self.shot_names.append("a%02d" % i)

		self.shots = []
		for name in self.shot_names:
			self.shots.append(self.project.create_shot(name))

		self.asset_names = []
		for i in xrange(self.create_count):
			self.asset_names.append("asset_name"+str(i))

		self.assets = []
		for name in self.asset_names:
			self.assets.append(self.project.create_asset(name))

	def test_body(self):

		# test shots		
		for i in xrange(self.create_count):
			self.assertEquals(self.shots[i].get_name(), self.shot_names[i])
			shotpath = os.path.join(self.shots_dir, self.shot_names[i])
			self.assertTrue(os.path.exists(os.path.join(shotpath, Shot.PIPELINE_FILENAME)))
			for dept in Department.BACKEND: # should create default elements for all backend departments
				self.assertTrue(os.path.exists(os.path.join(shotpath, dept, Element.DEFAULT_NAME, Element.PIPELINE_FILENAME)))
				element = self.shots[i].get_element(dept)
				self.assertEquals(element.get_name(), Element.DEFAULT_NAME)
				self.assertEquals(element.get_department(), dept)
				new_name = "test"
				self.shots[i].create_element(dept, new_name)
				element_list = self.shots[i].list_elements(dept)
				self.assertTrue(len(element_list)==2)
				self.assertTrue(new_name in element_list)
				self.assertTrue(Element.DEFAULT_NAME in element_list)

			self.assertRaises(EnvironmentError, self.project.create_shot, self.shot_names[i]) # can't create same shot twice

			# TODO: test referencing

		# test assets
		for i in xrange(self.create_count):
			self.assertEquals(self.assets[i].get_name(), self.asset_names[i])
			assetpath = os.path.join(self.assets_dir, self.asset_names[i])
			self.assertTrue(os.path.exists(os.path.join(assetpath, Asset.PIPELINE_FILENAME)))
			for dept in Department.FRONTEND: # should create default elements for all frontend departments
				self.assertTrue(os.path.exists(os.path.join(assetpath, dept, Element.DEFAULT_NAME, Element.PIPELINE_FILENAME)))
				element = self.assets[i].get_element(dept)
				self.assertEquals(element.get_name(), Element.DEFAULT_NAME)
				self.assertEquals(element.get_department(), dept)
				new_name = "test"
				self.assets[i].create_element(dept, new_name)
				element_list = self.assets[i].list_elements(dept)
				self.assertTrue(len(element_list)==2)
				self.assertTrue(new_name in element_list)
				self.assertTrue(Element.DEFAULT_NAME in element_list)

			self.assertRaises(EnvironmentError, self.project.create_asset, self.asset_names[i]) # can't create same asset twice


class TestElement(TestAssetManager):

	def setUp(self):
		TestAssetManager.setUp(self)
		self.bodies = []
		self.bodies.append(self.project.create_shot("a00"))
		self.bodies.append(self.project.create_asset("asset_name"))
		self.element_count = len(Department.FRONTEND) + len(Department.BACKEND)
		self.user = getpass.getuser()

	def test_element(self):

		count = 0
		for body in self.bodies:
			for dept in Department.ALL:
				try:
					element = body.get_element(dept)
				except EnvironmentError:
					continue
				count += 1
				self.assertEquals(element.get_parent(), body.get_name())
				self.assertEquals(element.get_department(), dept)
				self.assertEquals(element.get_status(), Status.WAIT)
				element.update_status(Status.DONE)
				element.update_assigned_user(self.user)
				self.assertEquals(element.get_status(), Status.DONE)
				self.assertEquals(element.get_assigned_user(), self.user)
				element = body.get_element(dept) # re-read data from file to ensure nothing gets lost in i/o
				self.assertEquals(element.get_status(), Status.DONE)
				self.assertEquals(element.get_assigned_user(), self.user)

				# test checkout
				checkout_path = element.checkout(self.user)
				self.assertTrue(os.path.exists(checkout_path))

				checkout_path2 = element.checkout(self.user)
				self.assertTrue(os.path.exists(checkout_path2))

				self.assertTrue(self.user in element.list_checkout_users())
				self.assertNotEqual(checkout_path, checkout_path2)

				checkout_dir = element.get_checkout_dir(self.user)
				checkout = self.project.get_checkout(checkout_dir)
				self.assertEquals(element.get_parent(), checkout.get_body())
				self.assertEquals(element.get_department(), checkout.get_department())
				self.assertEquals(element.get_name(), checkout.get_element())
				self.assertEquals(self.user, checkout.get_user())
				self.assertEquals(len(checkout.list_files()), 2)
				self.assertTrue(checkout_path in checkout.list_files())
				self.assertTrue(checkout_path2 in checkout.list_files())
				self.assertEquals(len(checkout.list_times()), 2)

				# test publish
				comment = "automated testing"
				element.publish(self.user, checkout_path, comment)
				self.assertEquals(len(element.list_publishes()), 1)
				publish = element.get_last_publish()
				self.assertEquals(self.user, publish[0])
				self.assertEquals(comment, publish[2])
				self.assertTrue(os.path.exists(element.get_version_dir(0)))

				element.replace_cache(self.user, checkout_path)
				self.assertTrue(os.path.exists(element.get_cache_filepath()))


		self.assertEquals(count, self.element_count)


if __name__ == "__main__":
	test_path = "byu-pipeline-tools/byuam/test/"
	if os.environ["BYU_PROJECT_DIR"].endswith(test_path) or os.environ["BYU_PROJECT_DIR"].endswith(test_path[:-1]):
		unittest.main()
	else:
		raise EnvironmentError("Cannot run automated tests on live project!!!")
		