#include "bmm150.h"
#include <Arduino.h>
#include <Wire.h>

BMM150::BMM150() {
}

int8_t BMM150::initialize(void) {
    // Wire.begin();

    /* Power up the sensor from suspend to sleep mode */
    set_op_mode(BMM150_SLEEP_MODE);
    delay(BMM150_START_UP_TIME);

    /* Check chip ID */
    uint8_t id = i2c_read(BMM150_CHIP_ID_ADDR);
    Serial.printf("id = %d\r\n", id);
    if (id != BMM150_CHIP_ID) {
        return BMM150_E_ID_NOT_CONFORM;
    }

    /* Function to update trim values */
    read_trim_registers();

    /* Setting the power mode as normal */
    set_op_mode(BMM150_NORMAL_MODE);

    /* Setting the preset mode as Low power mode
    i.e. data rate = 10Hz XY-rep = 1 Z-rep = 2*/
    set_presetmode(BMM150_PRESETMODE_LOWPOWER);
    // set_presetmode(BMM150_HIGHACCURACY_REPZ);

    return BMM150_OK;
}

void BMM150::calibrate(uint32_t timeout) {
    int16_t value_x_min = 0;
    int16_t value_x_max = 0;
    int16_t value_y_min = 0;
    int16_t value_y_max = 0;
    int16_t value_z_min = 0;
    int16_t value_z_max = 0;
    uint32_t timeStart  = 0;

    this->read_mag_data();
    value_x_min = this->raw_mag_data.raw_datax;
    value_x_max = this->raw_mag_data.raw_datax;
    value_y_min = this->raw_mag_data.raw_datay;
    value_y_max = this->raw_mag_data.raw_datay;
    value_z_min = this->raw_mag_data.raw_dataz;
    value_z_max = this->raw_mag_data.raw_dataz;
    delay(10);

    timeStart = millis();

    while ((millis() - timeStart) < timeout) {
        this->read_mag_data();

        /* Update x-Axis max/min value */
        if (value_x_min > this->raw_mag_data.raw_datax) {
            value_x_min = this->raw_mag_data.raw_datax;

        } else if (value_x_max < this->raw_mag_data.raw_datax) {
            value_x_max = this->raw_mag_data.raw_datax;
        }

        /* Update y-Axis max/min value */
        if (value_y_min > this->raw_mag_data.raw_datay) {
            value_y_min = this->raw_mag_data.raw_datay;

        } else if (value_y_max < this->raw_mag_data.raw_datay) {
            value_y_max = this->raw_mag_data.raw_datay;
        }

        /* Update z-Axis max/min value */
        if (value_z_min > this->raw_mag_data.raw_dataz) {
            value_z_min = this->raw_mag_data.raw_dataz;

        } else if (value_z_max < this->raw_mag_data.raw_dataz) {
            value_z_max = this->raw_mag_data.raw_dataz;
        }

        delay(1);
    }

    value_offset.x = value_x_min + (value_x_max - value_x_min) / 2;
    value_offset.y = value_y_min + (value_y_max - value_y_min) / 2;
    value_offset.z = value_z_min + (value_z_max - value_z_min) / 2;
}


void BMM150::read_mag_data() {
    int16_t msb_data;
    int8_t reg_data[BMM150_XYZR_DATA_LEN] = {0};

    i2c_read(BMM150_DATA_X_LSB, reg_data, BMM150_XYZR_DATA_LEN);

    /* Mag X axis data */
    reg_data[0] = BMM150_GET_BITS(reg_data[0], BMM150_DATA_X);
    /* Shift the MSB data to left by 5 bits */
    /* Multiply by 32 to get the shift left by 5 value */
    msb_data = ((int16_t)((int8_t)reg_data[1])) * 32;
    /* Raw mag X axis data */
    raw_mag_data.raw_datax = (int16_t)(msb_data | reg_data[0]);
    /* Mag Y axis data */
    reg_data[2] = BMM150_GET_BITS(reg_data[2], BMM150_DATA_Y);
    /* Shift the MSB data to left by 5 bits */
    /* Multiply by 32 to get the shift left by 5 value */
    msb_data = ((int16_t)((int8_t)reg_data[3])) * 32;
    /* Raw mag Y axis data */
    raw_mag_data.raw_datay = (int16_t)(msb_data | reg_data[2]);
    /* Mag Z axis data */
    reg_data[4] = BMM150_GET_BITS(reg_data[4], BMM150_DATA_Z);
    /* Shift the MSB data to left by 7 bits */
    /* Multiply by 128 to get the shift left by 7 value */
    msb_data = ((int16_t)((int8_t)reg_data[5])) * 128;
    /* Raw mag Z axis data */
    raw_mag_data.raw_dataz = (int16_t)(msb_data | reg_data[4]);
    /* Mag R-HALL data */
    reg_data[6] = BMM150_GET_BITS(reg_data[6], BMM150_DATA_RHALL);
    raw_mag_data.raw_data_r =
        (uint16_t)(((uint16_t)reg_data[7] << 6) | reg_data[6]);

    /* Compensated Mag X data in int16_t format */
    mag_data.x = compensate_x(raw_mag_data.raw_datax, raw_mag_data.raw_data_r);
    /* Compensated Mag Y data in int16_t format */
    mag_data.y = compensate_y(raw_mag_data.raw_datay, raw_mag_data.raw_data_r);
    /* Compensated Mag Z data in int16_t format */
    mag_data.z = compensate_z(raw_mag_data.raw_dataz, raw_mag_data.raw_data_r);
}

