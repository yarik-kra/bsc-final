import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Error: No product name provided.")
        return
    
    product_name = sys.argv[1]

    # Run GoogleSearch.py with product name
    subprocess.run(["python3", "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/GoogleSearch.py", product_name])

    # Run the rest of the pipeline
    subprocess.run(["python3", "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/GoogleSearchExtraction.py"])
    subprocess.run(["python3", "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/GoogleSearchCleaner.py"])
    subprocess.run(["python3", "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/ContextModelPrep.py"])
    subprocess.run(["python3", "/Users/yarik/Documents/GitHub/bsc-final/AI_Module/GoogleABSA.py"])

if __name__ == "__main__":
    main()
