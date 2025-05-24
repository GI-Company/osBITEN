# backend/peripheral_scanner.py
import platform
import logging

logger = logging.getLogger('Peripheral_Scanner')

# Conditional imports for external libraries
# These might need to be installed on the user's system for full functionality
try:
  import usb.core
  import usb.util
  USB_ENABLED = True
  logger.info("pyusb imported successfully.")
except ImportError:
  USB_ENABLED = False
  logger.warning("pyusb not found. USB device scanning will be disabled. Install with 'pip install pyusb'. Also ensure libusb is installed on your OS.")

try:
  import cv2
  CAMERA_ENABLED = True
  logger.info("opencv-python imported successfully.")
except ImportError:
  CAMERA_ENABLED = False
  logger.warning("opencv-python not found. Camera device scanning will be disabled. Install with 'pip install opencv-python'.")

try:
  import pyaudio
  MIC_ENABLED = True
  logger.info("pyaudio imported successfully.")
except ImportError:
  MIC_ENABLED = False
  logger.warning("pyaudio not found. Microphone device scanning will be disabled. Install with 'pip install PyAudio'.")

class PeripheralScanner:
  def __init__(self):
    logger.info("Peripheral Scanner initialized.")
    self.virtual_driver_status = {
      "status": "active",
      "device_name": "OBPI USB-C Hub (Simulated HDMI/USB)",
      "driver_version": "1.0.25-obpi",
      "display_out": "Connected (Conceptual 4K@60Hz)",
      "ports": {
        "usb_a_2_0_kb_mouse": "Connected (Virtual Keyboard, Mouse)",
        "usb_a_3_0_hdd": "Available",
        "usb_c_pd_3_0_power": "Connected (Power Delivery)"
      },
      "notes": "This driver status is simulated to represent a complex peripheral."
    }

  def get_system_info(self):
    logger.info("Scanning system information.")
    info = {
      "os_name": platform.system(),
      "os_version": platform.version(),
      "architecture": platform.machine(),
      "python_version": platform.python_version(),
      "virtual_driver_status": self.virtual_driver_status
    }

    # Add CPU/RAM info (conceptual, or use psutil if installed)
    try:
      import psutil
      info["total_memory_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
      info["available_memory_gb"] = round(psutil.virtual_memory().available / (1024**3), 2)
      info["cpu_percent_usage"] = psutil.cpu_percent(interval=1) # Get real-time CPU usage
      info["total_cpu_cores"] = psutil.cpu_count(logical=True)
      info["physical_cpu_cores"] = psutil.cpu_count(logical=False)
      logger.info("psutil imported and system info collected.")
    except ImportError:
      logger.warning("psutil not found. CPU/RAM info will be simulated. Install with 'pip install psutil'.")
      info["total_memory_gb"] = 16.0
      info["available_memory_gb"] = 8.0
      info["cpu_percent_usage"] = 25.5
      info["total_cpu_cores"] = 8
      info["physical_cpu_cores"] = 4
      info["simulated_stats_note"] = "CPU/RAM stats are simulated (install psutil for real data)."

    return info

  def get_usb_devices(self):
    logger.info("Scanning USB devices.")
    devices_info = []
    if USB_ENABLED:
      try:
        # find all USB devices
        devs = usb.core.find(find_all=True)

        if devs is None:
          logger.warning("No USB devices found by pyusb.")
          return {"devices": [], "error": None}

        for dev in devs:
          try:
            manufacturer = usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else "N/A"
            product = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else "Unknown Device"
            serial_number = usb.util.get_string(dev, dev.iSerialNumber) if dev.iSerialNumber else "N/A"

            # Attempt to determine device type based on class codes
            device_type = "Other"
            if dev.bDeviceClass == 0x01: device_type = "Audio"
            elif dev.bDeviceClass == 0x02: device_type = "Communication"
            elif dev.bDeviceClass == 0x03: device_type = "HID (Keyboard/Mouse)"
            elif dev.bDeviceClass == 0x06: device_type = "Imaging (Camera/Scanner)"
            elif dev.bDeviceClass == 0x07: device_type = "Printer"
            elif dev.bDeviceClass == 0x08: device_type = "Mass Storage"
            elif dev.bDeviceClass == 0x09: device_type = "Hub"
            elif dev.bDeviceClass == 0x0A: device_type = "CDC Data"
            elif dev.bDeviceClass == 0x0B: device_type = "Chipcard"
            elif dev.bDeviceClass == 0x0D: device_type = "Content Security"
            elif dev.bDeviceClass == 0x0E: device_type = "Video"
            elif dev.bDeviceClass == 0x0F: device_type = "Personal Healthcare"
            elif dev.bDeviceClass == 0xDC: device_type = "Diagnostic"
            elif dev.bDeviceClass == 0xE0: device_type = "Wireless Controller"
            elif dev.bDeviceClass == 0xEF: device_type = "Miscellaneous"
            elif dev.bDeviceClass == 0xFF: device_type = "Vendor Specific"


            devices_info.append({
              "vendor_id": hex(dev.idVendor),
              "product_id": hex(dev.idProduct),
              "bus": dev.bus,
              "address": dev.address,
              "manufacturer": manufacturer,
              "product": product,
              "serial_number": serial_number,
              "device_type": device_type,
              "raw_class": hex(dev.bDeviceClass)
            })
          except Exception as e:
            logger.error(f"Error processing USB device {dev}: {e}")
            devices_info.append({
              "error": str(e),
              "vendor_id": hex(dev.idVendor) if hasattr(dev, 'idVendor') else 'N/A',
              "product_id": hex(dev.idProduct) if hasattr(dev, 'idProduct') else 'N/A',
              "product": "Error reading device info"
            })
        logger.info(f"Found {len(devices_info)} USB devices.")
        return {"devices": devices_info, "error": None}
      except Exception as e:
        logger.error(f"Error during USB scan: {e}")
        return {"devices": [], "error": f"USB scan failed: {e}. Ensure libusb is installed and permissions are set."}
    else:
      return {"devices": [], "error": "pyusb not installed or failed to import. USB scanning disabled."}

  def get_camera_devices(self):
    logger.info("Scanning camera devices.")
    cameras = []
    if CAMERA_ENABLED:
      try:
        # Test index 0 to 10 for cameras
        for i in range(10):
          cap = cv2.VideoCapture(i)
          if cap.isOpened():
            # A rudimentary way to get a 'name' - depends on OS/driver
            # On some systems, cap.get(cv2.CAP_PROP_POS_FRAMES) might be 0, indicating success but no unique name
            # More robust would involve platform-specific APIs (e.g., DirectShow on Windows, AVFoundation on macOS)
            cameras.append({
              "id": i,
              "name": f"Camera {i}", # Placeholder name
              "status": "Available"
            })
            cap.release()
        logger.info(f"Found {len(cameras)} camera devices.")
        return {"devices": cameras, "error": None}
      except Exception as e:
        logger.error(f"Error during camera scan: {e}")
        return {"devices": [], "error": f"Camera scan failed: {e}. Check opencv-python installation."}
    else:
      return {"devices": [], "error": "opencv-python not installed. Camera scanning disabled."}

  def get_microphone_devices(self):
    logger.info("Scanning microphone devices.")
    mics = []
    if MIC_ENABLED:
      try:
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')

        for i in range(num_devices):
          device_info = p.get_device_info_by_host_api_device_index(0, i)
          if device_info.get('maxInputChannels') > 0:
            mics.append({
              "id": i,
              "name": device_info.get('name'),
              "status": "Available"
            })
        p.terminate()
        logger.info(f"Found {len(mics)} microphone devices.")
        return {"devices": mics, "error": None}
      except Exception as e:
        logger.error(f"Error during microphone scan: {e}")
        return {"devices": [], "error": f"Microphone scan failed: {e}. Check PyAudio installation and audio drivers."}
    else:
      return {"devices": [], "error": "PyAudio not installed. Microphone scanning disabled."}

# Global PeripheralScanner instance (or initialize in main.py)
# peripheral_scanner = PeripheralScanner()
