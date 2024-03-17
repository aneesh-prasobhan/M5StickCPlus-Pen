//main.cpp
#include <M5StickCPlus.h>
#include "bmm150.h"
#include "bmm150_defs.h"
#include <EEPROM.h>

BMM150 bmm = BMM150();

bmm150_mag_data value;

bool bigButtonPressed = true;
bool bigButtonReleased = false;

float accX = 0.0F;
float accY = 0.0F;
float accZ = 0.0F;

float gyroX = 0.0F;
float gyroY = 0.0F;
float gyroZ = 0.0F;

float pitch = 0.0F;
float roll  = 0.0F;
float yaw   = 0.0F;

float gyroOffsetX = 0;
float gyroOffsetY = 0;
float gyroOffsetZ = 0;

float magCalibX = 0;
float magCalibY = 0;
float magCalibZ = 0;

// EEPROM addresses
const int EEPROM_SIZE = 30;  // 3 floats, 4 bytes each
const int GYRO_X_ADDRESS = 0;
const int GYRO_Y_ADDRESS = 4;
const int GYRO_Z_ADDRESS = 8;

// Define new EEPROM addresses for magnetometer calibration data
// const int MAG_CALIB_SIZE = 12;  // 3 floats, 4 bytes each
const int MAG_CALIB_X_ADDRESS = 15;  // After gyro calibration data
const int MAG_CALIB_Y_ADDRESS = 20;
const int MAG_CALIB_Z_ADDRESS = 25;


void setupGpio() {
    gpio_config_t io_conf;
    io_conf.intr_type = GPIO_INTR_NEGEDGE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = (1ULL << M5_BUTTON_RST);
    // for big button
    io_conf.pin_bit_mask |= (1ULL << M5_BUTTON_HOME);
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&io_conf);

}

bool check_for_gyro_calib() {
    // Check if gyro calibration data is present in EEPROM
    if (EEPROM.read(GYRO_X_ADDRESS) != 0xFF) 
    {
        gyroOffsetX = EEPROM.readFloat(GYRO_X_ADDRESS);
        gyroOffsetY = EEPROM.readFloat(GYRO_Y_ADDRESS);
        gyroOffsetZ = EEPROM.readFloat(GYRO_Z_ADDRESS);

        // Print saved data
        Serial.println("Gyro calibration data (Read from EEPORM): ");
        Serial.print("X: ");
        Serial.println(gyroOffsetX);
        Serial.print("Y: ");
        Serial.println(gyroOffsetY);
        Serial.print("Z: ");
        Serial.println(gyroOffsetZ);

        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setTextSize(4);
        M5.Lcd.setTextColor(GREEN);
        M5.Lcd.setCursor(0, 0);
        M5.Lcd.print("GYRO CALIB FOUND");
        delay(2000);
        return true;
    } else 
    {
        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setTextSize(4);
        M5.Lcd.setCursor(0, 0);
        M5.Lcd.setTextColor(ORANGE);
        M5.Lcd.print("NO GYRO CALIB DATA");
        delay(1000);
        return false;
    }
}

bool check_for_mag_calib() {

    if (bmm.initialize() == BMM150_E_ID_NOT_CONFORM) 
    {
        Serial.println("Chip ID can not read!");
        while (1)
        ;
    } 
    // Check if magnetometer calibration data is present in EEPROM
    if (EEPROM.read(MAG_CALIB_X_ADDRESS) != 0xFF ) 
    {  
        // Set magnetometer calibration data from EEPROM
        magCalibX = EEPROM.readFloat(MAG_CALIB_X_ADDRESS);
        magCalibY = EEPROM.readFloat(MAG_CALIB_Y_ADDRESS);
        magCalibZ = EEPROM.readFloat(MAG_CALIB_Z_ADDRESS);

        // Print saved data
        Serial.println("Magnetometer calibration data (Read from EEPROM): ");
        Serial.print("X: ");
        Serial.println(magCalibX);
        Serial.print("Y: ");
        Serial.println(magCalibY);
        Serial.print("Z: ");
        Serial.println(magCalibZ);
        
        // Magnetometer calibration data found
        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setTextSize(4);
        M5.Lcd.setTextColor(GREEN);
        M5.Lcd.setCursor(0, 0);
        M5.Lcd.print("MAG CALIB FOUND");

        delay(2000);
        return true;
    } else 
    {
        // No magnetometer calibration data found
        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setTextSize(4);
        M5.Lcd.setCursor(0, 0);
        M5.Lcd.setTextColor(ORANGE);
        M5.Lcd.print("NO MAG CALIB DATA");
        delay(1000);
        return false;
    }
}

