from .. import main


@main.route('/', methods=['GET'])
def get_index():
    return "Delivery", 200
