// Define RX Channel Pins (Connect to RC Receiver)
const int PIN_YAW_IN   = 2;  // Input A
const int PIN_PITCH_IN = 3;  // Input B
const int PIN_HGHT_IN  = 4;  // Input C

// Define Motor Pins (Must be PWM pins to control speed)
const int PIN_MOTOR_LEFT_YAW  = 5;  // Yaw/Height Motor 1
const int PIN_MOTOR_RIGHT_YAW = 6;  // Yaw/Height Motor 2
const int PIN_MOTOR_PITCH     = 9;  // Pitch Motor
const int PIN_MOTOR_PITCH_low     = 10;  // Pitch Motor

// RC Signal Constants (Standard RC signals range from 1000us to 2000us)
const int RC_MIN = 1000;
const int RC_MID = 1500;
const int RC_MAX = 2000;
const int DEADZONE = 30; // Prevents motor twitching at center stick

void setup() {
  // Initialize Serial Communication at 9600 baud rate
  Serial.begin(9600);

  // Initialize RX pins as inputs
  pinMode(PIN_YAW_IN, INPUT);
  pinMode(PIN_PITCH_IN, INPUT);
  pinMode(PIN_HGHT_IN, INPUT);

  // Initialize Motor pins as outputs
  pinMode(PIN_MOTOR_LEFT_YAW, OUTPUT);
  pinMode(PIN_MOTOR_RIGHT_YAW, OUTPUT);
  pinMode(PIN_MOTOR_PITCH, OUTPUT);
  pinMode(PIN_MOTOR_PITCH_low, OUTPUT);

  digitalWrite(PIN_MOTOR_PITCH_low, LOW); 
}

void loop() {
  // 1. Read the pulse width (in microseconds) from each channel
  int rawYaw   = pulseIn(PIN_YAW_IN, HIGH, 25000);   // Input A
  int rawPitch = pulseIn(PIN_PITCH_IN, HIGH, 25000); // Input B
  int rawHght  = pulseIn(PIN_HGHT_IN, HIGH, 25000);  // Input C

  // Fallback to neutral defaults if receiver loses signal (returns 0)
  if (rawYaw == 0)   rawYaw = RC_MID;
  if (rawPitch == 0) rawPitch = RC_MID;
  if (rawHght == 0)  rawHght = RC_MIN; // Default height to off for safety

  // 2. Map Pitch directly to its motor (1000-2000us mapped to 0-255 PWM)
  int pitchPWM = map(rawPitch, RC_MID, RC_MAX, 0, 255);
  pitchPWM = constrain(pitchPWM, 0, 255);

  // 3. Process Yaw and Height for Differential Thrust
  int yawOffset = rawYaw - RC_MID;
  
  // Apply a small deadzone
  if (abs(yawOffset) < DEADZONE) {
    yawOffset = 0;
  }

  // Map the base height input to a PWM range
  int baseHeightPWM = map(rawHght, RC_MIN, RC_MAX, 0, 255);
  baseHeightPWM = constrain(baseHeightPWM, 0, 255);

  // Scale the yaw offset to fit within a reasonable PWM steering influence
  int steeringOutput = map(yawOffset, -500, 500, -100, 100);

  // Mix height and steering for the two individual motors
  int leftMotorPWM  = baseHeightPWM + steeringOutput;
  int rightMotorPWM = baseHeightPWM - steeringOutput;

  // Constrain final motor values to valid PWM limits (0 - 255)
  leftMotorPWM  = constrain(leftMotorPWM, 0, 255);
  rightMotorPWM = constrain(rightMotorPWM, 0, 255);

  // 4. Write PWM signals to the Motor Drivers/ESCs
  analogWrite(PIN_MOTOR_PITCH, pitchPWM);
  analogWrite(PIN_MOTOR_LEFT_YAW, leftMotorPWM);
  analogWrite(PIN_MOTOR_RIGHT_YAW, rightMotorPWM);

  // 5. Serial Printing Debugging Information
  // This prints values on a single line tab-separated, then jumps to a new line
  Serial.print("Yaw (In A): ");
  Serial.print(rawYaw);
  Serial.print(" us\t| Pitch (In B): ");
  Serial.print(rawPitch);
  Serial.print(" us\t| Height (In C): ");
  Serial.print(rawHght);
  Serial.print(" us");

  Serial.print("\t| Pitch pwm: ");
  Serial.println(pitchPWM);

  delay(20); // Slightly increased delay to keep the Serial monitor readable
}