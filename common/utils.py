import shortuuid

from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType


def generate_uuid():
    """
    Return a random UUID as a string with dashes removed
    Deberia reemplazar el encode(id) ya que es muy corto.
    """
    return shortuuid.uuid()[:8]

def add_log_entry(obj, user, mode, message):
    ct = ContentType.objects.get_for_model(type(obj))
    LogEntry.objects.log_action(
        user_id=user.id,
        content_type_id=ct.pk,
        object_id=obj.pk,
        object_repr=obj.__str__(),
        action_flag=mode,
        change_message=message)
