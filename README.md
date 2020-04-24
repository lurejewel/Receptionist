# Receptionist
code for task "Receptionist" in RoboCup Shaoxing 2020

## process
Segment into sub-tasks:
* **DoorDetection**: detect the door in front of the robot using laser or Kinect (hasn't decided yet), and prepare to enter the competition site (next sub-task) if it the door opens. 
  * **Related section**: vision(image)
* **EnterSite**: go to a predefined location in the site, with the map known already.
  * **Related section**: Navigation
* **CannotOpen**: ask the referee to open the door and let the guest come in
  * **Related section**: speech
  * **TODO**: use arm to open the door automatically
* **GuestRecognition**: recognize the guest, including the age, gender, color of dress, face(maybe).
  * **Related section**: vision(image)
  * **TODO**: age recognition may not be easy; has gender recognition finished yet?
* **Requesting**: ask the guest's name ,and then verify the name; ask the guest's favorite drink, and then verify the drink. Finally the robot is like "okay, (guest name), I will take you to the living room, please follow me". **ATTETION**: use the wrong name/drink if the robot cannot recognize the word correctly more than 3 times.
  * **Related section**: speech
  * **TODO**: age information may also be needed
* **Leading**: alomost the same as "EnterSite". Different locations.
* **Introducing**: find people in the living room, and then face him/her, and then say to the guest like "please stand by my right side"; then point at the guest, saying like "John (and another guest's name at 2nd round), this is (guest name), his/her favorite drink is (drink name). (vice versa)". Finally retract the arm.
  * **Related section**: vision(image), speech, arm, navigation
* **Serving**: find people and sofa in the living room, and then face the empty seat(sofa with no one seated); then point at the seat, saying like "you can sit here, (guest name)". Finally retract the arm.
  * **Related section**: vision(image), speech, arm, navigation
  * **TODO**: empty seat may be other than sofa —— recognizing other kinds of seat are needed.
* **Backward**: almost the same as "EnterSite". Different locations.

## description
* control: the control center of the task, deciding the current sub-task and next task, according to the message that 4 sections send to it. 
* arm/speech/image/navi: functional package of 4 sections