/*
 * @brief This internal API is used to obtain the compensated
 * magnetometer X axis data(micro-tesla) in int16_t.
 */
int16_t BMM150::compensate_x(int16_t mag_data_x, uint16_t data_rhall) {
    int16_t retval;
    uint16_t process_comp_x0 = 0;
    int32_t process_comp_x1;
    uint16_t process_comp_x2;
    int32_t process_comp_x3;
    int32_t process_comp_x4;
    int32_t process_comp_x5;
    int32_t process_comp_x6;
    int32_t process_comp_x7;
    int32_t process_comp_x8;
    int32_t process_comp_x9;
    int32_t process_comp_x10;

    /* Overflow condition check */
    if (mag_data_x != BMM150_XYAXES_FLIP_OVERFLOW_ADCVAL) {
        if (data_rhall != 0) {
            /* Availability of valid data*/
            process_comp_x0 = data_rhall;
        } else if (trim_data.dig_xyz1 != 0) {
            process_comp_x0 = trim_data.dig_xyz1;
        } else {
            process_comp_x0 = 0;
        }
        if (process_comp_x0 != 0) {
            /* Processing compensation equations*/
            process_comp_x1 = ((int32_t)trim_data.dig_xyz1) * 16384;
            process_comp_x2 = ((uint16_t)(process_comp_x1 / process_comp_x0)) -
                              ((uint16_t)0x4000);
            retval          = ((int16_t)process_comp_x2);
            process_comp_x3 = (((int32_t)retval) * ((int32_t)retval));
            process_comp_x4 =
                (((int32_t)trim_data.dig_xy2) * (process_comp_x3 / 128));
            process_comp_x5 = (int32_t)(((int16_t)trim_data.dig_xy1) * 128);
            process_comp_x6 = ((int32_t)retval) * process_comp_x5;
            process_comp_x7 = (((process_comp_x4 + process_comp_x6) / 512) +
                               ((int32_t)0x100000));
            process_comp_x8 =
                ((int32_t)(((int16_t)trim_data.dig_x2) + ((int16_t)0xA0)));
            process_comp_x9  = ((process_comp_x7 * process_comp_x8) / 4096);
            process_comp_x10 = ((int32_t)mag_data_x) * process_comp_x9;
            retval           = ((int16_t)(process_comp_x10 / 8192));
            retval = (retval + (((int16_t)trim_data.dig_x1) * 8)) / 16;
        } else {
            retval = BMM150_OVERFLOW_OUTPUT;
        }
    } else {
        /* Overflow condition */
        retval = BMM150_OVERFLOW_OUTPUT;
    }

    return retval;
}

/*
 * @brief This internal API is used to obtain the compensated
 * magnetometer Y axis data(micro-tesla) in int16_t.
 */
