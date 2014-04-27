void setup() {
  // put your setup code here, to run once:
Serial.begin(115200);

}

void loop() {
  // put your main code here, to run repeatedly: 
  
  // answer, qid=0, group 1 
  Serial.println("a,0,1");
  delay(2000);
  
  Serial.println("a,0,2");
  Serial.println("a,0,3");
}
