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
import shutil
from shutil import copyfile
import typing

import yaml
from sklearn.model_selection import train_test_split

y2s_flag = "y2s"
s2y_flag = "s2y"


class S2Y:
    @staticmethod
    def get_class_names_from_supervisely(input_path: str) -> typing.List:
        class_names_array = []
        class_names_path = os.path.join(input_path, 'meta.json')
        with open(class_names_path, "r") as file:
            json_classes = json.load(file)["classes"]
            for json_class in json_classes:
                class_names_array.append(json_class["title"])
        return class_names_array

    @staticmethod
    def create_yolo_file_structure(output_path: str) -> None:
        for step in ["train", "val"]:
            os.makedirs(os.path.join(output_path, step, 'labels'), exist_ok=True)
            os.makedirs(os.path.join(output_path, step, 'images'), exist_ok=True)

    @staticmethod
    def create_class_file(class_names_array, output_path) -> None:
        class_file_path = os.path.join(output_path, 'labels', 'classes.txt')
        with open(class_file_path, 'w') as f:
            for class_name in class_names_array:
                f.write("%s\n" % class_name)

    @staticmethod
    def create_data_file(class_name_list: typing.List, output_path: str) -> None:
        class_file_path = os.path.join(output_path, 'data.yaml')
        dict_yaml = {"train": "train/images",
                     "val": "val/images",
                     "nc": len(class_name_list),
                     "names": class_name_list}

        with open(class_file_path, 'w') as outfile:
            yaml.dump(dict_yaml, outfile, default_flow_style=False)

    @staticmethod
    def get_yolo_annotation_info(json_file: str, class_names_array: typing.List) -> typing.List:
        with open(json_file, "r") as file:
            json_object = json.load(file)

        class_coord_list = []

        class_id = 0
        if len(json_object["objects"]) > 0:

            for obj in json_object["objects"]:
                points = obj["points"]["exterior"]
                w = json_object["size"]["width"]
                h = json_object["size"]["height"]
                w_point = points[1][0] - points[0][0]
                h_point = points[1][1] - points[0][1]
                x1 = round((points[0][0] + w_point / 2) / w, 5)
                y1 = round((points[0][1] + h_point / 2) / h, 5)
                x2 = round(w_point / w, 5)
                y2 = round(h_point / h, 5)
                class_id = class_names_array.index(obj["classTitle"])

                class_coord_list.append({"class_id": class_id, "x1": x1, "y1": y1, "x2": x2, "y2": y2})

        return class_coord_list  # class_id, x1, y1, x2, y2

    @staticmethod
    def create_text_file(output_folder: str, y_file: str, class_names_array: typing.List) -> None:
        # class_id, x1, y1, x2, y2 = S2Y.get_yolo_annotation_info(folder_name, file_name, class_names_array)
        class_coord_list = S2Y.get_yolo_annotation_info(json_file=y_file, class_names_array=class_names_array)

        if len(class_coord_list) > 0:

            txt_path = os.path.join(output_folder, "labels", os.path.basename(y_file)[:-9] + ".txt")

            with open(txt_path, 'w') as text_file:
                for coord in class_coord_list:
                    class_id = coord["class_id"]
                    x1 = coord["x1"]
                    y1 = coord["y1"]
                    x2 = coord["x2"]
                    y2 = coord["y2"]

                    text_file.write('{} {} {} {} {}'.format(class_id, x1, y1, x2, y2))
                    text_file.write('\n')


