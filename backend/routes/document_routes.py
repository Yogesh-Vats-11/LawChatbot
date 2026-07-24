from flask import Blueprint, request, jsonify, send_file
from utils.pdf_generator import create_pdf
import datetime

document_bp = Blueprint("documents", __name__, url_prefix="/documents")

TEMPLATES = {
    "rent": {
        "name": "Rent Agreement",
        "fields": ["landlord_name", "tenant_name"]
    }
}

DOCUMENT_TEMPLATES = {
    "rent_agreement": {
        "name": "Rent / Lease Agreement",
        "description": "Standard residential rent agreement between landlord and tenant",
        "fields": ["landlord_name", "tenant_name", "property_address",
                   "monthly_rent", "security_deposit", "lease_start",
                   "lease_end", "notice_period_days"],
    },
    "affidavit": {
        "name": "General Affidavit",
        "description": "Sworn affidavit",
        "fields": ["deponent_name", "father_name", "age", "address", "statement"],
    },
    "legal_notice": {
        "name": "Legal Notice",
        "fields": ["sender_name", "sender_address", "recipient_name",
                   "recipient_address", "subject", "facts",
                   "demand", "notice_period_days"],
    },
    "power_of_attorney": {
        "name": "Power of Attorney",
        "fields": ["grantor_name", "grantor_address", "attorney_name",
                   "attorney_address", "purpose", "duration"],
    },
    "partnership_deed": {
        "name": "Partnership Deed",
        "fields": ["firm_name", "partner1_name", "partner2_name",
                   "business_nature", "capital_contribution",
                   "profit_sharing_ratio", "start_date"],
    },
}

@document_bp.route("/templates", methods=["GET"])
def list_templates():
    return jsonify({
        "simple_templates": TEMPLATES,
        "advanced_templates": DOCUMENT_TEMPLATES
    })

