/**
 * PAIMANA Interactive Geo-Spatial India Risk Map
 */

const MapEngine = {
  stateData: {},

  initMap(containerId, statesObj, onStateClick) {
    this.stateData = statesObj;
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      <div class="geo-map-wrapper" style="position: relative; width: 100%; height: 480px; background: rgba(10, 16, 30, 0.4); border-radius: 12px; overflow: hidden; display: flex;">
        <div id="india-svg-container" style="flex: 1; height: 100%; position: relative; display: flex; align-items: center; justify-content: center;">
          <!-- SVG Vector Representation of India Regions & Strategic Hubs -->
          <svg viewBox="0 0 600 650" style="width: 100%; height: 100%; max-height: 480px;">
            <defs>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>
            
            <!-- Map Background Ambient Rings -->
            <circle cx="300" cy="330" r="220" fill="none" stroke="rgba(56, 189, 248, 0.05)" stroke-dasharray="6,6" />
            <circle cx="300" cy="330" r="160" fill="none" stroke="rgba(56, 189, 248, 0.08)" stroke-dasharray="4,4" />

            <!-- Dynamic State Nodes / Geo Pins -->
            <g id="state-pins-group"></g>
          </svg>
        </div>
        
        <!-- Map Sidebar / Info Card -->
        <div id="state-info-panel" style="width: 320px; border-left: 1px solid rgba(255,255,255,0.08); padding: 20px; display: flex; flex-direction: column; justify-content: space-between; background: rgba(15,23,42,0.7); backdrop-filter: blur(10px);">
          <div>
            <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #38BDF8; font-weight: 700;">Geo-Spatial Surveillance</span>
            <h3 id="map-state-title" style="font-family: Outfit, sans-serif; font-size: 20px; color: #F8FAFC; margin-top: 4px;">National Infrastructure Grid</h3>
            <p id="map-state-sub" style="font-size: 12px; color: #94A3B8; margin-bottom: 20px;">Pan-India Monitored Portfolio (1,981 Projects)</p>
            
            <div style="display: flex; flex-direction: column; gap: 12px;">
              <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="font-size: 11px; color: #94A3B8;">Monitored Projects</div>
                <div id="map-state-projects" style="font-size: 22px; font-weight: 800; color: #F8FAFC;">1,981</div>
              </div>
              
              <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="font-size: 11px; color: #94A3B8;">Total Capex Allocation</div>
                <div id="map-state-capex" style="font-size: 20px; font-weight: 800; color: #38BDF8;">₹42.78 Lakh Cr</div>
              </div>
              
              <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="font-size: 11px; color: #94A3B8;">Average Composite Risk Score</div>
                <div id="map-state-risk" style="font-size: 20px; font-weight: 800; color: #F59E0B;">48.2 / 100</div>
              </div>
            </div>
          </div>
          
          <button id="btn-drilldown-state" class="btn btn-primary" style="width: 100%; justify-content: center; margin-top: 16px;">
            Explore State Projects
          </button>
        </div>
      </div>
    `;

    this.renderStatePins(statesObj, onStateClick);
  },

  renderStatePins(statesObj, onStateClick) {
    const pinsGroup = document.getElementById('state-pins-group');
    if (!pinsGroup) return;

    let pinsHTML = '';

    // Convert lat/lng to SVG coords (India approx bbox: Lat 8-36N, Lng 68-96E)
    Object.values(statesObj).forEach(st => {
      if (st.state_name === "Multi-State / National") return;
      
      const x = ((st.lng - 68.0) / (98.0 - 68.0)) * 520 + 40;
      const y = ((37.0 - st.lat) / (37.0 - 8.0)) * 540 + 40;

      const color = st.risk_color;
      const r = Math.min(18, Math.max(7, Math.sqrt(st.project_count) * 1.5));

      pinsHTML += `
        <g class="map-pin-node" data-state="${st.state_name}" style="cursor: pointer;">
          <!-- Pulse halo -->
          <circle cx="${x}" cy="${y}" r="${r + 6}" fill="${color}" opacity="0.15">
            <animate attributeName="r" values="${r + 4};${r + 14};${r + 4}" dur="2.5s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.3;0;0.3" dur="2.5s" repeatCount="indefinite" />
          </circle>
          <!-- Center Pin -->
          <circle cx="${x}" cy="${y}" r="${r}" fill="${color}" stroke="#FFFFFF" stroke-width="1.5" filter="url(#glow)" />
          <text x="${x}" y="${y + 3}" fill="#FFFFFF" font-size="9" font-weight="700" text-anchor="middle" font-family="Plus Jakarta Sans">${st.code}</text>
        </g>
      `;
    });

    pinsGroup.innerHTML = pinsHTML;

    // Attach click and hover listeners
    document.querySelectorAll('.map-pin-node').forEach(node => {
      const stateName = node.getAttribute('data-state');
      const st = this.stateData[stateName];

      node.addEventListener('mouseenter', () => {
        this.updateStatePanel(st);
      });

      node.addEventListener('click', () => {
        this.updateStatePanel(st);
        if (onStateClick) {
          onStateClick(stateName);
        }
      });
    });

    const drillBtn = document.getElementById('btn-drilldown-state');
    if (drillBtn) {
      drillBtn.addEventListener('click', () => {
        const title = document.getElementById('map-state-title').innerText;
        if (title !== "National Infrastructure Grid" && onStateClick) {
          onStateClick(title);
        }
      });
    }
  },

  updateStatePanel(st) {
    if (!st) return;
    document.getElementById('map-state-title').innerText = st.state_name;
    document.getElementById('map-state-sub').innerText = `Region: ${st.region} India | Code: ${st.code}`;
    document.getElementById('map-state-projects').innerText = `${st.project_count} Projects`;
    document.getElementById('map-state-capex').innerText = `₹${(st.total_rev_cr).toLocaleString('en-IN')} Cr (+${st.cost_overrun_pct}% Overrun)`;
    
    const riskEl = document.getElementById('map-state-risk');
    riskEl.innerText = `${st.composite_risk_score} / 100`;
    riskEl.style.color = st.risk_color;
  }
};
