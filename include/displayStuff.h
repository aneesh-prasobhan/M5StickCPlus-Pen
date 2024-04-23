//displaystuff.h
#ifndef DISPLAYSTUFF_H
#define DISPLAYSTUFF_H

#include <M5StickCPlus.h>

void display_gyro_calib_found();
void display_no_gyro_calib_data();
void display_mag_calib_found();
void display_no_mag_calib_data();
void display_dont_move();
void display_gyro_calib_progress();
void display_mag_calib_progress();
void data_display_setup();

#endif