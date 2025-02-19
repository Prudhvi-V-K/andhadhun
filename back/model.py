import cv2
import numpy as np
from PIL import Image

class ObjectDetector:
    def __init__(self, weights_path, config_path, labels_path):
        self.net = cv2.dnn.readNet(weights_path, config_path)
        self.labels = open(labels_path).read().strip().split("\n")
        self.layer_names = self.get_output_layers()
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        self.known_width = 0.2
        self.focal_length = 500

    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        return [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

    def detect_objects(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        return self.net.forward(self.layer_names)

    def process_detections(self, frame, detections):
        height, width = frame.shape[:2]
        boxes, confidences, class_ids = [], [], []

        for output in detections:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > self.confidence_threshold:
                    box = detection[0:4] * np.array([width, height, width, height])
                    (center_x, center_y, w, h) = box.astype("int")
                    x = int(center_x - (w / 2))
                    y = int(center_y - (h / 2))

                    boxes.append([x, y, int(w), int(h)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)

        if indices is None or len(indices) == 0:
            return []
        indices = indices.flatten() if len(indices) > 0 else []

        return [[boxes[i], class_ids[i], confidences[i]] for i in indices]

    def estimate_distance(self, object_width_pixels):
        return (self.known_width * self.focal_length) / object_width_pixels

    def draw_detections(self, frame, detections):
        for (box, class_id, confidence) in detections:
            x, y, w, h = box
            distance = self.estimate_distance(w)

            label = f"{self.labels[class_id]}: {confidence:.2f}, {distance:.2f}m"
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def process_pil_image(self, img: Image.Image):
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        detections = self.detect_objects(frame)
        processed_detections = self.process_detections(frame, detections)
        self.draw_detections(frame, processed_detections)

        cv2.imshow("Object Detection", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = ObjectDetector("yolov4-tiny.weights", "yolov4-tiny.cfg", "classes.txt")

    # Load an image using PIL
    pil_image = Image.open("src/person.jpg")  # Change this to your image path
    detector.process_pil_image(pil_image)
