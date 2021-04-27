import shortuuid

from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from collections import OrderedDict
from rest_framework.serializers import ValidationError

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

def standar_to_internal_value(self, datos):
    errors = OrderedDict()

    for field in datos:
        validate_method = getattr(self, 'validate_' + field, None)
        try:
            if validate_method:
                datos[field] = validate_method(datos[field])
        except ValidationError as e:
            errors[field] = e.detail
        except Exception as e:
            errors[field] = str(e)
    
    if errors:
        raise ValidationError(errors)
    return datos
