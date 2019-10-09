# supervisely_yolo.py

 ## Data Structure and Testing Example
    * Test Case 1:
        - copy the supervisely folder from examples into the root location (next to the supervisely_yolo.py)
        - cd (using CMD or terminal) to the root location (again where the supervisely_yolo.py location is)
        - run command: python supervisely_yolo.py
        - result: Yolo data structure created inside the same folder where the Supervisely folder is
     
     * Test Case 2 (similar to Test Case 1 only we convert from Yolo to Supervisely this time):
        - copy the yolo folder from examples into the root location (next to the supervisely_yolo.py)
        - cd (using CMD or terminal) to the root location (again where the supervisely_yolo.py location is)
        - run command (if you don't have OpenCV package): pip install opencv-python
        - run command: python supervisely_yolo.py -t y2s
        - result: Supervisely data structure created inside the same folder where the Yolo folder is
