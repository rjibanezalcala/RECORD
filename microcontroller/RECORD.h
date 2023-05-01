/*
 * RECORD.h
 *
 *  Created on: Mar 21, 2022
 *      Author: Raquel Ibáñez Alcalá
 *      Version: v1.2 (October 6, 2022) for MCU firmware version v2.1.1 and newer
 *
 *  Library of functions, structures, and definitions made for the RECORD system at the University of Texas at El Paso, Friedman Lab.
 *
 */

#ifndef RECORD_H_
#define RECORD_H_

/* CHANGE THIS FILE ACCORDING ON WHAT ARENA YOU'RE UPDATING */
#include <mcucfg_dev1.h>

/* ----------------------------------------------------------------------------------------------------------------- */

/* ------ GPIO Definitions ------ */
// DON'T TOUCH THESE!!
// Port 1
#define RXD     BIT6    // UART RX
#define TXD     BIT7    // UART TX
#define REDLED  BIT0    // LED1 output
// Port 2
#define BTN2    BIT3    // On-board button S2 (input)
// Port 3
#define ACK     BIT0    // Acknowledge command signal (output)
#define RELAY1  BIT1    // Relay to drive larger circuit (output)
#define RELAY2  BIT2    // Relay to drive larger circuit (output)
#define RELAY3  BIT7    // Relay to drive larger circuit (output)
#define RELAY4  BIT4    // Relay to drive larger circuit (output)
#define TTL_IN  BIT5    // TTL input from Noldus, stepped down to ~ 3.3V using a voltage divider (input)
#define TTL_OUT BIT6    // TTL output to Noldus (output)
// Port 4
#define BTN1    BIT1    // On-board button S1 (input)
// Port 5
#define LED1    BIT1    // External LED
#define LED2    BIT2    // External LED
#define LED3    BIT3    // External LED
#define LED4    BIT4    // External LED
// Port 6
#define TB3_1   BIT0    // Timer 3, CCR1 output: LED ring 1
#define TB3_2   BIT1    // Timer 3, CCR2 output: LED ring 2
#define TB3_3   BIT2    // Timer 3, CCR3 output: LED ring 3
#define TB3_4   BIT3    // Timer 3, CCR4 output: LED ring 4
#define TB3_5   BIT4    // Timer 3, CCR5 output: Cue LED
#define GRNLED  BIT6    // LED2 output

/* ----------- Other ----------- */
#define MCLK_FREQ_MHZ 8 // MCLK = 8MHz, affects pulse width modulation duty cycles and baud rate for UART communication. DO NOT CHANGE.
#define delay_us(x)     __delay_cycles((long) x* 8)
#define STEP 5          // Increment value for duty cycle modulation in PWM.
#define LOWER_LIMIT 80  // Lower limit of Timer capture compare register for PWM. Used for TB3CCR5 (cue LED).
#define UPPER_LIMIT 8000// Upper limit of Timer capture compare register for PWM. Used for TB3CCR5 (cue LED).
#define DOWN 0          // Used to define a downwards direction for Timer capture compare register for PWM.
#define UP   1          // Used to define an upwards direction for Timer capture compare register for PWM.

/* ------ Function Declarations ------ */
void ButtonSetup(void);         // Sets up button on P1.3 for interrupts to be used as a tester.
void UARTsendMsg(char* string); // Sends a string of characters through UCA0 in the configures UART mode.
void Software_Trim(void);       // Used to configure DCO (CPU clock).
inline int SetBrightness(char led, char brightness);  // Sets led brightness of one or more LEDs.
inline void ModifyCCR(struct LightLevel* entry, char feeder, unsigned int newValue);    // Modifies elements of structures of type LightLevel.
inline void UARTsendMsg(char* string);  // Send string through UART.
inline void itoa(long unsigned int value, char* result, int base);  // Utility function to convert integers to characters for sending through UART.

/* ------ Global Variables ------ */

/* ------ Timer Variables ------ */
volatile unsigned int ms = 0;  // Milliseconds counter (1000 ms in 1 s).
volatile unsigned int sc = 0;  // Seconds counter (maximum 65,536 seconds - 1, ~18.2 hours).

