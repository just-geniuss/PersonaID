# PersonaID - Complete Installation and Setup Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Project Structure](#project-structure)
4. [Running the System](#running-the-system)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Required Components:

- **Python**: 3.10, 3.11, or 3.12 (3.12 recommended)
- **Docker**: Latest version (for PostgreSQL)
- **Docker Compose**: Version 3.9 or higher
- **Git**: For cloning the repository
- **Camera**: USB camera or built-in webcam

### Operating Systems:

- Windows 10/11
- Linux (Ubuntu 20.04+, Debian 11+)
- macOS (with some limitations)

### Hardware Requirements:

- **CPU**: 4+ cores (recommended)
- **RAM**: Minimum 8 GB (16 GB recommended)
- **Disk Space**: Minimum 5 GB free space

---

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/just-geniuss/PersonaID.git

# Navigate to the project directory
cd PersonaID
```

### Step 2: Install Docker and Docker Compose

#### Windows:

1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Start Docker Desktop
3. Verify Docker is running:
   ```cmd
   docker --version
   docker-compose --version
   ```

#### Linux (Ubuntu/Debian):

```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run: newgrp docker
```

### Step 3: Create Python Virtual Environment

#### Windows:

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### Linux/macOS:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip to the latest version
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

**Note**: Installation may take 10-15 minutes, especially for dlib and other large packages.

### Step 5: Start PostgreSQL via Docker

```bash
# Navigate to Docker configuration directory
cd PostgresDocker

# Start PostgreSQL and pgAdmin
docker-compose -f stack.yml up -d

# Check that containers are running
docker ps
```

You should see two running containers:
- `postgres_container` (port 5432)
- `pgadmin_container` (port 5050)

### Step 6: Initialize Database

```bash
# Return to project root directory
cd ..

# Wait 10-15 seconds for PostgreSQL to fully start

# Create database tables
docker exec -i postgres_container psql -U personauser -d personadb < PostgresDocker/DokerCommand.txt
```

**Database connection parameters:**
- **Host**: 127.0.0.1
- **Port**: 5432
- **Database**: personadb
- **User**: personauser
- **Password**: pgpwd4persona

### Step 7: Create Required Directories

```bash
# Create directories for photos and frames
mkdir -p photo new del capture
```

**Directory descriptions:**
- `photo/` - Store photos for face recognition
- `new/` - New photos for training the system
- `del/` - Deleted photos
- `capture/` - Captured frames from camera

### Step 8: Add Photos for Recognition

```bash
# Place photos of people in the photo/ directory
# Naming format: FirstName_LastName.jpg or Name_Surname.jpg
# Example: John_Doe.jpg, Maria_Smith.jpg

# Each photo should contain a clear face image
# Recommended format: JPG, PNG
# Recommended resolution: 640x480 or higher
```

### Step 9: Configure Camera (Optional)

Edit `camera_config.py` to configure camera parameters:

```python
# Camera index (0 = first camera, 1 = second, etc.)
CAMERA_INDEX = 0

# Preferred resolution
CAMERA_WIDTH = 10000
CAMERA_HEIGHT = 10000

# Verbose logging
VERBOSE_LOGGING = True
```

### Step 10: Test Camera

```bash
# Test the camera before running the system
python util/test_cam.py
```

If the camera works correctly, you'll see:
- Messages about camera connection attempts
- Video from the camera in a separate window
- Press 'q' to exit

---

## Project Structure

```
PersonaID/
├── App.py                    # Flask web server for API
├── bot.py                    # Telegram bot (optional)
├── bot_config.py             # Bot configuration
├── camera_config.py          # Camera configuration
├── capture_streamer.py       # Video capture from camera
├── process.py                # Face processing and recognition
├── start_capture.py          # Start capture module
├── start_proc.py             # Start processing module
├── zdata.py                  # Data and embeddings management
├── cleanerDB.py              # Database cleanup
├── requirements.txt          # Python dependencies
│
├── PostgresDocker/           # PostgreSQL configuration
│   ├── stack.yml            # Docker Compose config
│   ├── DokerCommand.txt     # SQL commands for table creation
│   └── tables_sql.sql       # Database schema
│
├── photo/                    # Photos for recognition
├── new/                      # New photos for training
├── del/                      # Deleted photos
├── capture/                  # Captured frames
│
├── util/                     # Utilities
│   └── test_cam.py          # Camera test
│
├── README.md                 # Main documentation (Russian)
├── INSTALLATION_EN.md        # This file
├── UPGRADE_GUIDE.md          # Upgrade guide (Russian)
└── UPGRADE_GUIDE_EN.md       # Upgrade guide (English)
```

---

## Running the System

### Full System Launch

To run the face recognition system, you need to start **three components** in separate terminals:

#### Terminal 1: Start Video Capture Module

```bash
# Activate virtual environment (if not active)
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate      # Windows

# Start capture module
python start_capture.py
```

**What this module does:**
- Captures video from camera
- Detects faces in frames
- Saves frames to database for processing
- Creates virtual camera (pyvirtualcam)

#### Terminal 2: Start Processing and Recognition Module

```bash
# Activate virtual environment (if not active)
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate      # Windows

# Start processing module
python start_proc.py
```

**What this module does:**
- Retrieves frames from database
- Recognizes faces using face_recognition
- Compares with embeddings from database
- Saves results to zdash table

#### Terminal 3: Start Web Server API

```bash
# Activate virtual environment (if not active)
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate      # Windows

# Start Flask web server
python App.py
```

**What this module does:**
- Provides REST API for web interface
- Returns recognition results
- Serves photos and captured frames
- Available at: http://localhost:5000

### System Health Check

After starting all three components:

1. **Check API:**
   ```bash
   curl http://localhost:5000/
   ```
   Should return: `FaceRecog Items: N` (where N is the number of recognized faces)

2. **Check pgAdmin:**
   - Open browser: http://localhost:5050
   - Email: rusal@bk.ru
   - Password: pgadminpwd4persona
   - Connect to personadb database

3. **Check Virtual Camera:**
   - Open video conferencing app (Zoom, Teams, Skype)
   - Select "OBS Virtual Camera" in video settings
   - You should see video with face recognition

### Stopping the System

```bash
# In each terminal, press Ctrl+C to stop the process

# Stop Docker containers
cd PostgresDocker
docker-compose -f stack.yml down
```

---

## Configuration

### Camera Configuration

Edit `camera_config.py`:

```python
# Camera selection
CAMERA_INDEX = 0        # 0 = first camera, 1 = second, etc.

# Camera resolution
CAMERA_WIDTH = 10000    # Max width (limited by camera)
CAMERA_HEIGHT = 10000   # Max height (limited by camera)

# Logging
VERBOSE_LOGGING = True  # True = verbose logs, False = minimal
```

### Database Configuration

To change PostgreSQL connection parameters, edit:

**In Python files** (App.py, capture_streamer.py, process.py, zdata.py):
```python
connection = psycopg2.connect(
    user="personauser", 
    password="pgpwd4persona",
    host="127.0.0.1", 
    port="5432",
    database="personadb"
)
```

**In Docker Compose** (`PostgresDocker/stack.yml`):
```yaml
environment:
  POSTGRES_DB: "personadb"
  POSTGRES_USER: "personauser"
  POSTGRES_PASSWORD: "pgpwd4persona"
```

### Recognition Parameters

In `process.py`:

```python
max_face_distance = 0.5  # Recognition threshold (0.0-1.0)
                         # Lower = stricter, higher = looser
                         # Recommended: 0.4-0.6
```

In `capture_streamer.py`:

```python
detection_score = 0.4       # Face detection threshold (0.0-1.0)
minDetectionCon = 0.6       # Minimum detection confidence
number_of_processing_frame = 7  # Process every Nth frame
```

---

## Troubleshooting

### Issue: Camera Not Detected

**Solution:**

1. Check camera connection:
   ```bash
   python util/test_cam.py
   ```

2. Try different camera index in `camera_config.py`:
   ```python
   CAMERA_INDEX = 1  # or 2, 3...
   ```

3. Close other applications using the camera (Zoom, Skype, etc.)

4. On Linux, add user to video group:
   ```bash
   sudo usermod -a -G video $USER
   # Log out and log back in
   ```

### Issue: Database Connection Error

**Solution:**

1. Check that Docker containers are running:
   ```bash
   docker ps
   ```

2. Restart PostgreSQL:
   ```bash
   cd PostgresDocker
   docker-compose -f stack.yml restart
   ```

3. Check container logs:
   ```bash
   docker logs postgres_container
   ```

### Issue: Dependency Installation Errors

**Solution for dlib on Windows:**

```cmd
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/

# Or use prebuilt wheel:
pip install dlib==19.24.6
```

**Solution for Linux:**

```bash
# Install required system packages
sudo apt-get install -y build-essential cmake
sudo apt-get install -y libopencv-dev python3-opencv
```

### Issue: ModuleNotFoundError

**Solution:**

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Faces Not Recognized

**Solution:**

1. Check photo quality in `photo/` folder:
   - Clear face image
   - Good lighting
   - Face occupies most of the frame

2. Make sure system is trained:
   - Place photos in `new/` folder
   - System will automatically process them after 75 frames

3. Adjust recognition threshold in `process.py`:
   ```python
   max_face_distance = 0.6  # Increase for looser recognition
   ```

---

## Web Client (JS React)

The web client in JavaScript React is located in the file `Sourcecode Front web React Client.zip`

To run the web interface:

1. Extract `Sourcecode Front web React Client.zip`
2. Follow instructions in README inside the archive
3. Make sure Flask API (App.py) is running and accessible

---

## Additional Information

### Documentation:

- **README.md** - Main documentation (Russian)
- **UPGRADE_GUIDE.md** - Detailed upgrade guide (Russian)
- **UPGRADE_GUIDE_EN.md** - Upgrade guide (English)
- **CHANGES_SUMMARY.md** - Complete changelog

### Support:

If you encounter issues:

1. Check logs in each module's console
2. Review documentation in project folder
3. Ensure all dependencies are installed correctly
4. Verify Docker containers are running

### Technical Specifications:

- **Recognition libraries**: face_recognition, dlib, OpenCV, mediapipe
- **Web framework**: Flask 3.1.0 + Flask-CORS 5.0.0
- **Database**: PostgreSQL 14.4
- **Virtual camera**: pyvirtualcam 0.12.0
- **Python**: 3.10+ (tested with 3.12.3)

---

## License

See LICENSE file in the project root.

---

**Last updated:** 2024-12-19
