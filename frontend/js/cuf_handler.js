/**
 * PAIMANA Common Upload Form (CUF) Ingestion & Validation Handler
 */

const CUFHandler = {
  init() {
    this.attachEventListeners();
  },

  attachEventListeners() {
    const btnSample = document.getElementById('btn-load-sample-cuf');
    if (btnSample) {
      btnSample.addEventListener('click', async () => {
        const res = await fetch('/api/cuf/sample_template');
        const data = await res.json();
        document.getElementById('cuf-json-input').value = JSON.stringify(data, null, 2);
      });
    }

    const btnValidate = document.getElementById('btn-validate-cuf');
    if (btnValidate) {
      btnValidate.addEventListener('click', () => {
        this.validateInput();
      });
    }
  },

  async validateInput() {
    const raw = document.getElementById('cuf-json-input').value.trim();
    if (!raw) {
      alert('Please enter or upload CUF records in JSON format.');
      return;
    }

    let records;
    try {
      records = JSON.parse(raw);
      if (!Array.isArray(records)) {
        records = [records];
      }
    } catch (e) {
      alert('Invalid JSON format: ' + e.message);
      return;
    }

    try {
      const res = await fetch('/api/cuf/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ records: records })
      });
      const data = await res.json();
      this.renderValidationReport(data);
    } catch (err) {
      alert('Validation request failed: ' + err.message);
    }
  },

  renderValidationReport(report) {
    const container = document.getElementById('cuf-validation-results');
    if (!container) return;

    let html = `
      <div style="display: flex; gap: 16px; margin-bottom: 20px;">
        <div style="flex: 1; background: rgba(255,255,255,0.04); padding: 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
          <div style="font-size: 11px; color: #94A3B8;">Total Processed</div>
          <div style="font-size: 22px; font-weight: 800; color: #F8FAFC;">${report.total_submitted}</div>
        </div>
        <div style="flex: 1; background: rgba(16,185,129,0.1); padding: 14px; border-radius: 8px; border: 1px solid rgba(16,185,129,0.3);">
          <div style="font-size: 11px; color: #34D399;">Valid Submissions</div>
          <div style="font-size: 22px; font-weight: 800; color: #10B981;">${report.valid_count}</div>
        </div>
        <div style="flex: 1; background: rgba(239,68,68,0.1); padding: 14px; border-radius: 8px; border: 1px solid rgba(239,68,68,0.3);">
          <div style="font-size: 11px; color: #F87171;">Flagged / Errors</div>
          <div style="font-size: 22px; font-weight: 800; color: #EF4444;">${report.invalid_count}</div>
        </div>
      </div>
      
      <h4 style="font-family: Outfit, sans-serif; font-size: 15px; margin-bottom: 12px; color: #F8FAFC;">AI Audit & Validation Inspection</h4>
    `;

    report.results.forEach(r => {
      const statusBadge = r.is_valid 
        ? '<span class="badge badge-low">PASSED & AUDITED</span>'
        : '<span class="badge badge-critical">SCHEMA VIOLATION</span>';

      html += `
        <div style="background: rgba(15,23,42,0.6); border: 1px solid ${r.is_valid ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.3)'}; border-radius: 10px; padding: 16px; margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-weight: 700; color: #F8FAFC;">Record #${r.record_index}: <code>${r.project_id}</code></div>
            <div>${statusBadge}</div>
          </div>
      `;

      if (r.errors.length > 0) {
        html += `<div style="color: #F87171; font-size: 12px; margin-bottom: 4px;"><strong>Errors:</strong> ${r.errors.join(' | ')}</div>`;
      }

      if (r.warnings.length > 0) {
        html += `<div style="color: #FBBF24; font-size: 12px; margin-bottom: 4px;"><strong>Anomalies:</strong> ${r.warnings.join(' | ')}</div>`;
      }

      if (r.risk_audit && r.ml_prediction) {
        html += `
          <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; gap: 20px; font-size: 12px;">
            <div>AI Risk Index: <strong style="color:${r.risk_audit.risk_color};">${r.risk_audit.composite_risk_score}/100 (${r.risk_audit.risk_category})</strong></div>
            <div>Predicted Cost Escalation: <strong style="color: #38BDF8;">+${r.ml_prediction.predicted_cost_overrun_pct}% (₹${r.ml_prediction.predicted_cost_overrun_cr} Cr)</strong></div>
            <div>Predicted Delay: <strong>${r.ml_prediction.predicted_schedule_delay_months} Months</strong></div>
          </div>
        `;
      }

      html += `</div>`;
    });

    container.innerHTML = html;
  }
};
