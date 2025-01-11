from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0  # Return 0 if multiplication fails
