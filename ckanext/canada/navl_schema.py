# -*- coding: utf-8 -*-

from pylons.i18n import _
from ckan.plugins.toolkit import get_validator, Invalid, missing
from ckan.new_authz import is_sysadmin
from ckan import model

from ckanext.canada.helpers import may_publish_datasets
from shapely.geometry import asShape
import json
import uuid


tag_name_validator = get_validator('tag_name_validator')

def protect_portal_release_date(key, data, errors, context):
    """
    Ensure the portal_release_date is not changed by an unauthorized user.
    """
    if is_sysadmin(context['user']):
        return
    original = ''
    package = context.get('package')
    if package:
        original = package.extras.get('portal_release_date', '')
    value = data.get(key, '')
    if original == value:
        return

    user = context['user']
    user = model.User.get(user)
    if may_publish_datasets(user):
        return

    if value == '':
        # silently replace with the old value when none is sent
        data[key] = original
        return

    raise Invalid('Cannot change value of key from %s to %s. '
                  'This key is read-only' % (original, value))


def canada_tags(value, context):
    """
    Accept tags with apostrope, convert other apostrophe-like characters
    to straight apostrophe
    """
    value = value.replace(u"´", u"'")
    value = value.replace(u"‘", u"'")
    value = value.replace(u"’", u"'")
    try:
        tag_name_validator(value.replace(u"'", u"-"), {})
        return value
    except Invalid, e:
        e.error = e.error.replace("-_.", "' - _ .")
        raise e


def if_empty_generate_uuid(value):
    """
    Generate a uuid for this dataset early so that it may be
    copied into the name field.
    """
    if not value or value is missing:
        return str(uuid.uuid4())
    return value


def geojson_validator(value):
    if value:
        try:
            gjson = json.loads(value)
            shape = asShape(gjson)
        except ValueError:
            raise Invalid(_("Invalid GeoJSON"))
    return value
