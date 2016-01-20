import os

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
    def create_new_dict(name="", department=""):
        """
        populate a dictionary with defaults for all the fields needed to create a new element
        """
        datadict = {}
        datadict[Element.NAME] = name
        datadict[Element.DEPARTMENT] = department
        datadict[Element.STATUS] = "WAIT"
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

    def __update_pipeline_file(self):

        pipeline_io.writefile(self._pipeline_file, self._datadict)

    def get_name(self):

        return self._datadict[Element.NAME]

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

    def get_application_ext(self):
        """
        return the extension of the application files for this element (including the period)
        e.g. the result for an element that uses maya would return ".mb"
        """
        return self._datadict[Element.APP_EXT]

    def get_app_file_location(self):

        directory = os.path.join(self.get_dir(), self.get_department(), self.get_name())
        filename = get_name() + get_application_ext()
        return os.path.join(directory, filename)

    def get_cache_ext(self):
        """
        return the extension of the cache files for this element (including the period)
        e.g. the result for an element that uses alembic caches would return ".abc"
        """
        return self._datadict[Element.CACHE_EXT]

    def get_cache_location(self):

        raise NotImplementedError('subclass must implement get_cache_location')       

    def update_assigned_user(self, user):
        """
        Update the user assigned to this element.
        user -- the new user to be assigned
        """
        self._datadict[Element.ASSIGNED_USER] = user
        self.__update_pipeline_file()

    def update_start_date(self, date):
        """
        Update the start date of this element.
        date -- the new start date
        """
        self._datadict[Element.START_DATE] = date
        self.__update_pipeline_file()

    def update_end_date(self, date):
        """
        Update the end date of this element.
        date -- the new end date
        """
        self._datadict[Element.END_DATE] = date
        self.__update_pipeline_file()

    def version_up(self, date):
        """
        Increment this element's latest version
        """
        self._datadict[Element.LATEST_VERSION] += 1
        self.__update_pipeline_file()
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


class ShotElement(Element):
    """
    Abstract class describing elements that make up a shot.
    """


class AssetElement(Element):
    """
    Abstract class describing elements that make up an asset.
    """

