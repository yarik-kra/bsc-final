import subprocess

# Run GoogleSearch.py
subprocess.run(["python3", "Data_Collection_Module/GoogleSearchCollection/GoogleSearch.py"])

# Run GoogleSearchExtraction.py
subprocess.run(["python3", "Data_Collection_Module/GoogleSearchCollection/GoogleSearchExtraction.py"])

# Run GoogleSearchCleaner.py
subprocess.run(["python3", "Data_Collection_Module/GoogleSearchCollection/GoogleSearchCleaner.py"])

# Run ContextModelPrep.py
subprocess.run(["python3", "Data_Collection_Module/GoogleSearchCollection/ContextModelPrep.py"])

# Run GoogleABSA.py
subprocess.run(["python3", "AI_Module/GoogleABSA.py"])