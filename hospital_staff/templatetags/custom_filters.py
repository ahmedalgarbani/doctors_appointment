from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    فلتر للوصول إلى عناصر القاموس باستخدام المفتاح
    مثال: {{ my_dict|get_item:key_var }}
    """
    return dictionary.get(key)
