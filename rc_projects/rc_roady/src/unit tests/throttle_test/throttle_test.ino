#include <Servo.h>

// THROTTLE PARAMETERS
int min_pulse_th = 841;
int mid_pulse_th = 1400;
int max_pulse_th = 1968;
int dead_zone_th = 30;
int throttle;
unsigned long pulse_throttle;
const int init_throttle = 0;

// RECEVING CHANNELS - THROTTLE
const int RX_throttle = 9;
const int throttle_pwm_pin = 10;
const int dir_A_throttle = 12;
const int dir_B_throttle = 13;

void setup() {

  // THROTTLE PINs SETUP
  pinMode(RX_throttle, INPUT);
  pinMode(throttle_pwm_pin, OUTPUT);
  pinMode(dir_A_throttle, OUTPUT);
  pinMode(dir_B_throttle, OUTPUT);

  // IC (Initial Conditions)
  analogWrite(throttle_pwm_pin, init_throttle);
  digitalWrite(dir_A_throttle, HIGH);
  digitalWrite(dir_B_throttle, LOW);
}

//--------------------------------------------------------------------//

// LOOP FUNCTION
void loop() {
    analogWrite(throttle_pwm_pin, 30);  // PWM for motor speed
    digitalWrite(dir_A_throttle, HIGH);
    digitalWrite(dir_B_throttle, LOW);
}
