import subprocess
import sys
import platform

REQUIREMENTS = [
    "SpeechRecognition",
    "PyAudio",
    "pywin32",
    "pyttsx3",
    "openai==0.27.8",
    "wikipedia==1.4.0",
]


def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        print(f"[+] Installed {package}")

    except subprocess.CalledProcessError:
        print(f"[-] Failed to install {package}")


def check_system():

    system = platform.system()

    print(f"[+] Detected system: {system}")

    if system == "Linux":
        print("[!] Linux detected.")
        print("[!] You may need to install PortAudio manually:")
        print("    sudo apt install portaudio19-dev")

    elif system == "Darwin":
        print("[+] macOS detected.")

    elif system == "Windows":
        print("[+] Windows detected.")


def main():

    print("""
===========================
      Zeus Installer
===========================
""")

    check_system()

    print("\n[+] Installing dependencies...\n")

    for package in REQUIREMENTS:
        install(package)

    print("""
===========================
 Installation Completed!
===========================

You can run Zeus now.
""")


if __name__ == "__main__":
    main()
