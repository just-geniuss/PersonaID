# PersonaID Upgrade Guide (English)

## Overview

This update fixes camera capture issues and updates dependencies to modern, compatible versions.

## Key Changes

### 1. Updated Dependencies
- **mediapipe**: 0.10.11 → 0.10.21
- **protobuf**: 3.20.3 → 4.25.8
- **opencv-python**: 4.9.0.80 → 4.12.0.88
- **Flask**: 3.0.2 → 3.1.0
- All other packages updated to latest stable versions

### 2. Fixed Camera Capture Issue

**Problem**: Camera could only be captured through OBS.

**Solution**:
- Added multi-backend camera support (DirectShow, Media Foundation)
- DirectShow backend is tried first for Windows/OBS compatibility
- Automatic camera index fallback (tries 0, 1, 2)
- Improved error handling and camera validation

### 3. New Camera Configuration

Created `camera_config.py` for easy camera settings:

```python
CAMERA_INDEX = 0        # Camera index (0=default, 1=second, etc.)
CAMERA_WIDTH = 10000    # Preferred resolution
CAMERA_HEIGHT = 10000
VERBOSE_LOGGING = True  # Enable detailed logs
```

## Quick Start

### 1. Update Dependencies

```bash
# Linux
python3 -m pip install --upgrade -r requirements.txt

# Windows
python -m pip install --upgrade -r requirements.txt
```

### 2. Test Camera

```bash
python util/test_cam.py
```

### 3. Configure Camera (Optional)

Edit `camera_config.py` if you need a specific camera:

```python
CAMERA_INDEX = 1  # Use second camera
```

### 4. Run System

```bash
python start_capture.py
```

## Troubleshooting

### Camera Not Found

1. Check camera connection
2. Try different camera indices in `camera_config.py`
3. Close other applications using the camera

### Dependency Conflicts

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

## Benefits

- ✅ Camera works without OBS
- ✅ Better Windows compatibility
- ✅ Automatic camera detection
- ✅ Up-to-date dependencies
- ✅ Python 3.12 compatible
- ✅ No security vulnerabilities
- ✅ Improved error handling

## Code Changes

The main change is in `capture_streamer.py`:

**Before:**
```python
cap = cv2.VideoCapture(1)  # Hardcoded camera index
```

**After:**
```python
cap, width, height = init_camera(
    camera_index=CAMERA_INDEX,
    width=CAMERA_WIDTH,
    height=CAMERA_HEIGHT
)
```

The new `init_camera()` function:
- Tries multiple backends (DirectShow, Media Foundation, Any)
- Tests multiple camera indices
- Validates camera by reading a test frame
- Returns camera object and actual resolution

## Backward Compatibility

All changes are backward compatible. Existing functionality is preserved.

## Security

- All dependencies checked for vulnerabilities ✓
- CodeQL security scan passed ✓
- No security issues found ✓

For detailed information in Russian, see `UPGRADE_GUIDE.md`.
