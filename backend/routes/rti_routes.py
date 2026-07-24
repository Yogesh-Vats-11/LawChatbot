from flask import Blueprint, request, jsonify, send_file
from services.rti_service import generate_rti
from utils.pdf_generator import create_pdf
import datetime

rti_bp = Blueprint("rti", __name__, url_prefix="/rti")

RTI_TIMELINE = [
    {"day": "Day 1",    "action": "File RTI application with the PIO (Public Information Officer)"},
    {"day": "Day 30",   "action": "PIO must respond within 30 days (48 hrs for life/liberty matters)"},
    {"day": "Day 35",   "action": "File First Appeal if no/unsatisfactory response"},
    {"day": "Day 75",   "action": "First Appeal decided within 30–45 days"},
    {"day": "Day 90",   "action": "File Second Appeal with CIC/SIC"},
    {"day": "Ongoing",  "action": "CIC/SIC hears and may impose ₹25,000 penalty"},
]

@rti_bp.route("/guide", methods=["GET"])
def guide():
    return jsonify({
        "title": "RTI Filing Guide — Right to Information Act 2005",
        "overview": "Any Indian citizen can request information from any public authority.",
        "timeline": RTI_TIMELINE,
        "fees": {
            "central": "₹10 — IPO / DD / Court Fee Stamp",
            "state": "Varies by state",
            "bpl": "Free"
        },
        "tips": ["Be specific", "Keep proof", "Use RPAD"],
        "exemptions": ["National security", "Privacy"]
    })

@rti_bp.route("/draft_simple", methods=["POST"])
def draft_simple():
    return jsonify({"rti_text": generate_rti(request.json)})

@rti_bp.route("/draft", methods=["POST"])
def rti_draft():
    d = request.json or {}

    name = d.get("applicant_name", "").strip()
    info = d.get("information_sought", "").strip()

    if not name or not info:
        return jsonify({"error": "applicant_name and information_sought required"}), 400

    address = d.get("applicant_address", "")
    phone = d.get("applicant_phone", "")
    authority = d.get("authority_name", "")
    auth_type = d.get("authority_type", "central")
    period = d.get("period_of_info", "last 3 years")

    fee = "₹10" if auth_type == "central" else "As per state rules"
    date = datetime.datetime.now().strftime("%d %B %Y")

    rti_text = f"""RTI APPLICATION
================
Right to Information Act, 2005 — Section 6

Date: {date}

To,
The Public Information Officer (PIO),
{authority}

Subject: Request for information under the Right to Information Act, 2005

APPLICANT DETAILS
------------------
Name            : {name}
Address         : {address}
Phone           : {phone}
Citizenship     : Indian Citizen

INFORMATION SOUGHT
-------------------
I, {name}, hereby request the following information
under Section 6(1) of the RTI Act, 2005:

{info}

Period of Information Required: {period}

FEE ENCLOSED
-------------
Fee of {fee} is enclosed / paid herewith.

DECLARATION
------------
I hereby state that I am a citizen of India and the information
requested is not covered under Section 8 or 9 of the RTI Act.

I request that the information be provided within 30 days as
mandated by Section 7(1) of the RTI Act, 2005.

If the request is rejected, please provide reasons and the
name and contact of the First Appellate Authority.

Applicant Signature : ________________
Name                : {name}
Date                : {date}

================
SUBMISSION
  Fee required  : {fee}
  Send to       : PIO at {authority or '[Authority Name]'}
  By post       : Registered Post with Acknowledgement Due (RPAD)
  Online        : rtionline.gov.in (Central Govt only)
APPEAL
  First Appeal  : First Appellate Authority, same department
  Second Appeal : Central / State Information Commission
================
"""
    return jsonify({
            "rti_text":      rti_text,
            "fee_required":  fee,
            "authority_type": auth_type,
            "timeline":      RTI_TIMELINE,
            "submission": {
                "in_person": f"PIO office at {authority}",
                "by_post":   "Registered Post with RPAD",
                "online":    "rtionline.gov.in (Central only)",
            },
        })


@rti_bp.route("/download_pdf", methods=["POST"])
def download_pdf():
    text = request.json.get("rti_text", "").strip()

    if not text:
        return jsonify({"error": "rti_text required"}), 400

    file = create_pdf("RTI Draft", text.split("\n"))

    return send_file(
        file,
        as_attachment=True,
        download_name="RTI_Application.pdf",
        mimetype="application/pdf"
    )