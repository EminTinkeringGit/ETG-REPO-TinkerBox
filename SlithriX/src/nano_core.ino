// Pin Definitions
const int rcPin = 3;  // Input pin from RC Receiver Channel
const int in1 = 9;    // Output pin to H-Bridge IN1 (PWM)
const int in2 = 10;   // Output pin to H-Bridge IN2

// Calibration variables (Standard RC signals)
const int rcMin = 1400;  // Neutral / Stick all the way down for forward-only
const int rcMax = 1900;  // Full Throttle / Stick all the way up

void setup() {
  pinMode(rcPin, INPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  
  // Ensure the direction is locked to Forward
  digitalWrite(in2, LOW); 
  
  // Optional: Initialize serial monitor for debugging/calibration
  Serial.begin(9600);
}

void loop() {
  // Read the pulse duration from the RC receiver (in microseconds)
  unsigned long rcDuration = pulseIn(rcPin, HIGH, 25000); // 25ms timeout

  // If signal is lost or stick is below neutral, ensure motor stays stopped
  if (rcDuration < rcMin || rcDuration > 2200) {
    analogWrite(in1, 0); 
    Serial.println("Motor Stopped (Neutral or No Signal)");
  } 
  else {
    // Map the RC signal range (1500 to 2000) to Arduino PWM range (0 to 255)
    int motorSpeed = map(rcDuration, rcMin, rcMax, 0, 255);
    
    // Constrain the value to safety limits
    motorSpeed = constrain(motorSpeed, 0, 255);
    
    // Drive the motor
    analogWrite(in1, motorSpeed);
    
    // Debugging print to see your live stick values
    Serial.print("RC Pulse: ");
    Serial.print(rcDuration);
    Serial.print(" us | Motor Speed: ");
    Serial.println(motorSpeed);
  }

  delay(20); // Small delay to match standard RC refresh rates
}