from flask import Blueprint, request, jsonify, send_file
from services.consumer_service import generate_consumer
from utils.pdf_generator import create_pdf
import datetime

consumer_bp = Blueprint("consumer", __name__, url_prefix="/consumer")

CONSUMER_COURTS = [
    {"name": "District Consumer Disputes Redressal Commission",
     "jurisdiction": "Claims up to ₹1 crore",
     "fee": "₹200 — ₹4,000",
     "time_limit": "Within 2 years of deficiency"},
    {"name": "State Consumer Disputes Redressal Commission",
     "jurisdiction": "Claims ₹1 crore to ₹10 crore",
     "fee": "₹4,000 — ₹8,000",
     "time_limit": "Within 30 days of District order"},
    {"name": "National Consumer Disputes Redressal Commission",
     "jurisdiction": "Claims above ₹10 crore",
     "fee": "₹8,000 — ₹15,000",
     "time_limit": "Within 30 days of State order"},
]

@consumer_bp.route("/guide", methods=["GET"])
def guide():
    return jsonify({
        "title": "Consumer Court Guide — Consumer Protection Act 2019",
        "court_levels": CONSUMER_COURTS,
        "deficiency_types": [
            "Defective product / goods",
            "Deficiency in service (banking, insurance, telecom, medical)",
            "Unfair trade practice",
            "Overcharging / misleading pricing",
            "Non-delivery of goods or services",
            "Medical negligence",
            "Builder / real estate fraud",
            "E-commerce fraud",
        ],
        "documents_required": [
            "Complaint in prescribed format",
            "Proof of purchase (bill / invoice / receipt)",
            "Warranty / guarantee card (if applicable)",
            "All communication with seller / service provider",
            "Medical records (for medical negligence cases)",
            "Expert report (for defective goods)",
            "ID and address proof",
            "Court fee (varies by claim amount)",
        ],
        "relief_available": [
            "Refund of price paid",
            "Replacement of defective goods",
            "Removal of deficiency in service",
            "Compensation for loss / injury / mental agony",
            "Punitive damages",
            "Cost of litigation",
        ],
        "important_notes": [
            "Complaint must be filed within 2 years of cause of action",
            "No lawyer required at District Commission level",
            "Online filing at edaakhil.nic.in",
            "Video conferencing hearings available",
            "Mediation available before formal hearing",
        ],
    })

@consumer_bp.route("/complaint_simple", methods=["POST"])
def complaint_simple():
    return jsonify({
        "complaint_text": generate_consumer(request.json)
    })

@consumer_bp.route("/complaint", methods=["POST"])
def consumer_complaint():
    d = request.json or {}

    name = d.get("complainant_name", "").strip()
    facts = d.get("facts", "").strip()

    if not name or not facts:
        return jsonify({"error": "complainant_name and facts are required"}), 400

    complainant_address = d.get("complainant_address", "")
    op_name = d.get("opposite_party", "")
    op_address = d.get("op_address", "")
    purchase_date = d.get("purchase_date", "")
    deficiency = d.get("deficiency_type", "")
    relief_sought = d.get("relief_sought", "")

    try:
        amount = float(str(d.get("purchase_amount", "0")).replace(",", "").replace("₹", ""))
    except:
        amount = 0

    if amount <= 10_000_000:
        court = CONSUMER_COURTS[0]
    elif amount <= 100_000_000:
        court = CONSUMER_COURTS[1]
    else:
        court = CONSUMER_COURTS[2]

    date = datetime.datetime.now().strftime("%d %B %Y")
    case_ref = "CC-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    complaint_text = f"""CONSUMER COMPLAINT
====================
Consumer Protection Act, 2019 — Section 35

Case Reference : {case_ref}
Date           : {date}

Before the {court['name']}

COMPLAINANT
{name}
{complainant_address}
                                      ...Complainant

VERSUS

OPPOSITE PARTY
{op_name}
{op_address}
                                      ...Opposite Party

COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019

FACTS OF THE CASE
------------------
1. The Complainant purchased / availed {deficiency or 'goods/services'} from the
   Opposite Party on {purchase_date} for consideration of ₹{d.get('purchase_amount','___')}.

2. {facts}

3. The Complainant brought the matter to the attention of the Opposite
   Party but received no satisfactory response / remedy.

CAUSE OF ACTION
----------------
The cause of action arose on {purchase_date} and continues to subsist
due to the Opposite Party's failure to redress the grievance.

RELIEF SOUGHT
--------------
The Complainant respectfully prays that this Hon'ble Commission:

{relief_sought or '(a) Direct refund of amount.'}

(b) Compensation for mental agony.
(c) Cost of complaint.

DECLARATION
------------
I, {name}, declare that the above is true.

Signature : __________
Date      : {date}

====================
FILE AT    : {court['name']}
JURISDICTION: {court['jurisdiction']}
COURT FEE  : {court['fee']}
ONLINE     : edaakhil.nic.in
====================
"""

    return jsonify({
        "case_reference": case_ref,
        "complaint_text": complaint_text,
        "recommended_court": court,
        "next_steps": [
            f"File at {court['name']}",
            f"Pay fee: {court['fee']}",
            "Attach documents",
            "File online at edaakhil.nic.in"
        ],
    })

@consumer_bp.route("/download_pdf", methods=["POST"])
def download_pdf():
    d = request.json or {}
    complaint_text = d.get("complaint_text", "").strip()

    if not complaint_text:
        return jsonify({"error": "complaint_text is required"}), 400

    file = create_pdf("Consumer Complaint", complaint_text.split("\n"))

    return send_file(
        file,
        as_attachment=True,
        download_name="Consumer_Complaint.pdf",
        mimetype="application/pdf"
    )