/*
 * RECORD.h
 *
 *  Created on: Mar 24, 2022
 *      Author: Raquel Ibáñez Alcalá
 *      Version: v0.2 (October 6, 2022) for MCU firmware version v2.1.1 and newer and RECORD library v0.1 and newer
 *
 *  Duty cycle configurations for individual feeder LED rings.
 *  Configurations for Arena: Development.
 *
 */

#ifndef MCUCFG_DEV1_H_
#define MCUCFG_DEV1_H_

/* -------------------- Structures --------------------------------------------------------------------------------- */
/* Declare structures for light levels 1, 2, and 3. These structures will contain the CCR value for each LED ring for
 * all four feeders at each level, allowing fine-tuned control of the duty cycle for each LED ring. This is to account
 * for natural variations due to cable length, soldering, wires, etc.
 * MCUinfo structure has all the MCU parameters for this particular device.
 */
struct LightLevel
{
    unsigned int fdr1;
    unsigned int fdr2;
    unsigned int fdr3;
    unsigned int fdr4;
};

struct MCUinfo
{
    char* device;       // The microcontroller part #.
    char* device_id;    // The putty ID associated with this device.
    char* firm_ver;     // Firmware version indicated by the header on main__vX_x.c.
    char* lib_ver;      // RECORD library version indicated by the header on RECORD.h.
    char* cfg_ver;      // Configuration version indicated by the header on this file.
    char* updated;      // Last date the MCU was flashed with new parameters or firmware.
};

/*** RELAY CLOSE TIME:
* The following controls the amount of time a relay, which supplies its associated valve with power, will
* remain closed. A closed relay will supply power to its associated valve, which opens the valve and drops
* liquid reward into the feeder on the arena floor. The number corresponds to the amount of *milliseconds* the
* microcontroller must wait with the relay closed before opening it up again. 1 second corresponds to
* 1000 milliseconds, and one millisecond corresponds to 8 thousand (8,000) CPU cycles.
*/
unsigned long RELAY_ONTIME = 500;   // Default relay active time. Milliseconds to delay when toggling relays, which connect to valves. Configurable online. Default: 500 milliseconds, or 4,000,000 cycles.

/*** TTL UP TIME:
 * This system relies on TTL pulses to let other devices know when an instruction has been executed. They are also useful for this system to
 * know when to perform some action. The length of the outgoing TTL pulses can be controlled here, as different systems may need longer or
 * shorter pulses in order to be see by another device. The number below represents the amount of milliseconds a TTL should be.
 */
unsigned long TTL_LENGTH = 100;     // Default length of output TTL pulse, in milliseconds. Configurable online.

/* -------- System Information ------------------------------------------------------------------------------------- */
/*** SYSTEM INFORMATION:
* This structure is for informative purposes only. This information will be displayed at execution of the '?' command.
* User should update only the last 5 parameters in this structure. See above for information on each parameter.
*/
struct MCUinfo Device = { .device    = "MSP-EXP430FR2355 Rev. A",
                          .device_id = "FR2355_Dev",
                          .firm_ver  = "v2.2.0",
                          .lib_ver   = "v1.2",
                          .cfg_ver   = "v0.2",
                          // User, update these accordingly.
                          .updated   = "17-February-2023"};

/* -------- Independent Variables ---------------------------------------------------------------------------------- */

/*** LED BRIGHTNESS CONTROL:
* These three values control the brightness of the feeder LEDs.
* The number has an inverse relationship with brightness, meaning the lower the number, the brighter the
* LEDs will glow. A value of 0 is the minimum value you can set these to, which will correspond to the
* LED's maximum brightness capped by the LED itself. The maximum value is 8000, which will turn the LEDs off.
*
* - Set a value between 0 and 8000. Higher numbers will increase LED brightness. MODIFY ONLY THE NUMBER, NOT
*   THE DEFINITION NAME:
*/
/* Light Level 0 (0 Lux) */
struct LightLevel L0 = {.fdr1 = 8000,
                        .fdr2 = 8000,
                        .fdr3 = 8000,
                        .fdr4 = 8000};

/* Light Level 1 (15 Lux) */
struct LightLevel L1 = {.fdr1 = 7700,
                        .fdr2 = 7700,
                        .fdr3 = 7700,
                        .fdr4 = 7700};

/* Light Level 2 (140 Lux) */
struct LightLevel L2 = {.fdr1 = 3500,
                        .fdr2 = 3500,
                        .fdr3 = 3500,
                        .fdr4 = 3500};

/* Light Level 3 (240 Lux) */
struct LightLevel L3 = {.fdr1 = 250,
                        .fdr2 = 250,
                        .fdr3 = 250,
                        .fdr4 = 250};

#endif /* MCUCFG_DEV1_H_ */
