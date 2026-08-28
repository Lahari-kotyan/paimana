/**
 * PAIMANA Main Application Controller & State Manager
 */

const App = {
  state: {
    kpis: {},
    sectors: [],
    ministries: [],
    states: {},
    projects: [],
    alerts: [],
    benchmarks: {},
    cufAttribution: {},
    currentPage: 1,
    totalPages: 1,
    selectedProjectId: null,
    currentFilters: {
      search: '',
      ministry: 'ALL',
      sector: 'ALL',
      state: 'ALL',
      risk_level: 'ALL',
      status: 'ALL',
      sort_by: 'revised_cost_cr',
      sort_order: 'desc'
    }
  },

  async init() {
    console.log("⚡ Starting PAIMANA Application...");
    this.setupNavigation();
    this.setupFilterListeners();
    this.setupModalListeners();
    
    // Load initial data
    await this.loadNationalKPIs();
    await this.loadSectorData();
    await this.loadStateData();
    await this.loadProjects();
    await this.loadAlerts();
    await this.loadBenchmarks();
    
    // Initialize sub-engines
    SimulatorEngine.init(this.state.projects);
    CUFHandler.init();
    AssistantEngine.init();
  },

  setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const tabTarget = item.getAttribute('data-tab');
        
        navItems.forEach(n => n.classList.remove('active'));
        item.classList.add('active');

        document.querySelectorAll('.tab-pane').forEach(pane => {
          pane.classList.remove('active');
        });

        const activePane = document.getElementById(tabTarget);
        if (activePane) {
          activePane.classList.add('active');
        }

        // Trigger chart resizes if necessary
        if (tabTarget === 'tab-benchmarks' && this.state.benchmarks.cost_overrun_regression) {
          ChartEngine.renderBenchmarkChart('benchmark-bar-chart', this.state.benchmarks);
          ChartEngine.renderROCChart('roc-curves-chart', this.state.benchmarks.roc_curves);
          if (this.state.cufAttribution.attribution_summary) {
            ChartEngine.renderAttributionDonut('cuf-attribution-donut', this.state.cufAttribution);
          }
        }
      });
    });
  },

  setupFilterListeners() {
    const searchInput = document.getElementById('project-search-input');
    if (searchInput) {
      let debounceTimer;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          this.state.currentFilters.search = e.target.value;
          this.state.currentPage = 1;
          this.loadProjects();
        }, 300);
      });
    }

    const bindSelect = (id, filterKey) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('change', (e) => {
          this.state.currentFilters[filterKey] = e.target.value;
          this.state.currentPage = 1;
          this.loadProjects();
        });
      }
    };

    bindSelect('filter-ministry', 'ministry');
    bindSelect('filter-sector', 'sector');
    bindSelect('filter-state', 'state');
    bindSelect('filter-risk', 'risk_level');
    bindSelect('filter-sort', 'sort_by');

    // Pagination
    const prevBtn = document.getElementById('btn-prev-page');
    const nextBtn = document.getElementById('btn-next-page');
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (this.state.currentPage > 1) {
          this.state.currentPage--;
          this.loadProjects();
        }
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (this.state.currentPage < this.state.totalPages) {
          this.state.currentPage++;
          this.loadProjects();
        }
      });
    }
  },

  setupModalListeners() {
    // Project Drawer Close
    const closeDrawer = document.getElementById('btn-close-drawer');
    const drawerOverlay = document.getElementById('project-drawer-modal');
    if (closeDrawer && drawerOverlay) {
      closeDrawer.addEventListener('click', () => drawerOverlay.classList.remove('active'));
      drawerOverlay.addEventListener('click', (e) => {
        if (e.target === drawerOverlay) drawerOverlay.classList.remove('active');
      });
    }

    // Brief Modal Close
    const closeBrief = document.getElementById('btn-close-brief');
    const briefModal = document.getElementById('brief-modal');
    if (closeBrief && briefModal) {
      closeBrief.addEventListener('click', () => briefModal.classList.remove('active'));
      briefModal.addEventListener('click', (e) => {
        if (e.target === briefModal) briefModal.classList.remove('active');
      });
    }

    const btnDownloadBrief = document.getElementById('btn-download-brief');
    if (btnDownloadBrief) {
      btnDownloadBrief.addEventListener('click', () => {
        const text = document.getElementById('brief-memo-text').innerText;
        const blob = new Blob([text], { type: 'text/plain' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `MoSPI_IPMD_Escalation_Memo_${this.state.selectedProjectId || 'PRJ'}.txt`;
        a.click();
      });
    }
  },

  // 1. National KPIs
  async loadNationalKPIs() {
    try {
      const res = await fetch('/api/analytics/kpis');
      const data = await res.json();
      this.state.kpis = data;

      document.getElementById('kpi-total-projects').innerText = (data.total_projects).toLocaleString('en-IN');
      document.getElementById('kpi-revised-capex').innerText = `₹${data.total_revised_cost_lakh_cr}L Cr`;
      document.getElementById('kpi-cost-overrun').innerText = `₹${data.total_cost_overrun_lakh_cr}L Cr`;
      document.getElementById('kpi-overrun-pct').innerText = `+${data.aggregate_overrun_pct}%`;
      document.getElementById('kpi-avg-delay').innerText = `${data.average_delay_months} Mo`;
      document.getElementById('kpi-critical-count').innerText = `${data.critical_risk_projects_count} Critical`;
      document.getElementById('kpi-delayed-count').innerText = `${data.delayed_projects_count} Delayed`;

      ChartEngine.renderRiskDonut('risk-donut-chart', data);
    } catch (err) {
      console.error('Failed to load KPIs:', err);
    }
  },

  // 2. Sector Data
  async loadSectorData() {
    try {
      const res = await fetch('/api/analytics/sectors');
      const data = await res.json();
      this.state.sectors = data.sectors;

      ChartEngine.renderSectorChart('sector-bar-chart', data.sectors);
      this.populateSectorSelect(data.sectors);
    } catch (err) {
      console.error('Failed to load sectors:', err);
    }
  },

  populateSectorSelect(sectors) {
    const el = document.getElementById('filter-sector');
    if (!el) return;
    el.innerHTML = '<option value="ALL">All 22 Sectors</option>' + 
      sectors.map(s => `<option value="${s.sector_id}">${s.sector_name}</option>`).join('');
  },

  // 3. State Data & Geo Map
  async loadStateData() {
    try {
      const res = await fetch('/api/analytics/states');
      const data = await res.json();
      this.state.states = data.states;

      MapEngine.initMap('geo-map-container', data.states, (stateName) => {
        // Drill-down filter
        this.state.currentFilters.state = stateName;
        const stateSelect = document.getElementById('filter-state');
        if (stateSelect) stateSelect.value = stateName;
        
        // Switch to Project Explorer tab
        document.querySelector('[data-tab="tab-explorer"]').click();
        this.loadProjects();
      });

      this.populateStateSelect(data.states);
    } catch (err) {
      console.error('Failed to load states:', err);
    }
  },

  populateStateSelect(states) {
    const el = document.getElementById('filter-state');
    if (!el) return;
    el.innerHTML = '<option value="ALL">All States / UTs</option>' +
      Object.keys(states).map(s => `<option value="${s}">${s}</option>`).join('');
  },

  // 4. Projects Table & Pagination
  async loadProjects() {
    try {
      const f = this.state.currentFilters;
      const params = new URLSearchParams({
        page: this.state.currentPage,
        limit: 15,
        sort_by: f.sort_by,
        sort_order: f.sort_order
      });

      if (f.search) params.append('search', f.search);
      if (f.ministry !== 'ALL') params.append('ministry', f.ministry);
      if (f.sector !== 'ALL') params.append('sector', f.sector);
      if (f.state !== 'ALL') params.append('state', f.state);
      if (f.risk_level !== 'ALL') params.append('risk_level', f.risk_level);

      const res = await fetch(`/api/projects?${params.toString()}`);
      const data = await res.json();

      this.state.projects = data.projects;
      this.state.totalPages = data.total_pages;

      document.getElementById('project-results-count').innerText = `Showing ${data.projects.length} of ${data.total} Monitored Projects`;
      document.getElementById('current-page-display').innerText = `Page ${data.page} of ${data.total_pages}`;

      this.renderProjectsTable(data.projects);
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  },

  renderProjectsTable(projects) {
    const tbody = document.getElementById('projects-table-body');
    if (!tbody) return;

    if (projects.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 40px; color: #94A3B8;">No infrastructure projects match the selected filter criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = projects.map(p => {
      const badgeClass = `badge-${p.risk_category ? p.risk_category.toLowerCase() : 'moderate'}`;
      return `
        <tr onclick="App.openProjectDrawer('${p.project_id}')">
          <td>
            <div style="font-weight: 700; color: #F8FAFC;">${p.project_name}</div>
            <div style="font-size: 11px; color: #64748B;"><code>${p.project_id}</code> | ${p.agency_name}</div>
          </td>
          <td><span style="font-weight: 600; color: #BAE6FD;">${p.ministry_code}</span><br/><span style="font-size: 11px; color: #64748B;">${p.sector_name.split(' ')[0]}</span></td>
          <td>${p.state}</td>
          <td>
            <div style="font-weight: 700; color: #F8FAFC;">₹${(p.revised_cost_cr).toLocaleString('en-IN')} Cr</div>
            <div style="font-size: 11px; color: ${p.cost_overrun_cr > 0 ? '#EF4444' : '#10B981'};">
              ${p.cost_overrun_cr > 0 ? `+₹${(p.cost_overrun_cr).toLocaleString('en-IN')} Cr (+${p.cost_overrun_pct}%)` : 'On Budget'}
            </div>
          </td>
          <td>
            <div style="font-weight: 600; color: ${p.schedule_delay_months > 0 ? '#F59E0B' : '#10B981'};">
              ${p.schedule_delay_months > 0 ? `+${p.schedule_delay_months} Months` : 'On Schedule'}
            </div>
            <div style="font-size: 11px; color: #64748B;">DoC: ${p.anticipated_doc}</div>
          </td>
          <td>
            <div style="display: flex; align-items: center; gap: 8px;">
              <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; width: 60px;">
                <div style="width: ${p.physical_progress_pct}%; height: 100%; background: #0EA5E9;"></div>
              </div>
              <span style="font-size: 11px; font-weight: 600;">${p.physical_progress_pct}%</span>
            </div>
          </td>
          <td>
            <span class="badge ${badgeClass}">${p.composite_risk_score}/100</span>
          </td>
        </tr>
      `;
    }).join('');
  },

  // 5. Open Project 360° Drawer
  async openProjectDrawer(projectId) {
    this.state.selectedProjectId = projectId;
    try {
      const res = await fetch(`/api/projects/${projectId}`);
      const data = await res.json();
      const p = data.project;
      const risk = data.risk_evaluation;
      const pred = data.ml_prediction;
      const alerts = data.active_alerts;

      document.getElementById('drawer-project-name').innerText = p.project_name;
      document.getElementById('drawer-project-id').innerText = `${p.project_id} | ${p.ministry_name} | ${p.agency_name}`;

      // Metrics
      document.getElementById('drawer-orig-cost').innerText = `₹${(p.original_cost_cr).toLocaleString('en-IN')} Cr`;
      document.getElementById('drawer-rev-cost').innerText = `₹${(p.revised_cost_cr).toLocaleString('en-IN')} Cr`;
      document.getElementById('drawer-overrun').innerText = `+₹${(p.cost_overrun_cr).toLocaleString('en-IN')} Cr (+${p.cost_overrun_pct}%)`;
      document.getElementById('drawer-exp').innerText = `₹${(p.cumulative_exp_cr).toLocaleString('en-IN')} Cr (${p.financial_progress_pct}%)`;
      document.getElementById('drawer-phys').innerText = `${p.physical_progress_pct}%`;
      document.getElementById('drawer-delay').innerText = `${p.schedule_delay_months} Months (${p.critical_delay_days} Critical Days)`;

      // Risk & AI Predictions
      const riskEl = document.getElementById('drawer-risk-score');
      riskEl.innerText = `${risk.composite_risk_score} / 100 (${risk.risk_category.toUpperCase()})`;
      riskEl.style.color = risk.risk_color;

      document.getElementById('drawer-ai-cost-pred').innerText = `₹${(pred.predicted_revised_cost_cr).toLocaleString('en-IN')} Cr (+${pred.predicted_cost_overrun_pct}%)`;
      document.getElementById('drawer-ai-delay-pred').innerText = `${pred.predicted_schedule_delay_months} Months`;

      // Render Charts
      ChartEngine.renderRiskRadar('drawer-radar-chart', risk.dimensions);

      // Load S-Curve
      const sCurveRes = await fetch(`/api/projects/${projectId}/s_curve`);
      const sCurveData = await sCurveRes.json();
      ChartEngine.renderSCurve('drawer-s-curve-chart', sCurveData);

      // Render Active Alerts list
      const alertsContainer = document.getElementById('drawer-alerts-list');
      if (alerts.length === 0) {
        alertsContainer.innerHTML = `<div style="color: #34D399; font-size: 13px; padding: 12px; background: rgba(16,185,129,0.1); border-radius: 8px;">✓ Project is operating within normal variance parameters. No early warning alarms active.</div>`;
      } else {
        alertsContainer.innerHTML = alerts.map(a => `
          <div style="background: rgba(239,68,68,0.1); border-left: 3px solid #EF4444; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span style="font-weight: 700; color: #F87171; font-size: 13px;">${a.title}</span>
              <span style="font-size: 11px; background: rgba(239,68,68,0.2); color: #FCA5A5; padding: 2px 6px; border-radius: 4px;">${a.severity}</span>
            </div>
            <div style="font-size: 12px; color: #CBD5E1; margin-bottom: 4px;">• <strong>Root Cause:</strong> ${a.root_cause}</div>
            <div style="font-size: 12px; color: #38BDF8;">• <strong>Action:</strong> ${a.prescription}</div>
          </div>
        `).join('');
      }

      // Memo Brief button
      const memoBtn = document.getElementById('btn-generate-memo');
      if (memoBtn) {
        memoBtn.onclick = () => {
          AssistantEngine.loadProjectBrief(projectId);
        };
      }

      // Open in Simulator button
      const simBtn = document.getElementById('btn-open-in-sim');
      if (simBtn) {
        simBtn.onclick = () => {
          document.getElementById('project-drawer-modal').classList.remove('active');
          document.querySelector('[data-tab="tab-simulator"]').click();
          SimulatorEngine.setProject(p);
        };
      }

      document.getElementById('project-drawer-modal').classList.add('active');
    } catch (err) {
      console.error('Failed to open project drawer:', err);
    }
  },

  // 6. Early Warning Alert System (EWAS)
  async loadAlerts() {
    try {
      const res = await fetch('/api/ewas/alerts?limit=50');
      const data = await res.json();
      this.state.alerts = data.alerts;

      document.getElementById('ewas-total-badge').innerText = `${data.total_alerts} Active Alarms`;
      document.getElementById('nav-alert-badge').innerText = data.severity_counts.CRITICAL || 0;

      const tbody = document.getElementById('ewas-table-body');
      if (!tbody) return;

      tbody.innerHTML = data.alerts.map(a => `
        <tr onclick="App.openProjectDrawer('${a.project_id || a.alert_id.split('-')[2]}')">
          <td><span class="badge badge-${a.severity === 'CRITICAL' ? 'critical' : 'moderate'}">${a.severity}</span></td>
          <td>
            <div style="font-weight: 700; color: #F8FAFC;">${a.title}</div>
            <div style="font-size: 11px; color: #38BDF8;">${a.category}</div>
          </td>
          <td>
            <div style="font-weight: 600; color: #F8FAFC;">${a.project_name || 'Project'}</div>
            <div style="font-size: 11px; color: #64748B;">${a.ministry_code} | ${a.state}</div>
          </td>
          <td><div style="font-size: 12px; color: #CBD5E1;">${a.root_cause}</div></td>
          <td><div style="font-size: 12px; color: #BAE6FD;">${a.prescription}</div></td>
          <td><button class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;">Escalate</button></td>
        </tr>
      `).join('');
    } catch (err) {
      console.error('Failed to load alerts:', err);
    }
  },

  // 7. ML Benchmarks & CUF Attribution
  async loadBenchmarks() {
    try {
      const res = await fetch('/api/predict/benchmarks');
      const data = await res.json();
      this.state.benchmarks = data;

      const cufRes = await fetch('/api/predict/cuf_attribution');
      const cufData = await cufRes.json();
      this.state.cufAttribution = cufData;

      // Render Gain KPIs
      const gains = data.ai_gain_summary;
      document.getElementById('bench-cost-gain').innerText = `${gains.cost_mae_reduction_pct}%`;
      document.getElementById('bench-delay-gain').innerText = `${gains.delay_mae_reduction_pct}%`;
      document.getElementById('bench-acc-gain').innerText = `+${gains.classification_accuracy_gain_pct}%`;

      // Render CUF Attribution Rankings
      const rankContainer = document.getElementById('cuf-rankings-list');
      if (rankContainer && cufData.feature_importance_rankings) {
        rankContainer.innerHTML = cufData.feature_importance_rankings.slice(0, 10).map((f, idx) => `
          <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 12px; font-weight: 700; color: #64748B;">#${idx + 1}</span>
              <span style="font-size: 13px; font-weight: 600; color: #F8FAFC;">${f.feature.replace(/_/g, ' ')}</span>
              <span style="font-size: 10px; padding: 2px 6px; border-radius: 4px; background: ${f.is_cuf ? 'rgba(14,165,233,0.15)' : 'rgba(236,72,153,0.15)'}; color: ${f.is_cuf ? '#38BDF8' : '#F472B6'};">
                ${f.source}
              </span>
            </div>
            <div style="font-weight: 700; color: #38BDF8; font-size: 13px;">${f.importance_pct}%</div>
          </div>
        `).join('');
      }
    } catch (err) {
      console.error('Failed to load benchmarks:', err);
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
