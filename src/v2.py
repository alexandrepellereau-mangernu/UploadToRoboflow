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
PROJECTID = "sam3-lqgck"
VERSION = "1"

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

def upload_to_roboflow(image_path, shelfid):
    
    # Upload the image to your project
    #project.upload("UPLOAD_IMAGE.jpg")
    
    resp = project.upload(
        image_path=image_path,
        #batch_name="YOUR_BATCH_NAME",
        #split="train",
        #num_retry_uploads=3,
        tag_names=[shelfid]
        #sequence_number=99,
        #sequence_size=100
    )

    # print("Upload done")

    
def process_row(operationid, left_url, right_url, shelfid):
    for label, url in [("left", left_url), ("right", right_url)]:
        if not url.strip():
            continue

        # print(f"[Ligne {operationid}] Téléchargement {label} : {url}")

        # Download
        img = download_image(url)

        # Rotate
        rotated = rotate_image(img)

        # Save temporarily
        filename = f"ope_{operationid}_{label}_{shelfid}.jpg"
        rotated.save(filename)

        # Upload to Roboflow
        upload_to_roboflow(filename, shelfid)

        # Cleanup
        os.remove(filename)

def main():
    with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))
        total_rows = len(reader)

        with tqdm.tqdm(total=total_rows, desc="Processing", unit="file") as pbar:
            for i, row in enumerate(reader, start=1):
                operationid = row.get("OperationId", "")
                left = row.get("PictureLeft", "")
                right = row.get("PictureRight", "")
                shelfid = "shelf" + row.get("ShelfIndex", "")
                try:
                    process_row(operationid, left, right, shelfid)
                except Exception as e:
                    print(f"Error processing row {operationid}: {e}")
                pbar.update(1)

if __name__ == "__main__":
    main()