int16_t BMM150::compensate_y(int16_t mag_data_y, uint16_t data_rhall) {
    int16_t retval;
    uint16_t process_comp_y0 = 0;
    int32_t process_comp_y1;
    uint16_t process_comp_y2;
    int32_t process_comp_y3;
    int32_t process_comp_y4;
    int32_t process_comp_y5;
    int32_t process_comp_y6;
    int32_t process_comp_y7;
    int32_t process_comp_y8;
    int32_t process_comp_y9;

    /* Overflow condition check */
    if (mag_data_y != BMM150_XYAXES_FLIP_OVERFLOW_ADCVAL) {
        if (data_rhall != 0) {
            /* Availability of valid data*/
            process_comp_y0 = data_rhall;
        } else if (trim_data.dig_xyz1 != 0) {
            process_comp_y0 = trim_data.dig_xyz1;
        } else {
            process_comp_y0 = 0;
        }
        if (process_comp_y0 != 0) {
            /*Processing compensation equations*/
            process_comp_y1 =
                (((int32_t)trim_data.dig_xyz1) * 16384) / process_comp_y0;
            process_comp_y2 = ((uint16_t)process_comp_y1) - ((uint16_t)0x4000);
            retval          = ((int16_t)process_comp_y2);
            process_comp_y3 = ((int32_t)retval) * ((int32_t)retval);
            process_comp_y4 =
                ((int32_t)trim_data.dig_xy2) * (process_comp_y3 / 128);
            process_comp_y5 = ((int32_t)(((int16_t)trim_data.dig_xy1) * 128));
            process_comp_y6 =
                ((process_comp_y4 + (((int32_t)retval) * process_comp_y5)) /
                 512);
            process_comp_y7 =
                ((int32_t)(((int16_t)trim_data.dig_y2) + ((int16_t)0xA0)));
            process_comp_y8 =
                (((process_comp_y6 + ((int32_t)0x100000)) * process_comp_y7) /
                 4096);
            process_comp_y9 = (((int32_t)mag_data_y) * process_comp_y8);
            retval          = (int16_t)(process_comp_y9 / 8192);
            retval          = (retval + (((int16_t)trim_data.dig_y1) * 8)) / 16;
        } else {
            retval = BMM150_OVERFLOW_OUTPUT;
        }
    } else {
        /* Overflow condition*/
        retval = BMM150_OVERFLOW_OUTPUT;
    }

    return retval;
}

/*
 * @brief This internal API is used to obtain the compensated
 * magnetometer Z axis data(micro-tesla) in int16_t.
 */
int16_t BMM150::compensate_z(int16_t mag_data_z, uint16_t data_rhall) {
    int32_t retval;
    int16_t process_comp_z0;
    int32_t process_comp_z1;
    int32_t process_comp_z2;
    int32_t process_comp_z3;
    int16_t process_comp_z4;

    if (mag_data_z != BMM150_ZAXIS_HALL_OVERFLOW_ADCVAL) {
        if ((trim_data.dig_z2 != 0) && (trim_data.dig_z1 != 0) &&
            (data_rhall != 0) && (trim_data.dig_xyz1 != 0)) {
            /*Processing compensation equations*/
            process_comp_z0 =
                ((int16_t)data_rhall) - ((int16_t)trim_data.dig_xyz1);
            process_comp_z1 =
                (((int32_t)trim_data.dig_z3) * ((int32_t)(process_comp_z0))) /
                4;
            process_comp_z2 =
                (((int32_t)(mag_data_z - trim_data.dig_z4)) * 32768);
            process_comp_z3 =
                ((int32_t)trim_data.dig_z1) * (((int16_t)data_rhall) * 2);
            process_comp_z4 = (int16_t)((process_comp_z3 + (32768)) / 65536);
            retval          = ((process_comp_z2 - process_comp_z1) /
                      (trim_data.dig_z2 + process_comp_z4));

            /* saturate result to +/- 2 micro-tesla */
            if (retval > BMM150_POSITIVE_SATURATION_Z) {
                retval = BMM150_POSITIVE_SATURATION_Z;
            } else {
                if (retval < BMM150_NEGATIVE_SATURATION_Z)
                    retval = BMM150_NEGATIVE_SATURATION_Z;
            }
            /* Conversion of LSB to micro-tesla*/
            retval = retval / 16;
        } else {
            retval = BMM150_OVERFLOW_OUTPUT;
        }
    } else {
        /* Overflow condition*/
        retval = BMM150_OVERFLOW_OUTPUT;
    }

    return (int16_t)retval;
}

