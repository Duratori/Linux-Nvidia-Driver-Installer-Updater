# Linux NVIDIA Driver Check

A Python utility to check NVIDIA driver installation status, version, and GPU information. Automatically checks for updates and can download/install newer drivers.

## Features

- ✅ Verify NVIDIA driver installation
- 📊 Display driver version
- 🎮 Show GPU name and specifications
- 💾 Display CUDA version
- 📈 Show GPU memory usage (total, used, free)
- 🔄 Automatically check for driver updates from NVIDIA's website
- 📥 Download and install newer drivers automatically
- 🆕 Install NVIDIA drivers from scratch when none are detected (fresh installation)

## Requirements

- Python 3.6 or higher
- NVIDIA GPU (drivers optional - tool can install them for you)
- Internet connection (for checking updates and downloading drivers)
- Linux system (uses NVIDIA's Linux driver server)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd nvidia-driver-check
```

2. No additional Python packages required (uses only standard library)

## Usage

### Basic Usage (with automatic update check)

Run the script to check your current NVIDIA driver status and automatically check for updates:

```bash
python3 nvidia_check.py
```

Or make it executable and run:

```bash
chmod +x nvidia_check.py
./nvidia_check.py
```

The script will:
1. Display your current driver version and GPU information
2. Check NVIDIA's website for the latest available driver
3. Compare versions and notify you if an update is available
4. Offer to download and install the update if desired

### Skip Update Check

To only display current driver information without checking for updates:

```bash
python3 nvidia_check.py --skip-update-check
```

## Example Output

### With Update Available

```
============================================================
NVIDIA Driver Check
============================================================

✅ NVIDIA driver is installed

Driver Version: 580.105.08

GPU Information:
------------------------------------------------------------
  GPU Name:       NVIDIA GeForce GTX 1660 Ti
  Memory Total:   6144 MiB
  Memory Used:    0 MiB
  Memory Free:    5749 MiB

🔍 Checking for driver updates...
Current version: 580.105.08
Latest version:  581.80

🆕 A newer driver version is available!

Would you like to download and install it? (yes/no): yes
📥 Downloading driver...
URL: https://...
This may take several minutes...
File size: 345.2 MB
Progress: 100.0%
✅ Downloaded to: /tmp/.../NVIDIA-Linux-x86_64-581.80.run

⚠️  Driver installation requires root privileges
The installer will run: sudo /tmp/.../NVIDIA-Linux-x86_64-581.80.run

Proceed with installation? (yes/no): 
```

### When Up to Date

```
============================================================
NVIDIA Driver Check
============================================================

✅ NVIDIA driver is installed

Driver Version: 581.80

GPU Information:
------------------------------------------------------------
  GPU Name:       NVIDIA GeForce GTX 1660 Ti
  Memory Total:   6144 MiB
  Memory Used:    0 MiB
  Memory Free:    5749 MiB

🔍 Checking for driver updates...
Current version: 581.80
Latest version:  581.80

✅ Your driver is up to date

============================================================
```

### When NVIDIA Driver is Not Found (Fresh Installation)

```
============================================================
NVIDIA Driver Check
============================================================

❌ NVIDIA driver not found or nvidia-smi not available

Would you like to install the latest NVIDIA driver?

🔍 Fetching latest NVIDIA driver version...
Latest available version: 580.105.08

Would you like to download and install it? (yes/no): yes
📥 Downloading driver...
URL: https://download.nvidia.com/XFree86/Linux-x86_64/580.105.08/NVIDIA-Linux-x86_64-580.105.08.run
This may take several minutes...
File size: 345.2 MB
Progress: 100.0%
✅ Downloaded to: /tmp/.../NVIDIA-Linux-x86_64-580.105.08.run

⚠️  Driver installation requires root privileges
The installer will run: sudo /tmp/.../NVIDIA-Linux-x86_64-580.105.08.run

Proceed with installation? (yes/no): yes

🚀 Starting driver installation...
Note: This will likely require X server to be stopped.

[Installation proceeds...]

✅ Driver installation completed successfully!
⚠️  You may need to reboot your system for changes to take effect.
============================================================
```

## How It Works

The script uses NVIDIA's official Linux driver server (`download.nvidia.com/XFree86/Linux-x86_64/`) to fetch and install drivers. It queries the `latest.txt` endpoint to determine the newest Production Branch driver version available for Linux systems.

**Key Features:**
- Uses only Python standard library (no pip dependencies)
- All GPU information obtained via `nvidia-smi` command-line queries
- Downloads `.run` installer files directly from NVIDIA's servers
- Automatic timeout handling (5s for nvidia-smi, 10s for web requests, 10min for installation)
- Temporary file management with automatic cleanup
- Two-stage user confirmation (download and installation) for safety

## Exit Codes

- `0`: Success - NVIDIA driver found and working, or installation completed successfully
- `1`: Failure - NVIDIA driver not found and installation declined/failed, or error occurred

## Safety Notes

- Driver installation requires root/sudo privileges
- The installer may require stopping your X server (graphical environment)
- A system reboot is typically required after driver installation
- Consider backing up important data before installing or updating drivers
- Downloads come directly from NVIDIA's official Linux driver server
- Two confirmation prompts (download and installation) protect against accidental changes
- Downloaded files are stored in temporary directories and automatically cleaned up

## Command Line Options

- `--skip-update-check`: Skip checking for driver updates (only show current info)
- `--help`: Show help message and exit

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
