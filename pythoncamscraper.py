# %%
from datetime import datetime
import os
import pandas as pd
import pytz
import requests
import traceback


def create_directories(img_dir, camera_ids):
    for camera in camera_ids:
        path = os.path.join(img_dir, camera)

        if not os.path.exists(path):
            print(f"Creating path for camera {camera}")
            os.makedirs(path)
        else:
            print(f"Path for camera {camera} exists")


def capture_camera(row):
    camera_id = row["camera_id"]
    img_dir = row["img_dir"]
    url_front = row["url_front"]
    img_type = row["img_type"]

    time_zone = pytz.timezone("America/Denver")
    timestamp = (
        datetime
            .now()
            .astimezone(time_zone)
            .strftime("%Y-%m-%d-%H-%M-%S")
            #.isoformat().replace(":", "-") # cleaner alternative in the future
    )
    print(f"Capture at {timestamp}")

    url = f"{url_front} {camera_id}"
    print(url)

    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        img_path = os.path.join(img_dir, camera_id, f"{timestamp}.{img_type}")
        print(img_path)

        with open(img_path, "wb") as file:
            file.write(response.content)

        status = "success"
    except requests.ConnectionError:
        status = "ERROR (network)"
    except OSError:
        print(traceback.format_exc())
        status = "ERROR (file)"
    except:
        print(traceback.format_exc())
        status = "ERROR (other)"

    print(f"\t{camera_id}  \t\t {status}")


def main():
    df = pd.read_csv("MtnCams.csv", sep=",")
    pattern = r"[<>:'/\\\|\*\s]"
    df["camera_id"] = df["location"].str.replace(pattern, "_", regex=True)
    df = df.drop(df.columns[-1], axis=1)

    for img_dir, group in df.groupby("img_dir"):
        camera_ids = set(df["camera_id"].tolist())
        create_directories(img_dir, camera_ids)

        for _, row in group.iterrows():
            capture_camera(row)


if __name__ == "__main__":
    main()
