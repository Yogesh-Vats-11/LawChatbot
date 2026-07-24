

const API = "http://127.0.0.1:5000";


function go(sectionId) {
    document.querySelectorAll(".panel").forEach(p => p.style.display = "none");
    document.querySelectorAll("nav li").forEach(n => n.classList.remove("active"));
    document.getElementById(sectionId).style.display = "block";
    const navId = "nav-" + sectionId.replace("-section", "");
    const nav = document.getElementById(navId);
    if (nav) nav.classList.add("active");
}

function tab(btn, bodyId) {
    const panel = btn.closest(".panel");
    panel.querySelectorAll(".tab-body").forEach(t => t.style.display = "none");
    panel.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.getElementById(bodyId).style.display = "block";
    btn.classList.add("active");
}


function _addUserMsg(text) {
    const box = document.getElementById("chat-box");
    const d = document.createElement("div");
    d.className = "user-msg";
    d.innerHTML = `<div class="msg-who">You</div><div class="bubble">${text}</div>`;
    box.appendChild(d);
    box.scrollTop = box.scrollHeight;
}

function _addAIMsg(text) {
    const box = document.getElementById("chat-box");
    const d = document.createElement("div");
    d.className = "ai-msg";
    d.innerHTML = `<div class="msg-who">⚖ LegalAI</div><div class="bubble"></div>`;
    box.appendChild(d);
    const bubble = d.querySelector(".bubble");
    let i = 0;
    const tick = () => {
        if (i < text.length) { bubble.textContent += text[i]; i++; setTimeout(tick, 10); }
        box.scrollTop = box.scrollHeight;
    };
    tick();
    return d;
}

function _removeLast() {
    const box = document.getElementById("chat-box");
    if (box.lastChild) box.removeChild(box.lastChild);
}

