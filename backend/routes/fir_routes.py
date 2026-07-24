from flask import Blueprint, request, jsonify, send_file
from utils.pdf_generator import create_pdf
import datetime

fir_bp = Blueprint("fir", __name__, url_prefix="/fir")

FIR_SECTION_MAP = {
    "theft": [
        ("BNS 303", "Theft — up to 3 years + fine"),
        ("BNS 304", "Theft in dwelling — up to 7 years")
    ],
    "assault": [
        ("BNS 115", "Voluntarily causing hurt — up to 1 year"),
        ("BNS 117", "Voluntarily causing grievous hurt — up to 7 years")
    ],
    "fraud": [
        ("BNS 318", "Cheating — up to 3 years + fine"),
        ("BNS 319", "Cheating by impersonation — up to 5 years")
    ],
    "cybercrime": [
        ("IT Act 66", "Computer related offences"),
        ("IT Act 66C", "Identity theft — up to 3 years + ₹1 lakh fine"),
        ("IT Act 66D", "Cheating by personation using computer")
    ],
    "harassment": [
        ("BNS 351", "Criminal intimidation — up to 2 years"),
        ("BNS 79", "Stalking — up to 3 years (1st offence)")
    ],
    "robbery": [
        ("BNS 309", "Robbery — up to 10 years + fine"),
        ("BNS 310", "Dacoity — up to 10 years / life")
    ],
    "murder": [
        ("BNS 101", "Murder — death or life imprisonment"),
        ("BNS 105", "Culpable homicide not amounting to murder")
    ],
    "domestic_violence": [
        ("DV Act 3", "Physical / sexual / verbal / economic abuse"),
        ("BNS 85", "Cruelty by husband or relatives — up to 3 years")
    ],
}

@fir_bp.route("/assistant", methods=["POST"])
def fir_assistant():
    d = request.json or {}

    name = d.get("name", "").strip()
    incident = d.get("incident", "").strip()

    if not name or not incident:
        return jsonify({"error": "name and incident are required"}), 400

    incident_type = d.get("incident_type", "").lower()
    father_name = d.get("father_name", "")
    address = d.get("address", "")
    phone = d.get("phone", "")
    incident_date = d.get("incident_date", "")
    incident_loc = d.get("incident_location", "")
    accused = d.get("accused_details", "Unknown / not identified")
    witnesses = d.get("witnesses", "None")

    sections_list = FIR_SECTION_MAP.get(
        incident_type,
        [("BNS 351", "General offence — consult a lawyer")]
    )

    date_filed = datetime.datetime.now().strftime("%d-%m-%Y")
    fir_ref = "FIR-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    sec_lines = "\n".join(f"  • {s[0]}: {s[1]}" for s in sections_list)

    fir_text = f"""FIRST INFORMATION REPORT (DRAFT)
===================================
FIR Reference   : {fir_ref}
Date of Filing  : {date_filed}

COMPLAINANT DETAILS
--------------------
Name            : {name}
Father's Name   : {father_name}
Address         : {address}
Phone           : {phone}

INCIDENT DETAILS
-----------------
Type            : {incident_type.upper() or 'NOT SPECIFIED'}
Date            : {incident_date}
Location        : {incident_loc}
Accused         : {accused}
Witnesses       : {witnesses}

INCIDENT DESCRIPTION
---------------------
{incident}

APPLICABLE BNS / LAW SECTIONS
-------------------------------
{sec_lines}

DECLARATION
------------
I, {name}, solemnly declare that the above information is true and
correct to the best of my knowledge. I request the concerned police
station to register this FIR and take necessary legal action.

Complainant Signature : ________________
Date                  : {date_filed}

===================================
WHAT TO DO IF POLICE REFUSE TO REGISTER FIR
  1. Approach the Superintendent of Police (SP) in writing
  2. Send FIR by registered post to SP under Section 173 CrPC
  3. File a private complaint (Section 200 CrPC) before a Magistrate
  4. File a complaint on the National Police Portal: citizenportal.gov.in
===================================
"""

    return jsonify({
            "fir_reference":       fir_ref,
            "fir_text":            fir_text,
            "applicable_sections": sections_list,
            "next_steps": [
                "Visit nearest police station with this draft and valid ID proof",
                "Request a signed copy of the registered FIR",
                "Note down the FIR number for all future correspondence",
                "If police refuse, escalate to SP or Magistrate",
                "Seek legal counsel for serious offences",
            ]
        })


@fir_bp.route("/download_pdf", methods=["POST"])
def download_pdf():
    d = request.json or {}
    fir_text = d.get("fir_text", "").strip()

    if not fir_text:
        return jsonify({"error": "fir_text is required"}), 400

    file_path = create_pdf("FIR Draft", fir_text.split("\n"))

    return send_file(
        file_path,
        as_attachment=True,
        download_name="FIR_Draft.pdf",
        mimetype="application/pdf"
    )