void BMM150::set_presetmode(uint8_t preset_mode) {
    switch (preset_mode) {
        case BMM150_PRESETMODE_LOWPOWER:
            /* Set the data rate x,y,z repetition
            for Low Power mode */
            settings.data_rate = BMM150_DATA_RATE_10HZ;
            settings.xy_rep    = BMM150_LOWPOWER_REPXY;
            settings.z_rep     = BMM150_LOWPOWER_REPZ;
            set_odr_xyz_rep(settings);
            break;
        case BMM150_PRESETMODE_REGULAR:
            /* Set the data rate x,y,z repetition
            for Regular mode */
            settings.data_rate = BMM150_DATA_RATE_10HZ;
            settings.xy_rep    = BMM150_REGULAR_REPXY;
            settings.z_rep     = BMM150_REGULAR_REPZ;
            set_odr_xyz_rep(settings);
            break;
        case BMM150_PRESETMODE_HIGHACCURACY:
            /* Set the data rate x,y,z repetition
            for High Accuracy mode */
            settings.data_rate = BMM150_DATA_RATE_20HZ;
            settings.xy_rep    = BMM150_HIGHACCURACY_REPXY;
            settings.z_rep     = BMM150_HIGHACCURACY_REPZ;
            set_odr_xyz_rep(settings);
            break;
        case BMM150_PRESETMODE_ENHANCED:
            /* Set the data rate x,y,z repetition
            for Enhanced Accuracy mode */
            settings.data_rate = BMM150_DATA_RATE_10HZ;
            settings.xy_rep    = BMM150_ENHANCED_REPXY;
            settings.z_rep     = BMM150_ENHANCED_REPZ;
            set_odr_xyz_rep(settings);
            break;
        default:
            break;
    }
}

void BMM150::set_odr_xyz_rep(struct bmm150_settings settings) {
    /* Set the ODR */
    set_odr(settings);
    /* Set the XY-repetitions number */
    set_xy_rep(settings);
    /* Set the Z-repetitions number */
    set_z_rep(settings);
}

void BMM150::set_xy_rep(struct bmm150_settings settings) {
    uint8_t rep_xy;
    rep_xy = settings.xy_rep;
    i2c_write(BMM150_REP_XY_ADDR, rep_xy);
}

void BMM150::set_z_rep(struct bmm150_settings settings) {
    uint8_t rep_z;
    rep_z = settings.z_rep;
    i2c_write(BMM150_REP_Z_ADDR, rep_z);
}

void BMM150::soft_reset() {
    uint8_t reg_data;

    reg_data = i2c_read(BMM150_POWER_CONTROL_ADDR);
    reg_data = reg_data | BMM150_SET_SOFT_RESET;
    i2c_write(BMM150_POWER_CONTROL_ADDR, reg_data);
    delay(BMM150_SOFT_RESET_DELAY);
}

void BMM150::set_odr(struct bmm150_settings settings) {
    uint8_t reg_data;

    reg_data = i2c_read(BMM150_OP_MODE_ADDR);
    /*Set the ODR value */
    reg_data = BMM150_SET_BITS(reg_data, BMM150_ODR, settings.data_rate);
    i2c_write(BMM150_OP_MODE_ADDR, reg_data);
}

void BMM150::i2c_write(short address, short data) {
    Wire.beginTransmission(BMM150_I2C_Address);
    Wire.write(address);
    Wire.write(data);
    Wire.endTransmission();
}

void BMM150::i2c_read(short address, uint8_t *buffer, short length) {
    Wire.beginTransmission(BMM150_I2C_Address);
    Wire.write(address);
    Wire.endTransmission();

    Wire.beginTransmission(BMM150_I2C_Address);
    Wire.requestFrom(BMM150_I2C_Address, length);

    if (Wire.available() == length) {
        for (uint8_t i = 0; i < length; i++) {
            buffer[i] = Wire.read();
        }
    }

    Wire.endTransmission();
}

void BMM150::i2c_read(short address, int8_t *buffer, short length) {
    Wire.beginTransmission(BMM150_I2C_Address);
    Wire.write(address);
    Wire.endTransmission();

    Wire.beginTransmission(BMM150_I2C_Address);
    Wire.requestFrom(BMM150_I2C_Address, length);

    if (Wire.available() == length) {
        for (uint8_t i = 0; i < length; i++) {
            buffer[i] = Wire.read();
        }
    }

    Wire.endTransmission();
}

uint8_t BMM150::i2c_read(short address) {
    uint8_t byte;

    Wire.beginTransmission(BMM150_I2C_Address);
    Wire.write(address);
    Wire.endTransmission();

    Wire.beginTransmission(BMM150_I2C_Address);
    Wire.requestFrom(BMM150_I2C_Address, 1);
    byte = Wire.read();

    Wire.endTransmission();
    return byte;
}