/* ------ Function Definitions ------ */
inline void delay_ms(unsigned long d_ms)
{
    /* Makes use of Timer B0 ISR to implement a sleepy delay. The microcontroller will go to sleep while Timer B0 operates in up mode, counting up to the CCR value
     * declared during initialization which at the time of writing this was defined at 8000, giving a period of 1 millisecond. In this function, I trap the
     * microcontroller in a while loop and increment the counting variable every millisecond until it matches the desired delay in milliseconds. The timer is then
     * turned off before exiting.
     *      - unsigned long (integer) d_ms, the desired delay in milliseconds.
     */
    unsigned long i = 0;    // Declare local counting variable.
    TB1CTL |= MC_1;         // Turn delay timer on.
    while(i < d_ms){
        __bis_SR_register(LPM0_bits);  // Go to sleep while relay is closed.
        i++;                // Increment counting variable until it matches the desired delay.
    }
    TB1CTL &= ~MC_1;        // Turn delay timer off.
}

inline int SetBrightness(char led, char brightness)
{
    /* Sets the brightness of an LED using pulse width modulation by manipulating the duty cycle of the pulse.
     * Assumes each LED is connected to a separate Timer B.
     * Variables:
     *      - char led: Mask which identifies the target LED.
     *      - char brightness: Discrete brightness level from 0 to 3, where 0 is 0% duty cycle and 3 is 75% duty cycle.
     */

    struct LightLevel *lvl_ptr;

    /* Decide which structure to point to, depending on what brightness level is passed. */
    switch (brightness)
    {
    case ('0'):
        lvl_ptr = &L0;  // Off
        break;
    case ('1'):
        lvl_ptr = &L1;  // Point to level 1 structure
        break;
    case ('2'):
        lvl_ptr = &L2;  // Point to level 2 structure
        break;
    case ('3'):
        lvl_ptr = &L3;  // Point to level 3 structure
        break;
    default:
        // Randomize value to an integer between 1 and 3 (future work?)
        break;
    }

    /* Check which LEDs need to be given the setting */
    /* Assign the appropriate element of the structure to the timer B capture compare register corresponding to that feeder. */
    if (led == '1')
    {
        TB3CCR1 = lvl_ptr->fdr1;
    }
    else if (led == '2')
    {
        TB3CCR2 = lvl_ptr->fdr2;
    }
    else if (led == '3')
    {
        TB3CCR3 = lvl_ptr->fdr3;
    }
    else if (led == '4')
    {
        TB3CCR4 = lvl_ptr->fdr4;
    }
    else
        return 1;

    return 0;
}

inline void ModifyCCR(struct LightLevel* entry, char feeder, unsigned int newValue)
{
    /* Rewrites the levels structures. */
    switch (feeder)
    {
    case '1':
        entry->fdr1 = newValue;
        break;
    case '2':
        entry->fdr2 = newValue;
        break;
    case '3':
        entry->fdr3 = newValue;
        break;
    case '4':
        entry->fdr4 = newValue;
        break;
    default:
        break;
    }
}

void ButtonSetup(void)
{
    //P4.1 and P2.3 Setup in a Pull-up Configuration with Falling-Edge Triggered Interrupt
    P4DIR &= ~BTN1;
    P4REN |= BTN1;
    P4OUT |= BTN1;
    P4IE  |= BTN1;
    P4IES |= BTN1;
    P4IFG &= ~BTN1;
/*
    P2DIR &= ~BTN2;
    P2REN |= BTN2;
    P2OUT |= BTN2;
    P2IE  |= BTN2;
    P2IES |= BTN2;
    P2IFG &= ~BTN2;
*/
    return;
}

inline void UARTsendMsg(char* string)
{
    /* Simple function to send a message through UART */
    while(UCA0STATW & UCBUSY);        // May not be needed. Checks if the UCA0 module is busy sending or receiving a message.
    while(*string)
    {
        UCA0TXBUF = *string++;
        while(UCA0STATW & UCBUSY);   // May not be needed. Checks if the UCA0 module is busy sending or receiving a message.
    }

    return;
}