class Y2S:
    @staticmethod
    def create_supervisely_file_structure():
        os.makedirs(os.path.dirname(input_path + '//dataset_1//ann//'), exist_ok=True)
        os.makedirs(os.path.dirname(input_path + '//dataset_1//img//'), exist_ok=True)

    @staticmethod
    def get_class_names_from_yolo():
        class_names_path = output_path + '//labels//classes.txt'
        with open(class_names_path) as file:
            class_names_array = file.read().splitlines()
        return class_names_array

    @staticmethod
    def get_supervisely_annotation_info(file_name):
        import cv2
        for image_path in glob.glob(os.path.join(output_path + "//images//", file_name + '.*')):
            pass

        if not skip_copy:
            copy_path = input_path + '//dataset_1//img//' + os.path.basename(image_path)
            copyfile(image_path, copy_path)

        image = cv2.imread(image_path, 0)
        h, w = image.shape[:2]
        class_coord_list = []

        image_text_file = output_path + '//labels//' + file_name + '.txt'

        with open(image_text_file) as file:
            # read all labels, split by line and add to list
            all_labels = file.read().splitlines()

            for data in [x.split() for x in all_labels]:
                class_id = int(data[0])
                bbox_width = float(data[3]) * w
                bbox_height = float(data[4]) * h
                center_x = float(data[1]) * w
                center_y = float(data[2]) * h
                x1 = int(center_x - (bbox_width / 2))
                y1 = int(center_y - (bbox_height / 2))
                x2 = int(center_x + (bbox_width / 2))
                y2 = int(center_y + (bbox_height / 2))
                class_coord_list.append({"class_id": class_id, "x1": x1, "y1": y1, "x2": x2, "y2": y2})

        return w, h, class_coord_list

    @staticmethod
    def create_meta_file(class_names_array):
        classes_array = []
        for name in class_names_array:
            classes_array.append({"title": name, "shape": "rectangle", "color": "#FF0000"})

        meta_format = {
            "tags": [],
            "classes": classes_array
        }

        meta_file_path = input_path + '//meta.json'
        with open(meta_file_path, 'w') as json_file:
            json.dump(meta_format, json_file)

    @staticmethod
    def create_json_file(file_name, class_names_array):
        w, h, class_coord_list = Y2S.get_supervisely_annotation_info(file_name)

        json_format = {
            "description": "",
            "name": file_name,
            "size": {
                "width": w,
                "height": h
            },
            "tags": [],
            "objects": [
            ]
        }

        for class_coord in class_coord_list:
            json_format["objects"].append({
                "description": "",
                "tags": [],
                "bitmap": None,
                "classTitle": class_names_array[class_coord['class_id']],
                "points": {
                    "exterior": [
                        [
                            class_coord['x1'],
                            class_coord['y1']
                        ],
                        [
                            class_coord['x2'],
                            class_coord['y2']
                        ]
                    ],
                    "interior": []
                }
            })

        json_file_path = input_path + '//dataset_1//ann//' + file_name + '.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(json_format, json_file)


def img_path_from_label(y_path):
    head, tail = os.path.split(y_path)
    x_name = tail[:-5]
    list_path = head.split(os.sep)
    list_path[-1] = 'img'
    list_path.append(x_name)
    return os.path.join(*list_path)


def img_set_from_labels(annotation_files: typing.List):
    X = []
    for ann_file in annotation_files:
        X.append(img_path_from_label(y_path=ann_file))
    return X


def main(dest_path: str, input_path: str, skip_copy: bool, conversion_type: str, test_size: float):

    print("Processing...")
    if conversion_type == y2s_flag:
        try:
            class_names_array = Y2S.get_class_names_from_yolo()
        except IOError:
            print('Error [classes.txt not found] => There should be a folder "yolo" at {0}'.format(dest_path[:-4]))
            exit(1)
        Y2S.create_supervisely_file_structure()
        Y2S.create_meta_file(class_names_array)

        labels_path = dest_path + "//labels"
        for file_path in glob.glob(os.path.join(labels_path, '*.txt')):
            with open(file_path) as file:
                file_name = os.path.basename(file.name)[:-4]
                if file_name != 'classes':
                    Y2S.create_json_file(file_name, class_names_array)
        print("Supervisely structure created at => {}".format(input_path))
    else:
        try:
            class_names_array = S2Y.get_class_names_from_supervisely(input_path=input_path)
        except IOError:
            print('Error [meta.json not found] => There should be a folder "supervisely" at {0}'.format(
                input_path[:-11]))
            exit(1)
        S2Y.create_yolo_file_structure(output_path=dest_path)
        S2Y.create_data_file(class_names_array, output_path=dest_path)

        dataset_folders = [folder for folder in os.listdir(input_path)]

        y = []
        for folder in dataset_folders:

            labels_path = os.path.join(input_path, folder, "ann")
            print("labels_path", labels_path)

            for file_path in glob.glob(os.path.join(labels_path, '*.json')):
                y.append(file_path)

        X = img_set_from_labels(annotation_files=y)

        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        except Exception as e:
            raise ("An exception occurred when try to split the dataset_1 in test/val part due to : " + str(e))

        for step_name, step_tuples in zip(["train", "val"], [(X_train, y_train), (X_test, y_test)]):
            img_list, ann_list = step_tuples
            for x, y in zip(img_list, ann_list):
                dst_x = os.path.join(dest_path, step_name, 'images', os.path.split(x)[-1])
                shutil.copy(src=x, dst=dst_x)

                S2Y.create_text_file(output_folder=os.path.join(dest_path, step_name), y_file=y,
                                     class_names_array=class_names_array)
        print("Yolo structure created at => {}".format(dest_path))


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-p', '--path',
                      action="store", dest="dest_path",
                      help="full path of the source folder (default path is the location of this script)",
                      default=os.path.dirname(os.path.realpath(__file__)))

    parser.add_option('-i', '--input_path', dest="input_path",
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

    parser.add_option('--test_size',
                      dest="test_size",
                      # help="conversion type: yolo2supervisely or supervisely2yolo (default supervisely2yolo)",
                      default=0.15)

    options, args = parser.parse_args()

    main(**vars(options))
