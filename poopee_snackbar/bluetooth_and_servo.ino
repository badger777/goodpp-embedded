#include <SoftwareSerial.h>
#include <Servo.h>
 
Servo myservo;
int blueTx=2;
int blueRx=3;
SoftwareSerial mySerial(blueTx, blueRx);
String myString="";
 
void setup() {
  myservo.attach(9);
  myservo.write(140);
  mySerial.begin(9600);
}
 
void loop() {
  while(mySerial.available())
  {
    char myChar = (char)mySerial.read();
    myString+=myChar;
    delay(5);
  }

  if(!myString.equals(""))
  {
    int angle = 0;
    Serial.println("input value: "+myString);
      if(myString=="on")
      {
        myservo.write(0);
        delay(1000);
        myservo.write(140);
      }
    myString="";
  }
}
