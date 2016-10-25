#include <MySensor.h>
#include <SPI.h>

// Mysensors definitions
#define TEMPERATURE_ID 1
#define HUMIDITY_ID 2
#define LIGHT_ID 3
#define VOLTAGE_ID 4

MySensor gw;
// Initialize various messages
MyMessage tmp_msg(TEMPERATURE_ID, V_TEMP);
MyMessage hum_msg(HUMIDITY_ID, V_HUM);
MyMessage light_msg(LIGHT_ID, V_LIGHT_LEVEL);
MyMessage volt_msg(VOLTAGE_ID, V_VOLTAGE);

// LED definitions
#define DATAOUT 11 // MOSI
#define DATAIN 12 // MISO - not used, but part of builtin SPI
#define SPICLOCK 13 // SPI clock
#define DISPLAYONE 10 // Slave select

// PIR definitions
int PIR = A0; // select the input pin for the potentiometer
int PIRsensorValue; // variable to store the value coming from the sensor

// Temperature/pressure definitions
int DHpin = 8;
byte dat [5];

// Voltmeter
long voltage = 4000;

char spi_transfer(volatile char data)
{
    SPDR = data;                    // Start the transmission
    while (!(SPSR & (1<<SPIF))){};     // Wait the end of the transmission
    return SPDR;                    // return the received byte
}

void setup()
{
	
	// Set up the radio first
	gw.begin();

	delay(100);
	// Send the sketch version information to the gateway and Controller
	gw.sendSketchInfo("sosensy", "1.0");
	// Register all sensors to gw (they will be created as child devices)
	gw.present(TEMPERATURE_ID, V_TEMP);
	gw.present(HUMIDITY_ID, V_HUM);
	gw.present(LIGHT_ID, V_LIGHT_LEVEL);
	gw.present(VOLTAGE_ID, V_VOLTAGE);
    
    /*
    byte clr;
    pinMode(DATAOUT, OUTPUT);
    pinMode(DATAIN, INPUT);
    pinMode(SPICLOCK, OUTPUT);
    pinMode(DISPLAYONE, OUTPUT);
    digitalWrite(DISPLAYONE, HIGH); //disable device
    // SPCR = 01010010
    //interrupt disabled,spi enabled,msb 1st,master,clk low when idle,
    //sample on leading edge of clk,system clock/64 
    SPCR = (1<<SPE)|(1<<MSTR)|(1<<SPR1);
    clr=SPSR;
    clr=SPDR;
    delay(10);
    write_led_numbers(0x78,0x78,0x78,0x78); //Blank display
    write_led_decimals(0x00); // All decimal points off
    */
    
    // Set up the input modes
    pinMode(PIR, INPUT);
    pinMode (DHpin, OUTPUT);
}

void write_led_decimals(int value)
{
    digitalWrite(DISPLAYONE, LOW);
    delay(10);
    spi_transfer(0x77);     // Decimal Point OpCode
    spi_transfer(value);    // Decimal Point Values
    digitalWrite(DISPLAYONE, HIGH); //release chip, signal end transfer
}

void blank_screen()
{
    digitalWrite(DISPLAYONE, LOW);
    delay(10);
    spi_transfer(0x76);      // Reset code
    digitalWrite(DISPLAYONE, HIGH); //release chip, signal end transfer
}

void write_led_numbers(int digit1, int digit2, int digit3, int digit4)
{
    digitalWrite(DISPLAYONE, LOW);
    delay(10);
    spi_transfer(0x76);      // Reset code
    spi_transfer(digit1);    // Thousands Digit
    spi_transfer(digit2);    // Hundreds Digit
    spi_transfer(digit3);    // Tens Digit
    spi_transfer(digit4);    // Ones Digit
    digitalWrite(DISPLAYONE, HIGH); //release chip, signal end transfer
}
void write_led(unsigned short num, unsigned short base, unsigned short pad)
{
   unsigned short digit[4] = { 0, ' ', ' ', ' ' };
   unsigned short place = 0;

   if ( (base<2) || (base>16) || (num>(base*base*base*base-1)) ) {
       write_led_numbers(' ', 0x00, 0x0f, ' ');  // indicate overflow
   } else {
       while ( (num || pad) && (place<4) ) {
           if ( (num>0)  || pad )
               digit[place++] = num % base;
           num /= base;
       }
       write_led_numbers(digit[3], digit[2], digit[1], digit[0]);
   }
}

// Read PIR
void readPIR(){
	// Get photoresistor 
	PIRsensorValue = analogRead(PIR);
}

// Read sensor helper
byte read_data () {
  byte data;
  for (int i = 0; i < 8; i ++) {
    if (digitalRead (DHpin) == LOW) {
      while (digitalRead (DHpin) == LOW); // wait for 50us
      delayMicroseconds (30); // determine the duration of the high level to determine the data is '0 'or '1'
      if (digitalRead (DHpin) == HIGH)
        data |= (1 << (7-i)); // high front and low in the post
      while (digitalRead (DHpin) == HIGH); // data '1 ', wait for the next one receiver
     }
  }
return data;
}

void get_temperature_and_pressure () {
  digitalWrite (DHpin, LOW); // bus down, send start signal
  delay (30); // delay greater than 18ms, so DHT11 start signal can be detected
 
  digitalWrite (DHpin, HIGH);
  delayMicroseconds (40); // Wait for DHT11 response
 
  pinMode (DHpin, INPUT);
  while (digitalRead (DHpin) == HIGH);
  delayMicroseconds (80); // DHT11 response, pulled the bus 80us
  if (digitalRead (DHpin) == LOW);
  delayMicroseconds (80); // DHT11 80us after the bus pulled to start sending data
 
  for (int i = 0; i < 4; i ++) // receive temperature and humidity data, the parity bit is not considered
    dat[i] = read_data ();
 
  pinMode (DHpin, OUTPUT);
  digitalWrite (DHpin, HIGH); // send data once after releasing the bus, wait for the host to open the next Start signal
}

void readVcc() {
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
	voltage = result; // Vcc in millivolts
}


void print_readings(){
	Serial.print ("Current humdity =");
	Serial.print (dat [0], DEC); // display the humidity-bit integer;
	Serial.print ('.');
	Serial.print (dat [1], DEC); // display the humidity decimal places;
	Serial.println ('%');
	Serial.print ("Current temperature =");
	Serial.print (dat [2], DEC); // display the temperature of integer bits;
	Serial.print ('.');
	Serial.print (dat [3], DEC); // display the temperature of decimal places;
	Serial.println ('C');
	Serial.print ("Light reading = ");
	Serial.println(PIRsensorValue, DEC);
}

void loop()
{
	// Get the readings
	readPIR();
	get_temperature_and_pressure();
	readVcc();
	
	// Print the readings
	//print_readings();
	
	// Send the readings
	gw.send(tmp_msg.set(dat[2]));
	gw.send(hum_msg.set(dat[0]));
	gw.send(light_msg.set(PIRsensorValue));
	gw.send(volt_msg.set(voltage));

	//write_led(dat[2],10,0);	
	delay(30000);
}





