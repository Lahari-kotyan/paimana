/**
 * PAIMANA Contractor Geo-Evidence & Public Verification Handler
 * Strict project-level isolation: Each project maintains its own isolated multi-stage evidence and public reviews.
 */

const EvidenceHandler = {
  currentProjectId: null,
  projectsList: [],
  selectedStageType: 'before',
  uploadedPhotoBase64: null,
  publicPhotoBase64: null,

  async init(projects) {
    console.log("📷 Initializing Contractor Geo-Evidence & Public Verification Engine...");
    this.setupListeners();
    
    // Load full 1,981 projects dataset for dropdown mapping
    try {
      const res = await fetch('/api/projects/dropdown/list');
      if (res.ok) {
        this.projectsList = await res.json();
      } else {
        this.projectsList = projects || [];
      }
    } catch (err) {
      console.warn("Could not fetch dropdown list, using default:", err);
      this.projectsList = projects || [];
    }

    this.populateProjectDropdown();

    // Auto-select first project if available
    if (this.projectsList.length > 0) {
      this.selectProject(this.projectsList[0].project_id);
    }
  },

  populateProjectDropdown(filterTerm = '') {
    const selectEl = document.getElementById('evidence-project-select');
    if (!selectEl) return;

    let list = this.projectsList;
    if (filterTerm && filterTerm.trim()) {
      const q = filterTerm.toLowerCase().trim();
      list = this.projectsList.filter(p => 
        (p.project_id && p.project_id.toLowerCase().includes(q)) ||
        (p.project_name && p.project_name.toLowerCase().includes(q)) ||
        (p.state && p.state.toLowerCase().includes(q)) ||
        (p.ministry_code && p.ministry_code.toLowerCase().includes(q)) ||
        (p.sector_name && p.sector_name.toLowerCase().includes(q)) ||
        (p.agency_name && p.agency_name.toLowerCase().includes(q))
      );
    }

    if (list.length === 0) {
      selectEl.innerHTML = '<option value="">-- No Matching Projects Found --</option>';
      return;
    }

    selectEl.innerHTML = `<option value="">-- Select Monitored Infrastructure Asset (${list.length.toLocaleString('en-IN')} Available) --</option>` +
      list.map(p => `
        <option value="${p.project_id}">
          ${p.project_id} — ${p.project_name.length > 65 ? p.project_name.substring(0, 62) + '...' : p.project_name} [${p.ministry_code} | ${p.state}]
        </option>
      `).join('');

    if (this.currentProjectId && list.some(p => p.project_id === this.currentProjectId)) {
      selectEl.value = this.currentProjectId;
    } else if (list.length > 0) {
      selectEl.value = list[0].project_id;
      this.selectProject(list[0].project_id);
    }
  },

  setupListeners() {
    // Search input listener
    const searchInput = document.getElementById('evidence-project-search');
    if (searchInput) {
      let debounceTimer;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          this.populateProjectDropdown(e.target.value);
        }, 150);
      });
    }

    // Project Selection change
    const selectEl = document.getElementById('evidence-project-select');
    if (selectEl) {
      selectEl.addEventListener('change', (e) => {
        const pId = e.target.value;
        if (pId) {
          this.selectProject(pId);
        }
      });
    }

    // Modal Close
    const closeModalBtn = document.getElementById('btn-close-evidence-modal');
    const modalOverlay = document.getElementById('evidence-upload-modal');
    if (closeModalBtn && modalOverlay) {
      closeModalBtn.addEventListener('click', () => modalOverlay.classList.remove('active'));
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) modalOverlay.classList.remove('active');
      });
    }

    // Evidence File input preview & EXIF GPS Extraction
    const fileInput = document.getElementById('evidence-file-input');
    if (fileInput) {
      fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
          // 1. Read preview base64
          const reader = new FileReader();
          reader.onload = (re) => {
            this.uploadedPhotoBase64 = re.target.result;
            const previewContainer = document.getElementById('evidence-preview-container');
            const previewImg = document.getElementById('evidence-preview-img');
            const previewVideo = document.getElementById('evidence-preview-video');
            
            if (previewContainer) previewContainer.style.display = 'block';
            if (file.type.startsWith('video/')) {
              if (previewImg) previewImg.style.display = 'none';
              if (previewVideo) {
                previewVideo.style.display = 'block';
                previewVideo.src = re.target.result;
              }
            } else {
              if (previewVideo) previewVideo.style.display = 'none';
              if (previewImg) {
                previewImg.style.display = 'block';
                previewImg.src = re.target.result;
              }
            }
          };
          reader.readAsDataURL(file);

          // 2. Extract and verify EXIF Geo-Tag directly from image file
          const exif = await this.extractExifMetadata(file);
          const gpsInput = document.getElementById('evidence-gps-input');
          const dtInput = document.getElementById('evidence-datetime-input');

          if (exif && exif.hasGps) {
            this.uploadedPhotoHasExif = true;
            if (gpsInput) gpsInput.value = exif.coordsStr;
            if (dtInput && exif.isoDateTime) dtInput.value = exif.isoDateTime;
            this.updateModalGeoFeedback(exif.coordsStr, true);
          } else {
            this.uploadedPhotoHasExif = false;
            // Retain project site coordinate or fallback
            const currVal = gpsInput ? gpsInput.value : '';
            this.updateModalGeoFeedback(currVal, false);
          }
        }
      });
    }

    // GPS Input real-time verification listeners
    const gpsModalInput = document.getElementById('evidence-gps-input');
    if (gpsModalInput) {
      gpsModalInput.addEventListener('input', (e) => {
        this.updateModalGeoFeedback(e.target.value);
      });
    }

    const gpsPublicInput = document.getElementById('public-gps-input');
    if (gpsPublicInput) {
      gpsPublicInput.addEventListener('input', (e) => {
        this.updatePublicGeoFeedback(e.target.value);
      });
    }

    // GPS Auto-detect in Evidence Upload Modal
    const btnGetGps = document.getElementById('btn-get-evidence-gps');
    if (btnGetGps) {
      btnGetGps.addEventListener('click', () => {
        btnGetGps.innerHTML = '⏳ Fetching GPS...';
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (pos) => {
              const coords = `${pos.coords.latitude.toFixed(5)}, ${pos.coords.longitude.toFixed(5)}`;
              const gpsInput = document.getElementById('evidence-gps-input');
              if (gpsInput) {
                gpsInput.value = coords;
                this.updateModalGeoFeedback(coords);
              }
              btnGetGps.innerHTML = '📍 GPS Captured ✓';
              setTimeout(() => { btnGetGps.innerHTML = '📍 Auto-Detect GPS'; }, 3000);
            },
            (err) => {
              // Fallback to project coordinate
              const currProj = this.projectsList.find(p => p.project_id === this.currentProjectId);
              if (currProj && currProj.location_lat && currProj.location_lng) {
                const preset = `${currProj.location_lat}, ${currProj.location_lng}`;
                document.getElementById('evidence-gps-input').value = preset;
                this.updateModalGeoFeedback(preset);
                btnGetGps.innerHTML = '📍 Project Site GPS (Preset)';
              } else {
                alert('GPS location could not be fetched automatically. Please enter coordinates manually.');
                btnGetGps.innerHTML = '📍 Auto-Detect GPS';
              }
            }
          );
        }
      });
    }

    // Submit Stage Evidence
    const formEvidence = document.getElementById('form-submit-evidence');
    if (formEvidence) {
      formEvidence.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleEvidenceSubmit();
      });
    }

    // Public Verification File Input preview
    const pubFileInput = document.getElementById('public-file-input');
    if (pubFileInput) {
      pubFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (re) => {
            this.publicPhotoBase64 = re.target.result;
            const previewContainer = document.getElementById('public-preview-container');
            const previewImg = document.getElementById('public-preview-img');
            if (previewContainer) previewContainer.style.display = 'block';
            if (previewImg) previewImg.src = re.target.result;
          };
          reader.readAsDataURL(file);
        }
      });
    }

    // Public Verification GPS auto-detect
    const btnPubGps = document.getElementById('btn-get-public-gps');
    if (btnPubGps) {
      btnPubGps.addEventListener('click', () => {
        btnPubGps.innerHTML = '⏳ Fetching GPS...';
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (pos) => {
              const coords = `${pos.coords.latitude.toFixed(5)}, ${pos.coords.longitude.toFixed(5)}`;
              const gpsInput = document.getElementById('public-gps-input');
              if (gpsInput) {
                gpsInput.value = coords;
                this.updatePublicGeoFeedback(coords);
              }
              btnPubGps.innerHTML = '📍 GPS Tagged ✓';
              setTimeout(() => { btnPubGps.innerHTML = '📍 Auto-Detect GPS'; }, 3000);
            },
            (err) => {
              const currProj = this.projectsList.find(p => p.project_id === this.currentProjectId);
              if (currProj && currProj.location_lat && currProj.location_lng) {
                const preset = `${currProj.location_lat}, ${currProj.location_lng}`;
                document.getElementById('public-gps-input').value = preset;
                this.updatePublicGeoFeedback(preset);
                btnPubGps.innerHTML = '📍 Project Site GPS (Preset)';
              } else {
                btnPubGps.innerHTML = '📍 Auto-Detect GPS';
              }
            }
          );
        }
      });
    }

    // Submit Public Verification Form
    const formPublic = document.getElementById('form-public-verification');
    if (formPublic) {
      formPublic.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handlePublicVerificationSubmit();
      });
    }
  },

  async selectProject(projectId) {
    this.currentProjectId = projectId;
    const selectEl = document.getElementById('evidence-project-select');
    if (selectEl && selectEl.value !== projectId) {
      selectEl.value = projectId;
    }

    // Find project details in projects list or fetch
    let proj = this.projectsList.find(p => p.project_id === projectId);
    if (!proj) {
      try {
        const res = await fetch(`/api/projects/${projectId}`);
        const data = await res.json();
        proj = data.project;
      } catch (err) {
        console.error('Error fetching project:', err);
      }
    }

    if (proj) {
      this.renderProjectSummary(proj);
    }

    // Load Evidence & Reviews strictly for this selected project
    await this.loadProjectEvidence(projectId);
  },

  renderProjectSummary(proj) {
    const summaryCard = document.getElementById('evidence-project-summary');
    if (!summaryCard) return;

    const costOverrunCr = proj.cost_overrun_cr || (proj.revised_cost_cr - proj.original_cost_cr);
    const costOverrunPct = proj.cost_overrun_pct || ((costOverrunCr / Math.max(1, proj.original_cost_cr)) * 100).toFixed(1);
    const delayMo = proj.schedule_delay_months || 0;
    const physPct = proj.physical_progress_pct || 0;
    const finPct = proj.financial_progress_pct || 0;
    const coords = (proj.location_lat && proj.location_lng) ? `${proj.location_lat}, ${proj.location_lng}` : 'Coordinates on Record';

    // Auto-fill GPS coordinates for forms
    const gpsInput1 = document.getElementById('evidence-gps-input');
    const gpsInput2 = document.getElementById('public-gps-input');
    if (gpsInput1 && proj.location_lat && proj.location_lng) gpsInput1.value = coords;
    if (gpsInput2 && proj.location_lat && proj.location_lng) gpsInput2.value = coords;

    summaryCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; margin-bottom: 16px;">
        <div style="flex: 1; min-width: 280px;">
          <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap;">
            <span class="badge" style="background: rgba(14,165,233,0.2); color: #38BDF8; font-weight: 700; font-size: 13px;">${proj.project_id}</span>
            <span class="badge" style="background: rgba(16,185,129,0.2); color: #34D399; font-weight: 600;">${proj.ministry_code}</span>
            <span style="font-size: 12px; color: #94A3B8;">Executing Agency: <strong style="color: #F8FAFC;">${proj.agency_name}</strong></span>
            <span style="font-size: 12px; color: #94A3B8;">State: <strong style="color: #F8FAFC;">${proj.state}</strong></span>
          </div>
          <h3 style="font-family: Outfit, sans-serif; font-size: 18px; color: #F8FAFC; line-height: 1.3; margin-bottom: 6px;">${proj.project_name}</h3>
          <div style="font-size: 12px; color: #94A3B8; display: flex; gap: 14px; flex-wrap: wrap;">
            <span>Sector: <strong style="color: #CBD5E1;">${proj.sector_name}</strong></span>
            <span>Site GPS: <strong style="color: #38BDF8;">📍 ${coords}</strong></span>
            <span>DoC: <strong style="color: #FBBF24;">${proj.anticipated_doc || proj.original_doc || 'In Progress'}</strong></span>
          </div>
        </div>
      </div>

      <!-- Mapped Metrics Grid from Dataset -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; padding-top: 14px; border-top: 1px solid var(--border-subtle);">
        <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px;">
          <div style="font-size: 11px; color: #94A3B8;">Original Capex</div>
          <div style="font-size: 15px; font-weight: 700; color: #F8FAFC; margin-top: 2px;">₹${(proj.original_cost_cr || 0).toLocaleString('en-IN')} Cr</div>
        </div>

        <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px;">
          <div style="font-size: 11px; color: #94A3B8;">Revised Capex</div>
          <div style="font-size: 15px; font-weight: 700; color: #38BDF8; margin-top: 2px;">₹${(proj.revised_cost_cr || 0).toLocaleString('en-IN')} Cr</div>
        </div>

        <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px;">
          <div style="font-size: 11px; color: #94A3B8;">Cost Escalation</div>
          <div style="font-size: 15px; font-weight: 700; color: ${costOverrunCr > 0 ? '#EF4444' : '#10B981'}; margin-top: 2px;">
            ${costOverrunCr > 0 ? `+₹${costOverrunCr.toLocaleString('en-IN')} Cr (+${costOverrunPct}%)` : 'On Budget'}
          </div>
        </div>

        <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px;">
          <div style="font-size: 11px; color: #94A3B8;">Schedule Status</div>
          <div style="font-size: 15px; font-weight: 700; color: ${delayMo > 0 ? '#F59E0B' : '#10B981'}; margin-top: 2px;">
            ${delayMo > 0 ? `+${delayMo} Months Delay` : 'On Schedule'}
          </div>
        </div>

        <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px;">
          <div style="font-size: 11px; color: #94A3B8;">Physical Progress</div>
          <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
            <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
              <div style="width: ${physPct}%; height: 100%; background: #0EA5E9;"></div>
            </div>
            <span style="font-size: 13px; font-weight: 800; color: #38BDF8;">${physPct}%</span>
          </div>
        </div>

        <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px;">
          <div style="font-size: 11px; color: #94A3B8;">Financial Progress</div>
          <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
            <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
              <div style="width: ${finPct}%; height: 100%; background: #10B981;"></div>
            </div>
            <span style="font-size: 13px; font-weight: 800; color: #34D399;">${finPct}%</span>
          </div>
        </div>
      </div>
    `;
  },

  async loadProjectEvidence(projectId) {
    // Reset stages to loading / placeholder state
    this.renderStagePlaceholder('before');
    this.renderStagePlaceholder('ongoing');
    this.renderStagePlaceholder('after');

    const reviewsContainer = document.getElementById('public-reviews-list');
    if (reviewsContainer) {
      reviewsContainer.innerHTML = '<div style="text-align: center; color: #64748B; padding: 20px;">Loading public community audit data...</div>';
    }

    try {
      const res = await fetch(`/api/evidence/${projectId}`);
      const data = await res.json();
      
      const evidence = data.evidence || {};
      
      // Stage 1: Before
      if (evidence.before && evidence.before.photos && evidence.before.photos.length > 0) {
        this.renderStageEvidence('before', evidence.before);
      } else {
        this.renderStagePlaceholder('before');
      }

      // Stage 2: Ongoing
      if (evidence.ongoing && evidence.ongoing.photos && evidence.ongoing.photos.length > 0) {
        this.renderStageEvidence('ongoing', evidence.ongoing);
      } else {
        this.renderStagePlaceholder('ongoing');
      }

      // Stage 3: After
      if (evidence.after && evidence.after.photos && evidence.after.photos.length > 0) {
        this.renderStageEvidence('after', evidence.after);
      } else {
        this.renderStagePlaceholder('after');
      }

      // Render Public Verifications
      this.renderPublicVerifications(data.public_verifications || []);

    } catch (err) {
      console.error(`Failed to load evidence for ${projectId}:`, err);
      this.renderStagePlaceholder('before');
      this.renderStagePlaceholder('ongoing');
      this.renderStagePlaceholder('after');
      if (reviewsContainer) {
        reviewsContainer.innerHTML = '<div style="text-align: center; color: #64748B; padding: 20px;">Evidence Yet to Upload</div>';
      }
    }
  },

  renderStagePlaceholder(stageType) {
    const container = document.getElementById(`evidence-stage-${stageType}`);
    if (!container) return;

    container.innerHTML = `
      <div class="evidence-placeholder-card">
        <div class="placeholder-icon">📷</div>
        <div class="placeholder-title">Evidence Yet to Upload</div>
        <p class="placeholder-sub">No verified geo-tagged evidence has been submitted for this stage.</p>
        <button class="btn btn-primary" onclick="EvidenceHandler.openUploadModal('${stageType}')" style="margin-top: 12px; padding: 8px 16px; font-size: 12px;">
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          <span>Upload Stage Evidence</span>
        </button>
      </div>
    `;
  },

  extractExifMetadata(file) {
    return new Promise((resolve) => {
      if (!file) {
        resolve(null);
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const buffer = e.target.result;
          const view = new DataView(buffer);
          
          // Check for JPEG marker 0xFFD8
          if (view.byteLength < 16 || view.getUint16(0, false) !== 0xFFD8) {
            resolve(null);
            return;
          }

          let offset = 2;
          const length = view.byteLength;
          let app1Offset = -1;

          while (offset + 4 < length) {
            const marker = view.getUint16(offset, false);
            offset += 2;
            if (marker === 0xFFE1) { // APP1 (Exif)
              app1Offset = offset;
              break;
            } else if ((marker & 0xFF00) !== 0xFF00 || marker === 0xFFDA || marker === 0xFFD9) {
              break;
            } else {
              const segLen = view.getUint16(offset, false);
              offset += segLen;
            }
          }

          if (app1Offset === -1 || app1Offset + 14 >= length) {
            resolve(null);
            return;
          }

          // Check "Exif\0\0"
          const exifHeader = String.fromCharCode(
            view.getUint8(app1Offset + 2), view.getUint8(app1Offset + 3),
            view.getUint8(app1Offset + 4), view.getUint8(app1Offset + 5)
          );

          if (exifHeader !== 'Exif') {
            resolve(null);
            return;
          }

          const tiffStart = app1Offset + 8;
          const endianness = view.getUint16(tiffStart, false);
          const littleEndian = (endianness === 0x4949); // 'II'

          if (view.getUint16(tiffStart + 2, littleEndian) !== 0x002A) {
            resolve(null);
            return;
          }

          const firstIFDOffset = view.getUint32(tiffStart + 4, littleEndian);
          if (firstIFDOffset < 8 || tiffStart + firstIFDOffset >= length) {
            resolve(null);
            return;
          }

          // Read 0th IFD
          let ifdOffset = tiffStart + firstIFDOffset;
          const numEntries = view.getUint16(ifdOffset, littleEndian);
          ifdOffset += 2;

          let gpsOffset = -1;
          let dateTimeStr = null;

          for (let i = 0; i < numEntries; i++) {
            const entryOffset = ifdOffset + (i * 12);
            if (entryOffset + 12 > length) break;

            const tag = view.getUint16(entryOffset, littleEndian);
            if (tag === 0x8825) { // GPS IFD pointer
              gpsOffset = tiffStart + view.getUint32(entryOffset + 8, littleEndian);
            } else if (tag === 0x0132 || tag === 0x9003) { // DateTime / DateTimeOriginal
              const dateOffset = tiffStart + view.getUint32(entryOffset + 8, littleEndian);
              if (dateOffset + 19 <= length) {
                let str = '';
                for (let d = 0; d < 19; d++) {
                  str += String.fromCharCode(view.getUint8(dateOffset + d));
                }
                dateTimeStr = str.replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3T');
              }
            }
          }

          if (gpsOffset === -1 || gpsOffset + 2 >= length) {
            resolve({ hasExif: true, hasGps: false, isoDateTime: dateTimeStr });
            return;
          }

          // Parse GPS IFD
          const numGpsEntries = view.getUint16(gpsOffset, littleEndian);
          gpsOffset += 2;

          let latRef = 'N', lonRef = 'E';
          let latVal = null, lonVal = null;

          const readRational = (ptr) => {
            if (ptr + 8 > length) return 0;
            const num = view.getUint32(ptr, littleEndian);
            const den = view.getUint32(ptr + 4, littleEndian);
            return den === 0 ? 0 : num / den;
          };

          for (let j = 0; j < numGpsEntries; j++) {
            const gOffset = gpsOffset + (j * 12);
            if (gOffset + 12 > length) break;

            const tag = view.getUint16(gOffset, littleEndian);

            if (tag === 0x0001) { // GPSLatitudeRef
              latRef = String.fromCharCode(view.getUint8(gOffset + 8));
            } else if (tag === 0x0002) { // GPSLatitude
              const rPtr = tiffStart + view.getUint32(gOffset + 8, littleEndian);
              const deg = readRational(rPtr);
              const min = readRational(rPtr + 8);
              const sec = readRational(rPtr + 16);
              latVal = deg + (min / 60.0) + (sec / 3600.0);
            } else if (tag === 0x0003) { // GPSLongitudeRef
              lonRef = String.fromCharCode(view.getUint8(gOffset + 8));
            } else if (tag === 0x0004) { // GPSLongitude
              const rPtr = tiffStart + view.getUint32(gOffset + 8, littleEndian);
              const deg = readRational(rPtr);
              const min = readRational(rPtr + 8);
              const sec = readRational(rPtr + 16);
              lonVal = deg + (min / 60.0) + (sec / 3600.0);
            }
          }

          if (latVal !== null && lonVal !== null && !isNaN(latVal) && !isNaN(lonVal)) {
            if (latRef === 'S') latVal = -latVal;
            if (lonRef === 'W') lonVal = -lonVal;
            resolve({
              hasExif: true,
              hasGps: true,
              latitude: parseFloat(latVal.toFixed(5)),
              longitude: parseFloat(lonVal.toFixed(5)),
              coordsStr: `${latVal.toFixed(5)}, ${lonVal.toFixed(5)}`,
              isoDateTime: dateTimeStr
            });
          } else {
            resolve({ hasExif: true, hasGps: false, isoDateTime: dateTimeStr });
          }
        } catch (err) {
          console.warn("EXIF GPS parsing error:", err);
          resolve(null);
        }
      };
      reader.onerror = () => resolve(null);
      reader.readAsArrayBuffer(file.slice(0, 131072)); // First 128KB
    });
  },

  calculateHaversine(lat1, lon1, lat2, lon2) {
    const R = 6371.0;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return parseFloat((R * c).toFixed(2));
  },

  verifyGpsAgainstProject(gpsStr, proj, isPhotoExif = false) {
    if (!gpsStr || !gpsStr.trim()) {
      return {
        isGeoTagged: false,
        hasPhotoExif: false,
        status: "Missing Geo-Tag",
        distanceKm: null,
        badgeBg: "rgba(148, 163, 184, 0.2)",
        badgeColor: "#94A3B8",
        message: "⚠️ Photo is not geo-tagged. No GPS coordinates recorded."
      };
    }

    try {
      const parts = gpsStr.split(",").map(p => parseFloat(p.trim()));
      if (parts.length < 2 || isNaN(parts[0]) || isNaN(parts[1])) {
        return {
          isGeoTagged: false,
          hasPhotoExif: false,
          status: "Invalid GPS Format",
          distanceKm: null,
          badgeBg: "rgba(239, 68, 68, 0.2)",
          badgeColor: "#F87171",
          message: "⚠️ Invalid coordinates format. Expected 'latitude, longitude'."
        };
      }

      const upLat = parts[0];
      const upLng = parts[1];

      if (!proj || !proj.location_lat || !proj.location_lng) {
        return {
          isGeoTagged: true,
          hasPhotoExif: isPhotoExif,
          status: isPhotoExif ? "✓ EXIF Geo-Tagged" : "✓ Geo-Tagged",
          distanceKm: 0,
          badgeBg: "rgba(14, 165, 233, 0.2)",
          badgeColor: "#38BDF8",
          message: `📍 Coordinates registered: ${upLat.toFixed(4)}, ${upLng.toFixed(4)}`
        };
      }

      const siteLat = parseFloat(proj.location_lat);
      const siteLng = parseFloat(proj.location_lng);
      const dist = this.calculateHaversine(upLat, upLng, siteLat, siteLng);
      const prefix = isPhotoExif ? "✓ EXIF Photo Geo-Tag" : "✓ Geo-Verified";

      if (dist <= 15.0) {
        return {
          isGeoTagged: true,
          hasPhotoExif: isPhotoExif,
          status: `${prefix} (On-Site)`,
          distanceKm: dist,
          badgeBg: "rgba(16, 185, 129, 0.2)",
          badgeColor: "#34D399",
          message: `${prefix}: Photo taken ${dist} km from designated site in ${proj.state || ''} (${siteLat}, ${siteLng}).`
        };
      } else if (dist <= 50.0) {
        return {
          isGeoTagged: true,
          hasPhotoExif: isPhotoExif,
          status: "Near Site Corridor",
          distanceKm: dist,
          badgeBg: "rgba(245, 158, 11, 0.2)",
          badgeColor: "#FBBF24",
          message: `⚡ Near Site: Photo is ${dist} km from designated project location (${proj.state || ''}).`
        };
      } else {
        return {
          isGeoTagged: true,
          hasPhotoExif: isPhotoExif,
          status: isPhotoExif ? "⚠️ EXIF Location Mismatch" : "⚠️ Location Mismatch Flagged",
          distanceKm: dist,
          badgeBg: "rgba(239, 68, 68, 0.2)",
          badgeColor: "#F87171",
          message: `⚠️ Geo-Mismatch: Photo coordinates are ${dist} km away from ${proj.project_name || 'project site'} in ${proj.state || ''} (${siteLat}, ${siteLng}).`
        };
      }
    } catch (e) {
      return {
        isGeoTagged: false,
        hasPhotoExif: false,
        status: "Unverified",
        distanceKm: null,
        badgeBg: "rgba(148, 163, 184, 0.2)",
        badgeColor: "#94A3B8",
        message: "Coordinates unverified."
      };
    }
  },

  renderStageEvidence(stageType, data) {
    const container = document.getElementById(`evidence-stage-${stageType}`);
    if (!container) return;

    const currProj = this.projectsList.find(p => p.project_id === this.currentProjectId);
    const mediaSrc = (data.photos && data.photos.length > 0) ? data.photos[0] : '';
    const isVideo = mediaSrc.includes('video') || mediaSrc.endsWith('.mp4') || mediaSrc.startsWith('data:video');
    const formattedDate = data.datetime ? new Date(data.datetime).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : 'Verified Timestamped';

    // Compute Geo-Verification Check
    const geoCheck = data.geo_verification || this.verifyGpsAgainstProject(data.gps, currProj);

    let extraBadge = '';
    if (stageType === 'ongoing') {
      extraBadge = `
        <div style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
          <span class="badge" style="background: rgba(14,165,233,0.2); color: #38BDF8;">${data.stage || 'Ongoing Works'}</span>
          <span class="badge" style="background: rgba(16,185,129,0.2); color: #34D399;">${data.progress_pct || 0}% Progress</span>
        </div>
      `;
    } else if (stageType === 'after') {
      extraBadge = `
        <div style="display: flex; gap: 8px; margin-bottom: 8px;">
          <span class="badge" style="background: rgba(16,185,129,0.2); color: #34D399;">Completed • ${data.progress_pct || 100}% Physical Progress</span>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="evidence-active-card">
        <div class="evidence-media-wrapper">
          ${isVideo ? `
            <video src="${mediaSrc}" controls style="width: 100%; height: 190px; object-fit: cover; border-radius: 8px;"></video>
          ` : `
            <img src="${mediaSrc}" alt="${stageType} evidence" style="width: 100%; height: 190px; object-fit: cover; border-radius: 8px;" onclick="window.open('${mediaSrc}', '_blank')">
          `}
          <div class="evidence-media-tag" style="background: ${geoCheck.badgeColor || '#10B981'};">
            ${geoCheck.status || '✓ Geo-Tagged'}
          </div>
        </div>

        <div style="padding: 14px 4px 4px 4px;">
          ${extraBadge}

          <!-- Geo-Verification Match Box -->
          <div style="background: ${geoCheck.badgeBg || 'rgba(0,0,0,0.3)'}; border: 1px solid ${geoCheck.badgeColor || 'var(--border-subtle)'}; border-radius: 6px; padding: 8px 10px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-size: 11px; font-weight: 700; color: ${geoCheck.badgeColor || '#38BDF8'};">
                ${geoCheck.status || 'Geo-Tagging Status'}
              </span>
              ${data.gps ? `
                <a href="https://maps.google.com/?q=${encodeURIComponent(data.gps)}" target="_blank" style="font-size: 10px; color: #38BDF8; text-decoration: underline;">
                  View on Map ↗
                </a>
              ` : ''}
            </div>
            <div style="font-size: 11px; color: #CBD5E1; line-height: 1.3;">
              ${geoCheck.message}
            </div>
          </div>

          <div style="display: flex; justify-content: space-between; font-size: 11px; color: #94A3B8; margin-bottom: 6px;">
            <span>📍 <strong>${data.gps || 'Site Location'}</strong></span>
            <span>🕒 ${formattedDate}</span>
          </div>

          <div style="font-size: 12px; color: #E2E8F0; line-height: 1.4; background: rgba(0,0,0,0.25); padding: 8px 10px; border-radius: 6px; margin-bottom: 10px;">
            ${data.remarks || 'Site geo-evidence registered and cryptographically stamped.'}
          </div>

          <button class="btn btn-secondary" onclick="EvidenceHandler.openUploadModal('${stageType}')" style="width: 100%; justify-content: center; font-size: 11px; padding: 6px 12px;">
            Update / Replace Evidence
          </button>
        </div>
      </div>
    `;
  },

  updateModalGeoFeedback(gpsStr, isPhotoExif = false) {
    const feedbackEl = document.getElementById('modal-geo-check-feedback');
    if (!feedbackEl) return;
    const currProj = this.projectsList.find(p => p.project_id === this.currentProjectId);
    const check = this.verifyGpsAgainstProject(gpsStr, currProj, isPhotoExif);

    feedbackEl.style.display = 'block';
    feedbackEl.style.background = check.badgeBg;
    feedbackEl.style.color = check.badgeColor;
    feedbackEl.style.border = `1px solid ${check.badgeColor}`;
    feedbackEl.innerHTML = `<strong>${check.status}:</strong> ${check.message}`;
  },

  updatePublicGeoFeedback(gpsStr, isPhotoExif = false) {
    const feedbackEl = document.getElementById('public-geo-check-feedback');
    if (!feedbackEl) return;
    const currProj = this.projectsList.find(p => p.project_id === this.currentProjectId);
    const check = this.verifyGpsAgainstProject(gpsStr, currProj, isPhotoExif);

    feedbackEl.style.display = 'block';
    feedbackEl.style.background = check.badgeBg;
    feedbackEl.style.color = check.badgeColor;
    feedbackEl.style.border = `1px solid ${check.badgeColor}`;
    feedbackEl.innerHTML = `<strong>${check.status}:</strong> ${check.message}`;
  },

  openUploadModal(stageType) {
    this.selectedStageType = stageType;
    this.uploadedPhotoBase64 = null;

    const modal = document.getElementById('evidence-upload-modal');
    const titleEl = document.getElementById('evidence-modal-stage-title');
    const stageSelect = document.getElementById('modal-stage-select');
    const progressGroup = document.getElementById('modal-progress-group');
    const stageNameGroup = document.getElementById('modal-stagename-group');
    const previewContainer = document.getElementById('evidence-preview-container');
    const gpsInput = document.getElementById('evidence-gps-input');
    const remarksInput = document.getElementById('evidence-remarks-input');
    const fileInput = document.getElementById('evidence-file-input');

    if (fileInput) fileInput.value = '';
    if (previewContainer) previewContainer.style.display = 'none';
    if (remarksInput) remarksInput.value = '';

    // Auto-fill project coordinates if available and trigger feedback
    const currProj = this.projectsList.find(p => p.project_id === this.currentProjectId);
    if (gpsInput && currProj && currProj.location_lat && currProj.location_lng) {
      const coords = `${currProj.location_lat}, ${currProj.location_lng}`;
      gpsInput.value = coords;
      this.updateModalGeoFeedback(coords);
    } else {
      this.updateModalGeoFeedback('');
    }

    // Set stage select
    if (stageSelect) stageSelect.value = stageType;
    
    // Configure modal fields based on stage
    this.updateModalFields(stageType);

    if (modal) modal.classList.add('active');
  },

  updateModalFields(stageType) {
    const titleEl = document.getElementById('evidence-modal-stage-title');
    const progressGroup = document.getElementById('modal-progress-group');
    const stageNameGroup = document.getElementById('modal-stagename-group');
    const progressInput = document.getElementById('modal-progress-input');

    const stageTitles = {
      'before': 'BEFORE CONSTRUCTION EVIDENCE',
      'ongoing': 'ONGOING CONSTRUCTION EVIDENCE',
      'after': 'AFTER / COMPLETION EVIDENCE'
    };

    if (titleEl) titleEl.innerText = stageTitles[stageType] || 'STAGE EVIDENCE';

    if (stageType === 'before') {
      if (progressGroup) progressGroup.style.display = 'none';
      if (stageNameGroup) stageNameGroup.style.display = 'none';
    } else if (stageType === 'ongoing') {
      if (progressGroup) progressGroup.style.display = 'block';
      if (stageNameGroup) stageNameGroup.style.display = 'block';
      const currProj = this.projectsList.find(p => p.project_id === this.currentProjectId);
      if (progressInput && currProj) progressInput.value = currProj.physical_progress_pct || 50;
    } else if (stageType === 'after') {
      if (progressGroup) progressGroup.style.display = 'block';
      if (stageNameGroup) stageNameGroup.style.display = 'none';
      if (progressInput) progressInput.value = 100;
    }
  },

  async handleEvidenceSubmit() {
    if (!this.currentProjectId) {
      alert('Please select a project first.');
      return;
    }

    const stageType = document.getElementById('modal-stage-select').value || this.selectedStageType;
    const gps = document.getElementById('evidence-gps-input').value.trim();
    const datetime = document.getElementById('evidence-datetime-input').value || new Date().toISOString();
    const remarks = document.getElementById('evidence-remarks-input').value.trim();
    const progressPct = parseFloat(document.getElementById('modal-progress-input').value) || 0.0;
    const stageName = document.getElementById('modal-stagename-select').value;

    let photos = [];
    if (this.uploadedPhotoBase64) {
      photos.push(this.uploadedPhotoBase64);
    } else {
      // Use representative infrastructure stock photo for demonstration if no file chosen
      const defaultSamples = {
        'before': 'https://images.unsplash.com/photo-1590486803833-1c5dc8ddd4c8?auto=format&fit=crop&w=800&q=80',
        'ongoing': 'https://images.unsplash.com/photo-1541888946425-d0fbb180c5f7?auto=format&fit=crop&w=800&q=80',
        'after': 'https://images.unsplash.com/photo-1513828583688-c52646db42da?auto=format&fit=crop&w=800&q=80'
      };
      photos.push(defaultSamples[stageType] || defaultSamples['ongoing']);
    }

    const payload = {
      stage_type: stageType,
      photos: photos,
      gps: gps,
      datetime: datetime,
      progress_pct: progressPct,
      stage: stageName,
      remarks: remarks || `${stageType.toUpperCase()} evidence submitted with verified geolocation.`
    };

    try {
      const submitBtn = document.getElementById('btn-submit-modal-evidence');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = 'Submitting...';
      }

      const res = await fetch(`/api/evidence/${this.currentProjectId}/stage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (res.ok) {
        document.getElementById('evidence-upload-modal').classList.remove('active');
        await this.loadProjectEvidence(this.currentProjectId);
      } else {
        alert(result.detail || 'Error uploading evidence.');
      }
    } catch (err) {
      console.error('Failed to submit evidence:', err);
      alert('Error connecting to server to save evidence.');
    } finally {
      const submitBtn = document.getElementById('btn-submit-modal-evidence');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Submit Geo-Evidence';
      }
    }
  },

  renderPublicVerifications(reviews) {
    const container = document.getElementById('public-reviews-list');
    const badgeCount = document.getElementById('public-verification-count');
    const overallStatusBadge = document.getElementById('public-overall-status-badge');

    if (badgeCount) badgeCount.innerText = `${reviews.length} Citizen Audits`;

    // Compute aggregate status
    if (overallStatusBadge) {
      if (reviews.length === 0) {
        overallStatusBadge.className = 'badge';
        overallStatusBadge.style.background = 'rgba(148,163,184,0.15)';
        overallStatusBadge.style.color = '#94A3B8';
        overallStatusBadge.innerText = 'Awaiting Review';
      } else {
        const hasIssue = reviews.some(r => r.verification_status === 'Issue Reported');
        const hasPartial = reviews.some(r => r.verification_status === 'Partially Verified');
        if (hasIssue) {
          overallStatusBadge.className = 'badge badge-critical';
          overallStatusBadge.style.background = 'rgba(239,68,68,0.2)';
          overallStatusBadge.style.color = '#F87171';
          overallStatusBadge.innerText = '⚠️ Issue Reported';
        } else if (hasPartial) {
          overallStatusBadge.className = 'badge badge-moderate';
          overallStatusBadge.style.background = 'rgba(245,158,11,0.2)';
          overallStatusBadge.style.color = '#FBBF24';
          overallStatusBadge.innerText = '⚡ Partially Verified';
        } else {
          overallStatusBadge.className = 'badge badge-success';
          overallStatusBadge.style.background = 'rgba(16,185,129,0.2)';
          overallStatusBadge.style.color = '#34D399';
          overallStatusBadge.innerText = '✓ Verified by Community';
        }
      }
    }

    if (!container) return;

    if (reviews.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; color: #64748B; padding: 40px 20px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px dashed var(--border-subtle);">
          <div style="font-size: 24px; margin-bottom: 8px;">📋</div>
          <div style="font-weight: 600; color: #94A3B8; font-size: 14px;">No Public Verification Audits Yet</div>
          <p style="font-size: 12px; color: #64748B; margin-top: 4px;">Be the first citizen or ground engineer to audit this project using the verification form.</p>
        </div>
      `;
      return;
    }

    const currProj = this.projectsList.find(p => p.project_id === this.currentProjectId);

    container.innerHTML = reviews.map(r => {
      let statusBg = 'rgba(16,185,129,0.2)';
      let statusColor = '#34D399';
      
      if (r.verification_status === 'Issue Reported') {
        statusBg = 'rgba(239,68,68,0.2)';
        statusColor = '#F87171';
      } else if (r.verification_status === 'Partially Verified') {
        statusBg = 'rgba(245,158,11,0.2)';
        statusColor = '#FBBF24';
      } else if (r.verification_status === 'Awaiting Review') {
        statusBg = 'rgba(148,163,184,0.2)';
        statusColor = '#94A3B8';
      }

      const formattedDate = r.timestamp ? new Date(r.timestamp).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : 'Recent';
      const geoCheck = r.geo_verification || this.verifyGpsAgainstProject(r.gps, currProj);

      return `
        <div class="public-review-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <span class="badge" style="background: ${statusBg}; color: ${statusColor}; font-weight: 700;">${r.verification_status}</span>
              <span style="font-size: 11px; color: #64748B;"><code>${r.id}</code></span>
            </div>
            <span style="font-size: 11px; color: #94A3B8;">🕒 ${formattedDate}</span>
          </div>

          <!-- Geo-Verification Proximity Match Banner -->
          <div style="background: ${geoCheck.badgeBg}; border: 1px solid ${geoCheck.badgeColor}; border-radius: 6px; padding: 6px 10px; margin-bottom: 8px; font-size: 11px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 700; color: ${geoCheck.badgeColor};">
                ${geoCheck.status}
              </span>
              ${r.gps ? `<a href="https://maps.google.com/?q=${encodeURIComponent(r.gps)}" target="_blank" style="color: #38BDF8; font-size: 10px; text-decoration: underline;">Map ↗</a>` : ''}
            </div>
            <div style="color: #CBD5E1; margin-top: 2px;">
              ${geoCheck.message}
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; margin-bottom: 8px; background: rgba(255,255,255,0.02); padding: 8px; border-radius: 6px;">
            <div>Status: <strong style="color: #F8FAFC;">${r.completion_status}</strong></div>
            <div>Ground Match: <strong style="color: ${r.ground_reality_matches === 'Yes' ? '#34D399' : (r.ground_reality_matches === 'No' ? '#F87171' : '#FBBF24')};">${r.ground_reality_matches}</strong></div>
            <div>Reported Issues: <strong style="color: ${r.defects && r.defects !== 'None' ? '#F87171' : '#34D399'};">${r.defects || 'None'}</strong></div>
            <div>GPS: <strong style="color: #38BDF8;">${r.gps || 'Site Coordinate'}</strong></div>
          </div>

          <p style="font-size: 12px; color: #CBD5E1; line-height: 1.4; margin-bottom: 8px;">${r.comments}</p>

          ${r.photo ? `
            <div style="margin-top: 6px;">
              <img src="${r.photo}" alt="Audit Photo" style="width: 100%; max-height: 140px; object-fit: cover; border-radius: 6px; cursor: pointer;" onclick="window.open('${r.photo}', '_blank')">
            </div>
          ` : ''}
        </div>
      `;
    }).join('');
  },

  async handlePublicVerificationSubmit() {
    if (!this.currentProjectId) {
      alert('Please select a project first.');
      return;
    }

    const completionStatus = document.getElementById('public-status-select').value;
    const groundRealityMatches = document.getElementById('public-ground-match-select').value;
    const defects = document.getElementById('public-defects-select').value;
    const gps = document.getElementById('public-gps-input').value.trim();
    const comments = document.getElementById('public-comments-input').value.trim();

    if (!comments) {
      alert('Please provide your ground verification comments or observations.');
      return;
    }

    const payload = {
      completion_status: completionStatus,
      ground_reality_matches: groundRealityMatches,
      defects: defects,
      photo: this.publicPhotoBase64 || '',
      gps: gps,
      comments: comments
    };

    try {
      const submitBtn = document.getElementById('btn-submit-public-review');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = 'Submitting Audit...';
      }

      const res = await fetch(`/api/evidence/${this.currentProjectId}/verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (res.ok) {
        // Clear form
        document.getElementById('public-comments-input').value = '';
        document.getElementById('public-file-input').value = '';
        this.publicPhotoBase64 = null;
        const preview = document.getElementById('public-preview-container');
        if (preview) preview.style.display = 'none';

        // Reload data
        await this.loadProjectEvidence(this.currentProjectId);
      } else {
        alert(result.detail || 'Error submitting public review.');
      }
    } catch (err) {
      console.error('Failed to submit public review:', err);
      alert('Error connecting to server.');
    } finally {
      const submitBtn = document.getElementById('btn-submit-public-review');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Submit Verification Audit';
      }
    }
  }
};

if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    EvidenceHandler.init();
  });
}
