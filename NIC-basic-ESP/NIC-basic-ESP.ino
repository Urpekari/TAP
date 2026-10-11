void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  while (!Serial){
  }
  // Wait for serial port to be available
}

void loop() 
{
  // Serial data is pending
  if (Serial.available()) 
  { 
    // Echo serial data on serial device
    Serial.write( Serial.read() );
  }  
}