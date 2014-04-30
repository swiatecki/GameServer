#include <RF24Network.h>
#include <RF24.h>
#include <SPI.h>

#define ANSLEN 6


RF24 radio(8,7);

// Network uses that radio
RF24Network network(radio);

// Address of our node
const uint16_t this_node = 01;

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
const byte TRANSMIT_ANS = 1;
const byte RECV_Q = 2;

 int curTeam = 1;

int to_send=0;

byte currentQuestion =0;

void setup(void)
{
  Serial.begin(115200);
  Serial.println("41030 Test Client");
 
 
 state =PREGAME;
 
  SPI.begin();
  radio.begin();
  network.begin(/*channel*/ 100, /*node address*/ this_node);
  Serial.println("INIT OK");
}

void loop(void)
{
  
 
  
  while(Serial.available()){
   // Serial.println("got something");
  byte incomming = Serial.read();
    if(incomming == 'n'){
      // if s, then next is state
    curTeam++;
    }
    
    Serial.println("Team IS NOW");
    Serial.print(curTeam);
  }
  
  
  
  switch(state){
  
  case PREGAME:
  {
      /* SEND JOIN REQUESTS */
    
      // Pump network
      network.update();
      
 
      // Transmit join request,
      
      Serial.println("Sending join");

       const uint16_t to = 00;
       
       answer.questionID = 0;
       answer.teamID = curTeam;
       answer.answer = 3;
       
       
       RF24NetworkHeader header_a(to);
      bool ok = network.write(header_a,&answer,sizeof(answer));
      //if (ok)
       // Serial.println("ok.");
      //else
        //Serial.println("failed.");
        
       
        
     while ( network.available() )
      {
        
        // Got something!!
        
        /* RF24NetworkHeader header_b;
     network.read(header_b,&question,sizeof(question));
      
        
      Serial.print("QID:");
        Serial.println(question.questionID);
        if(question.questionID != 0){*/
        
        state = RECV_Q;
        break;
        
        /*Serial.println("GOT First question");
       break;
        
        }*/
      
      }
       delay(2000);

  }
  break;
  
  
  case TRANSMIT_ANS:
     
     {
     network.update();
     
      RF24NetworkHeader header(to_send);
      
      answer.questionID = currentQuestion;
      answer.teamID = curTeam;
      answer.answer = 3;
      
      
      bool ok = network.write(header,&answer,sizeof(answer));
        if(ok){
          Serial.println(answer.questionID);
        Serial.println("Answer sent!");
        }else{
        // Serial.print("Answer send failed!");
        }
        
        network.update();
        
        
       while ( network.available() )
      {
     
        state = RECV_Q;
        break;
      }
      
      delay(5000);
        
     }
  
  break;
 
   case RECV_Q:
  {
     
    
      // Pump network
      network.update();
      
        
     while ( network.available() )
      {
      RF24NetworkHeader header;
      network.read(header,&question,sizeof(question));
      
        
        Serial.print("QID:");
        Serial.print(question.questionID);
        if(question.questionID != currentQuestion){
        currentQuestion = question.questionID;
        state = TRANSMIT_ANS;
        
       
       Serial.println(question.optionA);
       
        break;
        }
      
      }

  }
  break;
  
  
  
  
  }
   
  
}



