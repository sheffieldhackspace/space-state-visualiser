"""shared functions"""

import os
import re


def parse_listener_coordinates(listeners):
    image_ids = sorted(
        list(
            set(
                im.replace(".on.png", "").replace(".off.png", "").replace(".NA.png", "")
                for im in os.listdir("static/icons_crop")
            )
        )
    )
    # edit IDs to add image coordinates
    for listener in listeners:
        id_ = listener["id"]
        matching_ids = [imgid for imgid in image_ids if imgid.startswith(id_)]
        if len(matching_ids) != 1:
            raise ValueError(
                f"could not find matching listener for {id_}. Look in static/icons_crop"
            )
        listener["id"] = matching_ids[0]
        matches = re.search(r"([0-9]*)x([0-9]*)y$", matching_ids[0])
        listener["x"] = int(matches.group(1))
        listener["y"] = int(matches.group(2))
    return listeners
