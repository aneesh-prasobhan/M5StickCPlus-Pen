
#include <M5StickCPlus.h>
#define RESET_BUTTON_PIN GPIO_NUM_39

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

void IRAM_ATTR reset_isr(void *arg) 
{
    esp_restart();
}

void setupGpio() {
    gpio_config_t io_conf;
    io_conf.intr_type = GPIO_INTR_NEGEDGE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = (1ULL << RESET_BUTTON_PIN);
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&io_conf);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(RESET_BUTTON_PIN, reset_isr, NULL);
}

void setup() 
{   
    setupGpio();
    M5.begin();             // Init M5StickC Plus.
    M5.Imu.Init();          // Init IMU.  
    M5.Lcd.setRotation(3);  // Rotate the screen. 
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(1);
    M5.Lcd.setCursor(80, 15);  // set the cursor location. 
    M5.Lcd.println("IMU TEST");
    M5.Lcd.setCursor(30, 30);
    M5.Lcd.println("  X       Y       Z");
    M5.Lcd.setCursor(30, 70);
    M5.Lcd.println("  Pitch   Roll    Yaw");
    //Setup Serial
    Serial.begin(115200);

    M5.IMU.CalibrateGyro(20);
    M5.IMU.getCalibData(&gyroOffsetX, &gyroOffsetY, &gyroOffsetZ);  // Get gyro offsets after calibration

}


void loop() {
    static float temp = 0;
    M5.IMU.getGyroData(&gyroX, &gyroY, &gyroZ);
    
    gyroX -= gyroOffsetX;  // Subtract gyro offset from gyro reading
    gyroY -= gyroOffsetY;
    gyroZ -= gyroOffsetZ;
    
    M5.IMU.getAccelData(&accX, &accY, &accZ);
    M5.IMU.getAhrsData(&pitch, &roll, &yaw);
    // define sampleFreq 110.0f in library for this to work with correct scaling as per current sampling rate with serial print 
    M5.IMU.getTempData(&temp);
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
    M5.Lcd.printf("Temperature : %.2f C", temp);

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

    Serial.write((uint8_t *)&gyroXInt, 2);
    Serial.write((uint8_t *)&gyroYInt, 2);
    Serial.write((uint8_t *)&gyroZInt, 2);
    Serial.write((uint8_t *)&accXInt, 2);
    Serial.write((uint8_t *)&accYInt, 2);
    Serial.write((uint8_t *)&accZInt, 2);
    Serial.write((uint8_t *)&yawInt, 2);
    Serial.write((uint8_t *)&pitchInt, 2);
    Serial.write((uint8_t *)&rollInt, 2);
    // delay(50);
}
