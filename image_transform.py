# for each ID
# get the NA, off, and on images
# get the biggest combined bounding box coords
# crop the NA, off, and on images to this bounding box
# save the top-left coordinate of the bounding box relative to the original image size
#   …in the filename, "image.NA.png" -> "image_243X159Y.NA.png"

import os
import sys
from PIL import Image

image_ids = sorted(
    list(
        set(
            im.replace(".on.png", "").replace(".off.png", "").replace(".NA.png", "")
            for im in os.listdir("static/icons")
        )
    )
)


def get_biggest_bbox(bbox1, *bboxes):
    x1, y1, x2, y2 = bbox1
    for bbox in bboxes:
        a1, b1, a2, b2 = bbox
        x1 = min(x1, a1)
        y1 = min(y1, b1)
        x2 = max(x2, a2)
        y2 = max(y2, b2)
    return [x1, y1, x2, y2]


# delete images in static/icons_crop
if not os.path.isdir("static/icons_crop"):
    os.mkdir("static/icons_crop")
for filename in os.listdir("static/icons_crop"):
    os.unlink(f"static/icons_crop/{filename}")

for image_id in image_ids:
    print(f"==== transforming {image_id} ====")
    imgNA = Image.open(f"static/icons/{image_id}.NA.png")
    imgon = Image.open(f"static/icons/{image_id}.on.png")
    imgoff = Image.open(f"static/icons/{image_id}.off.png")

    bbox_NA = imgNA.getbbox()
    bbox_on = imgon.getbbox()
    bbox_off = imgoff.getbbox()
    bbox = get_biggest_bbox(bbox_NA, bbox_on, bbox_off)
    x1, y1, x2, y2 = bbox
    print(f"image size (x×y): {imgNA.size}")
    print(f"bbox NA is: {bbox_NA}")
    print(f"bbox NA is: {bbox_on}")
    print(f"bbox NA is: {bbox_off}")
    print(f"biggest bbox is: {bbox}")
    print(f"top left (x,y): [{x1}, {y1}]")
    print(f"bottom right (x,y): [{x2}, {y2}]")

    filename_id = f"{image_id}_{x1}x{y1}y"
    print(f"saving {filename_id}")

    imgNA_crop = imgNA.crop(bbox)
    imgon_crop = imgon.crop(bbox)
    imgoff_crop = imgoff.crop(bbox)

    imgNA_crop.save(f"static/icons_crop/{filename_id}.NA.png")
    imgon_crop.save(f"static/icons_crop/{filename_id}.on.png")
    imgoff_crop.save(f"static/icons_crop/{filename_id}.off.png")
