#include <RF24Network.h>
#include <RF24.h>
#include <SPI.h>

#define ANSLEN 6


RF24 radio(8,7);

// Network uses that radio
RF24Network network(radio);

// Address of our node
const uint16_t this_node = 1;

const unsigned long interval = 2000; //ms

// How many have we sent already
unsigned long packets_sent;

// Structure of our payload
struct question_t
{
  byte questionID;
  char optionA[ANSLEN];
  char optionB[ANSLEN];
  char optionC[ANSLEN];
  char optionD[ANSLEN];
  
}question;

struct answer_t
{
  byte questionID;
  byte teamID;
  byte answer;
  
}answer;

byte state;

const byte PREGAME = 0;
const byte TRANSMIT = 1;
const byte RECV = 2;



int to_send=0;

void setup(void)
{
  Serial.begin(115200);
  Serial.println("RF24Network/examples/helloworld_rx/");
 
 
 state =0;
 
  SPI.begin();
  radio.begin();
  network.begin(/*channel*/ 100, /*node address*/ this_node);
}

void loop(void)
{
  
  int curTeam = 1;
  
  while(Serial.available()){
  byte incomming = Serial.read();
    if(incomming == 's'){
      // if s, then next is state
    state = Serial.read();
    }
    
    Serial.println("STATE IS NOW");
    Serial.print(state);
  
  switch(state){
  
  case PREGAME:
      /* LISTEN FOR JOIN REQUESTS */
    
      // Pump network
      network.update();
      
 
      // Transmit join request,
      
      Serial.print("Sending...");
      Serial.println("");

       const uint16_t to = 00;
       
       answer.questionID = 0;
       answer.teamID = curTeam;
       answer.answer = 3;
       
       
       RF24NetworkHeader header(to);
      bool ok = network.write(header,&answer,sizeof(answer));
      if (ok)
        Serial.println("ok.");
      else
        Serial.println("failed.");
        
        curTeam++;
        delay(3000);
      
      
     
  break;
 
  
  
  
  
  
  }
   
  
}

}

