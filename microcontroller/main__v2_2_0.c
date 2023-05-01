/*
 * main.c
 *
 *  Created on: Mar 23, 2021
 *      Author: Raquel Ibáñez Alcalá
 *      Version: v2.2.0 (February 16, 2023)
 */

/****************************************************************************************************
 * MSP430-FR2355 R.E.C.O.R.D. (Reward-Cost in Rodent Decision-making) System Embedded Electronics
 *
 * Description: Proof of concept rodent arena controller for Friedman Lab rodent decision-making tasks.
 *  Communicates microcontroller with serial COM client running Windows 10 and connects to Noldus' TTL
 *  IO-Box. Microcontroller will receive commands from client called by Ethovision XT 16 and
 *  communicate back with a TTL pulse (ACK) after command finishes executing.
 *
 *                                                -------->| Inscopix TTL2_IN        |
 *                                               |   ----->| Inscopix TTL1_IN        |
 *                                               |  |       -------------------------
 *                                               |  |
 *                      MSP430FR2355             |  |            Noldus IO Box
 *             -------------------------------   |  |       -------------------------
 *            |                               |  |  |      |                         |
 *           <| P1.0 (LED1)      P3.0 (ACK)   |--|--o----->| TTL1_IN                 |
 *   PuTTY--->| P1.6 (UART RX)   P3.5 (TTL_IN)|<[]o--------| TTL1_OUT                |
 *   PuTTY<---| P1.7 (UART TX)   P3.6(TTL_OUT)|            |                         |
 *           >| P4.1 (SWITCH1)                |            |                         |
 *           >| P2.3 (SWITCH2)                |            |                         |
 *            |                               |            -------------------------
 *            |                               |                Open-Field Rodent Arena
 *            |                               |             -----------------------------
 *            |                               |            |                             |
 *            |                  P6.0 (TB3_1) |----------->| 1 Feeder1 LED ring          |
 *            |                  P6.1 (TB3_2) |----------->| 2 Feeder2 LED ring          |
 *            |                  P6.2 (TB3_3) |----------->| 3 Feeder3 LED ring          |
 *            |                  P6.3 (TB3_4) |----------->| 4 Feeder4 LED ring          |
 *            |                  P6.4 (TB3_5) |----------->| 5 Cue LED                   |
 *            |                  P3.1 (GPIO)  |---[Rly1]-->| 6 Valve 1                   |
 *            |                  P3.2 (GPIO)  |---[Rly2]-->| 7 Valve 2                   |
 *            |                  P3.7 (GPIO)  |---[Rly3]-->| 8 Valve 3                   |
 *            |                  P3.4 (GPIO)  |---[Rly4]-->| 9 Valve 4                   |
 *            |                               |            |                         GND |----< GND
 *            |                               |             -----------------------------
 *
 * Written by: Raquel Ibáñez Alcalá in March 2021 for Dr. Alexander Friedman
 * Version 2.2.0: 16 February 2023
 *
 ***************************************************************************************************/

#include <msp430.h>
#include <RECORD.h>
#include <stdio.h>
#include <stdlib.h>

