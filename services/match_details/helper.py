async def format_queue(params):
    template_elements = []

    for param in params:
        if type(param) == str:
            template_elements.append("'%s'")
        else:
            template_elements.append("%s")
    return "(" + ", ".join(template_elements) + ")"
