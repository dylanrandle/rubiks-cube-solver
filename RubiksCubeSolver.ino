#include <AccelStepper.h>

const int ENABLE_PIN = 11;
const int MOTOR_STEPS_PER_REVOLUTION = 200;
const int MOTOR_STEPS_PER_TURN = MOTOR_STEPS_PER_REVOLUTION / 4;  // one turn is a quarter revolution
const int MOTOR_SPEED_CONSTANT = 10;
const int MOTOR_ACCELERATION_CONSTANT = MOTOR_SPEED_CONSTANT;
const int MOTOR_MAX_SPEED = MOTOR_SPEED_CONSTANT * MOTOR_STEPS_PER_REVOLUTION;
const int MOTOR_ACCELERATION = MOTOR_ACCELERATION_CONSTANT * MOTOR_STEPS_PER_REVOLUTION;

const int NUM_STEPPERS = 6;
AccelStepper steppers[NUM_STEPPERS] = {
  AccelStepper(AccelStepper::DRIVER, 2, 5),
  AccelStepper(AccelStepper::DRIVER, 3, 6),
  AccelStepper(AccelStepper::DRIVER, 4, 7),
  AccelStepper(AccelStepper::DRIVER, 5, 8),
  AccelStepper(AccelStepper::DRIVER, 6, 9),
  AccelStepper(AccelStepper::DRIVER, 7, 10),
};

struct Command {
  char face;
  int numTurns;
  bool inverted;
};

void setup() {
  Serial.begin(9600);

  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW);

  for (int i = 0; i < NUM_STEPPERS; i++) {
    steppers[i].setMaxSpeed(MOTOR_MAX_SPEED);
    steppers[i].setAcceleration(MOTOR_ACCELERATION);
  }

  Serial.println("ARDUINO:READY");
}

int getStepperIndex(char face) {
  switch (face) {
    case 'L':
      return 0;
    case 'R':
      return 1;
    case 'F':
      return 2;
    case 'U':
      return 3;
    case 'D':
      return 4;
    case 'B':
      return 5;
  }
}

void runMove(char face, int numTurns, bool inverted) {
  int stepperIdx = getStepperIndex(face);
  AccelStepper stepper = steppers[stepperIdx];
  long currentPosition = stepper.currentPosition();
  long deltaPosition;

  if (inverted) {
    deltaPosition = MOTOR_STEPS_PER_TURN * (-numTurns);
  } else {
    deltaPosition = MOTOR_STEPS_PER_TURN * numTurns;
  }

  Serial.print("Moving stepper ");
  Serial.print(stepperIdx);
  Serial.print(" by ");
  Serial.println(deltaPosition);

  stepper.runToNewPosition(currentPosition + deltaPosition);
}

struct Command getNextCommand() {
    String command = Serial.readStringUntil('\n');

    command.trim();
    command.toUpperCase();

    Serial.println("Got command: " + command);

    char face = command.charAt(0);
    bool inverted = command.endsWith("'");
    int numTurns;
    if (command.length() == 1) {
      numTurns = 1;
    } else if (command.length() == 2 & inverted) {
      numTurns = 1;
    } else {
      numTurns = constrain(command.substring(1, 2).toInt(), 1, 2);
    }

    Serial.print("Face: ");
    Serial.print(face);
    Serial.print(", numTurns: ");
    Serial.print(numTurns);
    Serial.print(", inverted: ");
    Serial.print(inverted);
    Serial.println();

    Command parsedCommand = { face, numTurns, inverted };
    return parsedCommand;
}

void loop() {
  if (Serial.available() > 0) {
    Command command = getNextCommand();
    runMove(command.face, command.numTurns, command.inverted);
  }
}
