
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
# from email_generator_gui_pyqt_v2 import SOCEmailGeneratorApp
from main_gui import SOCEmailGeneratorApp


def main():
    try:
        print("[main] Starting application...")
        app = QApplication(sys.argv)

        try:
            app.setWindowIcon(QIcon("assets/mail.ico"))
        except Exception:
            pass  # icon is optional

        window = SOCEmailGeneratorApp()
        window.show()
        sys.exit(app.exec_())      # PyQt6: app.exec()

    except Exception as e:
        print(f"[main][ERROR] {e}")


if __name__ == "__main__":
    print("=== SOC Security News Email Generator (Outlook) ===")
    main()