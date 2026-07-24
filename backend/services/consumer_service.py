def generate_consumer(data):
    return f"""
Consumer Complaint

{data.get('name')} complains about:
{data.get('issue')}
"""