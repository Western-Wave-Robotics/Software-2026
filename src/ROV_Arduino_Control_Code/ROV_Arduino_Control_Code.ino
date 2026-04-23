#include <Servo.h>
#define MOTOR_FL 5 // Front Left Motor pin
#define MOTOR_FR 11 // Front Right Motor pin
#define MOTOR_BL 6 // Back Left Motor pin
#define MOTOR_BR 9 // Back Right Motor pin
#define MOTOR_UPL 3// Up Motor 1 pin
#define MOTOR_UPR 10 // Up Motor 2 pin  

Servo motorFL, motorFR, motorBL, motorBR, motorUPL, motorUPR;

// Variables to store motor values (1000-2000 for ESC control via Servo library)
int motorSpeedFL = 1500;
int motorSpeedFR = 1500;
int motorSpeedBL = 1500;
int motorSpeedBR = 1500;
int motorSpeedUpL = 1500;
int motorSpeedUpR = 1500;

void setup() {
  Serial.begin(9600);

  // Attach ESCs to the correct pins
  motorFL.attach(MOTOR_FL);
  motorFR.attach(MOTOR_FR);
  motorBL.attach(MOTOR_BL);
  motorBR.attach(MOTOR_BR);
  motorUpL.attach(MOTOR_UPL);
  motorUpR.attach(MOTOR_UPR);

// Set all motors to the neutral speed (1500 is neutral for most ESCs)
  motorFL.writeMicroseconds(1500);
  motorFR.writeMicroseconds(1500);
  motorBL.writeMicroseconds(1500);
  motorBR.writeMicroseconds(1500);
  motorUpL.writeMicroseconds(1500);
  motorUpR.writeMicroseconds(1500);
}

void loop () {
  if (Serial.available() > 0) {
    // Read the serial input from the laptop
    String inputString = Serial.readStringUntil('\n');
    // Parse the input into individual motor speeds
    sscanf(inputString.c_str(), "%d %d %d %d %d %d", &motorSpeedFL, &motorSpeedFR, &motorSpeedBL, &motorSpeedBR, &motorSpeedUp1, &motorSpeedUp2);
// Ensure values stay within ESC range (1000-2000 microseconds)
    motorSpeedFL = constrain(motorSpeedFL, 1000, 2000);
    motorSpeedFR = constrain(motorSpeedFR, 1000, 2000);
    motorSpeedBL = constrain(motorSpeedBL, 1000, 2000);
    motorSpeedBR = constrain(motorSpeedBR, 1000, 2000);
    motorSpeedUp1 = constrain(motorSpeedUp1, 1000, 2000);
    motorSpeedUp2 = constrain(motorSpeedUp2, 1000, 2000);
// Set motor speeds
   motorFL.writeMicroseconds(motorSpeedFL);
   motorFR.writeMicroseconds(motorSpeedFR);
   motorBL.writeMicroseconds(motorSpeedBL);
   motorBR.writeMicroseconds(motorSpeedBR);
   motorUPL.writeMicroseconds(motorSpeedUp1);
   motorUPR.writeMicroseconds(motorSpeedUp2);
  }
}
