#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#      Author = "Namik Delilovic"
#      Contact = "namikdelilovic@gmail.com"
#      License = "GPLv3"
#      Version = "0.9"
#      Date = "2019/10/09"

import glob
import json
import optparse
import os
from shutil import copyfile

y2s_flag = "y2s"
s2y_flag = "s2y"


class S2Y:
    @staticmethod
    def get_class_names_from_supervisely():
        class_names_array = []
        class_names_path = supervisely_path + '\\meta.json'
        with open(class_names_path, "r") as file:
            json_classes = json.load(file)["classes"]
            for json_class in json_classes:
                class_names_array.append(json_class["title"])
        return class_names_array

    @staticmethod
    def create_yolo_file_structure():
        os.makedirs(os.path.dirname(yolo_path + '\\labels\\'), exist_ok=True)
        os.makedirs(os.path.dirname(yolo_path + '\\images\\'), exist_ok=True)

    @staticmethod
    def create_class_file(class_names_array):
        class_file_path = yolo_path + '\\labels\\classes.txt'
        with open(class_file_path, 'w') as f:
            for class_name in class_names_array:
                f.write("%s\n" % class_name)

    @staticmethod
    def get_yolo_annotation_info(file_name, class_names_array):
        image_path = supervisely_path + "\\dataset\\img\\" + file_name

        if not skip_copy:
            copy_path = yolo_path + '\\images\\' + os.path.basename(image_path)
            copyfile(image_path, copy_path)

        image_json_file = supervisely_path + '\\dataset\\ann\\' + file_name + '.json'
        with open(image_json_file, "r") as file:
            json_object = json.load(file)
        points = json_object["objects"][0]["points"]["exterior"]
        w = json_object["size"]["width"]
        h = json_object["size"]["height"]
        w_point = points[1][0] - points[0][0]
        h_point = points[1][1] - points[0][1]
        x1 = round((points[0][0] + w_point / 2) / w, 5)
        y1 = round((points[0][1] + h_point / 2) / h, 5)
        x2 = round(w_point / w, 5)
        y2 = round(h_point / h, 5)
        class_id = class_names_array.index(json_object["objects"][0]["classTitle"])

        return class_id, x1, y1, x2, y2

    @staticmethod
    def create_text_file(file_name, class_names_array):
        class_id, x1, y1, x2, y2 = S2Y.get_yolo_annotation_info(file_name, class_names_array)

        text_file_path = yolo_path + '\\labels\\' + os.path.splitext(file_name)[0] + ".txt"
        with open(text_file_path, 'w') as text_file:
            text_file.write('{} {} {} {} {}'.format(class_id, x1, y1, x2, y2))


class Y2S:
    @staticmethod
    def create_supervisely_file_structure():
        os.makedirs(os.path.dirname(supervisely_path + '\\dataset\\ann\\'), exist_ok=True)
        os.makedirs(os.path.dirname(supervisely_path + '\\dataset\\img\\'), exist_ok=True)

    @staticmethod
    def get_class_names_from_yolo():
        class_names_path = yolo_path + '\\labels\\classes.txt'
        with open(class_names_path) as file:
            class_names_array = file.read().splitlines()
        return class_names_array

    @staticmethod
    def get_supervisely_annotation_info(file_name):
        import cv2
        for image_path in glob.glob(os.path.join(yolo_path + "\\images\\", file_name + '.*')):
            pass

        if not skip_copy:
            copy_path = supervisely_path + '\\dataset\\img\\' + os.path.basename(image_path)
            copyfile(image_path, copy_path)

        image = cv2.imread(image_path, 0)
        h, w = image.shape[:2]

        image_text_file = yolo_path + '\\labels\\' + file_name + '.txt'
        with open(image_text_file) as file:
            data = file.readline().split()
            class_id = int(data[0])
            bbox_width = float(data[3]) * w
            bbox_height = float(data[4]) * h
            center_x = float(data[1]) * w
            center_y = float(data[2]) * h
            x1 = int(center_x - (bbox_width / 2))
            y1 = int(center_y - (bbox_height / 2))
            x2 = int(center_x + (bbox_width / 2))
            y2 = int(center_y + (bbox_height / 2))

        return w, h, class_id, x1, y1, x2, y2

    @staticmethod
    def create_meta_file(class_names_array):
        classes_array = []
        for name in class_names_array:
            classes_array.append({"title": name, "shape": "rectangle", "color": "#FF0000"})

        meta_format = {
            "tags": [],
            "classes": classes_array
        }

        meta_file_path = supervisely_path + '\\meta.json'
        with open(meta_file_path, 'w') as json_file:
            json.dump(meta_format, json_file)

    @staticmethod
    def create_json_file(file_name, class_names_array):
        w, h, class_id, x1, y1, x2, y2 = Y2S.get_supervisely_annotation_info(file_name)

        json_format = {
            "description": "",
            "name": file_name,
            "size": {
                "width": w,
                "height": h
            },
            "tags": [],
            "objects": [{
                "description": "",
                "tags": [],
                "bitmap": None,
                "classTitle": class_names_array[class_id],
                "points": {
                    "exterior": [
                        [
                            x1,
                            y1
                        ],
                        [
                            x2,
                            y2
                        ]
                    ],
                    "interior": []
                }
            }]
        }

        json_file_path = supervisely_path + '\\dataset\\ann\\' + file_name + '.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(json_format, json_file)


def main():
    print("Processing...")
    if conversion_type == y2s_flag:
        try:
            class_names_array = Y2S.get_class_names_from_yolo()
        except IOError:
            print('Error [classes.txt not found] => There should be a folder "yolo" at {0}'.format(yolo_path[:-4]))
            exit(1)
        Y2S.create_supervisely_file_structure()
        Y2S.create_meta_file(class_names_array)

        labels_path = yolo_path + "\\labels"
        for file_path in glob.glob(os.path.join(labels_path, '*.txt')):
            with open(file_path) as file:
                file_name = os.path.basename(file.name)[:-4]
                if file_name != 'classes':
                    Y2S.create_json_file(file_name, class_names_array)
        print("Supervisely structure created at => {}".format(supervisely_path))
    else:
        try:
            class_names_array = S2Y.get_class_names_from_supervisely()
        except IOError:
            print('Error [meta.json not found] => There should be a folder "supervisely" at {0}'.format(
                supervisely_path[:-11]))
            exit(1)
        S2Y.create_yolo_file_structure()
        S2Y.create_class_file(class_names_array)
        labels_path = supervisely_path + "\\dataset\\ann"
        for file_path in glob.glob(os.path.join(labels_path, '*.json')):
            with open(file_path) as file:
                file_name = os.path.basename(file.name)[:-5]
                S2Y.create_text_file(file_name, class_names_array)
        print("Yolo structure created at => {}".format(yolo_path))


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-p', '--path',
                      action="store", dest="dest_path",
                      help="full path of the source folder (default path is the location of this script)",
                      default=os.path.dirname(os.path.realpath(__file__)))

    parser.add_option('-s', '--skip',
                      action="store_true", dest="skip_copy",
                      help="disable copying images from the source folder to the destination folder",
                      default=False)

    parser.add_option('-t', '--type',
                      type='choice',
                      choices=[y2s_flag, s2y_flag],
                      action="store",
                      dest="conversion_type",
                      help="conversion type: yolo2supervisely or supervisely2yolo (default supervisely2yolo)",
                      default=s2y_flag)

    options, args = parser.parse_args()
    conversion_type = options.conversion_type
    yolo_path = options.dest_path + "\\yolo"
    supervisely_path = options.dest_path + "\\supervisely"

    skip_copy = options.skip_copy

    main()
