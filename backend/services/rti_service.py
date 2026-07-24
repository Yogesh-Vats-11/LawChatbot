def generate_rti(data):
    return f"""
RTI APPLICATION

Name: {data.get('name')}
Info Requested:
{data.get('info')}
"""