async function sendMsg() {
    const input = document.getElementById("chat-input");
    const q = input.value.trim();
    if (!q) return;

    const welcome = document.querySelector(".chat-welcome");
    if (welcome) welcome.remove();

    _addUserMsg(q);
    _saveHistory(q);
    input.value = "";
    _addAIMsg("⏳ Searching BNS sections...");

    try {
        const res  = await fetch(`${API}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: q })
        });
        const data = await res.json();
        _removeLast();

        if (!data.results || !data.results.length) {
            _addAIMsg("No relevant BNS section found. Try rephrasing or use the Case Analysis tool.");
            return;
        }

        let reply = `Found ${data.results.length} relevant section(s):\n\n`;
        data.results.forEach(law => {
            reply += `${law.content}\n\n`;
        });
        _addAIMsg(reply);
    } catch {
        _removeLast();
        _addAIMsg("⚠ Backend not responding. Please start: python backend/app.py");
    }
}

function quickAsk(q) {
    document.getElementById("chat-input").value = q;
    sendMsg();
}

function startVoice() {
    try {
        const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        r.lang = "en-IN";
        r.start();
        r.onresult = e => { document.getElementById("chat-input").value = e.results[0][0].transcript; };
    } catch { alert("Voice not supported in this browser."); }
}


function _saveHistory(q) {
    let h = JSON.parse(localStorage.getItem("legalai_h") || "[]");
    h.unshift({ q, t: new Date().toLocaleString("en-IN") });
    localStorage.setItem("legalai_h", JSON.stringify(h.slice(0, 50)));
}

function loadHistory() {
    const h   = JSON.parse(localStorage.getItem("legalai_h") || "[]");
    const box = document.getElementById("history-list");
    if (!box) return;
    if (!h.length) { box.innerHTML = "<p style='color:var(--muted);padding:16px'>No history yet.</p>"; return; }
    box.innerHTML = h.map(item => `
        <div class="hist-item" onclick="quickAsk('${item.q.replace(/'/g, "\\'")}')">
            <span class="hist-q">${item.q}</span>
            <span class="hist-t">${item.t}</span>
        </div>`).join("");
}

function clearHistory() {
    localStorage.removeItem("legalai_h");
    loadHistory();
}


async function analyzeCase() {
    const txt = document.getElementById("case-input").value.trim();
    const out = document.getElementById("case-result");
    if (!txt) return;
    out.innerHTML = "<p style='color:var(--muted)'>⏳ Analyzing...</p>";
    try {
        const res  = await fetch(`${API}/analyze_case`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ case: txt })
        });
        const data = await res.json();
        let html = "<h3>Relevant Laws</h3>";
        (data.relevant_laws || []).forEach(l => {
            html += `<div class="law-card" style="margin-bottom:10px;cursor:default">
                <span class="sec-num">Section ${l.section_number}</span>
                <span class="sec-title" style="font-size:13px;color:var(--text)">${l.section_title}</span>
                <div style="font-size:12px;color:var(--muted);margin-top:5px">${(l.content||"").slice(0,160)}…</div>
            </div>`;
        });
        if (data.related_crimes?.length) {
            html += `<h3>Related Offences</h3><div class="tags">${
                data.related_crimes.map(c => `<span class="tag">${c}</span>`).join("")
            }</div>`;
        }
        out.innerHTML = html;
    } catch { out.innerHTML = "<p style='color:var(--muted)'>Backend not running.</p>"; }
}

let _firText = "";

async function generateFIR() {
    const name     = document.getElementById("fir-name").value.trim();
    const incident = document.getElementById("fir-incident").value.trim();
    if (!name || !incident) { alert("Name and Incident Description are required."); return; }

    const payload = {
        name,
        father_name:      document.getElementById("fir-father").value,
        address:          document.getElementById("fir-address").value,
        phone:            document.getElementById("fir-phone").value,
        incident_type:    document.getElementById("fir-type").value,
        incident_date:    document.getElementById("fir-date").value,
        incident_location:document.getElementById("fir-location").value,
        accused_details:  document.getElementById("fir-accused").value,
        witnesses:        document.getElementById("fir-witnesses").value,
        incident
    };

    try {
        const res  = await fetch(`${API}/fir/assistant`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.error) { alert(data.error); return; }

        _firText = data.fir_text;

        document.getElementById("fir-sections").innerHTML = `
            <h3>Applicable Sections</h3>
            <div class="tags">${(data.applicable_sections || []).map(s =>
                `<span class="tag warn">${s[0]}: ${s[1]}</span>`).join("")}</div>`;

        document.getElementById("fir-text").textContent = data.fir_text;

        document.getElementById("fir-steps").innerHTML = `
            <div class="steps-box">
                <h4>Next Steps</h4>
                <ol>${(data.next_steps || []).map(s => `<li>${s}</li>`).join("")}</ol>
            </div>`;

        document.getElementById("fir-result").style.display = "block";
        document.getElementById("fir-pdf-btn").style.display = "inline-block";
    } catch { alert("Backend not running. Start app.py first."); }
}

async function downloadFIRPDF() {
    if (!_firText) return;
    const res  = await fetch(`${API}/fir/download_pdf`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fir_text: _firText })
    });
    _dl(await res.blob(), "FIR_Draft.pdf");
}


let _rtiText = "";

async function loadRTIGuide() {
    const box = document.getElementById("rti-guide-content");
    if (box.innerHTML.trim()) return;
    try {
        const data = await (await fetch(`${API}/rti/guide`)).json();
        box.innerHTML = `
            <div class="info-card">
                <h4>📖 Overview</h4>
                <p>${data.overview}</p>
            </div>
            <div class="info-card">
                <h4>⏱ 30-Day Timeline</h4>
                <ol>${data.timeline.map(t => `<li><b>${t.day}:</b> ${t.action}</li>`).join("")}</ol>
            </div>
            <div class="info-card">
                <h4>💰 Filing Fees</h4>
                ${Object.entries(data.fees).map(([k,v]) => `<p><b>${k}:</b> ${v}</p>`).join("")}
            </div>
            <div class="info-card">
                <h4>💡 Tips</h4>
                <ul>${data.tips.map(t => `<li>${t}</li>`).join("")}</ul>
            </div>
            <div class="info-card">
                <h4>🚫 Exemptions</h4>
                <ul>${data.exemptions.map(e => `<li>${e}</li>`).join("")}</ul>
            </div>`;
    } catch { box.innerHTML = "<p style='color:var(--muted)'>Backend not running.</p>"; }
}

async function generateRTI() {
    const name = document.getElementById("rti-name").value.trim();
    const info = document.getElementById("rti-info").value.trim();
    if (!name || !info) { alert("Applicant Name and Information Sought are required."); return; }
    try {
        const res  = await fetch(`${API}/rti/draft`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                applicant_name:    name,
                applicant_address: document.getElementById("rti-address").value,
                applicant_phone:   document.getElementById("rti-phone").value,
                authority_name:    document.getElementById("rti-authority").value,
                authority_type:    document.getElementById("rti-type").value,
                information_sought: info,
                period_of_info:    document.getElementById("rti-period").value,
            })
        });
        const data = await res.json();
        _rtiText = data.rti_text;
        document.getElementById("rti-text").textContent = data.rti_text;
        document.getElementById("rti-preview").style.display = "block";
        document.getElementById("rti-pdf-btn").style.display = "inline-block";
    } catch { alert("Backend not running."); }
}

async function downloadRTIPDF() {
    if (!_rtiText) return;
    const res = await fetch(`${API}/rti/download_pdf`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rti_text: _rtiText })
    });
    _dl(await res.blob(), "RTI_Application.pdf");
}


let _ccText = "";

async function loadConsumerGuide() {
    const box = document.getElementById("cc-guide-content");
    if (box.innerHTML.trim()) return;
    try {
        const data = await (await fetch(`${API}/consumer/guide`)).json();
        box.innerHTML = data.court_levels.map(c => `
            <div class="info-card gold-left">
                <h4>🏛 ${c.name}</h4>
                <p><b>Jurisdiction:</b> ${c.jurisdiction}</p>
                <p><b>Fee:</b> ${c.fee}</p>
                <p><b>Time Limit:</b> ${c.time_limit}</p>
            </div>`).join("") + `
            <div class="info-card">
                <h4>📋 Documents Required</h4>
                <ul>${data.documents_required.map(d => `<li>${d}</li>`).join("")}</ul>
            </div>
            <div class="info-card">
                <h4>⚖ Relief Available</h4>
                <ul>${data.relief_available.map(r => `<li>${r}</li>`).join("")}</ul>
            </div>
            <div class="info-card">
                <h4>📌 Important Notes</h4>
                <ul>${data.important_notes.map(n => `<li>${n}</li>`).join("")}</ul>
            </div>`;
    } catch { box.innerHTML = "<p style='color:var(--muted)'>Backend not running.</p>"; }
}

async function generateComplaint() {
    const name  = document.getElementById("cc-name").value.trim();
    const facts = document.getElementById("cc-facts").value.trim();
    if (!name || !facts) { alert("Complainant Name and Facts are required."); return; }
    try {
        const res  = await fetch(`${API}/consumer/complaint`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                complainant_name:    name,
                complainant_address: document.getElementById("cc-address").value,
                opposite_party:      document.getElementById("cc-op").value,
                op_address:          document.getElementById("cc-op-addr").value,
                purchase_date:       document.getElementById("cc-date").value,
                purchase_amount:     document.getElementById("cc-amount").value,
                deficiency_type:     document.getElementById("cc-deficiency").value,
                facts,
                relief_sought:       document.getElementById("cc-relief").value,
            })
        });
        const data = await res.json();
        _ccText = data.complaint_text;
        const c = data.recommended_court;
        document.getElementById("cc-court-banner").innerHTML = `
            <div class="court-banner">
                🏛 <b>${c.name}</b> &nbsp;|&nbsp; ${c.jurisdiction} &nbsp;|&nbsp; Fee: ${c.fee}
            </div>`;
        document.getElementById("cc-text").textContent = data.complaint_text;
        document.getElementById("cc-result").style.display = "block";
        document.getElementById("cc-pdf-btn").style.display = "inline-block";
    } catch { alert("Backend not running."); }
}

async function downloadCCPDF() {
    if (!_ccText) return;
    const res = await fetch(`${API}/consumer/download_pdf`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ complaint_text: _ccText })
    });
    _dl(await res.blob(), "Consumer_Complaint.pdf");
}


let _templates = {}, _currentTmpl = "", _docText = "";

const FIELD_LABELS = {
    landlord_name:"Landlord Name", tenant_name:"Tenant Name",
    property_address:"Property Address", monthly_rent:"Monthly Rent (₹)",
    security_deposit:"Security Deposit (₹)", lease_start:"Lease Start Date",
    lease_end:"Lease End Date", notice_period_days:"Notice Period (days)",
    deponent_name:"Deponent Name", father_name:"Father's Name",
    age:"Age", address:"Address", statement:"Statement",
    sender_name:"Sender Name", sender_address:"Sender Address",
    recipient_name:"Recipient Name", recipient_address:"Recipient Address",
    subject:"Subject", facts:"Facts", demand:"Demand",
    grantor_name:"Grantor Name", grantor_address:"Grantor Address",
    attorney_name:"Attorney Name", attorney_address:"Attorney Address",
    purpose:"Purpose", duration:"Duration",
    firm_name:"Firm Name", partner1_name:"Partner 1 Name",
    partner2_name:"Partner 2 Name", business_nature:"Nature of Business",
    capital_contribution:"Capital Contribution",
    profit_sharing_ratio:"Profit Sharing Ratio", start_date:"Start Date"
};
const LONG_FIELDS = ["statement","facts","demand","purpose"];

async function loadTemplates() {
    const grid = document.getElementById("tmpl-grid");
    if (grid.innerHTML.trim()) return;
    try {
        const data = await (await fetch(`${API}/documents/templates`)).json();
        _templates = {
    ...data.simple_templates,
    ...data.advanced_templates
};
        grid.innerHTML = Object.entries(_templates).map(([key, t]) => `
            <div class="tmpl-card" onclick="openDocForm('${key}')">
                <div class="tmpl-icon">📄</div>
                <div class="tmpl-name">${t.name}</div>
                <div class="tmpl-desc">${t.description}</div>
            </div>`).join("");
    } catch { grid.innerHTML = "<p style='color:var(--muted)'>Backend not running.</p>"; }
}

function openDocForm(key) {
    _currentTmpl = key;
    const t = _templates[key];
    document.getElementById("doc-form-title").textContent = t.name;
    const fieldsDiv = document.getElementById("doc-fields");
    fieldsDiv.innerHTML = t.fields.map(f => `
        <div class="field ${LONG_FIELDS.includes(f) ? 'full-w' : ''}">
            <label>${FIELD_LABELS[f] || f}</label>
            ${LONG_FIELDS.includes(f)
                ? `<textarea id="df-${f}" class="sm-ta" placeholder="${FIELD_LABELS[f]||f}"></textarea>`
                : `<input id="df-${f}" placeholder="${FIELD_LABELS[f]||f}">`}
        </div>`).join("");
    document.getElementById("tmpl-grid").style.display = "none";
    document.getElementById("doc-form").style.display = "block";
    document.getElementById("doc-pdf-btn").style.display = "none";
    document.getElementById("doc-preview").style.display = "none";
}

function hideDocForm() {
    document.getElementById("doc-form").style.display = "none";
    document.getElementById("tmpl-grid").style.display = "grid";
}

async function generateDoc() {
    const t = _templates[_currentTmpl];
    const fields = {};
    t.fields.forEach(f => { const el = document.getElementById(`df-${f}`); if (el) fields[f] = el.value; });
    try {
        const res  = await fetch(`${API}/documents/generate`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ template_type: _currentTmpl, fields })
        });
        const data = await res.json();
        if (data.error) { alert(data.error); return; }
        _docText = data.document_text;
        document.getElementById("doc-text").textContent = data.document_text;
        document.getElementById("doc-preview").style.display = "block";
        document.getElementById("doc-pdf-btn").style.display = "inline-block";
    } catch { alert("Backend not running."); }
}

async function downloadDocPDF() {
    if (!_docText) return;
    const t = _templates[_currentTmpl];
    const res = await fetch(`${API}/documents/download_pdf`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_text: _docText, doc_title: t.name })
    });
    _dl(await res.blob(), `${t.name.replace(/ /g,"_")}.pdf`);
}


function openPlanForm(plan) {
    document.getElementById("api-plan-val").value = plan;
    document.getElementById("api-plan-label").textContent =
        `Register for ${plan.charAt(0).toUpperCase()+plan.slice(1)} Plan`;
    document.getElementById("api-register").style.display = "block";
    document.getElementById("api-register").scrollIntoView({ behavior: "smooth" });
}

async function registerKey() {
    const name  = document.getElementById("api-name").value.trim();
    const email = document.getElementById("api-email").value.trim();
    const plan  = document.getElementById("api-plan-val").value;
    if (!name || !email) { alert("Please enter your name and email."); return; }
    try {
        const res  = await fetch(`${API}/api/register`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, plan })
        });
        const data = await res.json();
        document.getElementById("api-key-val").textContent = data.api_key;
        document.getElementById("api-key-meta").innerHTML = `
            <p style="font-size:13px;margin-bottom:10px">
                ✅ Plan: <b>${data.plan}</b> &nbsp;|&nbsp; Usage: <b>${data.usage}</b>
                &nbsp;|&nbsp; <code style="font-size:12px">X-API-Key: ${data.api_key}</code>
            </p>`;
        document.getElementById("api-snippet").textContent =
`const res = await fetch("${API}/api/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "${data.api_key}"
  },
  body: JSON.stringify({ query: "Punishment for theft?" })
});
const result = await res.json();
console.log(result.results);`;
        document.getElementById("api-register").style.display = "none";
        document.getElementById("api-key-display").style.display = "block";
    } catch { alert("Backend not running."); }
}

function copyKey(btn) {
    navigator.clipboard.writeText(document.getElementById("api-key-val").textContent);
    btn.textContent = "✓ Copied";
    setTimeout(() => btn.textContent = "Copy", 2000);
}

async function loadAPIDocs() {
    const box = document.getElementById("api-docs-content");
    if (box.innerHTML.trim()) return;
    try {
        const data = await (await fetch(`${API}/api/docs`)).json();
        box.innerHTML = Object.entries(data.endpoints).map(([ep, desc]) => {
            const [method, path] = ep.trim().split(" ");
            return `<div class="ep-row">
                <span class="ep-method ep-${method.toLowerCase()}">${method}</span>
                <code class="ep-path">${path}</code>
                <span class="ep-desc">${desc}</span>
            </div>`;
        }).join("");
    } catch {}
}


async function summarize() {
    const text = document.getElementById("judgment-text").value.trim();
    if (!text) return;
    try {
        const res  = await fetch(`${API}/summarize`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        document.getElementById("summary-text").textContent = data.summary;
        document.getElementById("summary-box").style.display = "block";
    } catch { alert("Backend not running."); }
}


let _allSecs = [];

async function loadSections() {
    if (_allSecs.length) return;
    try {
        const data = await (await fetch(`${API}/sections`)).json();
        _allSecs = data.sections;
        _renderSecs(_allSecs);
    } catch {}
}

function _renderSecs(list) {
    document.getElementById("sections-grid").innerHTML = list.map(s => `
        <div class="law-card" onclick="quickAsk('Explain Section ${s.section_number}: ${s.section_title}')">
            <span class="sec-num">§ ${s.section_number}</span>
            <span class="sec-title">${s.section_title}</span>
        </div>`).join("");
}

function filterSections() {
    const q = document.getElementById("sec-search").value.toLowerCase();
    _renderSecs(_allSecs.filter(s =>
        s.section_number.toLowerCase().includes(q) ||
        s.section_title.toLowerCase().includes(q)));
}


function _dl(blob, filename) {
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;

    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
        window.URL.revokeObjectURL(url);
        a.remove();
    }, 100);
}


window.addEventListener("DOMContentLoaded", () => {
    go("chat-section");
    loadHistory();
    const today = new Date().toISOString().slice(0, 10);
    document.querySelectorAll("input[type='date']").forEach(el => { if (!el.value) el.value = today; });
});
