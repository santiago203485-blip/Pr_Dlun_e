from django import template

register = template.Library()


@register.filter
def pesos(valor):
    """Formatea un número como pesos colombianos: 85000 -> $85.000"""
    try:
        return '$' + f'{float(valor):,.0f}'.replace(',', '.')
    except (TypeError, ValueError):
        return valor
