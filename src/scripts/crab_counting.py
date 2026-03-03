import cv2
from ultralytics import solutions


def count_crabs(
    cap: cv2.VideoCapture,
    model_path="yolo26n.pt",
    cls=[2],
    region_pts=[(0, 1000), (1900, 1000), (1900, 0), (0, 0)],
):
    """Count the number of Invasive European Green Crabs in a video stream"""

    # Check video stream is open
    assert cap.isOpened(), "Error: cant open video"

    # Initalizie counter for detections inside defined region
    # docs: https://docs.ultralytics.com/solutions/#solutions
    counter = solutions.ObjectCounter(
        model=model_path, classes=cls, conf=0.25, region=region_pts, device="cpu", show_out=False
    )

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Error: failed to read capture")
            break
        # Count number of EU green crabs inside region
        counter(frame)

        cv2.imshow("Live Camera Feed", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # For testing purposes
    count_crabs(cv2.VideoCapture(0), model_path="./models/crabs_exp9.pt", cls=[2])
