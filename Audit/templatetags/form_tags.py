from django import template

register = template.Library()

@register.filter
def add_attr(field, attr_string):
    """Dodaje atrybuty do widgetu w formacie 'key1:value1; key2:value2'"""
    attrs = {}
    for attr in attr_string.split(';'):
        attr = attr.strip()
        if not attr:
            continue
        key, value = attr.split(':', 1)
        attrs[key.strip()] = value.strip()
    return field.as_widget(attrs=attrs)