// char* BMM150::getErrorText(short errorCode);
// {
//     if(ERRORCODE_1_NUM == 1)
//     return ERRORCODE_1;

//     return "Error not defined.";
// }

void BMM150::set_op_mode(uint8_t pwr_mode) {
    /* Select the power mode to set */
    switch (pwr_mode) {
        case BMM150_NORMAL_MODE:
            /* If the sensor is in suspend mode
            put the device to sleep mode */
            suspend_to_sleep_mode();
            /* write the op mode */
            write_op_mode(pwr_mode);
            break;
        case BMM150_FORCED_MODE:
            /* If the sensor is in suspend mode
            put the device to sleep mode */
            suspend_to_sleep_mode();
            /* write the op mode */
            write_op_mode(pwr_mode);
            break;
        case BMM150_SLEEP_MODE:
            /* If the sensor is in suspend mode
            put the device to sleep mode */
            suspend_to_sleep_mode();
            /* write the op mode */
            write_op_mode(pwr_mode);
            break;
        case BMM150_SUSPEND_MODE:
            /* Set the power control bit to zero */
            set_power_control_bit(BMM150_POWER_CNTRL_DISABLE);
            break;
        default:
            break;
    }
}

void BMM150::suspend_to_sleep_mode(void) {
    set_power_control_bit(BMM150_POWER_CNTRL_ENABLE);
    /* Start-up time delay of 3ms*/
    delay(3);
}

void BMM150::read_trim_registers() {
    uint8_t trim_x1y1[2]     = {0};
    uint8_t trim_xyz_data[4] = {0};
    uint8_t trim_xy1xy2[10]  = {0};
    uint16_t temp_msb        = 0;

    /* Trim register value is read */
    i2c_read(BMM150_DIG_X1, trim_x1y1, 2);
    i2c_read(BMM150_DIG_Z4_LSB, trim_xyz_data, 4);
    i2c_read(BMM150_DIG_Z2_LSB, trim_xy1xy2, 10);
    /* Trim data which is read is updated
    in the device structure */
    trim_data.dig_x1   = (int8_t)trim_x1y1[0];
    trim_data.dig_y1   = (int8_t)trim_x1y1[1];
    trim_data.dig_x2   = (int8_t)trim_xyz_data[2];
    trim_data.dig_y2   = (int8_t)trim_xyz_data[3];
    temp_msb           = ((uint16_t)trim_xy1xy2[3]) << 8;
    trim_data.dig_z1   = (uint16_t)(temp_msb | trim_xy1xy2[2]);
    temp_msb           = ((uint16_t)trim_xy1xy2[1]) << 8;
    trim_data.dig_z2   = (int16_t)(temp_msb | trim_xy1xy2[0]);
    temp_msb           = ((uint16_t)trim_xy1xy2[7]) << 8;
    trim_data.dig_z3   = (int16_t)(temp_msb | trim_xy1xy2[6]);
    temp_msb           = ((uint16_t)trim_xyz_data[1]) << 8;
    trim_data.dig_z4   = (int16_t)(temp_msb | trim_xyz_data[0]);
    trim_data.dig_xy1  = trim_xy1xy2[9];
    trim_data.dig_xy2  = (int8_t)trim_xy1xy2[8];
    temp_msb           = ((uint16_t)(trim_xy1xy2[5] & 0x7F)) << 8;
    trim_data.dig_xyz1 = (uint16_t)(temp_msb | trim_xy1xy2[4]);
}

void BMM150::write_op_mode(uint8_t op_mode) {
    uint8_t reg_data = 0;
    reg_data         = i2c_read(BMM150_OP_MODE_ADDR);
    /* Set the op_mode value in Opmode bits of 0x4C */
    reg_data = BMM150_SET_BITS(reg_data, BMM150_OP_MODE, op_mode);
    i2c_write(BMM150_OP_MODE_ADDR, reg_data);
}

void BMM150::set_power_control_bit(uint8_t pwrcntrl_bit) {
    uint8_t reg_data = 0;
    /* Power control register 0x4B is read */
    reg_data = i2c_read(BMM150_POWER_CONTROL_ADDR);
    /* Sets the value of power control bit */
    reg_data = BMM150_SET_BITS_POS_0(reg_data, BMM150_PWR_CNTRL, pwrcntrl_bit);
    i2c_write(BMM150_POWER_CONTROL_ADDR, reg_data);
}
