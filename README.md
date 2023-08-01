# supervisely_yolo.py
### (Script to convert Supervisely to Yolo (Darknet) data structure/format and vice versa)

* If you convert from Yolo to Supervisely (supervisely_yolo -t y2s) then you need to install the OpenCV python package:
    pip install opencv-python

* You can specify the location of your source dataset using -p flag
    - example 1 => python supervisely_yolo.py -p C:\yolo -t y2s
    - example 2 => python supvervisely_yolo.py -p C:\Users\Delilovic\Desktop  ([-t s2y] is not required as it is the default flag)
 
* You can specify if you want to skip copying images from the source to the destination dataset with the -s flag
    - WARNING: consider using this flag if you have a lot of images and might run out of space
    
* When downloading images from Supervisely, images get the extension attached to their names 
    - e.g. downloading foo.jpg gets renamed as foo.jpg.jpg
    - this behaviour is handled  by the supervisely_yolo.py script, but it also means you can not currently convert Supervisely data structure created by
    y2s flag back to Yolo data using the s2y flag (this shouldn't be a use case anyway but is worth mentioning here) 


## Required Folder Structure
   * Please follow this structure strictly 
        - you can not have two different Supervisely datasets at the moment (if you do, put everything into the dataset folder)
        - you can not have Yolo images and labels in one folder (if you do, separate them into labels and images folder)
        - data structure is case sensitive (e.g. yolo can not be Yolo)
        
#### Supervisely (-t s2y)
```
├── supervisely
    ├── meta.json
    └── dataset1
        ├── img
        │    ├── any_name.jpg or(.jpeg, .png)
        │    └── ...
        └── ann
            ├── any_name.json
            └── ...
    └── dataset2
        ├── img
        │    ├── any_name.jpg or(.jpeg, .png)
        │    └── ...
        └── ann
            ├── any_name.json
            └── ...
```
#### Yolo (-t y2s)
```
├── yolo
    ├── images
    │   ├── any_name.jpg or(.jpeg, .png)
    │   └── ...
    └── labels
        ├── any_name.txt
        └── ...
```  
        
## Contributions
   * This is the first version and many updates will be required, everybody interested is gladly invited to contribute     
     
