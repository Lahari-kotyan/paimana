"""
Contractor Geo-Evidence & Public Verification Routes
Manages project-specific multi-stage geo-tagged evidence and community audits.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from backend.config import DATA_DIR

router = APIRouter(prefix="/api/evidence", tags=["Contractor Geo-Evidence"])

EVIDENCE_STORE_PATH = DATA_DIR / "paimana_evidence_store.json"

def get_evidence_store() -> Dict[str, Any]:
    if not EVIDENCE_STORE_PATH.exists():
        # Seed initial store with sample evidence for first 2 projects
        seed_store = {
            "PAIMANA-SEC_INLAND-2015-1001": {
                "project_id": "PAIMANA-SEC_INLAND-2015-1001",
                "evidence": {
                    "before": {
                        "photos": ["https://images.unsplash.com/photo-1590486803833-1c5dc8ddd4c8?auto=format&fit=crop&w=800&q=80"],
                        "gps": "26.1397, 92.6714",
                        "datetime": "2015-01-24T09:30:00",
                        "remarks": "Baseline greenfield riverbank survey completed for Bongaigaon Multimodal Terminal. Soil density tests verified."
                    },
                    "ongoing": {
                        "photos": ["https://images.unsplash.com/photo-1541888946425-d0fbb180c5f7?auto=format&fit=crop&w=800&q=80"],
                        "gps": "26.1402, 92.6720",
                        "datetime": "2026-03-15T14:45:00",
                        "progress_pct": 81.0,
                        "stage": "Superstructure & Berth Decking",
                        "remarks": "Main jetty pile cap placement active. 27 out of 27 structural milestones underway with 81% physical progress."
                    },
                    "after": None
                },
                "public_verifications": [
                    {
                        "id": "REV-INLAND-01",
                        "timestamp": "2026-04-12T11:20:00",
                        "completion_status": "On Track",
                        "ground_reality_matches": "Yes",
                        "defects": "None",
                        "photo": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80",
                        "gps": "26.1399, 92.6718",
                        "comments": "Inspected riverfront terminal construction. Structural work on terminal jetty is active and corresponds to 80%+ progress.",
                        "verification_status": "Verified"
                    }
                ]
            },
            "PAIMANA-SEC_HWY-2016-1002": {
                "project_id": "PAIMANA-SEC_HWY-2016-1002",
                "evidence": {
                    "before": {
                        "photos": ["https://images.unsplash.com/photo-1508873535684-277a3cbcc4e8?auto=format&fit=crop&w=800&q=80"],
                        "gps": "30.6417, 75.0930",
                        "datetime": "2016-04-10T10:00:00",
                        "remarks": "Original 2-lane alignment right-of-way prior to 6-lane expansion handover."
                    },
                    "ongoing": None,
                    "after": None
                },
                "public_verifications": []
            }
        }
        with open(EVIDENCE_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(seed_store, f, indent=2)
        return seed_store

    with open(EVIDENCE_STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_evidence_store(store: Dict[str, Any]):
    with open(EVIDENCE_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)

class StageEvidencePayload(BaseModel):
    stage_type: str  # "before", "ongoing", "after"
    photos: List[str] = []
    gps: str = ""
    datetime: Optional[str] = None
    progress_pct: Optional[float] = None
    stage: Optional[str] = None
    remarks: Optional[str] = ""

class PublicVerificationPayload(BaseModel):
    completion_status: str
    ground_reality_matches: str
    defects: str
    photo: Optional[str] = ""
    gps: Optional[str] = ""
    comments: str
    verification_status: Optional[str] = "Awaiting Review"

import math

import base64
import io

def extract_exif_from_base64(b64_str: str) -> Optional[Dict[str, Any]]:
    """Extracts GPS coordinates directly from base64 image EXIF header if present."""
    if not b64_str or not isinstance(b64_str, str) or not b64_str.startswith("data:image"):
        return None
    try:
        from PIL import Image, ExifTags
        raw_data = base64.b64decode(b64_str.split(",")[1])
        img = Image.open(io.BytesIO(raw_data))
        exif_raw = getattr(img, "_getexif", lambda: None)()
        if not exif_raw:
            return None
        
        exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}
        gps_info = exif.get("GPSInfo")
        if not gps_info:
            return None
            
        def convert_to_degrees(value):
            if isinstance(value, (int, float)):
                return float(value)
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)
            
        lat_ref = gps_info.get(1, 'N')
        lat = convert_to_degrees(gps_info[2])
        if lat_ref != 'N':
            lat = -lat
            
        lon_ref = gps_info.get(3, 'E')
        lon = convert_to_degrees(gps_info[4])
        if lon_ref != 'E':
            lon = -lon
            
        return {
            "has_exif_gps": True,
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "coords": f"{round(lat, 5)}, {round(lon, 5)}"
        }
    except Exception:
        return None

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates distance between two GPS coordinates in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def verify_geo_tagging(gps_str: str, project_id: str, photo_b64: Optional[str] = None) -> Dict[str, Any]:
    """Verifies if GPS coordinate is valid, extracts photo EXIF if available, and matches against project site."""
    # Check if photo itself has embedded EXIF GPS
    exif_meta = extract_exif_from_base64(photo_b64) if photo_b64 else None
    has_photo_exif = False
    
    if exif_meta and exif_meta.get("has_exif_gps"):
        has_photo_exif = True
        gps_str = exif_meta["coords"]

    if not gps_str or not gps_str.strip():
        return {
            "is_geo_tagged": False,
            "has_photo_exif": False,
            "status": "Missing Geo-Tag",
            "distance_km": None,
            "match_verdict": "Unverified",
            "badge_color": "#94A3B8",
            "message": "Photo is not geo-tagged. No GPS coordinates provided."
        }
        
    try:
        parts = [p.strip() for p in gps_str.split(",")]
        if len(parts) < 2:
            return {
                "is_geo_tagged": False,
                "has_photo_exif": False,
                "status": "Invalid GPS Format",
                "distance_km": None,
                "match_verdict": "Format Error",
                "badge_color": "#EF4444",
                "message": "Invalid GPS format. Expected 'latitude, longitude'."
            }
            
        up_lat = float(parts[0])
        up_lng = float(parts[1])
    except (ValueError, IndexError):
        return {
            "is_geo_tagged": False,
            "has_photo_exif": False,
            "status": "Invalid GPS",
            "distance_km": None,
            "match_verdict": "Format Error",
            "badge_color": "#EF4444",
            "message": "Coordinates could not be parsed."
        }

    # Fetch project site location from projects dataset
    from backend.routes.project_routes import load_projects_json
    projects = load_projects_json()
    proj = next((p for p in projects if p["project_id"] == project_id), None)
    
    if not proj or "location_lat" not in proj or "location_lng" not in proj:
        return {
            "is_geo_tagged": True,
            "has_photo_exif": has_photo_exif,
            "status": "Geo-Tagged (Site Unknown)",
            "distance_km": 0.0,
            "match_verdict": "Site Coords Not Configured",
            "badge_color": "#38BDF8",
            "message": f"GPS coordinates {up_lat:.4f}, {up_lng:.4f} recorded."
        }
        
    site_lat = float(proj["location_lat"])
    site_lng = float(proj["location_lng"])
    
    distance_km = calculate_haversine_distance(up_lat, up_lng, site_lat, site_lng)
    tag_prefix = "✓ EXIF Geo-Tag Verified" if has_photo_exif else "✓ Geo-Verified"
    
    if distance_km <= 15.0:
        return {
            "is_geo_tagged": True,
            "has_photo_exif": has_photo_exif,
            "status": f"{tag_prefix} (On-Site)",
            "distance_km": distance_km,
            "site_coords": f"{site_lat}, {site_lng}",
            "match_verdict": "Site Matched (Within 15km)",
            "badge_color": "#10B981",
            "message": f"{tag_prefix}: Photo taken {distance_km} km from project site in {proj.get('state', '')} ({site_lat}, {site_lng})."
        }
    elif distance_km <= 50.0:
        return {
            "is_geo_tagged": True,
            "has_photo_exif": has_photo_exif,
            "status": "Near Site Corridor",
            "distance_km": distance_km,
            "site_coords": f"{site_lat}, {site_lng}",
            "match_verdict": "Near Site Corridor",
            "badge_color": "#F59E0B",
            "message": f"⚡ Near Site: Photo is {distance_km} km from designated project location."
        }
    else:
        return {
            "is_geo_tagged": True,
            "has_photo_exif": has_photo_exif,
            "status": "Location Mismatched",
            "distance_km": distance_km,
            "site_coords": f"{site_lat}, {site_lng}",
            "match_verdict": "Mismatch Flagged",
            "badge_color": "#EF4444",
            "message": f"⚠️ Geo-Mismatch: Coordinates are {distance_km} km away from {proj.get('project_name', 'project site')} in {proj.get('state', '')} ({site_lat}, {site_lng})."
        }

@router.get("/{project_id}")
def get_project_evidence(project_id: str):
    """
    Returns stage evidence and public verifications specifically for the requested project.
    """
    store = get_evidence_store()
    project_record = store.get(project_id)
    
    if not project_record:
        return {
            "project_id": project_id,
            "evidence": {
                "before": None,
                "ongoing": None,
                "after": None
            },
            "public_verifications": []
        }
        
    return project_record

@router.post("/{project_id}/stage")
def upload_stage_evidence(project_id: str, payload: StageEvidencePayload):
    """
    Saves/updates contractor evidence for a specific stage with Haversine site verification.
    """
    store = get_evidence_store()
    if project_id not in store:
        store[project_id] = {
            "project_id": project_id,
            "evidence": {
                "before": None,
                "ongoing": None,
                "after": None
            },
            "public_verifications": []
        }
        
    stage_key = payload.stage_type.lower().strip()
    if stage_key not in ["before", "ongoing", "after"]:
        raise HTTPException(status_code=400, detail="Invalid stage type. Must be 'before', 'ongoing', or 'after'.")
        
    # Execute geo-verification against project site & photo EXIF
    photo_b64 = payload.photos[0] if payload.photos else None
    geo_check = verify_geo_tagging(payload.gps, project_id, photo_b64)
        
    evidence_item = {
        "photos": payload.photos,
        "gps": payload.gps if not geo_check.get("has_photo_exif") else geo_check.get("site_coords", payload.gps),
        "datetime": payload.datetime or datetime.now().isoformat(),
        "remarks": payload.remarks or "",
        "geo_verification": geo_check
    }
    
    if stage_key == "ongoing":
        evidence_item["progress_pct"] = payload.progress_pct if payload.progress_pct is not None else 0.0
        evidence_item["stage"] = payload.stage or "Construction in Progress"
    elif stage_key == "after":
        evidence_item["progress_pct"] = payload.progress_pct if payload.progress_pct is not None else 100.0
        
    store[project_id]["evidence"][stage_key] = evidence_item
    save_evidence_store(store)
    
    return {
        "status": "success",
        "message": f"Evidence for stage '{stage_key}' successfully saved for {project_id}.",
        "project_id": project_id,
        "geo_verification": geo_check,
        "evidence": store[project_id]["evidence"]
    }

@router.post("/{project_id}/verification")
def submit_public_verification(project_id: str, payload: PublicVerificationPayload):
    """
    Submits a public community ground verification audit for project_id.
    """
    store = get_evidence_store()
    if project_id not in store:
        store[project_id] = {
            "project_id": project_id,
            "evidence": {
                "before": None,
                "ongoing": None,
                "after": None
            },
            "public_verifications": []
        }
        
    # Execute geo-verification against project site & photo EXIF
    geo_check = verify_geo_tagging(payload.gps, project_id, payload.photo)

    # Auto-calculate verification status if not explicitly set
    computed_status = payload.verification_status
    if not computed_status or computed_status == "Awaiting Review":
        if geo_check["status"] == "Location Mismatched":
            computed_status = "Issue Reported"
        elif payload.ground_reality_matches == "Yes" and (payload.defects == "None" or not payload.defects):
            computed_status = "Verified"
        elif payload.ground_reality_matches == "Partial":
            computed_status = "Partially Verified"
        elif payload.ground_reality_matches == "No" or (payload.defects and payload.defects != "None"):
            computed_status = "Issue Reported"
        else:
            computed_status = "Awaiting Review"
            
    review_record = {
        "id": f"REV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "completion_status": payload.completion_status,
        "ground_reality_matches": payload.ground_reality_matches,
        "defects": payload.defects,
        "photo": payload.photo or "",
        "gps": payload.gps or "",
        "geo_verification": geo_check,
        "comments": payload.comments,
        "verification_status": computed_status
    }
    
    store[project_id]["public_verifications"].insert(0, review_record)
    save_evidence_store(store)
    
    return {
        "status": "success",
        "message": f"Public verification submitted successfully for {project_id}.",
        "geo_verification": geo_check,
        "review": review_record
    }
