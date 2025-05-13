#include <AccelStepper.h>

const int MOTOR_STEPS_PER_REVOLUTION = 400;
const int MOTOR_STEPS_PER_TURN = MOTOR_STEPS_PER_REVOLUTION / 4;  // one turn is a quarter revolution
const int MOTOR_VELOCITY_CONSTANT = 100;
const int MOTOR_ACCELERATION_CONSTANT = 100;
const int MOTOR_MAX_SPEED = MOTOR_VELOCITY_CONSTANT * MOTOR_STEPS_PER_REVOLUTION;
const int MOTOR_ACCELERATION = MOTOR_ACCELERATION_CONSTANT * MOTOR_STEPS_PER_REVOLUTION;

const int NUM_STEPPERS = 6;
AccelStepper steppers[NUM_STEPPERS] = {
  AccelStepper(AccelStepper::DRIVER, 2, 5),
  AccelStepper(AccelStepper::DRIVER, 3, 6),
  AccelStepper(AccelStepper::DRIVER, 4, 7),
  AccelStepper(AccelStepper::DRIVER, 8, 11),
  AccelStepper(AccelStepper::DRIVER, 9, 12),
  AccelStepper(AccelStepper::DRIVER, 10, 13),
};

struct Move {
  char face;
  
  int numTurns;
  bool inverted;
};

void setup() {
  Serial.begin(9600);

  pinMode(A0, OUTPUT);
  pinMode(A1, OUTPUT);

  for (int i = 0; i < NUM_STEPPERS; i++) {
    steppers[i].setMaxSpeed(MOTOR_MAX_SPEED);
    steppers[i].setAcceleration(MOTOR_ACCELERATION);
  }

  Serial.println("STATUS:READY");
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

  stepper.runToNewPosition(currentPosition + deltaPosition);
}

struct Move getMove(String command) {
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

  Move move = { face, numTurns, inverted };
  return move;
}

void handleCommand(String command) {
  if (command.startsWith("MOVE:")) {
    handleMoveCommand(command.substring(5));
  } else if (command.startsWith("LIGHT:")) {
    handleLightCommand(command.substring((6)));
  } 
}

void handleMoveCommand(String command) {
  Move move = getMove(command);
  runMove(move.face, move.numTurns, move.inverted);
}

void handleLightCommand(String command) {
  if (command.endsWith("U0")) { // upper off
    digitalWrite(A0, LOW);
  } else if (command.endsWith("U1")) { // upper on
    digitalWrite(A0, HIGH);
  } else if (command.endsWith("L0")) { // lower off
    digitalWrite(A1, LOW);
  } else if (command.endsWith("L1")) { // lower on
    digitalWrite(A1, HIGH);
  }
}


void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();

    handleCommand(command);

    Serial.print("DONE:");
    Serial.println(command);
  }
}