def _build_doc(template_type, f, date):

    if template_type == "rent_agreement":
        return f"""
RENT / LEASE AGREEMENT
=======================
Date: {date}

PARTIES
--------
LANDLORD : {f.get('landlord_name', '________________')}
TENANT   : {f.get('tenant_name',   '________________')}

PROPERTY
---------
{f.get('property_address', '________________')}

TERMS
------
Monthly Rent       : ₹{f.get('monthly_rent', '________________')} (payable by 5th of each month)
Security Deposit   : ₹{f.get('security_deposit', '________________')} (refundable at end of tenancy)
Lease Period       : {f.get('lease_start', '________________')} to {f.get('lease_end', '________________')}
Notice Period      : {f.get('notice_period_days', '30')} days written notice required by either party

CONDITIONS
-----------
1. Property shall be used for residential purposes only.
2. Tenant shall not sublet without written consent of Landlord.
3. Minor repairs are the Tenant's responsibility; major repairs are the Landlord's.
4. Tenant shall maintain the property in good condition.
5. Landlord may inspect with 24-hour written notice.

IN WITNESS WHEREOF the parties sign on {date}.

Landlord Signature : ________________   Tenant Signature : ________________
Name               : {f.get('landlord_name','________________')}   Name : {f.get('tenant_name','________________')}

Witness 1 : ________________           Witness 2 : ________________
"""

    if template_type == "affidavit":
        return f"""
AFFIDAVIT
==========
I, {f.get('deponent_name', '________________')},
Son / Daughter of {f.get('father_name', '________________')},
Age: {f.get('age', '___')} years,
Residing at: {f.get('address', '________________')},

do hereby solemnly affirm and declare as under:

1. I am the deponent herein and the facts stated are within my personal knowledge.
2. {f.get('statement', '________________')}
3. Nothing stated above is false and nothing material has been concealed.

DEPONENT
Signature : ________________
Name      : {f.get('deponent_name', '________________')}
Date      : {date}

VERIFICATION
I, the deponent, verify that the contents of this affidavit are true
and correct to the best of my knowledge and belief.

Verified at ________________ on {date}.

Notary / Oath Commissioner : ________________
"""

    if template_type == "legal_notice":
        return f"""
LEGAL NOTICE
=============
Date: {date}

FROM:
{f.get('sender_name', '________________')}
{f.get('sender_address', '________________')}

TO:
{f.get('recipient_name', '________________')}
{f.get('recipient_address', '________________')}

SUBJECT: {f.get('subject', '________________')}

Dear Sir / Madam,

On behalf of and under the instructions of my client
{f.get('sender_name', '________________')}, I hereby issue
you this legal notice on the following facts and grounds:

FACTS
------
{f.get('facts', '________________')}

DEMAND
-------
{f.get('demand', '________________')}

You are hereby called upon to comply with the above demand within
{f.get('notice_period_days', '15')} days from receipt of this notice,
failing which my client shall initiate appropriate legal proceedings
against you entirely at your risk, cost and consequences.

This notice is issued without prejudice to all other rights and
remedies available to my client under law.

Advocate / Authorised Signatory : ________________
For: {f.get('sender_name', '________________')}
"""

    if template_type == "power_of_attorney":
        return f"""
POWER OF ATTORNEY
==================
Date: {date}

KNOW ALL MEN BY THESE PRESENTS that I,
{f.get('grantor_name', '________________')},
residing at {f.get('grantor_address', '________________')},
(hereinafter "Grantor")

hereby appoint and constitute
{f.get('attorney_name', '________________')},
residing at {f.get('attorney_address', '________________')},
(hereinafter "Attorney")

as my true and lawful Attorney to act on my behalf for the following:

PURPOSE
--------
{f.get('purpose', '________________')}

DURATION: {f.get('duration', 'Until revoked in writing')}

My Attorney is hereby authorised to do all acts, deeds, matters and
things as may be necessary for the above purpose, as fully and
effectually as I could do if personally present.

I hereby ratify and confirm all that my Attorney shall lawfully do
by virtue of this Power of Attorney.

GRANTOR Signature  : ________________
Name               : {f.get('grantor_name', '________________')}

ATTORNEY Signature : ________________
Name               : {f.get('attorney_name', '________________')}

Witness 1 : ________________           Witness 2 : ________________
Notarised on : {date}
"""

    if template_type == "partnership_deed":
        return f"""
PARTNERSHIP DEED
=================
Date: {date}

PARTIES
--------
Partner 1 : {f.get('partner1_name', '________________')}
Partner 2 : {f.get('partner2_name', '________________')}

FIRM
-----
Firm Name       : {f.get('firm_name', '________________')}
Nature of Biz   : {f.get('business_nature', '________________')}
Commencement    : {f.get('start_date', date)}

FINANCIAL TERMS
----------------
Capital Contribution  : {f.get('capital_contribution', 'As agreed')}
Profit / Loss Ratio   : {f.get('profit_sharing_ratio', '50 : 50')}

TERMS AND CONDITIONS
---------------------
1. The firm shall operate under the name {f.get('firm_name', '________________')}.
2. Each partner shall devote full time and attention to the firm's business.
3. Proper books of accounts shall be maintained at the principal place of business.
4. Bank accounts shall be operated jointly by both partners.
5. Either partner may retire by giving 30 days written notice to the other.
6. Any dispute shall be referred to arbitration under the Arbitration and
   Conciliation Act, 1996.
7. This deed shall be governed by the Indian Partnership Act, 1932.

IN WITNESS WHEREOF the Partners execute this deed on {date}.

Partner 1 Signature : ________________   Partner 2 Signature : ________________
Name                : {f.get('partner1_name','________________')}   Name : {f.get('partner2_name','________________')}

Witness 1 : ________________            Witness 2 : ________________
"""

    return "Template not found."

@document_bp.route("/generate", methods=["POST"])
def generate_document():
    d = request.json or {}

    tmpl_type = d.get("template_type", "")
    fields = d.get("fields", {})

    if tmpl_type not in DOCUMENT_TEMPLATES:
        return jsonify({
            "error": f"Unknown template type. Available: {list(DOCUMENT_TEMPLATES.keys())}"
        }), 400

    date = datetime.datetime.now().strftime("%d %B %Y")
    doc_text = _build_doc(tmpl_type, fields, date)

    return jsonify({
        "template": DOCUMENT_TEMPLATES[tmpl_type]["name"],
        "document_text": doc_text,
        "generated_on": date,
    })

@document_bp.route("/download_pdf", methods=["POST"])
def download_pdf():
    d = request.json or {}

    doc_text = d.get("document_text", "").strip()
    doc_title = d.get("doc_title", "Legal Document")

    if not doc_text:
        return jsonify({"error": "document_text is required"}), 400

    file = create_pdf(doc_title, doc_text.split("\n"))

    safe_name = doc_title.replace(" ", "_").replace("/", "-") + ".pdf"

    return send_file(
        file,
        as_attachment=True,
        download_name=safe_name,
        mimetype="application/pdf"
    )