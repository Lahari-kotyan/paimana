/**
 * PAIMANA What-If Predictive Scenario Simulator
 */

const SimulatorEngine = {
  currentProject: null,

  init(projectsList) {
    const selectEl = document.getElementById('sim-project-select');
    if (!selectEl) return;

    selectEl.innerHTML = projectsList.slice(0, 50).map(p => `
      <option value="${p.project_id}">${p.project_name.substring(0, 45)}... (₹${p.revised_cost_cr} Cr)</option>
    `).join('');

    this.currentProject = projectsList[0];
    this.attachListeners();
    this.runSimulation();
  },

  setProject(projectObj) {
    this.currentProject = projectObj;
    const selectEl = document.getElementById('sim-project-select');
    if (selectEl) selectEl.value = projectObj.project_id;
    this.resetSliders();
    this.runSimulation();
  },

  resetSliders() {
    document.getElementById('sim-land-slider').value = 0;
    document.getElementById('sim-land-val').innerText = '0%';
    document.getElementById('sim-delay-slider').value = 0;
    document.getElementById('sim-delay-val').innerText = '+0 Mo';
    document.getElementById('sim-inflation-slider').value = 0;
    document.getElementById('sim-inflation-val').innerText = '+0%';
    document.getElementById('sim-disputes-slider').value = 0;
    document.getElementById('sim-disputes-val').innerText = '+0';
  },

  attachListeners() {
    const selectEl = document.getElementById('sim-project-select');
    selectEl.addEventListener('change', async (e) => {
      const pId = e.target.value;
      const res = await fetch(`/api/projects/${pId}`);
      const data = await res.json();
      this.currentProject = data.project;
      this.resetSliders();
      this.runSimulation();
    });

    const bindSlider = (sliderId, valId, suffix, isSigned = true) => {
      const slider = document.getElementById(sliderId);
      slider.addEventListener('input', (e) => {
        const val = e.target.value;
        const prefix = (isSigned && val > 0) ? '+' : '';
        document.getElementById(valId).innerText = `${prefix}${val}${suffix}`;
        this.runSimulation();
      });
    };

    bindSlider('sim-land-slider', 'sim-land-val', '%');
    bindSlider('sim-delay-slider', 'sim-delay-val', ' Mo');
    bindSlider('sim-inflation-slider', 'sim-inflation-val', '%');
    bindSlider('sim-disputes-slider', 'sim-disputes-val', '');
  },

  async runSimulation() {
    if (!this.currentProject) return;

    const landDelta = parseFloat(document.getElementById('sim-land-slider').value);
    const delayDelta = parseFloat(document.getElementById('sim-delay-slider').value);
    const inflationDelta = parseFloat(document.getElementById('sim-inflation-slider').value);
    const disputeDelta = parseInt(document.getElementById('sim-disputes-slider').value);

    const payload = {
      base_project: this.currentProject,
      adjustments: {
        land_acquired_pct_delta: landDelta,
        additional_delay_months: delayDelta,
        inflation_surge_pct: inflationDelta,
        dispute_count_delta: disputeDelta
      }
    };

    try {
      const res = await fetch('/api/predict/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      this.renderResults(data);
    } catch (err) {
      console.error('Simulation error:', err);
    }
  },

  renderResults(simResult) {
    const orig = simResult.original_project;
    const sim = simResult.simulated_prediction;
    const risk = simResult.simulated_risk;
    const delta = simResult.delta;

    document.getElementById('sim-res-cost-pred').innerText = `₹${sim.predicted_revised_cost_cr.toLocaleString('en-IN')} Cr`;
    document.getElementById('sim-res-cost-pct').innerText = `+${sim.predicted_cost_overrun_pct}% Overrun`;

    const deltaCostEl = document.getElementById('sim-res-cost-delta');
    const costPrefix = delta.cost_overrun_cr_delta >= 0 ? '+₹' : '-₹';
    deltaCostEl.innerText = `${costPrefix}${Math.abs(delta.cost_overrun_cr_delta).toLocaleString('en-IN')} Cr Delta`;
    deltaCostEl.style.color = delta.cost_overrun_cr_delta > 0 ? '#EF4444' : '#10B981';

    document.getElementById('sim-res-delay-pred').innerText = `${sim.predicted_schedule_delay_months} Months`;
    const deltaDelayEl = document.getElementById('sim-res-delay-delta');
    const delPrefix = delta.delay_months_delta >= 0 ? '+' : '';
    deltaDelayEl.innerText = `${delPrefix}${delta.delay_months_delta} Months Shift`;

    const riskScoreEl = document.getElementById('sim-res-risk-score');
    riskScoreEl.innerText = `${risk.composite_risk_score} / 100`;
    riskScoreEl.style.color = risk.risk_color;

    document.getElementById('sim-res-risk-badge').innerText = risk.risk_category.toUpperCase();
    document.getElementById('sim-res-risk-badge').className = `badge badge-${risk.risk_category.toLowerCase()}`;

    // Render Radar in simulation view
    ChartEngine.renderRiskRadar('sim-risk-radar-chart', risk.dimensions);
  }
};
