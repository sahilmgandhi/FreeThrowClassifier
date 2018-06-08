#include "mbed.h"
#include "Hexi_KW40Z.h"
#include "Hexi_OLED_SSD1351.h"
#include "FXAS21002.h"
#include "FXOS8700.h"

Serial pc(USBTX, USBRX);
Ticker systick;

DigitalOut redLed(LED1,1);
DigitalOut greenLed(LED2,1);
DigitalOut blueLed(LED3,1);
DigitalOut haptic(PTB9);

//void StartHaptic(void);
//void StopHaptic(void const *n);

//RtosTimer hapticTimer(StopHaptic, osTimerOnce);
KW40Z kw40z_device(PTE24, PTE25);

// setup sensors
FXAS21002 gyro(PTC11,PTC10);
FXOS8700 accel(PTC11, PTC10);
FXOS8700 mag(PTC11, PTC10);

const float SYSTICK_PERIOD = .01;  // seconds

const int tick_duration = 5;  // duration/period
volatile int tick_counter = 0;

// flags to indicate state
volatile bool buttonPressed = 0;
volatile bool doMotion = 0;
volatile bool done = 1;
volatile bool overflow = 0;
volatile bool startHaptic = 0;

// accelerometer data
volatile float x_accel = 0;
volatile float x_velocity = 0;
volatile float x_distance = 0;

volatile float y_accel = 0;
volatile float y_velocity = 0;
volatile float y_distance = 0;

volatile float z_accel = 0;
volatile float z_velocity = 0;
volatile float z_distance = 0;

// gyroscope data
volatile float x_omega = 0;
volatile float x_theta = 0;

volatile float y_omega = 0;
volatile float y_theta = 0;

volatile float z_omega = 0;
volatile float z_theta = 0;

// arrays to store sample data
// data[0][] = accel
// data[1][] = velocity
// data[2][] = position 
const int DATA_SIZE = 500;
volatile float x_data[3][DATA_SIZE];
volatile float y_data[3][DATA_SIZE];
volatile float z_data[3][DATA_SIZE];

// angle[0][] = angular velocity
// angle[1][] = angle
volatile float x_angle[2][DATA_SIZE];
volatile float y_angle[2][DATA_SIZE];
volatile float z_angle[2][DATA_SIZE];

volatile int data_index = 0;


void updateValues(float dt) {
    float gyro_data[3];
    float accel_data[3];
    float mag_data[3];

    accel.acquire_accel_data_g(accel_data);
    gyro.acquire_gyro_data_dps(gyro_data);
    mag.acquire_mag_data_uT(mag_data);

    // convert to m/s^2
    x_accel = accel_data[0] * 9.8f;
    y_accel = accel_data[1] * 9.8f;
    z_accel = accel_data[2] * 9.8f;
    
    x_omega = gyro_data[0];
    y_omega = gyro_data[1];
    z_omega = gyro_data[2];
    
    // zero out readings for when stationary
    if (abs(x_accel) < 0.3f) {
        x_accel = 0;
    }
    if (abs(y_accel) < 0.3f) {
        y_accel = 0;  
    }
    if (abs(z_accel) < 0.3f) {
        z_accel = 0;
    }
    
    if (abs(x_omega) < 0.5f) {
        x_omega = 0;
    }
    if (abs(y_omega) < 0.5f) {
        y_omega = 0;  
    }
    if (abs(z_omega) < 0.5f) {
        z_omega = 0;
    }
    
    // integrate acceleration
    x_velocity += x_accel * dt;
    y_velocity += y_accel * dt;
    z_velocity += z_accel * dt;
    
    // integrate velocity
    x_distance += x_velocity * dt;
    y_distance += y_velocity * dt;
    z_distance += z_velocity * dt;
    
    // integrate angular velocity
    x_theta += x_omega * dt;
    y_theta += y_omega * dt;
    z_theta += z_omega * dt;

    // store values to print later
    x_data[0][data_index] = x_accel;
    x_data[1][data_index] = x_velocity;
    x_data[2][data_index] = x_distance;

    y_data[0][data_index] = y_accel;
    y_data[1][data_index] = y_velocity;
    y_data[2][data_index] = y_distance;
    
    z_data[0][data_index] = z_accel;
    z_data[1][data_index] = z_velocity;
    z_data[2][data_index] = z_distance;
    
    x_angle[0][data_index] = x_omega;
    x_angle[1][data_index] = x_theta;

    y_angle[0][data_index] = y_omega;
    y_angle[1][data_index] = y_theta;
    
    z_angle[0][data_index] = z_omega;
    z_angle[1][data_index] = z_theta;

    data_index++;
    
    // stop if index equals array size    
    if (data_index == DATA_SIZE) {
        overflow = 1;
        doMotion = 0;
    }
}