void main(void)
{
    WDTCTL = WDTHOLD + WDTPW;   // Stop Watchdog timer

    /** ------ Calibrate clock ------ **/
    // Calibrate CPU clock to 8 MHz
    PM5CTL0 &= ~LOCKLPM5;       // Disable the GPIO power-on default high-impedance mode
                                // to activate 1previously configured port settings

    __bis_SR_register(SCG0);    // disable FLL
    CSCTL3 |= SELREF__REFOCLK;  // Set REFO as FLL reference source
    CSCTL1 = DCOFTRIMEN_1 |
             DCOFTRIM0    |
             DCOFTRIM1    |
             DCORSEL_3;         // DCOFTRIM=3, DCO Range = 8MHz
    CSCTL2 = FLLD_0 + 243;      // DCODIV = 8MHz
    __delay_cycles(3);
    __bic_SR_register(SCG0);    // enable FLL
    Software_Trim();            // Software Trim to get the best DCOFTRIM value

    CSCTL4 = SELMS__DCOCLKDIV |
             SELA__REFOCLK;     // set default REFO(~32768Hz) as ACLK source,
                                // default DCODIV as MCLK and SMCLK source


    /** ------ Setup GPIO ------ **/
    // Port 1
    P1DIR |= 0xFF;          // Set all pins on this port as output to start.
    P1OUT = 0x00;           // Turn all outputs off.

    P1SEL0 |= RXD | TXD;    // Set the UART pins to second function.
    P1SEL1 &= ~(RXD | TXD); // Make sure these bits are not set.

    // Port 2
    P2DIR |= 0xFF;          // Set all pins as output.
    P2OUT = 0x00;           // Set all outputs to 0

    // Port 3
    P3DIR |= 0xFF;          // Set all pins to output.
    P3OUT = 0x00;
    P3OUT |= RELAY1 | RELAY2    // Set these high for the relay array that toggles only when signal is low.
             | RELAY3 | RELAY4;
    P3DIR &= ~(TTL_IN);     // Input TTL signal for external TTLs.
    P3IES  &= ~(TTL_IN);    // Low to high input signal transition for input activation.

    // Port 4
    P4DIR |= 0xFF;          // Set all pins to output.
    P4OUT  = 0x00;          // Make sure they're all off.
    P4DIR &= ~(BTN1);       // Set on-board button 1 as input.
    P4IES &= ~(BTN1);       // Low to high input signal transition for interrupt activation.

    // Port 5
    P5DIR |= 0xFF;
    P5OUT = 0x00;

    // Port 6
    P6DIR |= 0xFF;
    P6OUT = 0x00;

    P6SEL0 |= ( TB3_1 |
                TB3_2 |
                TB3_3 |
                TB3_4 |
                TB3_5 );    // Select second function for these pins, Timer B3 for PWM.
    P6SEL1 &= ~( TB3_1 |
                 TB3_2 |
                 TB3_3 |
                 TB3_4 |
                 TB3_5 );   // Unset these bits.

    ButtonSetup();          // Optional internal button setup

    PM5CTL0 &= ~LOCKLPM5;   // Disable the GPIO power-on default high-impedance mode
                            // to activate previously configured port settings

    /** --- Setup RealTime Clock --- **/
    // The real time clock will be used to keep MCU time.
    // This peripheral will keep track of how long a command takes to execute, the value
    // will then be passed to the eUSCI peripheral to communicate this to a PC.

    // Source = Subsystem Master Clock (8 MHz, RTCSS), divided by 100 (80 kHz, RTCPS),
    // ensure software timer reset (RTCSR), and enable interrupts (RTCIE).
    // Start with clock disabled for now though. Set RTCSS bits to __SMCLK to activate.
    RTCCTL = RTCSS__DISABLED | RTCSR | RTCPS__100;

    // Set RTC count re-load compare value at 80 to get a tick every millisecond.
    // 100/8,000,000 * 80 = 0.001 sec.
    RTCMOD = 80-1;
    // Set both counting variables to 0.
    ms &= 0x0000;
    sc &= 0x0000;
    // Read the RTC Interrupt Vector register to reset RTC Interrupt Flag.
    if(RTCIV>0);

    /** ------ Setup Timer B1 ------ **/
    // This times is used for delays. Instead of using a busy wait with polling, we wish to put the system to sleep while closing a relay
    // or performing some other timed action such as raising a TTL signal.
    TB1CTL &= ~MC_3;        // Start with timer stopped. Mode referenced has no relevance to functionality, I'm just clearing the bits.
    TB1CTL |= TBSSEL_2;     // Select SMCLK source CONSIDER CHANGING THIS

    TB1CCTL0 |= CCIFG_0 | CCIE_1;     // Enable interrupts on this timer's capture compare module.
    TB1CCR0 = 8000;         // This will give me a period of 1 ms before an interrupt is requested. An interrupt will be requested when timer counts to this number.

    /** ------ Setup Timer B3 ------ **/
    // This is for PWM. Timer B3 will drive the LED rings to control brightness, and the Cue LED to make it glow.
    TB3CTL &= ~MC_3;        // Start with timer stopped. Mode referenced has no relevance to functionality, I'm just clearing the bits.
    TB3CTL |= TBSSEL_2;     // Select SMCLK source CONSIDER CHANGING THIS

    TB3CCTL1 |= OUTMOD_6 | CCIE_0;  // Set OUTMOD to Toggle/Set to output a pulse width modulated signal.
    TB3CCTL2 |= OUTMOD_6 | CCIE_0;
    TB3CCTL3 |= OUTMOD_6 | CCIE_0;
    TB3CCTL4 |= OUTMOD_6 | CCIE_0;
    TB3CCTL5 |= OUTMOD_6 | CCIE_0;  // Make sure interrupts are disabled.

    TB3CCR0 = 8000;         // f(out) = SMCLK/TB1CCR0 = frequency of 1kHz, consider this for calculating duty cycle

    TB3CCR1 = 8000;         // This determines duty cycle: DC = (1-(TBCCR1/TBCCR0))*100%, if TB1CCR1 = TB1CCR0, duty cycle is 0%.
    TB3CCR2 = 8000;
    TB3CCR3 = 8000;
    TB3CCR4 = 8000;
    TB3CCR5 = 8000;

    /** ------ Setup UART ------ **/
    UCA0CTLW0 |= UCSWRST;                      // Disable UART module and reset its registers for configuration.
    UCA0CTLW0 |= UCSSEL__SMCLK;                // Use SMCLK as source.

    // Baud Rate calculation
    // 8000000/(16*9600) = 52.083
    // Fractional portion = 0.083
    // User's Guide Table 22-4: UCBRSx = 0x49
    // UCBRFx = int ( (52.083-52)*16) = 1
    UCA0BR0 = 52;                             // 8000000/16/9600
    UCA0BR1 = 0x00;
    UCA0MCTLW = 0x4900 | UCOS16 | UCBRF_1;

    UCA0CTLW0 &= ~UCSWRST;                    // Initialize eUSCI

    //** ------ Setup Interrupts ------ **//

    UCA0IE |= UCRXIE;       // Enable USCI_A0 RX interrupt
    RTCCTL |= RTCIE;        // Enable real time clock interrupt
    P3IE   &= ~(TTL_IN);    // Disable interrupts for the incoming TTL port by default. This can be enabled later on.
    P4IE   |= BTN1;         // Enable interrupts for button 1, a test button.

    //** ------ Finish Initialization ------ **//
    TB3CTL |= MC_3;               // Start timer and start PWM, saving this for later

    SetBrightness('1', '0');      // Turn all LEDs off
    SetBrightness('2', '0');
    SetBrightness('3', '0');
    SetBrightness('4', '0');

    char int_string[5];                // Set length character array for storing user-entered integers which will be converted to integer types.
    struct LightLevel *lvl_ptr;        // Pointer for light level structure contained in arenacfgX.h.
    struct MCUinfo *dev_ptr = &Device; // Pointer to the MCUinfo structure, which contains information about the device, contained in arenacfgX.h.
    //unsigned long          RELAY_ONTIME = 500;  // Amount of time relays are set to be on.
    //unsigned long          TTL_LENGTH = 500;    // Amount of time TTLs are set to be on.
    volatile unsigned int * reg_ptr;   // A simple register pointer for dynamic register selection.
    volatile unsigned int ts_sc;       // Snapshot variable for storing the current seconds on seconds counter.
    volatile unsigned int ts_ms;       // Snapshot variable for storing the current milliseconds on milliseconds counter.
    char c, INPUT_1, INPUT_2, INPUT_3; // Single character containers for handling command inputs.

    unsigned short int  _ERROR = 0;  // Error flag.
    unsigned int             i = 0;  // Iterating variable.
    char              CCRVAL[] = ""; // Character array for handling CCR value input for PWM.
    char*               string = ""; // Character array pointer for sending messages through UART.
    unsigned int          temp = 0;  // Temporary variable for storing a previous CCR value before committing it to the light-level structure.
    unsigned short      _BLINK = 0;  // Indicates that the system must service the trial indication LED.
    unsigned short      _EXTTL = 0;  // Indicates whether or not the system will react to external TTLs.
    unsigned short      _TTLOP = 0;  // Indicates TTL operating mode. 0 for "toggle", 2 for "on request", 3 for "off"
    char           rxstring[4] = ""; // String buffer to store incoming messages from PC.
    unsigned short int  length = 4;  // Length of the string buffer. For LED commands.

    while(1)
    {
        //** ------ Go to sleep :3 ------ **//
        __bis_SR_register(LPM0_bits | GIE);       // Enable global interrupts and go into LPM0
        i = 0;
        _ERROR = 0;
        lvl_ptr = 0;

        //** ------ Command Servicing Routine ------ **//
        P3OUT &= ~(ACK);    // Make sure ACK signal is low, but not TTL

        c = UCA0RXBUF;              // Store received character
        while(UCA0STATW & UCBUSY);  // Wait here while the eUSCI module is busy.
        // Interpret received command.
        switch (c)
        {
    // '#': LED COMMAND
            case '#':
                // Hang here while receiving characters one by one.
                // Acknowledgment won't be sent until ISR is pretty much done in order to parse stream.
                // In other words, ACK won't be sent until all characters are received and appropriate actions have been executed.
                // Instructions will look like this: #FxLy, where x is a feeder ID number, and y is a brightness level between 0 and 3.
                UCA0TXBUF = c;
                while (i <= length -1)
                {
                    __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                    rxstring[i] = UCA0RXBUF;
                    UCA0TXBUF = rxstring[i];       // Send the input characters back to the user so they know wtf they're typing lmao.
                    i++;
                }

                // Parse the received command:
                INPUT_1 = rxstring[1];
                INPUT_2 = rxstring[3];
                // Time stamp before continuing:
                ts_ms = ms;
                ts_sc = sc;
                // Execute command:
                SetBrightness(INPUT_1,INPUT_2);
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UARTsendMsg(": feeder configured at ");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                // Report time stamp:
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // '$': CONFIG MODE COMMAND FOR BRIGHTNESS LEVELS.
            case '$':
                // Asks for user input to change the CCR value for a brightness level. Changes will not be committed to memory (yet). Future update must write to Flash.
                // Command indication
                UARTsendMsg(" Entering configuration mode...\r\n Keep in mind any configuration done here will be lost when the system is powered off. Commit these changes as default by changing the system's code.\r\n\n");
                UARTsendMsg(" A.........Configure feeder LED brightness\r\n B.........Configure relay active time\r\n C.........Configure TTL length\r\n D.........TTL operating mode\r\n>");
                // Wait for input...
                __bis_SR_register(LPM0_bits);   // Go to sleep while user inputs the next character.
                INPUT_1 = UCA0RXBUF;
                // Display input...
                while(UCA0STATW & UCBUSY);
                UCA0TXBUF = INPUT_1;                   // Echo character back
                if(INPUT_1 == 'A'){
                    // ----- Give instructions (1/2)... -----
                    UARTsendMsg("\r\n Please enter the level to reconfigure (1, 2, or 3).\r\n> ");
                    // Wait for input...
                    __bis_SR_register(LPM0_bits);   // Go to sleep while user inputs the next character.
                    INPUT_1 = UCA0RXBUF;
                    // Display input...
                    while(UCA0STATW & UCBUSY);
                    UCA0TXBUF = INPUT_1;                   // Echo character back

                    UARTsendMsg("\r\n Please enter the feeder to reconfigure (1, 2, 3, or 4).\r\n> ");
                    // Wait for input...
                    __bis_SR_register(LPM0_bits);   // Go to sleep while user inputs the next character.
                    INPUT_2 = UCA0RXBUF;
                    // Display input...
                    while(UCA0STATW & UCBUSY);
                    UCA0TXBUF = INPUT_2;            // Echo character back

                    // ----- Give instructions (2/2)... -----
                    UARTsendMsg("\r\n Please enter the new integer CCR value for this level and feeder (0 through 8000, whole numbers only).\r\n Enter up to 4 characters or press enter if you're entering less than 4 characters.\r\n> ");
                    // Wait for input and display it...
                    length = 4;
                    while (i <= length -1)
                    {
                        __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                        if (UCA0RXBUF == '\r')         // User can press ENTER to finish inputting a value if their input contains less than 4 characters.
                        {
                            CCRVAL[i] = '\0';
                            break;
                        }
                        else
                        {
                            CCRVAL[i] = UCA0RXBUF;
                            UCA0TXBUF = CCRVAL[i];
                            i++;
                        }
                        while(UCA0STATW & UCBUSY);
                    }
                    UARTsendMsg("\r\n");

                    // Parse CCRVAL:
                    if (atoi((const char *)CCRVAL) > 8000 || atoi((const char *)INPUT_1) > 3 || atoi((const char *)INPUT_2) > 4)
                    {
                        // Indicate an error if inputs are not valid.
                        _ERROR = 1;
                    }
                    else
                    {
                        // Check what level to modify point to the correct structure.
                        switch (INPUT_1)
                        {
                        case '1':
                            // Variable for level 1
                            lvl_ptr = &L1;
                            break;
                        case '2':
                            // Variable for level 2
                            lvl_ptr = &L2;
                            break;
                        case '3':
                            // Variable for level 3
                            lvl_ptr = &L3;
                            break;
                        default:
                            UARTsendMsg(" Error: CCR value should not exceed 8000 or LEVEL should not exceed 3. Configuration not set.\r\n");
                            _ERROR = 1;
                            break;
                        }
                    }
                    if (!_ERROR)
                    {
                        ModifyCCR(lvl_ptr, INPUT_2, atoi(CCRVAL));
                        // Test new value?
                        UARTsendMsg(" Would you like to test the new value? [y/n]\r\n> ");
                        // Wait for input...
                        __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                        INPUT_3 = UCA0RXBUF;
                        // Display input...
                        while(UCA0STATW & UCBUSY);
                        UCA0TXBUF = INPUT_3;                   // Echo character back
                        UARTsendMsg("\r\n\n");
                        if (INPUT_3 == 'y' || INPUT_3 == 'Y')
                        {
                            SetBrightness('1', INPUT_1);
                            SetBrightness('2', INPUT_1);
                            SetBrightness('3', INPUT_1);
                            SetBrightness('4', INPUT_1);
                            UARTsendMsg("$: New settings applied! Entering low power mode...\r\n\n");
                        }
                        else
                        {
                            UARTsendMsg("$: Configuration applied! Feeders reset, changes will be reflected upon turning them back on. Entering low power mode...\r\n\n");
                        }
                    }
                    else
                    {
                        UARTsendMsg("$: Configuration aborted due to error, try again. Entering low power mode...\r\n\n");
                    }
                    break;
                }
                else if (INPUT_1 == 'B'){
                    // ----- Give instructions (1/2)... -----
                    UARTsendMsg("\r\n Please enter the desired relay active time in milliseconds (whole numbers only, maximum of 9999 milliseconds).\r\n Enter up to 4 characters or press enter if you're entering less than 4 characters.\r\n> ");
                    // Wait for input and display it...
                    length = 4;
                    while (i <= length -1)
                    {
                        __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                        if (UCA0RXBUF == '\r')         // User can press ENTER to finish inputting a value if their input contains less than 4 characters.
                        {
                            CCRVAL[i] = '\0';
                            break;
                        }
                        else
                        {
                            CCRVAL[i] = UCA0RXBUF;
                            UCA0TXBUF = CCRVAL[i];
                            i++;
                        }
                        while(UCA0STATW & UCBUSY);
                    }
                    UARTsendMsg("\r\n\n");

                    // Parse input:
                    if (atoi((const char *)CCRVAL) > 9999 || atoi((const char *)CCRVAL) < 0)
                    {
                        // Indicate an error if inputs are not valid.
                        UARTsendMsg("$: Invalid input, value exceeds 9999 or is negative. Loading previous values and aborting configuration.\r\n\n");
                    }
                    else
                    {
                        RELAY_ONTIME = atoi(CCRVAL);
                        UARTsendMsg("$: Configuration applied! Relay active time has been configured. Entering low power mode...\r\n\n");
                    }
                    break;
                }
                else if (INPUT_1 == 'C'){
                    // ----- Give instructions (1/2)... -----
                    UARTsendMsg("\r\n Please enter the TTL length in milliseconds (whole numbers only, maximum of 9999 milliseconds).\r\n Enter a 4-character number or press enter if you're entering less than 4 characters.\r\n> ");
                    // Wait for input and display it...
                    length = 4;
                    while (i <= length -1)
                    {
                        __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                        if (UCA0RXBUF == '\r')         // User can press ENTER to finish inputting a value if their input contains less than 4 characters.
                        {
                            CCRVAL[i] = '\0';
                            break;
                        }
                        else
                        {
                            CCRVAL[i] = UCA0RXBUF;
                            UCA0TXBUF = CCRVAL[i];
                            i++;
                        }
                        while(UCA0STATW & UCBUSY);
                    }
                    UARTsendMsg("\r\n\n");

                    // Parse input:
                    if (atoi((const char *)CCRVAL) > 9999 || atoi((const char *)CCRVAL) < 0)
                    {
                        // Indicate an error if inputs are not valid.
                        UARTsendMsg("$: Invalid input, value exceeds 9999 or is negative. Loading previous values and aborting configuration.\r\n\n");
                    }
                    else
                    {
                        TTL_LENGTH = atoi(CCRVAL);
                        UARTsendMsg("$: Configuration applied! TTL length has been configured. Entering low power mode...\r\n\n");
                    }
                    break;
                }
                else if (INPUT_1 == 'D'){
                    // ----- Give instructions (1/2)... -----
                    UARTsendMsg("\r\n\n Please enter the desired TTL operating mode from the list below:");
                    UARTsendMsg("\r\n\n 1.........Toggle (TTL stays on/off until the next request) - "); if (_TTLOP == 0) UARTsendMsg("Active"); else UARTsendMsg("Inactive");
                    UARTsendMsg("\r\n 2.........Pulse (TTL goes high upon request and goes low after [TTL length]) - "); if (_TTLOP == 1) UARTsendMsg("Active"); else UARTsendMsg("Inactive");
                    UARTsendMsg("\r\n 3.........Off (TTL requests are ignored) - "); if (_TTLOP == 2) UARTsendMsg("Active\r\n>"); else UARTsendMsg("Inactive\r\n>");

                    // Wait for input and display it...
                    __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                    INPUT_2 = UCA0RXBUF;
                    // Display input...
                    while(UCA0STATW & UCBUSY);
                    UCA0TXBUF = INPUT_2;
                    switch (INPUT_2)
                    {
                    case '1':
                        _TTLOP = 0;
                        break;
                    case '2':
                        _TTLOP = 1;
                        break;
                    case '3':
                        _TTLOP = 2;
                        break;
                    default:
                        UARTsendMsg("Error: Invalid input. Exiting...");
                        break;
                    }
                    UARTsendMsg("\r\n\n");
                }
                else{

                    UARTsendMsg("\r\n\n$: Input unrecognized, exiting configuration mode.\r\n\n");
                }
                P3OUT &= ~(TTL_OUT);
                UARTsendMsg("$: TTL output operation mode applied. Entering low power mode...\r\n\n");
                break;

    // '%': CALIBRATION MODE COMMAND
            case '%':
                // Command indication
                UARTsendMsg(" Entering calibration mode...\r\n Keep in mind any configuration done here will be lost when the system is powered off. Commit these changes as default by changing the system's code.\r\n\n");
                // ----- Give instructions (1/3)... -----
                UARTsendMsg(" Please enter the level to reconfigure (1, 2, or 3).\r\n> ");
                // Wait for input...
                __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                INPUT_1 = UCA0RXBUF;
                // Display input...
                while(UCA0STATW & UCBUSY);        // May not be needed. Checks if the UCA0 module is busy sending or receiving a message.
                UCA0TXBUF = INPUT_1;                   // Echo character back
                UARTsendMsg("\r\n");
                if (atoi((const char *)INPUT_1) > 3)
                {
                    // Indicate an error if inputs are not valid.
                    _ERROR = 1;
                }
                else
                {
                    switch (INPUT_1)
                    {
                    case '1':
                        // Variable for level 1
                        lvl_ptr = &L1;
                        break;
                    case '2':
                        // Variable for level 2
                        lvl_ptr = &L2;
                        break;
                    case '3':
                        // Variable for level 3
                        lvl_ptr = &L3;
                        break;
                    default:
                        _ERROR = 1;
                        UARTsendMsg("Error: Invalid input. Exiting...");
                        break;
                    }
                }
                // ----- Give instructions (2/3)... ----
                UARTsendMsg(" Please enter the feeder to reconfigure (1, 2, 3, or 4).\r\n> ");
                // Wait for input...
                __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                INPUT_2 = UCA0RXBUF;
                // Display input...
                while(UCA0STATW & UCBUSY);
                UCA0TXBUF = INPUT_2;                   // Echo character back
                UARTsendMsg("\r\n");
                switch (INPUT_2)
                {
                case '1':
                    reg_ptr = &TB3CCR1;
                    break;
                case '2':
                    reg_ptr = &TB3CCR2;
                    break;
                case '3':
                    reg_ptr = &TB3CCR3;
                    break;
                case '4':
                    reg_ptr = &TB3CCR4;
                    break;
                default:
                    _ERROR = 1;
                    UARTsendMsg("Error: Invalid input. Exiting...");
                    break;
                }
                if (!_ERROR)
                {
                    SetBrightness(INPUT_2, INPUT_1);
                    temp = *reg_ptr; // Will contain the temporary CCR value.
                    i = 50;          // Will contain a number to step up or down.
                    // ----- Give instructions (3/3)... -----
                    UARTsendMsg(" Use '[' and ']' to decrease or increase the CCR value for the selected feeder. Press 'Enter' when done.\r\n");
                    INPUT_3 = ' ';
                    // Wait for user to enter '[' or ']'. Go through this loop at least once.
                    do{
                        UARTsendMsg("> CCR value is currently: ");
                        itoa(temp, int_string, 10);
                        UARTsendMsg(int_string);
                        UARTsendMsg("\r\n");
                        // Wait for input
                        __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                        INPUT_3 = UCA0RXBUF;

                        if(INPUT_3 == '[') // Decrease CCR value
                        {
                            temp = temp + i;
                            if(temp > 8000)
                            {
                                temp = 0;
                                UARTsendMsg(" CCR value upper limit reached, looped back to 0.\r\n");
                            }
                        }
                        else if(INPUT_3 == ']') // Increase CCR
                        {
                            temp = temp - i;
                            if(temp > 8000)
                            {
                                temp = 8000;
                                UARTsendMsg(" CCR value lower limit reached, looped back to 8000.\r\n");
                            }
                        }
                        else
                        {
                            if(INPUT_3 != *("\r"))
                            {
                                UARTsendMsg(" Please only use '[' or ']'. Press 'Enter' to exit calibration mode.\r\n");
                            }
                        }
                        *reg_ptr = temp;
                    }while(INPUT_3 != '\r');

                    UARTsendMsg(" Would you like to apply these changes? [y/n]\r\n> ");
                    // Wait for input...
                    __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                    INPUT_3 = UCA0RXBUF;
                    // Display input...
                    while(UCA0STATW & UCBUSY);        // May not be needed. Checks if the UCA0 module is busy sending or receiving a message.
                    UCA0TXBUF = INPUT_3;                   // Echo character back
                    UARTsendMsg("\r\n\n");

                    if(INPUT_3 == 'y' || INPUT_3 == 'Y')    // Modify the level structure if yes.
                    {
                        ModifyCCR(lvl_ptr, INPUT_2, temp);
                        SetBrightness('1', INPUT_1);
                        SetBrightness('2', INPUT_1);
                        SetBrightness('3', INPUT_1);
                        SetBrightness('4', INPUT_1);
                        UCA0TXBUF = c;
                        UARTsendMsg(": New settings applied! Resuming previous operations...\r\n\n");
                    }
                    else    // Do not modify level structure and revert if no.
                    {
                        SetBrightness('1', INPUT_1);
                        SetBrightness('2', INPUT_1);
                        SetBrightness('3', INPUT_1);
                        SetBrightness('4', INPUT_1);
                        UCA0TXBUF = c;
                        UARTsendMsg(": Rolled back to previous configuration. Resuming previous operations...\r\n\n");
                    }
                }
                else
                {
                    UCA0TXBUF = c;
                    UARTsendMsg(": Cannot continue due to error. Check that both level and feeder values are between their respective ranges. Calibration aborted.\r\n\n");
                }
                lvl_ptr = 0;
                break;
    // 'A': ALL LIGHTS ON
            case 'A':   // NOT USED
                P1OUT |= REDLED;
                P6OUT |= GRNLED;
                SetBrightness('1', '3');
                SetBrightness('2', '3');
                SetBrightness('3', '3');
                SetBrightness('4', '3');
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": all on\r\n\n");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                break;
    // 'g': GREEN ON-BOARD LED ON (DEBUGGING)
            case 'g':   // NOT USED
                P6OUT ^= GRNLED;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": green toggled\r\n\n");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                break;
    // 'r': RED ON-BOARD LED ON (DEBUGGING)
            case 'r':   // NOT USED
                P1OUT ^= REDLED;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": red toggled\r\n\n");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                break;
    // 'K': TOGGLE INDICATOR LIGHT
            case 'K':   // ACTIVATE (TOGGLE) RED LIGHT (TRIAL START LIGHT) & WILL SEND A MESSAGE TO CONSOLE (CMD PROMPT)
                ts_ms = ms;
                ts_sc = sc;
                if (_BLINK)
                    { _BLINK = 0; TB3CCR5 = 8000; string = ": trial indication off at "; }
                else
                    { _BLINK = 1; TB3CCR5 = 6000; string = ": trial indication on at ";  }
                //TB3CCTL5 ^=  CCIE_1;  // Toggle interrupt requests on/off.
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(string);
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                // Report timestamp
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // 'R': TURN ALL LIGHTS OFF
            case 'R':   // RESETS ALL LIGHT TO OFF & SENDS MESSAGE TO CONSOLE
                ts_ms = ms;
                ts_sc = sc;
                P1OUT &= ~(REDLED);
                // P3OUT &= ~(ACK | TTL_OUT);
                P3OUT |= ( RELAY1 | RELAY2 | RELAY3 | RELAY4 );
                P5OUT &= ~(LED1 | LED2 | LED3 | LED4);
                P6OUT &= ~(GRNLED);
                TB3CCR1 = 8000;
                TB3CCR2 = 8000;
                TB3CCR3 = 8000;
                TB3CCR4 = 8000;
                TB3CCR5 = 8000;
                _BLINK = 0;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": reset all peripherals at ");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                // Report timestamp
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // 'F': ACTIVATE VALVE 1
            case 'F':   // ACTIVATES RELAY (VALVE) #1 & SENDS MESSAGE
                ts_ms = ms;
                ts_sc = sc;
                P3OUT &= ~RELAY1;
                delay_ms(RELAY_ONTIME);
                P3OUT |= RELAY1;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": relay1 toggled at ");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                // Report timestamp
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // 'G': ACTIVATE VALVE 2
            case 'G':   // ACTIVATES RELAY (VALVE) #2 & SENDS MESSAGE
                ts_ms = ms;
                ts_sc = sc;
                P3OUT &= ~RELAY2;
                delay_ms(RELAY_ONTIME);
                P3OUT |= RELAY2;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": relay2 toggled at ");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                // Report timestamp
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // 'H': ACTIVATE VALVE 3
            case 'H':   // ACTIVATES RELAY (VALVE) #3 & SENDS MESSAGE
                ts_ms = ms;
                ts_sc = sc;
                P3OUT &= ~RELAY3;
                delay_ms(RELAY_ONTIME);
                P3OUT |= RELAY3;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": relay3 toggled at ");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                // Report timestamp
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // 'J': ACTIVATE VALVE 4
            case 'J':   // ACTIVATES RELAY (VALVE) #4 & SENDS MESSAGE
                ts_ms = ms;
                ts_sc = sc;
                P3OUT &= ~RELAY4;
                delay_ms(RELAY_ONTIME);
                P3OUT |= RELAY4;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": relay4 toggled at ");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                // Report timestamp
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // '?': DISPLAY HELP DOCUMENTATION
            case '?': // Help section. Lists available commands and gives a short explanation of what they do.
                UARTsendMsg("-------------------------------------------------------------------------------------------------\r\n");
                UARTsendMsg("Device ID: ");
                UARTsendMsg(dev_ptr->device_id);
                UARTsendMsg("\r\n");
                UARTsendMsg("Date of last firmware flash: ");
                UARTsendMsg(dev_ptr->updated);
                UARTsendMsg("\r\n");
                UARTsendMsg("Firmware version: ");
                UARTsendMsg(dev_ptr->firm_ver);
                UARTsendMsg("\r\n");
                UARTsendMsg("RECORD library version: ");
                UARTsendMsg(dev_ptr->lib_ver);
                UARTsendMsg("\r\n");
                UARTsendMsg("Arena settings version: ");
                UARTsendMsg(dev_ptr->cfg_ver);
                UARTsendMsg("\r\n");
                UARTsendMsg("Device: ");
                UARTsendMsg(dev_ptr->device);
                UARTsendMsg("\r\n");
                UARTsendMsg("External TTL servicing: ");
                (_EXTTL)? UARTsendMsg("Active\r\n") : UARTsendMsg("Inactive\r\n");
                UARTsendMsg("Output TTL operation mode: ");
                switch(_TTLOP){ case 0: UARTsendMsg("TOGGLE\r\n"); break; case 1: UARTsendMsg("PULSE\r\n"); break; case 2: UARTsendMsg("OFF\r\n"); break; }

                lvl_ptr = &L1;
                UARTsendMsg("CCR values:\r\n  L1\r\n  Feeder 1: ");
                itoa(lvl_ptr->fdr1,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 2: ");
                itoa(lvl_ptr->fdr2,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 3: ");
                itoa(lvl_ptr->fdr3,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 4: ");
                itoa(lvl_ptr->fdr4,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                lvl_ptr = &L2;
                UARTsendMsg("  L2\r\n  Feeder 1: ");
                itoa(lvl_ptr->fdr1,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 2: ");
                itoa(lvl_ptr->fdr2,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 3: ");
                itoa(lvl_ptr->fdr3,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 4: ");
                itoa(lvl_ptr->fdr4,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                lvl_ptr = &L3;
                UARTsendMsg("  L3\r\n  Feeder 1: ");
                itoa(lvl_ptr->fdr1,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 2: ");
                itoa(lvl_ptr->fdr2,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 3: ");
                itoa(lvl_ptr->fdr3,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");
                UARTsendMsg("  Feeder 4: ");
                itoa(lvl_ptr->fdr4,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg("\r\n");

                UARTsendMsg("Relay active time: ");
                itoa(RELAY_ONTIME,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg(" milliseconds.");
                UARTsendMsg("\r\n");
                UARTsendMsg("TTL active time: ");
                itoa(TTL_LENGTH,int_string,10);
                UARTsendMsg(int_string); UARTsendMsg(" milliseconds.");
                UARTsendMsg("\r\n");
                UARTsendMsg("-------------------------------------------------------------------------------------------------\r\n\n");

                UARTsendMsg("For additional help, enter 'H', otherwise use Enter key to exit\r\n\n");
                __bis_SR_register(LPM0_bits);  // Go to sleep while user inputs the next character.
                if (UCA0RXBUF == 'H' || UCA0RXBUF == 'h')        // If user entered return character (enter key), exit
                {
                    UARTsendMsg(" Welcome to the about section! I will list all the commands I have available for you to use and will give you a short description of what each of them does.\r\n\n");
                    UARTsendMsg(" 1.  '#': Turn on a specific feeder LED ring at a specified level.\r\nI will quietly wait for your input and only execute it once you're done.\r\nPlease format your input like this: FxLy. X is the feeder you want to activate, and Y is the brightness level you want to set it to.\r\n\n");
                    UARTsendMsg(" 2.  '$': Starts configuration mode. Instructions will pop up as soon as you input this command.\r\nThis will allow you to reconfigure how bright feeder LEDs should be, how long valves stay open, how long TTL pulses are, amongst other settings.\r\n\n");
                    UARTsendMsg(" 3.  'K': Toggles the 'trial in progress' light.\r\n\n");
                    UARTsendMsg(" 4.  'R': Resets everything. All LEDs are turned off and relays are opened.\r\n\n");
                    UARTsendMsg(" 5.  'F': Toggles relay 1, which will open and close valve 1.\r\nThe amount of time that the relay will be closed can be configured at the beginning of the code I'm executing.\r\nYou'll need to edit that yourself.\r\n\n");
                    UARTsendMsg(" 6.  'G': Toggles relay 2, which will open and close valve 2.\r\nThe amount of time that the relay will be closed can be configured at the beginning of the code I'm executing.\r\nYou'll need to edit that yourself.\r\n\n");
                    UARTsendMsg(" 7.  'H': Toggles relay 3, which will open and close valve 3.\r\nThe amount of time that the relay will be closed can be configured at the beginning of the code I'm executing.\r\nYou'll need to edit that yourself.\r\n\n");
                    UARTsendMsg(" 8.  'J': Toggles relay 4, which will open and close valve 4.\r\nThe amount of time that the relay will be closed can be configured at the beginning of the code I'm executing.\r\nYou'll need to edit that yourself.\r\n\n");
                    UARTsendMsg(" 9.  'Q': Starts the internal timer. This timer counts seconds and milliseconds.\r\n\n");
                    UARTsendMsg(" 10. 'W': Gets the current time from internal timer. Time will be formatted as [seconds].[milliseconds]\r\n\n");
                    UARTsendMsg(" 11. 'E': Stops the internal timer.\r\n\n");
                    UARTsendMsg(" 12. 'T': Send a TTL out through port 3.6.\r\n\n");
                    UARTsendMsg(" 13. 'Y': Allows the system to respond to external TTLs received through P3.5.\r\n\n");
                    UARTsendMsg(" All commands (with the exception of 'T') will be acknowledged with the ACK signal through port 3.0 upon execution.\r\n\n");
                    UCA0TXBUF = c;
                    UARTsendMsg(": Information.\r\n\n");
                    break;
                }
                else
                {
                    UCA0TXBUF = c;
                    UARTsendMsg(": Information.\r\n\n");
                    break;
                }
    // 'Q': TIMER START COMMAND
            case 'Q':
                RTCCTL |= RTCSR | RTCSS__SMCLK;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                //UARTsendMsg("Time will read as [seconds].[milliseconds]\r\n");
                UCA0TXBUF = c;
                UARTsendMsg(": timer started.\r\n\n");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                break;
    // 'W': TIMER GET TIME COMMAND
            case 'W':
                ts_ms = ms;
                ts_sc = sc;
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": time requested at ");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // 'E': TIMER STOP COMMAND
            case 'E':
                ts_ms = ms;
                ts_sc = sc;
                RTCCTL &= ~RTCSS__SMCLK;
                RTCMOD = 80-1;
                // Set both counting variables to 0.
                ms &= 0x0000;
                sc &= 0x0000;
                // Read the RTC Interrupt Vector register to reset RTC Interrupt Flag.
                if(RTCIV>0);
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(": timer stopped at ");
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // 'T': TTL Out
            case 'T':
                ts_ms = ms;
                ts_sc = sc;
                switch (_TTLOP){
                    case 0:
                        P3OUT ^= TTL_OUT;
                        UCA0TXBUF = c;
                        UARTsendMsg(": TTL toggled at ");
                        break;
                    case 1:
                        P3OUT |= TTL_OUT;
                        UCA0TXBUF = c;
                        UARTsendMsg(": TTL requested at ");
                        delay_ms(TTL_LENGTH);
                        P3OUT &= ~(TTL_OUT);
                        break;
                    case 2:
                        UCA0TXBUF = c;
                        UARTsendMsg(": TTL requested but not serviced at ");
                        break;
                    default:
                        break;
                }
                itoa(ts_sc, int_string, 10);
                UARTsendMsg(int_string);
                UCA0TXBUF = '.';
                itoa(ts_ms, int_string, 10);
                UARTsendMsg(int_string);
                UARTsendMsg("\r\n\n");
                break;
    // 't': Report TTL state HI or LOW
            case 't':
                if (P3OUT & TTL_OUT)
                    UARTsendMsg("t: TTL is HIGH");
                else
                    UARTsendMsg("t: TTL is LOW");
                UARTsendMsg("\r\n\n");
                break;
    // 'Y': Toggle external TTLs
            case 'Y':
                if (_EXTTL)
                    { _EXTTL = 0; string = ": external TTLs toggled off.\r\n\n"; }
                else
                    { _EXTTL = 1; string = ": external TTLs toggled on.\r\n\n";  }

                P3IFG &= ~(TTL_IN); // Make sure interrupt flag is clear.
                P3IE  ^= TTL_IN;    // Toggle interrupt requests on/off.
                // Acknowledge with TTL first then message:
                P3OUT |= ACK;
                UCA0TXBUF = c;
                UARTsendMsg(string);
                delay_ms(TTL_LENGTH);
                P3OUT &= ~(ACK);
                break;
            default:    // RESPONSE MESSAGE WHEN MCU RECIEVES AN UNKNOWN COMMAND
                UCA0TXBUF = c;
                UARTsendMsg(": I cannot recognize that command. Send me a '?' for a list of commands.\r\n\n");
                break;
        }
    }

}


//** ------ eUSCI ISR for serial communication ------ **//
#pragma vector=USCI_A0_VECTOR
__interrupt void USCI_A0_ISR(void)
{
    __bic_SR_register_on_exit(LPM0_bits);   // Clear LPM_0 bits from status register and continue to next instruction.
    UCA0IFG &= ~(UCRXIFG);                  // Clear the RX interrupt flag and exit.
}

//** ------ RTC ISR for time keeping ------ **//
// Check what compiler is being used and declare interrupt service routine accordingly.
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector=RTC_VECTOR
__interrupt void RTC_ISR(void)
#elif defined(__GNUC__)
void __attribute__ ((interrupt(RTC_VECTOR))) RTC_ISR (void)
#else
#error Compiler not supported!
#endif

{
    switch(__even_in_range(RTCIV,RTCIV_RTCIF))
    {
        case  RTCIV_NONE:   break;  // No interrupt
        case  RTCIV_RTCIF:          // RTC Overflow, triggered when RTC counter reaches the value in RTDMOD register.
            ms++;                   // Increment ms every tick.
            if (ms == 0x03E7)       // If ms reaches 1000-1, increment seconds and reset ms.
            {
                sc++;
                ms &= 0x0000;
            }
            break;
        default: break;
    }
}

//** ------ Timer B1 for waits ------ **//
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector = TIMER1_B0_VECTOR
__interrupt void Timer_B1 (void)
#elif defined(__GNUC__)
void __attribute__ ((interrupt(TIMER1_B0_VECTOR))) Timer_B1 (void)
#else
#error Compiler not supported!
#endif
{
    __bic_SR_register_on_exit(LPM0_bits);   // Clear LPM_0 bits from status register and continue to next instruction.
    TB1CCTL0 |= CCIFG_0;                    // Clear the interrupt flag and exit.
}

//** ------ GPIO ISR  ------ **//
#pragma vector=PORT4_VECTOR
__interrupt void Port_4_ISR(void)
{
    P6OUT |= GRNLED;
    P1OUT |= REDLED;
    UARTsendMsg(" Button 1 pushed...\r\n\n");

    P3OUT |= ACK | TTL_OUT;
    delay_ms(TTL_LENGTH);
    P3OUT &= ~(ACK | TTL_OUT);
    P6OUT &= ~(GRNLED);
    P1OUT &= ~(REDLED);

    P4IFG &= ~BTN1;                  // Clear port interrupt flag
}

#pragma vector=PORT3_VECTOR
__interrupt void Port_3_ISR(void)
{
    P6OUT |= GRNLED;
    P1OUT |= REDLED;
    UARTsendMsg(" External TTL detected...\r\n\n");

    P3OUT |= ACK | TTL_OUT;
    delay_ms(TTL_LENGTH);
    P3OUT &= ~(ACK | TTL_OUT);
    P6OUT &= ~(GRNLED);
    P1OUT &= ~(REDLED);

    P3IFG &= ~TTL_IN;                  // Clear port interrupt flag
}
