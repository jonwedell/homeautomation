/**
 * The MySensors Arduino library handles the wireless radio link and protocol
 * between your home built sensors/actuators and HA controller of choice.
 * The sensors forms a self healing radio network with optional repeaters. Each
 * repeater and gateway builds a routing tables in EEPROM which keeps track of the
 * network topology allowing messages to be routed to nodes.
 *
 * Created by Henrik Ekblad <henrik.ekblad@mysensors.org>
 * Copyright (C) 2013-2015 Sensnology AB
 * Full contributor list: https://github.com/mysensors/Arduino/graphs/contributors
 *
 * Documentation: http://www.mysensors.org
 * Support Forum: http://forum.mysensors.org
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * version 2 as published by the Free Software Foundation.
 *
 *******************************
 *
 * REVISION HISTORY
 * Version 1.0 - Henrik Ekblad
 *
 * DESCRIPTION
 * Motion Sensor example using HC-SR501
 * http://www.mysensors.org/build/motion
 *
 */

#include <MySensor.h>
#include <SPI.h>

#define INTERRUPT DIGITAL_INPUT_SENSOR-2 // Usually the interrupt = pin -2 (on uno/nano anyway)
#define VOLTAGE_ID 1   // Id of the sensor child

MySensor gw;
// Initialize motion message
MyMessage volt_msg(VOLTAGE_ID, V_VOLTAGE);

long readVcc() {
	// Read 1.1V reference against AVcc
	// set the reference to Vcc and the measurement to the internal 1.1V reference
	#if defined(__AVR_ATmega32U4__) || defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)
	ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
	#elif defined (__AVR_ATtiny24__) || defined(__AVR_ATtiny44__) || defined(__AVR_ATtiny84__)
	 ADMUX = _BV(MUX5) | _BV(MUX0) ;
	#else
	ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
	#endif  
	
	delay(2); // Wait for Vref to settle
	ADCSRA |= _BV(ADSC); // Start conversion
	while (bit_is_set(ADCSRA,ADSC)); // measuring
	
	uint8_t low  = ADCL; // must read ADCL first - it then locks ADCH  
	uint8_t high = ADCH; // unlocks both
	
	long result = (high<<8) | low;
	
	result = 1125300L / result; // Calculate Vcc (in mV); 1125300 = 1.1*1023*1000
	return result; // Vcc in millivolts
}

void setup()
{
	gw.begin();

	// Send the sketch version information to the gateway and Controller
	gw.sendSketchInfo("volt_test", "1.0");

	// Register all sensors to gw (they will be created as child devices)
	gw.present(VOLTAGE_ID, S_MULTIMETER);
}

void loop()
{
	// Timer wakeup - send voltage every 10 minutes
	gw.send(volt_msg.set(readVcc()));
	gw.sleep(3600000);
}

