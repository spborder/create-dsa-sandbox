"""

Main scripts for creating a sandbox directory for one/more DSA items.

"""

import json
import os
import sys
import threading
import time
from argparse import ArgumentParser

import girder_client
import requests
from tqdm import tqdm


def connect_client(
    apiUrl: str, username: str | None = None, password: str | None = None
):
    gc = girder_client.GirderClient(apiUrl=apiUrl)

    if username is not None and password is not None:
        _ = gc.authenticate(username, password)
    else:
        username = os.environ.get("DSA_USER", None)
        password = os.environ.get("DSA_PASSWORD", None)
        if username is not None and password is not None:
            _ = gc.authenticate(username, password)

    return gc


def download_annotation(gc, ann_dict, output_path):

    annotation_data = gc.get(f"annotation/{ann_dict.get('_id')}/geojson")
    ann_output_path = os.path.join(output_path, ann_dict["annotation"]["name"])
    with open(ann_output_path + ".json", "w") as f:
        json.dump(annotation_data, f, indent=4)

        f.close()


def download_slide(gc, item_dict, output_path):

    image_file = item_dict.get("largeImage").get("fileId")
    user_token = gc.get("token/session")["token"]

    with requests.get(
        gc.urlBase + f"file/{image_file}/download?token={user_token}", stream=True
    ) as data_stream:
        data_stream.raise_for_status()
        with open(os.path.join(output_path, item_dict.get("name")), "wb") as f:
            for chunk in data_stream.iter_content(chunk_size=8192):
                f.write(chunk)

            f.close()


def create_sandbox_directory(
    gc: girder_client.GirderClient, item_id: str, output_path: str, options: dict
):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    item_info = gc.get(f"item/{item_id}")
    item_ext = item_info.get("name").split(".")[-1]

    with open(
        os.path.join(output_path, item_info.get("name").replace(item_ext, "json")), "w"
    ) as f:
        json.dump(item_info, f, indent=4)

        f.close()

    thread_list = []
    if options.get("download_slide"):
        # download the item to the output path
        slide_thread = threading.Thread(
            target=download_slide, args=(gc, item_info, output_path), daemon=True
        )
        thread_list.append(slide_thread)
        _ = slide_thread.start()

    if options.get("download_annotations"):
        # download the annotations to the output path
        item_annotations = gc.get("annotation", parameters={"itemId": item_id})
        for ann in item_annotations:
            ann_thread = threading.Thread(
                target=download_annotation, args=(gc, ann, output_path), daemon=True
            )
            thread_list.append(ann_thread)

            _ = ann_thread.start()

    if options.get("download_files"):
        # download files associated with the item
        item_files = gc.get(f"item/{item_id}/files")
        for file in item_files:
            if file.get("_id") != item_info["largeImage"]["fileId"]:
                file_output_path = os.path.join(output_path, file.get("name"))
                file_thread = threading.Thread(
                    target=gc.downloadFile,
                    args=(file.get("_id"), file_output_path),
                    daemon=True,
                )
                thread_list.append(file_thread)
                _ = file_thread.start()

    with tqdm(thread_list) as pbar:
        alive_list = [t.is_alive() for t in thread_list]
        current_alive = sum(alive_list)
        start_time = time.time()
        while any(alive_list):
            pbar.set_description(f"Remaining Threads: {sum(alive_list)}")
            if sum(alive_list) != current_alive:
                pbar.update(1)
                current_alive = sum(alive_list)

            alive_list = [t.is_alive() for t in thread_list]
            time.sleep(1)

        pbar.set_description("All Done!: 0")
        pbar.update(1)
        time.sleep(1)
        pbar.close()
        print(f"\nTime elapsed: {round((time.time() - start_time) / 60, 2)} minutes")
        print("-----------------------------------------")


def run(args):

    dsa_url = args.dsa_url
    if not dsa_url.endswith("api/v1"):
        dsa_url += "/api/v1"

    options_dict = {
        "download_slide": args.download_slide,
        "download_annotations": args.download_annotations,
        "download_files": args.download_files,
    }

    gc = connect_client(dsa_url, args.username, args.password)

    try:
        _ = create_sandbox_directory(
            gc, args.item_id, args.output_path, options=options_dict
        )

    except (girder_client.HttpError, girder_client.AuthenticationError) as e:
        if isinstance(e, girder_client.AuthenticationError):
            provided_username = args.username
            if provided_username is None:
                provided_username = os.environ.get("DSA_USER", None)
            print(
                f"Error signing in or accessing requested resources with username: {provided_username}"
            )
        else:
            print(f"Error accessing resources at the provided URL: {args.dsa_url}")
            print(e)


if __name__ == "__main__":
    args = ArgumentParser()
    _ = args.add_argument(
        "--dsa-url",
        type=str,
        help="The URL for the DSA instance you would like to connect to.",
    )
    _ = args.add_argument(
        "--item-id",
        type=str,
        help="The Item ID for the item you would like to copy to your sandbox environment",
    )

    _ = args.add_argument(
        "--output-path", type=str, help="The path to store the downloaded files to."
    )

    _ = args.add_argument(
        "--dsa-user",
        type=str,
        default=None,
        help="[Optional] The username to use to authenticate and access protected items.",
    )

    _ = args.add_argument(
        "--dsa-password",
        type=str,
        default=None,
        help="[Optional] The password to use to authenticate and access protected items.",
    )

    _ = args.add_argument(
        "--download-slide",
        type=bool,
        default=False,
        help="Whether or not to download the slide to your sandbox directory.",
    )

    _ = args.add_argument(
        "--download-annotations",
        type=bool,
        default=False,
        help="Whether or not to download annotations to your sandbox directory.",
    )

    _ = args.add_argument(
        "--download-files",
        type=bool,
        default=False,
        help="Whether or not to download files other than the slide to your sandbox directory.",
    )
    run(args.parse_args())
