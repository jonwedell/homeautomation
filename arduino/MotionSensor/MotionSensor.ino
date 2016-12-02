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

#define DIGITAL_INPUT_SENSOR 3   // The digital input you attached your motion sensor.  (Only 2 and 3 generates interrupt!)
#define INTERRUPT DIGITAL_INPUT_SENSOR-2 // Usually the interrupt = pin -2 (on uno/nano anyway)
#define CHILD_ID 1   // Id of the sensor child

MySensor gw;
// Initialize motion message
MyMessage msg(CHILD_ID, V_TRIPPED);

void setup()
{
	gw.begin();

	// Send the sketch version information to the gateway and Controller
	gw.sendSketchInfo("Debounced Motion Sensor", "1.0");

	// sets the motion sensor digital pin as input
	pinMode(DIGITAL_INPUT_SENSOR, INPUT);
	// Register all sensors to gw (they will be created as child devices)
	gw.present(CHILD_ID, S_MOTION);
	
	// Read digital motion value and send tripped value to gw
	boolean tripped = digitalRead(DIGITAL_INPUT_SENSOR) == HIGH;
	gw.send(msg.set(tripped ? "1" : "0"));
}

void loop()
{
	// As long as the sensor is tripped, have bursts of 5 second sleep
	// and only go into interrupt-based sleep once the sensor is low again.
	// This is done to ensure we avoid the brief LOW signal that the motion
	// sensor always sends between high signals.
	while (digitalRead(DIGITAL_INPUT_SENSOR) == HIGH){
		// Sleep until we go to low
		gw.sleep(INTERRUPT, FALLING, 0);
		// Okay, we went to low. Sleep 5 seconds to make sure we didn't go
		// right back to high. (The LOW state between HIGH states seems to last
		// 2.15 seconds and the shortest HIGH signal we can receive from testing
		// is about 3 seconds, so regardless of the timing setting of the sensor
		// this should avoid sending a LOW signal between highs
		gw.sleep(5000);	
	}
	
	// When we get here the signal is actually LOW so send that message
	gw.send(msg.set("0"));
	// Sleep until the signal goes HIGH (motion detected)
	gw.sleep(INTERRUPT, RISING, 0);
	// When we get here it is because there was motion so send that message
	gw.send(msg.set("1"));
}

