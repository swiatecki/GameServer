#include <RF24Network.h>
#include <RF24.h>
#include <SPI.h>

#define ANSLEN 6
#define MAXCLIENTS 18


RF24 radio(8,7);

// Network uses that radio
RF24Network network(radio);

// Address of our node
const uint16_t this_node = 0;

const unsigned long interval = 2000; //ms

// When did we last send?
unsigned long last_sent;

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

uint16_t clients[MAXCLIENTS] = {0};


int to_send=0;

void setup(void)
{
  Serial.begin(115200);
  Serial.println("RF24Network/examples/helloworld_rx/");
 
  SPI.begin();
  radio.begin();
  network.begin(/*channel*/ 100, /*node address*/ this_node);
}

void loop(void)
{
  
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
      
      
      while ( network.available() )
      {
      RF24NetworkHeader header;
      
       // Check if its a new client.
      
        for(byte i =0;i<MAXCLIENTS;i++){
          if(clients[i] != header.from_node){
            // New client, add it! 
            clients[i] = header.from_node;
            break;
          }
        
        }
      
      // Lets see what he has
      network.read(header,&answer,sizeof(answer));
      
        if(answer.questionID == 0){
        // This is a join request, lets send it to the server
        
        sendToServer(0,answer.teamID,answer.answer);
        
        }else{
        // Ignore
        }
      
      }
  break;
  
  
  case TRANSMIT:
  
  
  
  break;
  
  
  
  
  
  }
   
  
}

}


void sendToServer(byte Qid, byte Tid, byte ans){

//  typeAsChar = '';
//  if(type == joinrequest){typeAsChar = '}
  /* //a,Qid,Tid,ans \n \r */
  Serial.print("//a,");
  Serial.print(Qid);
  Serial.print(",");
  Serial.print(Tid);
  Serial.print(",");
  Serial.println(ans);

}