void do_gyro_calibration() {
    // Perform gyro calibration

        
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(4);
    M5.Lcd.setTextColor(RED);
    M5.Lcd.setCursor(0, 0);  // set the cursor location.
    M5.Lcd.print("DONT  ");
    M5.Lcd.println("MOVE");
    delay(2000);
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.println("GYRO CALIB. 20sec");
    

    M5.IMU.CalibrateGyro(20);
    M5.IMU.getCalibData(&gyroOffsetX, &gyroOffsetY, &gyroOffsetZ);  // Get gyro offsets after calibration

    //Print Calibration data
    Serial.println("Gyro calibration data (Just calibrated): ");
    Serial.print("X: ");
    Serial.println(gyroOffsetX);
    Serial.print("Y: ");
    Serial.println(gyroOffsetY);
    Serial.print("Z: ");
    Serial.println(gyroOffsetZ);

    EEPROM.writeFloat(GYRO_X_ADDRESS, gyroOffsetX);
    EEPROM.writeFloat(GYRO_Y_ADDRESS, gyroOffsetY);
    EEPROM.writeFloat(GYRO_Z_ADDRESS, gyroOffsetZ);
    EEPROM.commit();


}

void do_mag_calibration() {
    // Perform magnetometer calibration
    if (bmm.initialize() == BMM150_E_ID_NOT_CONFORM) 
    {
        Serial.println("Chip ID can not read!");
        while (1)
        ;
    } 
    else 
    {
        Serial.println("Initialize done!");
        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setCursor(0, 0);
        M5.Lcd.setTextColor(GREEN);
        M5.Lcd.println("MOVE.. 10sec");
        bmm.calibrate(10000);
        Serial.print("\n\rCalibrate done..");

        // Print calibration data
        Serial.println("Magnetometer calibration data (Just calibrated): ");
        Serial.print("X: ");
        Serial.println(bmm.value_offset.x);
        Serial.print("Y: ");
        Serial.println(bmm.value_offset.y);
        Serial.print("Z: ");
        Serial.println(bmm.value_offset.z);

        // Save magnetometer calibration data to EEPROM
        magCalibX = bmm.value_offset.x;
        magCalibY = bmm.value_offset.y;
        magCalibZ = bmm.value_offset.z;
        EEPROM.put(MAG_CALIB_X_ADDRESS, magCalibX);
        EEPROM.put(MAG_CALIB_Y_ADDRESS, magCalibY);
        EEPROM.put(MAG_CALIB_Z_ADDRESS, magCalibZ);
        EEPROM.commit();
    }
}

void display_setup() {
    // Display other setup components
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setCursor(80, 15);  // set the cursor location. 
    M5.Lcd.println("PEN TEST");
    M5.Lcd.setCursor(30, 30);
    M5.Lcd.println("  X       Y       Z");
    M5.Lcd.setCursor(30, 70);
    M5.Lcd.println("  Pitch   Roll    Yaw");
}

void setup() 
{   
    setupGpio();
    M5.begin();             // Init M5StickC Plus.
    Wire.begin(0, 26);
    M5.Imu.Init();          // Init IMU.  
    M5.Lcd.setRotation(3);  // Rotate the screen. 

    EEPROM.begin(EEPROM_SIZE);  // Initialize EEPROM with defined size

    // Check for gyro calibration
    if (!check_for_gyro_calib()) {
        do_gyro_calibration();
    }

    // Check for magnetometer calibration
    if (!check_for_mag_calib()) {
        do_mag_calibration();
    }

    // Display other setup components
    display_setup();

}


