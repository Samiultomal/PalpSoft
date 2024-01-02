import uuid

def generate_barcode():
    barcode_value = str(uuid.uuid4().hex)[:20]
    return barcode_value
