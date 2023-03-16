# %%
import pytz
from datetime import datetime
import time, requests, os
import glob
import boto3
import pandas as pd


def configure_folders():
     for camera in camera_ids:
        path = f'{img_dir}/{camera}'
        pathExists = os.path.exists(path)
        if not pathExists:
            print(f"Creating path for camera {camera}")
            os.makedirs(path)
        else:
             print(f"Path for camera {camera} exists")

def capture_all_cameras(url_front,camera_id):
    currentTimeDate = datetime.now().astimezone(pytz.timezone('America/Denver')).strftime('%Y-%m-%d-%H-%M-%S')
    print(f"Capture at {currentTimeDate}")

    # Combines the URL
    url = f'{url_front} {camera_id}'
    print(url)
    print(f'{img_dir}/{camera_id}/{camera_id}-{currentTimeDate}.{img_type}')
    try:
        r = requests.get(url, allow_redirects=True)
        with open(f'{img_dir}/{camera_id}/{camera_id}-{currentTimeDate}.jpg', 'wb') as file:
            file.write(r.content)

        status = "success"
    except requests.ConnectionError:
        status = "ERROR (network)"
    except OSError:
        status = "ERROR (file)"
    except:
        status = "ERROR (other)"
    print(f"\t{camera_id}  \t\t {status}")

def runCameras():
    df['filename'] = df.apply(lambda x: capture_all_cameras(x['url_front'],
                                                            x['camera_id'],
                                                           ),
                              axis=1)
    
    return None

#Read in CSV
df = pd.read_csv('MtnCams.csv',sep=';')

#Populate camera_id column with camera_id based on the url
df['camera_id'] = df['location'].str.replace(r'[<|>|:|"|/|\\|\||\*|\s]','_', regex=True)
#df['camera_id'] = df['url_front'].str.extract('.+/(.+)\.jpg')

#Hardcode img_dir and img_type
img_dir = './NMtns'
img_type = 'jpg'

#Create list of camera_ids for configure_folders function
camera_ids = list(set(df['camera_id'].tolist()))

#Run configure_folders to check if folders exist and, if not, create them
configure_folders()

while(True):
    runCameras()
    quit()


