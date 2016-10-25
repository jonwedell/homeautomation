int led = 13;
int motion = 3;
int prev_state = 0;

void setup()
{
	Serial.begin(9600);
	pinMode(led, OUTPUT);
	pinMode(motion, INPUT);
	prev_state = digitalRead(motion);
}

void loop()
{
	if (digitalRead(motion) == HIGH) {
		digitalWrite(led, HIGH);
		if (prev_state == LOW){
			Serial.println("State changed to high.");
		}
		prev_state = HIGH;
	}
	else {
		digitalWrite(led, LOW);
		if (prev_state == HIGH){
			Serial.println("State changed to low.");
		}
		prev_state = LOW;
	}
}
