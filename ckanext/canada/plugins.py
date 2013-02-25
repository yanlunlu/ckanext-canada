import ckan.plugins as p
from ckan.lib.plugins import DefaultDatasetForm
import ckan.logic.schema as ckan_schema
from ckan.lib.base import c, model
import ckan.logic as logic
import ckan.logic.schema as ckan_schema
import ckan.lib.plugins as lib_plugins
from ckan.logic.converters import convert_from_extras, convert_to_extras
from ckan.lib.navl.validators import ignore_missing
from ckan.plugins import toolkit

from ckanext.canada.metadata_schema import schema_description

class DataGCCAPublic(p.SingletonPlugin):
    """
    Plugin for public-facing version of data.gc.ca site, aka the "portal"
    This plugin requires the DataGCCAForms plugin
    """
    p.implements(p.IConfigurer)

    def update_config(self, config):
        # add our templates
        p.toolkit.add_template_directory(config, 'templates/public')
        p.toolkit.add_public_directory(config, 'public')

class DataGCCAInternal(p.SingletonPlugin):
    """
    Plugin for internal version of data.gc.ca site, aka the "registry"
    This plugin requires the DataGCCAPublic and DataGCCAForms plugins
    """
    p.implements(p.IConfigurer)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates/internal')


class DataGCCAForms(p.SingletonPlugin, DefaultDatasetForm):
    """
    Plugin for dataset forms for Canada's metadata schema
    """
    p.implements(p.IDatasetForm, inherit=True)

    def is_fallback(self):
        """
        Return True to register this plugin as the default handler for
        package types not handled by any other IDatasetForm plugin.
        """
        return True

    def package_types(self):
        """
        This plugin doesn't handle any special package types, it just
        registers itself as the default (above).
        """
        return []
    
    def form_to_db_schema(self):
        """
        Add our custom fields for validation from the form
        """
        schema = super(DataGCCAForms, self).form_to_db_schema()
        self._schema_update(schema, form_to_db=True)
        return schema

    def db_to_form_schema(self):
        """
        Add our custom fields for converting from the db
        """
        schema = super(DataGCCAForms, self).db_to_form_schema()
        self._schema_update(schema, form_to_db=False)
        return schema

    def _schema_update(self, schema, form_to_db):
        """
        schema: schema dict to update
        form_to_db: True for form_to_db_schema, False for db_to_form_schema
        """
        for name, lang, field in schema_description.dataset_fields_by_ckan_id():
            if name in ('id', 'language'):
                continue
            if name in schema:
                continue
            if form_to_db:
                schema[name] = [unicode, ignore_missing, convert_to_extras]
            else:
                schema[name] = [convert_from_extras, ignore_missing]
        for name in ('maintainer', 'author', 'author_email',
                'maintainer_email', 'license_id', 'department_number'):
            del schema[name]



    def setup_template_variables(self, context, data_dict=None):
        """
        Add variables to c just prior to the template being rendered.
        """
        DefaultDatasetForm.setup_template_variables(self, context, data_dict)

        toolkit.c.schema_description = schema_description


