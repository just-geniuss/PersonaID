"""
Camera Configuration File
Modify these settings to customize camera behavior
"""

# Camera index to use (0 = default camera, 1 = second camera, etc.)
# Set to -1 to auto-detect first available camera
CAMERA_INDEX = 0

# Preferred camera resolution (actual resolution may differ based on camera capabilities)
CAMERA_WIDTH = 10000  # High value to get maximum available resolution
CAMERA_HEIGHT = 10000

# Camera backend preference order (for Windows)
# Options: 'DSHOW' (DirectShow), 'MSMF' (Media Foundation), 'ANY'
BACKEND_PREFERENCE = ['DSHOW', 'MSMF', 'ANY']

# Enable verbose camera initialization logging
VERBOSE_LOGGING = True
