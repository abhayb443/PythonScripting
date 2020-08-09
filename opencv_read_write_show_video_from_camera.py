import cv2

# Capturing live feed from the video

img_path = "C://Users//Work-Pc//PycharmProjects//Rest_API//Python//Python_Scripting_Local_Project//Videos//"
cap = cv2.VideoCapture(img_path+'Friends.mp4')

# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('Output.avi', fourcc, 20.0, (640, 480))

while (cap.isOpened()):
    ret, frame = cap.read()

    if ret:
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)      # For Grayscale

        cv2.imshow("Frame", frame)                            # Normal

        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

        # out.write(frame)
        print(height, ' * ', width)

        # cv2.imshow("Frame", gray)                           # For Grayscale

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
# out.release()
cv2.destroyAllWindows()
