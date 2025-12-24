#include <Servo.h>

// THROTTLE PARAMETERS
int min_pulse_th = 841;
int mid_pulse_th = 1400;
int max_pulse_th = 1968;
int dead_zone_th = 30;
int throttle;
int target_throttle;
unsigned long pulse_throttle;
const int init_throttle = 0;
const int ramp_step = 5;
int dir_A_prev;
int dir_B_prev;

// PINS - THROTTLE
const int RX_throttle = 3;
const int throttle_pwm_pin = 11;
const int dir_A_throttle = 6;
const int dir_B_throttle = 7;

// STEERING PARAMETERS
int min_pulse_st = 1050;
int mid_pulse_st = 1600;
int max_pulse_st = 2180;
int dead_zone_st = 25;
unsigned long pulse_steering;
const int steering_range = 40;
int new_steering_angle;

// STEERING SERVO
Servo servo_motor;
int steering_angle = 90;
const int servo_pwm = 5;
const int RX_steering = 2;


volatile unsigned long throttle_pulse_width = 0;
volatile unsigned long rising_time_throttle = 0;

volatile unsigned long steering_pulse_width = 0;
volatile unsigned long rising_time_steering = 0;

void throttle_ISR();
void steering_ISR();

//--------------------------------------------------------------------//

// SETUP FUNCTION
void setup() {

  Serial.begin(9600);

  // THROTTLE PINs SETUP
  pinMode(RX_throttle, INPUT);
  pinMode(throttle_pwm_pin, OUTPUT);
  pinMode(dir_A_throttle, OUTPUT);
  pinMode(dir_B_throttle, OUTPUT);
  dir_A_prev = HIGH;
  dir_B_prev = LOW;


  // STEERING SERVO PIN SETUP
  servo_motor.attach(servo_pwm);
  servo_motor.write(90);

  // STEERING PINs SETUP
  pinMode(RX_steering, INPUT);

  attachInterrupt(digitalPinToInterrupt(RX_throttle), throttle_ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(RX_steering), steering_ISR, CHANGE);
}

//--------------------------------------------------------------------//

// LOOP FUNCTION
void loop() {

  // STEERING CONTROL
  noInterrupts();
  unsigned long pulse_steering = steering_pulse_width;
  interrupts();

  if (pulse_steering < (mid_pulse_st - dead_zone_st)) {
    new_steering_angle = map(pulse_steering, mid_pulse_st, min_pulse_st, 89, (90 - steering_range));
  } else if (pulse_steering > (mid_pulse_st + dead_zone_st)) {
    new_steering_angle = map(pulse_steering, mid_pulse_st, max_pulse_st, 91, (90 + steering_range));
  } else {
    new_steering_angle = 90;
  }
  if (new_steering_angle != steering_angle) {servo_motor.write(new_steering_angle); steering_angle = new_steering_angle;}
  
  delay(100);

  noInterrupts();
  unsigned long pulse_throttle = throttle_pulse_width;
  interrupts();

  if (pulse_throttle < (mid_pulse_th - dead_zone_th)) {
              target_throttle = map(pulse_throttle, min_pulse_th, mid_pulse_th, 255, 0);

                if (throttle < target_throttle) throttle += ramp_step;
                if (throttle > target_throttle) throttle -= ramp_step;

              digitalWrite(dir_A_throttle, HIGH);
              digitalWrite(dir_B_throttle, LOW);
              dir_A_prev = HIGH;
              dir_B_prev = LOW;
  } else if (pulse_throttle > (mid_pulse_th + dead_zone_th)) {
                target_throttle = map(pulse_throttle, mid_pulse_th, max_pulse_th, 0, 255);

              if (throttle < target_throttle) throttle += ramp_step;
              if (throttle > target_throttle) throttle -= ramp_step;

              digitalWrite(dir_A_throttle, LOW);
              digitalWrite(dir_B_throttle, HIGH);
              dir_A_prev = LOW;
              dir_B_prev = HIGH;
  } else {
              target_throttle = 0;
              if (throttle > target_throttle) throttle -= ramp_step;

              digitalWrite(dir_A_throttle, dir_A_prev);
              digitalWrite(dir_B_throttle, dir_B_prev);
  }
  throttle = constrain(throttle, 0, 255);
  analogWrite(throttle_pwm_pin, throttle);

  Serial.println("RX throttle pulse: " + String(pulse_throttle) + "// OUT-THROTTLE: " + String(throttle) + "// RX steering pulse: " + String(pulse_steering) + "// OUT-STEERING ANGLE: " + String(steering_angle));
}

//---------------ISR---------------

void throttle_ISR() {
  if(digitalRead(RX_throttle)) rising_time_throttle = micros();
  else throttle_pulse_width = micros() - rising_time_throttle;
}

void steering_ISR() {
  if(digitalRead(RX_steering)) rising_time_steering = micros();
  else steering_pulse_width = micros() - rising_time_steering;
}