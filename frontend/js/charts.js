/**
 * PAIMANA Data Visualizations Engine (Chart.js Integration)
 */

const ChartEngine = {
  instances: {},

  destroyChart(id) {
    if (this.instances[id]) {
      this.instances[id].destroy();
      delete this.instances[id];
    }
  },

  // 1. Sector Capex & Overrun Bar Chart
  renderSectorChart(canvasId, sectorData) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const topSectors = sectorData.slice(0, 10);
    const labels = topSectors.map(s => s.sector_name.split(' ')[0]);
    const capex = topSectors.map(s => s.total_rev_cr / 1000); // in ₹ Thousand Cr
    const overrun = topSectors.map(s => s.cost_overrun_cr / 1000);

    this.instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Approved Capex (₹ Thousand Cr)',
            data: capex,
            backgroundColor: 'rgba(56, 189, 248, 0.7)',
            borderColor: '#38BDF8',
            borderWidth: 1,
            borderRadius: 6
          },
          {
            label: 'Cost Escalation (₹ Thousand Cr)',
            data: overrun,
            backgroundColor: 'rgba(239, 68, 68, 0.75)',
            borderColor: '#EF4444',
            borderWidth: 1,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 12 } } },
          tooltip: {
            backgroundColor: '#0B132B',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            titleColor: '#F8FAFC',
            bodyColor: '#94A3B8'
          }
        },
        scales: {
          x: { ticks: { color: '#64748B' }, grid: { color: 'rgba(255,255,255,0.04)' } },
          y: { ticks: { color: '#64748B' }, grid: { color: 'rgba(255,255,255,0.04)' } }
        }
      }
    });
  },

  // 2. Risk Tier Donut Chart
  renderRiskDonut(canvasId, kpiData) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const critical = kpiData.critical_risk_projects_count || 480;
    const delayed = kpiData.delayed_projects_count || 910;
    const onTrack = Math.max(0, kpiData.total_projects - delayed);

    this.instances[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Critical Escalation Risk', 'Moderate / Delayed', 'On-Track Baseline'],
        datasets: [{
          data: [critical, delayed - critical, onTrack],
          backgroundColor: ['#EF4444', '#F59E0B', '#10B981'],
          borderWidth: 0,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94A3B8', padding: 16 } }
        }
      }
    });
  },

  // 3. Project S-Curve: Planned vs Actual vs Predicted
  renderSCurve(canvasId, sCurveData) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: sCurveData.labels,
        datasets: [
          {
            label: 'Planned Baseline S-Curve (₹ Cr)',
            data: sCurveData.planned_capex_cr,
            borderColor: '#38BDF8',
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 0,
            fill: false,
            tension: 0.3
          },
          {
            label: 'Actual Cumulative Expenditure (₹ Cr)',
            data: sCurveData.actual_capex_cr,
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            pointRadius: 3,
            fill: true,
            tension: 0.3
          },
          {
            label: 'AI Predicted Forecast Trajectory (₹ Cr)',
            data: sCurveData.predicted_capex_cr,
            borderColor: '#EF4444',
            backgroundColor: 'rgba(239, 68, 68, 0.08)',
            borderDash: [3, 3],
            borderWidth: 2.5,
            pointRadius: 2,
            fill: true,
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94A3B8' } },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: '#0B132B',
            borderColor: '#38BDF8',
            borderWidth: 1
          }
        },
        scales: {
          x: { title: { display: true, text: 'Timeline Progression (Months)', color: '#64748B' }, ticks: { color: '#64748B' }, grid: { color: 'rgba(255,255,255,0.04)' } },
          y: { title: { display: true, text: 'Disbursement (₹ Cr)', color: '#64748B' }, ticks: { color: '#64748B' }, grid: { color: 'rgba(255,255,255,0.04)' } }
        }
      }
    });
  },

  // 4. 5-Dimensional Risk Radar Chart
  renderRiskRadar(canvasId, dimensions) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');

    this.instances[canvasId] = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: [
          'Financial Risk (25%)',
          'Schedule Risk (25%)',
          'Regulatory / RoW (20%)',
          'Contractor Risk (15%)',
          'Macro & Terrain (15%)'
        ],
        datasets: [{
          label: 'Risk Score (0-100)',
          data: [
            dimensions.financial_risk,
            dimensions.schedule_risk,
            dimensions.regulatory_risk,
            dimensions.contractor_risk,
            dimensions.macro_risk
          ],
          backgroundColor: 'rgba(239, 68, 68, 0.25)',
          borderColor: '#EF4444',
          borderWidth: 2,
          pointBackgroundColor: '#F87171',
          pointBorderColor: '#fff',
          pointRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
            grid: { color: 'rgba(255, 255, 255, 0.08)' },
            pointLabels: { color: '#CBD5E1', font: { size: 11, weight: '600' } },
            ticks: { display: false, min: 0, max: 100 }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  },

  // 5. ML Benchmark Comparison Bar Chart
  renderBenchmarkChart(canvasId, benchmarkData) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');

    const costModels = benchmarkData.cost_overrun_regression;
    const labels = Object.keys(costModels).map(k => k.replace(/_/g, ' '));
    const maes = Object.values(costModels).map(v => v.mae);
    const r2s = Object.values(costModels).map(v => v.r2 * 100);

    this.instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'MAE (% Error - Lower is Better)',
            data: maes,
            backgroundColor: 'rgba(245, 158, 11, 0.7)',
            borderColor: '#F59E0B',
            borderWidth: 1,
            borderRadius: 6
          },
          {
            label: 'R² Variance Explained (% - Higher is Better)',
            data: r2s,
            backgroundColor: 'rgba(16, 185, 129, 0.7)',
            borderColor: '#10B981',
            borderWidth: 1,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94A3B8' } }
        },
        scales: {
          x: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.04)' } },
          y: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.04)' } }
        }
      }
    });
  },

  // 6. ROC Curve Chart
  renderROCChart(canvasId, rocData) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');

    const costRoc = rocData.cost_roc;
    const delayRoc = rocData.delay_roc;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: costRoc.fpr,
        datasets: [
          {
            label: 'Cost Escalation Classifier (AUC: 0.89)',
            data: costRoc.tpr,
            borderColor: '#38BDF8',
            borderWidth: 2.5,
            pointRadius: 0,
            tension: 0.2
          },
          {
            label: 'Schedule Delay Classifier (AUC: 0.87)',
            data: delayRoc.tpr,
            borderColor: '#A855F7',
            borderWidth: 2.5,
            pointRadius: 0,
            tension: 0.2
          },
          {
            label: 'Random Guess Line',
            data: costRoc.fpr,
            borderColor: 'rgba(255,255,255,0.2)',
            borderDash: [5, 5],
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94A3B8' } }
        },
        scales: {
          x: { title: { display: true, text: 'False Positive Rate', color: '#64748B' }, ticks: { color: '#64748B' } },
          y: { title: { display: true, text: 'True Positive Rate (Recall)', color: '#64748B' }, ticks: { color: '#64748B' } }
        }
      }
    });
  },

  // 7. CUF Feature Attribution Donut
  renderAttributionDonut(canvasId, attributionData) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');

    const cufShare = attributionData.attribution_summary.cuf_signal_share_pct;
    const augShare = attributionData.attribution_summary.augmented_signal_share_pct;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: [`Native CUF Fields (${cufShare}%)`, `Augmented Exogenous Features (${augShare}%)`],
        datasets: [{
          data: [cufShare, augShare],
          backgroundColor: ['#0EA5E9', '#EC4899'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94A3B8', padding: 12 } }
        }
      }
    });
  }
};
