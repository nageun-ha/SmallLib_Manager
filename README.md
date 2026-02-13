# SmallLib_Manager
A Python-based lightweight library management system featuring real-time barcode scanning with OpenCV.
# SmallLib Manager 📚
**A Python-based lightweight library management system featuring real-time barcode scanning.**

This project is a practical tool designed for small-scale libraries or personal book collections. It focuses on high utility and logical structure, using **OpenCV** for seamless barcode-based check-in/out.

## 💻 Environment & Compatibility
* **Language**: Python 3.12
* **Development OS**: macOS (Apple Silicon optimized)
* **Special Note**: This system includes a specific patch for the `zbar` library path on macOS, ensuring it works out of the box for Mac users using Homebrew (Homebrew paths: `/opt/homebrew/lib/libzbar.dylib` or `/usr/local/lib/libzbar.dylib`).

## 🚀 Key Features
* **Real-time Barcode Scanning**: Fast book identification using a webcam and `pyzbar`.
* **Inventory Management**: Efficient book registration and tracking via a structured CSV database.
* **Loan & Return System**: 
    * Automated due-date calculation (14-day loan period).
    * Real-time status updates (Available/Borrowed/Overdue).
* **Overdue Tracking**: Integrated logic to monitor overdue items based on the current system date.

## 🛠 Tech Stack
* **OpenCV (cv2)**: Image processing and camera control.
* **pyzbar**: Barcode decoding logic.
* **CSV**: Lightweight and portable data storage (`books.csv`).
* **Datetime**: Handling loan periods and overdue calculations.

## 📋 Installation & Usage

### 1. Requirements
Install the necessary Python libraries:
```bash
pip install opencv-python pyzbar

brew install zbar
