//displaystuff.cpp
//LCD is 320x240 pixels, index 0,0 is top left corner while using M5.Lcd.draw...
//While using Sprite, 0,0 of pushSprite is top left corner of the sprite canvas, not the screen

#include "displaystuff.h"

void display_gyro_calib_found() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(4);
    M5.Lcd.setTextColor(GREEN);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.print("GYRO CALIB FOUND");
    delay(2000);
}

void display_no_gyro_calib_data() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(4);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.setTextColor(ORANGE);
    M5.Lcd.print("NO GYRO CALIB DATA");
    delay(1000);
}

void display_mag_calib_found() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(4);
    M5.Lcd.setTextColor(GREEN);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.print("MAG CALIB FOUND");
    delay(2000);
}

void display_no_mag_calib_data() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(4);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.setTextColor(ORANGE);
    M5.Lcd.print("NO MAG CALIB DATA");
    delay(1000);
}

void display_dont_move() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(4);
    M5.Lcd.setTextColor(RED);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.print("DONT  ");
    M5.Lcd.println("MOVE");
    delay(2000);
}

void display_gyro_calib_progress() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.println("GYRO CALIB. 20sec");
}

void display_mag_calib_progress() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.setTextColor(GREEN);
    M5.Lcd.println("MOVE.. 10sec");
}

void data_display_setup() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setCursor(80, 15);
    M5.Lcd.println("PEN TEST");
    M5.Lcd.setCursor(30, 30);
    M5.Lcd.println("  X       Y       Z");
    M5.Lcd.setCursor(30, 70);
    M5.Lcd.println("  Pitch   Roll    Yaw");
}

void display_ble_adv_started() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(4);
    M5.Lcd.setTextColor(BLUE);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.print("BLE Adv.  Started");
}

void displayBLEDisconnected() {
        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setTextSize(4);
        M5.Lcd.setTextColor(RED);
        M5.Lcd.setCursor(0, 0);
        M5.Lcd.print("BLE Disconnected");
}

void displayBLEConnected() {
        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setTextSize(4);
        M5.Lcd.setTextColor(GREEN);
        M5.Lcd.setCursor(0, 0);
        M5.Lcd.print("BLE Connected");
}