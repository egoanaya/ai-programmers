import csv
import os
from pathlib import Path
from langsmith import Client

# Connect to LangSmith using the Windows Environment Variable
client = Client(api_key=os.environ["LANGCHAIN_API_KEY"])

# Use the existing Springboard Week 4 dataset
dataset = client.read_dataset(dataset_name="news_dataset_class")

# Check whether the examples have already been imported
existing = next(iter(client.list_examples(dataset_id=dataset.id)), None)

if existing is not None:
    print("Dataset already contains examples. Import skipped.")
else:
    # Read the Springboard's CSV File
    csv_path = Path(__file__).with_name("news_dataset.csv")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        examples = [
            {
                "inputs": {"news": row["news"]},
                "outputs": {"output": row["output"]}
            }
            for row in reader
        ]

    # Upload the Examples into the existing LangSmith Dataset
    client.create_examples(
        dataset_id=dataset.id,
        examples=examples
    )

    print(f"Successfully Imported {len(examples)} Examples!")