void printValues() {
    pc.printf("***Data Dump***\ntime,x_accel,y_accel,z_accel,x_velo,y_velo,z_velo,x_pos,y_pos,z_pos,x_omega,y_omega,z_omega,x_angle,y_angle,z_angle\n");
    for (int i = 0; i < data_index; i+=4) {
        pc.printf(
        "%0.2f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n%0.2f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n%0.2f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n%0.2f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n",
            (i+1)*0.01,x_data[0][i],y_data[0][i],z_data[0][i],x_data[1][i],y_data[1][i],z_data[1][i],
            x_data[2][i],y_data[2][i],z_data[2][i],x_angle[0][i],y_angle[0][i],z_angle[0][i],
            x_angle[1][i],y_angle[1][i],z_angle[1][i],
            
            (i+1+1)*0.01,x_data[0][i+1],y_data[0][i+1],z_data[0][i+1],x_data[1][i+1],y_data[1][i+1],z_data[1][i+1],
            x_data[2][i+1],y_data[2][i+1],z_data[2][i+1],x_angle[0][i+1],y_angle[0][i+1],z_angle[0][i+1],
            x_angle[1][i+1],y_angle[1][i+1],z_angle[1][i+1],
            
            (i+2+1)*0.01,x_data[0][i+2],y_data[0][i+2],z_data[0][i+2],x_data[1][i+2],y_data[1][i+2],z_data[1][i+2],
            x_data[2][i+2],y_data[2][i+2],z_data[2][i+2],x_angle[0][i+2],y_angle[0][i+2],z_angle[0][i+2],
            x_angle[1][i+2],y_angle[1][i+2],z_angle[1][i+2],
            
            (i+3+1)*0.01,x_data[0][i+3],y_data[0][i+3],z_data[0][i+3],x_data[1][i+3],y_data[1][i+3],z_data[1][i+3],
            x_data[2][i+3],y_data[2][i+3],z_data[2][i+3],x_angle[0][i+3],y_angle[0][i+3],z_angle[0][i+3],
            x_angle[1][i+3],y_angle[1][i+3],z_angle[1][i+3]
        );
    }
}

// zero out all variables
void resetValues() {
    x_accel = 0;
    x_velocity = 0;  
    x_distance = 0;  

    y_accel = 0;
    y_velocity = 0;  
    y_distance = 0;  
        
    z_accel = 0;
    z_velocity = 0;  
    z_distance = 0;  
    
    x_omega = 0;  
    x_theta = 0;  

    y_omega = 0;  
    y_theta = 0;  
        
    z_omega = 0;  
    z_theta = 0;
    
    data_index = 0;
    for (int i = 0; i < DATA_SIZE; i++) {
        x_data[0][i] = 0;
        x_data[1][i] = 0;
        x_data[2][i] = 0;        
        
        y_data[0][i] = 0;
        y_data[1][i] = 0;
        y_data[2][i] = 0;
                
        z_data[0][i] = 0;
        z_data[1][i] = 0;
        z_data[2][i] = 0;
        
        x_angle[0][i] = 0;
        x_angle[1][i] = 0;
        
        y_angle[0][i] = 0;
        y_angle[1][i] = 0;
        
        z_angle[0][i] = 0;
        z_angle[1][i] = 0;
    } 
}

void btnLeft(void) {
    startHaptic = 1;
    haptic = 1;
    doMotion = !doMotion; // start and stop motion with a button press
    done = 1;
}

void btnRight(void) {
    startHaptic = 1;
    haptic = 1;
    doMotion = !doMotion; // start and stop motion with a button press
    done = 1;
}

void systick_function() {    
    if (doMotion) {
        done = 0;
        blueLed = 0;
        updateValues(SYSTICK_PERIOD);
    } else {
        blueLed = 1;
    }
    if (startHaptic) {
        tick_counter++;
        
        if (tick_counter == tick_duration) {
            haptic = 0;
            startHaptic = 0;
            tick_counter = 0;
        }
    }
}

int main() {
    kw40z_device.attach_buttonLeft(&btnLeft);
    kw40z_device.attach_buttonRight(&btnRight);
    
    pc.printf("----This program has started----\n");
    redLed = 0;
    
    gyro.gyro_config();
    accel.accel_config();
    mag.mag_config();

//     read sensors in systick
    systick.attach(&systick_function, SYSTICK_PERIOD);
        
    while (1) {
//        doMotion = 0;
//        updateValues(SYSTICK_PERIOD);
//        pc.printf("x_ang,%.3f,%.3f,\t", x_omega, x_theta);
//        pc.printf("y_ang,%.3f,%.3f,\t", y_omega, y_theta);
//        pc.printf("z_ang,%.3f,%.3f,\n", z_omega, z_theta);
//        wait(SYSTICK_PERIOD);
        
        if (done) {
            printValues();
            resetValues();
            done = 0;
        }
        if (overflow) {
            pc.printf("Max number of samples exceeded\n");
            printValues();
            resetValues();
            overflow = 0;
        }
    }         
}
