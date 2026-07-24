import datetime

FIR_SECTION_MAP = {
    "theft": [("BNS 303", "Theft")],
    "murder": [("BNS 101", "Murder")]
}

def generate_fir(data):
    name = data.get("name")
    incident = data.get("incident")
    incident_type = data.get("incident_type", "").lower()

    sections = FIR_SECTION_MAP.get(incident_type, [("BNS 351", "General offence")])

    date = datetime.datetime.now().strftime("%d-%m-%Y")

    return {
        "fir_text": f"""
FIR REPORT

Name: {name}
Date: {date}

Incident:
{incident}

Applicable Sections:
{sections}
"""
    }