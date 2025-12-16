import csv
import requests
import os
import tqdm

from PIL import Image
from io import BytesIO
from roboflow import Roboflow


# ---------------------------
# CONFIGURATION ROBOFLOW
# ---------------------------
ROBOFLOW_API_KEY = "wHviEkEcARlfONcsGn1t"
WORKSPACEID = "nushelf"
PROJECTID = "temporary-experiments"
VERSION = "1"

START_INDEX = 0
END_INDEX = 10

# ---------------------------
# FICHIER CSV À LIRE
# ---------------------------
CSV_FILE = "data/v2.csv"

# Initialize the Roboflow object with your API key
rf = Roboflow(api_key=ROBOFLOW_API_KEY)

# Retrieve your current workspace and project name
print(rf.workspace())

# Specify the project for upload
# let's you have a project at https://app.roboflow.com/my-workspace/my-project
project = rf.workspace(WORKSPACEID).project(PROJECTID)


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def rotate_image(img):
    return img.rotate(180, expand=True)

def upload_to_roboflow(image_path):
    
    # Upload the image to your project
    #project.upload("UPLOAD_IMAGE.jpg")
    
    resp = project.upload(
        image_path=image_path,
        #batch_name="YOUR_BATCH_NAME",
        #split="train",
        #num_retry_uploads=3,
        #tag_names=[shelfid]
        #sequence_number=99,
        #sequence_size=100
    )

    # print("Upload done")

    
def process_row(operationId, left_before_url, right_before_url, left_after_url, right_after_url):
    for label, url in [("left_before", left_before_url), ("right_before", right_before_url), ("left_after", left_after_url), ("right_after", right_after_url)]:
        if not url.strip():
            continue

        # print(f"[Ligne {operationId}] Téléchargement {label} : {url}")

        # Download
        img = download_image(url)

        # Rotate
        rotated = rotate_image(img)

        # Get image camera
        camera = url.split("/")[-1].split(".")[0]  # Extract filename without extension

        # Save temporarily
        filename = f"temp/ope_{operationId}_{camera}.jpg"
        rotated.save(filename)

        # Upload to Roboflow
        upload_to_roboflow(filename)

        # Cleanup
        os.remove(filename)

def main():
    with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))
        total_rows = len(reader)

        with tqdm.tqdm(total=total_rows, desc="Processing", unit="file") as pbar:
            for i, row in enumerate(reader, start=1):
                while i < START_INDEX:
                    continue  # Skip until row START_INDEX for resuming purposes
                if i > END_INDEX:
                    break  # Stop processing after END_INDEX

                operationId = row.get("OperationId", "")
                left_before = row.get("PictureLeftBefore", "")
                right_before = row.get("PictureRightBefore", "")
                left_after = row.get("PictureLeftAfter", "")
                right_after = row.get("PictureRightAfter", "")
                try:
                    process_row(operationId, left_before, right_before, left_after, right_after)
                except Exception as e:
                    print(f"Error processing row {operationId}: {e}")
                pbar.update(1)

if __name__ == "__main__":
    main()