void Software_Trim()
{
    unsigned int oldDcoTap = 0xffff;
    unsigned int newDcoTap = 0xffff;
    unsigned int newDcoDelta = 0xffff;
    unsigned int bestDcoDelta = 0xffff;
    unsigned int csCtl0Copy = 0;
    unsigned int csCtl1Copy = 0;
    unsigned int csCtl0Read = 0;
    unsigned int csCtl1Read = 0;
    unsigned int dcoFreqTrim = 3;
    unsigned char endLoop = 0;

    do
    {
        CSCTL0 = 0x100;                         // DCO Tap = 256
        do
        {
            CSCTL7 &= ~DCOFFG;                  // Clear DCO fault flag
        }while (CSCTL7 & DCOFFG);               // Test DCO fault flag

        __delay_cycles((unsigned int)3000 * MCLK_FREQ_MHZ);// Wait FLL lock status (FLLUNLOCK) to be stable
                                                           // Suggest to wait 24 cycles of divided FLL reference clock
        while((CSCTL7 & (FLLUNLOCK0 | FLLUNLOCK1)) && ((CSCTL7 & DCOFFG) == 0));

        csCtl0Read = CSCTL0;                   // Read CSCTL0
        csCtl1Read = CSCTL1;                   // Read CSCTL1

        oldDcoTap = newDcoTap;                 // Record DCOTAP value of last time
        newDcoTap = csCtl0Read & 0x01ff;       // Get DCOTAP value of this time
        dcoFreqTrim = (csCtl1Read & 0x0070)>>4;// Get DCOFTRIM value

        if(newDcoTap < 256)                    // DCOTAP < 256
        {
            newDcoDelta = 256 - newDcoTap;     // Delta value between DCPTAP and 256
            if((oldDcoTap != 0xffff) && (oldDcoTap >= 256)) // DCOTAP cross 256
                endLoop = 1;                   // Stop while loop
            else
            {
                dcoFreqTrim--;
                CSCTL1 = (csCtl1Read & (~DCOFTRIM)) | (dcoFreqTrim<<4);
            }
        }
        else                                   // DCOTAP >= 256
        {
            newDcoDelta = newDcoTap - 256;     // Delta value between DCPTAP and 256
            if(oldDcoTap < 256)                // DCOTAP cross 256
                endLoop = 1;                   // Stop while loop
            else
            {
                dcoFreqTrim++;
                CSCTL1 = (csCtl1Read & (~DCOFTRIM)) | (dcoFreqTrim<<4);
            }
        }

        if(newDcoDelta < bestDcoDelta)         // Record DCOTAP closest to 256
        {
            csCtl0Copy = csCtl0Read;
            csCtl1Copy = csCtl1Read;
            bestDcoDelta = newDcoDelta;
        }

    }while(endLoop == 0);                      // Poll until endLoop == 1

    CSCTL0 = csCtl0Copy;                       // Reload locked DCOTAP
    CSCTL1 = csCtl1Copy;                       // Reload locked DCOFTRIM
    while(CSCTL7 & (FLLUNLOCK0 | FLLUNLOCK1)); // Poll until FLL is locked
}

// Utility
inline void itoa(long unsigned int value, char* result, int base)
    {
      // check that the base if valid
      if (base < 2 || base > 36) { *result = '\0';}

      char* ptr = result, *ptr1 = result, tmp_char;
      int tmp_value;

      do {
        tmp_value = value;
        value /= base;
        *ptr++ = "zyxwvutsrqponmlkjihgfedcba9876543210123456789abcdefghijklmnopqrstuvwxyz" [35 + (tmp_value - value * base)];
      } while ( value );

      // Apply negative sign
      if (tmp_value < 0) *ptr++ = '-';
      *ptr-- = '\0';
      while(ptr1 < ptr) {
        tmp_char = *ptr;
        *ptr--= *ptr1;
        *ptr1++ = tmp_char;
      }

    }

#endif /* RECORD_H_ */
