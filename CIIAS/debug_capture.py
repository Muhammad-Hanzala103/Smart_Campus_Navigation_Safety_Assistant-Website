import sys
import traceback
import os

log_path = os.path.join(os.getcwd(), 'crash.log')

try:
    with open(log_path, 'w') as f:
        f.write("Starting debug...\n")
        try:
            from app import create_app
            app = create_app()
            f.write("App created successfully.\n")
        except Exception as e:
            f.write("Caught exception:\n")
            traceback.print_exc(file=f)
            print("Exception captured to crash.log")
except Exception as wrapper_e:
    print(f"Wrapper failed: {wrapper_e}")
