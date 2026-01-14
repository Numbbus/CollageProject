import cv2

img = cv2.imread("test.png")
h, w = img.shape[:2]

win_w, win_h = 800, 600
zoom = 1.0

cv2.namedWindow("viewer", cv2.WINDOW_NORMAL)
cv2.resizeWindow("viewer", win_w, win_h)

while True:
    if zoom <= 1.0:
        # overview mode (fit whole image)
        display = cv2.resize(
            img, (win_w, win_h), interpolation=cv2.INTER_AREA
        )
    else:
        # zoom mode: crop from original, then scale
        view_w = int(w / zoom)
        view_h = int(h / zoom)

        x1 = (w - view_w) // 2
        y1 = (h - view_h) // 2

        roi = img[y1:y1+view_h, x1:x1+view_w]
        display = cv2.resize(
            roi, (win_w, win_h), interpolation=cv2.INTER_LINEAR
        )

    cv2.imshow("viewer", display)

    key = cv2.waitKey(20) & 0xFF
    if key == ord('+'):
        zoom *= 1.2
    elif key == ord('-'):
        zoom /= 1.2
        zoom = max(zoom, 1.0)
    elif key == 27:
        break

cv2.destroyAllWindows()
