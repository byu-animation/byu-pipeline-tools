import os
import shutil

from .environment import Environment
from . import pipeline_io

"""
element module
"""

class Element:
    """
    Abstract class describing elements that make up an asset or shot body.
    """
    PIPELINE_FILENAME = ".element"

    NAME = "name"
    PARENT_NAME = "parent_name"
    DEPARTMENT = "department"
    STATUS = "status"
    LATEST_VERSION = "latest_version"
    ASSIGNED_USER = "assigned_user"
    START_DATE = "start_date"
    END_DATE = "end_date"
    APP_EXT = "app_ext"
    CACHE_EXT = "cache_ext"
    CHECKOUT_USERS = "checkout_users"

    @staticmethod
    def create_new_dict(name, department, parent_name):
        """
        populate a dictionary with defaults for all the fields needed to create a new element
        """
        datadict = {}
        datadict[Element.NAME] = name
        datadict[Element.PARENT_NAME] = parent_name
        datadict[Element.DEPARTMENT] = department
        datadict[Element.STATUS] = "WAIT" # TODO: status enumeration?
        datadict[Element.LATEST_VERSION] = 0
        datadict[Element.ASSIGNED_USER] = ""
        datadict[Element.START_DATE] = ""
        datadict[Element.END_DATE] = ""
        datadict[Element.APP_EXT] = ""
        datadict[Element.CACHE_EXT] = ""
        datadict[Element.CHECKOUT_USERS] = []
        return datadict

    def __init__(self, filepath=None):
        """
        create an element instance describing the element stored in the given filepath
        """
        self._env = Environment()
        if filepath is not None:
            self.load_pipeline_file(filepath)
        else:
            self._filepath = None
            self._pipeline_file = None
            self._datadict = None

    def load_pipeline_file(self, filepath):
        """
        load the pipeline file that describes this element
        """
        self._filepath = filepath
        self._pipeline_file = os.path.join(filepath, Element.PIPELINE_FILENAME)
        if not os.path.exists(self._pipeline_file):
            raise EnvironmentError("not a valid element: " + self._pipeline_file + " does not exist")
        self._datadict = pipeline_io.readfile(self._pipeline_file)

    def _update_pipeline_file(self):

        pipeline_io.writefile(self._pipeline_file, self._datadict)

    def get_name(self):

        return self._datadict[Element.NAME]

    def get_parent_name(self):

        return self._datadict[Element.PARENT_NAME]

    def get_dir(self):
        """
        return the directory all data for this element is stored in
        """
        return self._filepath

    def get_department(self):

        return self._datadict[Element.DEPARTMENT]

    def get_status(self):

        return self._datadict[Element.STATUS]

    def get_assigned_user(self):

        return self._datadict[Element.ASSIGNED_USER]

    def get_start_date(self):

        return self._datadict[Element.START_DATE]

    def get_end_date(self):

        return self._datadict[Element.END_DATE]

    def get_app_ext(self):
        """
        return the extension of the application files for this element (including the period)
        e.g. the result for an element that uses maya would return ".mb"
        """
        return self._datadict[Element.APP_EXT]

    def get_app_filename(self):
        """
        return the name of the application file for this element. This is just the basename
        of the file, not the absolute filepath.
        """
        return self.get_name()+self.get_app_ext()

    def get_app_file(self):
        """
        return a string containing the absolute filepath for the application file of this element
        """
        filename = self.get_app_filename()
        return os.path.join(self._filepath, filename)

    def get_cache_ext(self):
        """
        return the extension of the cache files for this element (including the period)
        e.g. the result for an element that uses alembic caches would return ".abc"
        """
        return self._datadict[Element.CACHE_EXT]

    def get_cache_location(self):

        raise NotImplementedError('subclass must implement get_cache_location')       

    def get_checkout_users(self):
        """
        return a list of all users who have checked out this element
        """
        return self._datadict[Element.CHECKOUT_USERS]

    def update_assigned_user(self, user):
        """
        Update the user assigned to this element.
        user -- the new user to be assigned
        """
        self._datadict[Element.ASSIGNED_USER] = user
        self._update_pipeline_file()

    def update_start_date(self, date):
        """
        Update the start date of this element.
        date -- the new start date
        """
        self._datadict[Element.START_DATE] = date
        self._update_pipeline_file()

    def update_end_date(self, date):
        """
        Update the end date of this element.
        date -- the new end date
        """
        self._datadict[Element.END_DATE] = date
        self._update_pipeline_file()

    def update_checkout_users(self, user):
        """
        add the given user to the checkout_users list, if they aren't already in it.
        """
        if user not in self._datadict[Element.CHECKOUT_USERS]:
            self._datadict[Element.CHECKOUT_USERS].append(user)
            self._update_pipeline_file()

    def version_up(self, date):
        """
        Increment this element's latest version
        """
        self._datadict[Element.LATEST_VERSION] += 1
        self._update_pipeline_file()
        # TODO: create new version of the element and update stable reference
        return self._datadict[Element.LATEST_VERSION]

    def replace_app_file(self, src, user):
        """
        Replace the applcation file of this element. Create a new version with the new file.
        src -- the file to be placed in the new version
        user -- the user performing this action
        """
        raise NotImplementedError('subclass must implement update_file')

    def replace_cache(self, src, user):
        """
        Replace the cache of this element. Create a new version with the new cache.
        src -- the cache to be placed in the new version
        user -- the user performing this action
        """
        raise NotImplementedError('subclass must implement update_cache')

    def create_new_app_file(self, location):
        """
        creates a new empty file for this element at the given location.
        """
        raise NotImplementedError('subclass must implement create_new_app_file')

    def checkout(self, user):
        """
        Copies the element to the given user's work area in a directory with the following name:
            {the parent body's name}_{this element's name} 
        Returns the absolute filepath to the copied file. Adds user to the list of checkout users.
        """
        app_file = self.get_app_file()
        if not os.path.exists(app_file):
            self.create_new_app_file(app_file)
        checkout_dir = os.path.join(self._env.get_users_dir(), user, self.get_parent_name()+"_"+self.get_department()) # TODO: decide on convention for checkout directories
        pipeline_io.mkdir(checkout_dir)
        checkout_filename = self.get_app_filename()
        checkout_file = pipeline_io.version_file(os.path.join(checkout_dir, checkout_filename))
        shutil.copyfile(app_file, checkout_file)
        self.update_checkout_users(user)
        return checkout_file


class ShotElement(Element):
    """
    Abstract class describing elements that make up a shot.
    """


class AssetElement(Element):
    """
    Abstract class describing elements that make up an asset.
    """

