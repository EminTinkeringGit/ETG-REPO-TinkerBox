#include <Servo.h>

// SERVO CABLES
// BROWN: GND
// RED: POSITIVE
// ORANGE: PWM

// STEERING SERVO
Servo servo_motor;
const int servo_pwm = 9;
int init_angle = 90;
int oper_angle;
int pulse_width;

// SETUP FUNCTION
void setup() {

  Serial.begin(9600);

  // STEERING SERVO PIN SETUP
  servo_motor.attach(servo_pwm);
  servo_motor.write(init_angle);
}

// LOOP FUNCTION
void loop() {

  pulse_width = servo_motor.read();
  Serial.println("oper_angle: " + String(pulse_width));

  //for(oper_angle = 0; oper_angle <= 180; oper_angle++){
  //oper_angle = oper_angle + 1;
  //servo_motor.write(oper_angle);
  //delay(90);
  //}
}
