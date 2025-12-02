#!/usr/bin/env python3
"""
NVIDIA Driver Check Tool
A utility to check NVIDIA driver installation and version information.
"""

import subprocess
import sys
import re
import os
import stat
import tempfile
from typing import Optional, Dict
from urllib.request import urlopen, Request
from urllib.error import URLError


class NvidiaDriverCheck:
    """Check NVIDIA driver installation and version."""
    
    # NVIDIA Linux driver download endpoints
    NVIDIA_LINUX_LATEST_URL = "https://download.nvidia.com/XFree86/Linux-x86_64/latest.txt"
    NVIDIA_LINUX_DOWNLOAD_BASE = "https://download.nvidia.com/XFree86/Linux-x86_64"
    
    def check_nvidia_smi(self) -> bool:
        """Check if nvidia-smi is available."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_driver_version(self) -> Optional[str]:
        """Get NVIDIA driver version."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
    
    def get_gpu_info(self) -> Dict[str, str]:
        """Get detailed GPU information."""
        info = {}
        try:
            # Get GPU name
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['gpu_name'] = result.stdout.strip()
            
            # Get CUDA version
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=cuda_version', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['cuda_version'] = result.stdout.strip()
            
            # Get memory info
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                memory_parts = result.stdout.strip().split(', ')
                if len(memory_parts) == 3:
                    info['memory_total'] = memory_parts[0]
                    info['memory_used'] = memory_parts[1]
                    info['memory_free'] = memory_parts[2]
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return info
    
    def get_latest_driver_version(self) -> Optional[str]:
        """Fetch the latest NVIDIA Linux driver version from NVIDIA's server."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            
            req = Request(self.NVIDIA_LINUX_LATEST_URL, headers=headers)
            with urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8').strip()
                # Format: "580.105.08 580.105.08/NVIDIA-Linux-x86_64-580.105.08.run"
                # First part is the version
                parts = content.split()
                if parts:
                    return parts[0]
                
        except (URLError, Exception) as e:
            print(f"⚠️  Could not fetch latest driver version: {e}")
        
        return None
    
    def compare_versions(self, current: str, latest: str) -> int:
        """
        Compare two version strings.
        Returns: 1 if latest > current, 0 if equal, -1 if current > latest
        """
        def version_tuple(v):
            # Remove any non-numeric parts and split
            parts = re.findall(r'\d+', v)
            return tuple(map(int, parts))
        
        try:
            current_tuple = version_tuple(current)
            latest_tuple = version_tuple(latest)
            
            if latest_tuple > current_tuple:
                return 1
            elif latest_tuple == current_tuple:
                return 0
            else:
                return -1
        except (ValueError, AttributeError):
            return 0
    
    def get_download_url(self, version: str) -> str:
        """Get the download URL for a specific driver version."""
        return f"{self.NVIDIA_LINUX_DOWNLOAD_BASE}/{version}/NVIDIA-Linux-x86_64-{version}.run"
    
    def download_driver(self, url: str, dest_path: str) -> bool:
        """Download driver file from URL."""
        try:
            print(f"📥 Downloading driver...")
            print(f"URL: {url}")
            print("This may take several minutes...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            
            req = Request(url, headers=headers)
            with urlopen(req, timeout=300) as response:
                file_size = response.headers.get('Content-Length')
                if file_size:
                    file_size = int(file_size)
                    print(f"File size: {file_size / (1024*1024):.1f} MB")
                
                with open(dest_path, 'wb') as f:
                    chunk_size = 8192
                    downloaded = 0
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if file_size:
                            progress = (downloaded / file_size) * 100
                            print(f"\rProgress: {progress:.1f}%", end='', flush=True)
                
                print()  # New line after progress
                print(f"✅ Downloaded to: {dest_path}")
                
                # Make executable
                os.chmod(dest_path, os.stat(dest_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                return True
                
        except (URLError, Exception) as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def install_driver(self, driver_path: str) -> bool:
        """Execute the driver installer."""
        print()
        print("⚠️  Driver installation requires root privileges")
        print(f"The installer will run: sudo {driver_path}")
        print()
        response = input("Proceed with installation? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("Installation cancelled.")
            return False
        
        try:
            print()
            print("🚀 Starting driver installation...")
            print("Note: This will likely require X server to be stopped.")
            print()
            
            # Run the installer with sudo
            result = subprocess.run(
                ['sudo', driver_path],
                timeout=600  # 10 minute timeout for installation
            )
            
            if result.returncode == 0:
                print()
                print("✅ Driver installation completed successfully!")
                print("⚠️  You may need to reboot your system for changes to take effect.")
                return True
            else:
                print(f"❌ Installation failed with exit code: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Installation timed out")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    
    def _download_and_install_driver(self, version: str) -> bool:
        """Download and install a specific driver version. Returns True on success."""
        download_url = self.get_download_url(version)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            driver_filename = f"NVIDIA-Linux-x86_64-{version}.run"
            driver_path = os.path.join(temp_dir, driver_filename)
            
            if self.download_driver(download_url, driver_path):
                return self.install_driver(driver_path)
            else:
                print("❌ Download failed. Please try manually:")
                print("Visit: https://www.nvidia.com/Download/index.aspx")
                return False
    
    def install_fresh_driver(self) -> bool:
        """Install NVIDIA driver when none is currently installed."""
        print()
        print("🔍 Fetching latest NVIDIA driver version...")
        latest_version = self.get_latest_driver_version()
        
        if not latest_version:
            print("⚠️  Could not determine latest driver version")
            print("Please check manually at: https://www.nvidia.com/Download/index.aspx")
            return False
        
        print(f"Latest available version: {latest_version}")
        print()
        response = input("Would you like to download and install it? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("Installation cancelled. To install manually, visit:")
            print("https://www.nvidia.com/Download/index.aspx")
            return False
        
        return self._download_and_install_driver(latest_version)
    
    def check_for_updates(self) -> None:
        """Check for driver updates and offer to download/install."""
        current_version = self.get_driver_version()
        if not current_version:
            print("⚠️  Cannot check for updates - current driver version unknown")
            return
        
        print()
        print("🔍 Checking for driver updates...")
        latest_version = self.get_latest_driver_version()
        
        if not latest_version:
            print("⚠️  Could not determine latest driver version")
            print("Please check manually at: https://www.nvidia.com/Download/index.aspx")
            return
        
        print(f"Current version: {current_version}")
        print(f"Latest version:  {latest_version}")
        print()
        
        comparison = self.compare_versions(current_version, latest_version)
        
        if comparison < 0:
            print("✅ Your driver is up to date (or newer than latest release)")
        elif comparison == 0:
            print("✅ Your driver is up to date")
        else:
            print("🆕 A newer driver version is available!")
            print()
            response = input("Would you like to download and install it? (yes/no): ").strip().lower()
            
            if response == 'yes':
                self._download_and_install_driver(latest_version)
            else:
                print("Update cancelled. To update manually, visit:")
                print("https://www.nvidia.com/Download/index.aspx")
    
    def run_check(self, skip_update_check: bool = False) -> int:
        """Run the complete driver check."""
        print("=" * 60)
        print("NVIDIA Driver Check")
        print("=" * 60)
        print()
        
        # Check if nvidia-smi exists
        if not self.check_nvidia_smi():
            print("❌ NVIDIA driver not found or nvidia-smi not available")
            print("\nWould you like to install the latest NVIDIA driver?")
            
            if self.install_fresh_driver():
                print("\n✅ Installation process completed!")
                print("⚠️  Please reboot your system and run this tool again to verify.")
                return 0
            else:
                print("\nFor manual installation, visit:")
                print("https://www.nvidia.com/Download/index.aspx")
                return 1
        
        print("✅ NVIDIA driver is installed")
        print()
        
        # Get driver version
        driver_version = self.get_driver_version()
        if driver_version:
            print(f"Driver Version: {driver_version}")
        
        # Get GPU info
        gpu_info = self.get_gpu_info()
        if gpu_info:
            print()
            print("GPU Information:")
            print("-" * 60)
            if 'gpu_name' in gpu_info:
                print(f"  GPU Name:       {gpu_info['gpu_name']}")
            if 'cuda_version' in gpu_info:
                print(f"  CUDA Version:   {gpu_info['cuda_version']}")
            if 'memory_total' in gpu_info:
                print(f"  Memory Total:   {gpu_info['memory_total']}")
                print(f"  Memory Used:    {gpu_info['memory_used']}")
                print(f"  Memory Free:    {gpu_info['memory_free']}")
        
        # Check for updates by default (unless explicitly skipped)
        if not skip_update_check:
            self.check_for_updates()
        
        print()
        print("=" * 60)
        return 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check NVIDIA driver status and version')
    parser.add_argument(
        '--skip-update-check',
        action='store_true',
        help='Skip checking for driver updates (only show current info)'
    )
    
    args = parser.parse_args()
    
    checker = NvidiaDriverCheck()
    sys.exit(checker.run_check(skip_update_check=args.skip_update_check))


if __name__ == '__main__':
    main()
