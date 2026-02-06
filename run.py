import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))


parent_dir = os.path.dirname(current_dir)


sys.path.insert(0, parent_dir)
# -------------------

from fusionbrain import FusionBrain

if __name__ == "__main__":
    print("Initializing FusionBrain System...")

    try:
        agent = FusionBrain()

        agent.repl()
    except KeyboardInterrupt:
        print("\n[System] Shutdown initiated.")
    except Exception as e:
        print(f"\n[System] Critical Startup Error: {e}")