void loop() {
    M5.IMU.getGyroData(&gyroX, &gyroY, &gyroZ);
    
    gyroX -= gyroOffsetX;  // Subtract gyro offset from gyro reading
    gyroY -= gyroOffsetY;
    gyroZ -= gyroOffsetZ;
    
    M5.IMU.getAccelData(&accX, &accY, &accZ);
    M5.IMU.getAhrsData(&pitch, &roll, &yaw);

    // define sampleFreq 110.0f in library for this to work with correct scaling as per current sampling rate with serial print 
    
    // Magnetometer Math
   
    bmm.read_mag_data();
    
    value.x = bmm.raw_mag_data.raw_datax - magCalibX;
    value.y = bmm.raw_mag_data.raw_datay - magCalibY;
    value.z = bmm.raw_mag_data.raw_dataz - magCalibZ;

    float xyHeading = atan2(value.x, value.y);
    // float zxHeading = atan2(value.z, value.x);
    float heading   = xyHeading;

    if (heading < 0) heading += 2 * PI;
    if (heading > 2 * PI) heading -= 2 * PI;
    float headingDegrees   = heading * 180 / M_PI;
    // float xyHeadingDegrees = xyHeading * 180 / M_PI;
    // float zxHeadingDegrees = zxHeading * 180 / M_PI;

    M5.Lcd.setCursor(30, 40);
    M5.Lcd.printf("%6.2f  %6.2f  %6.2f      ", gyroX, gyroY, gyroZ);
    M5.Lcd.setCursor(170, 40);
    M5.Lcd.print("o/s");
    M5.Lcd.setCursor(30, 50);
    M5.Lcd.printf(" %5.2f   %5.2f   %5.2f   ", accX, accY, accZ);
    M5.Lcd.setCursor(170, 50);
    M5.Lcd.print("G");
    M5.Lcd.setCursor(30, 80);
    M5.Lcd.printf(" %5.2f   %5.2f   %5.2f   ", pitch, roll, yaw);

    M5.Lcd.setCursor(30, 95);
    M5.Lcd.printf("headingDegrees: %2.1f", headingDegrees);

    // Assuming the following order: gyroX, gyroY, gyroZ, accX, accY, accZ
    int16_t gyroXInt = gyroX * 100;  // Convert float to int16_t by multiplying by 100
    int16_t gyroYInt = gyroY * 100;
    int16_t gyroZInt = gyroZ * 100;
    int16_t accXInt = accX * 100;
    int16_t accYInt = accY * 100;
    int16_t accZInt = accZ * 100;

    int16_t yawInt = yaw * -100;
    int16_t pitchInt = pitch * 100;
    int16_t rollInt = roll * -100;

    int16_t headingDegreesInt = headingDegrees * 100;

    Serial.write((uint8_t *)&gyroXInt, 2);
    Serial.write((uint8_t *)&gyroYInt, 2);
    Serial.write((uint8_t *)&gyroZInt, 2);
    Serial.write((uint8_t *)&accXInt, 2);
    Serial.write((uint8_t *)&accYInt, 2);
    Serial.write((uint8_t *)&accZInt, 2);
    Serial.write((uint8_t *)&yawInt, 2);
    Serial.write((uint8_t *)&pitchInt, 2);
    Serial.write((uint8_t *)&rollInt, 2);
    Serial.write((uint8_t *)&headingDegreesInt, 2);
    // delay(50);
    // if BIG Button is pressed, send 1  or 0 if not pressed
    if (digitalRead(M5_BUTTON_HOME) == 0) {
        Serial.write((uint8_t *)&bigButtonPressed, 2);
        M5.Lcd.fillRect(220, 0, 20, 135, GREEN);
    } else {
        Serial.write((uint8_t *)&bigButtonReleased, 2);
        M5.Lcd.fillRect(220, 0, 20, 135, RED);
    }

    if (digitalRead(M5_BUTTON_RST) == LOW) 
    {
        while (digitalRead(M5_BUTTON_RST) == LOW)
            ;
        // Recalibrate gyro if needed
        do_gyro_calibration();
        // Recalibrate magnetometer if needed
        do_mag_calibration();

        // Update display after recalibration
        display_setup();  
    }

}
