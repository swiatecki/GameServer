#include <RF24Network.h>
#include <RF24.h>
#include <SPI.h>

#define ANSLEN 6
#define MAXCLIENTS 18
#define BUFFERLEN 30

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

}
question;

struct answer_t
{
  byte questionID;
  byte teamID;
  byte answer;

}
answer;

byte state;

char buffer[BUFFERLEN];

const byte PREGAME = 0;
const byte TRANSMIT_Q = 1;
const byte RECV_A = 2;

uint16_t clients[MAXCLIENTS] = {
  0};

byte save =0;

int to_send=0;

 char incomming;
     int bufPos;

void setup(void)
{
  Serial.begin(115200);
  Serial.println("Starting gameserver Modem");


  state = 0; // Start state.. 

  SPI.begin();
  radio.begin();
  network.begin(/*channel*/ 100, /*node address*/ this_node);
  Serial.println("Init complete");
}

void loop(void)
{
  if(state == PREGAME){
    while(Serial.available()){
      byte incomming = Serial.read();
      Serial.print("State was:");
      Serial.println(state);
      if(incomming == 's'){
        // if s, then next is state

        state = Serial.read();
        if(state-'0' == 1){
        state = state-'0'; // Convert from char to int the snakey way
        }

        Serial.print("STATE IS NOW:");
        Serial.print(state);
        Serial.println(".");
        break;

      }


    }
  }


  switch(state){

  case PREGAME:
    /* LISTEN FOR JOIN REQUESTS */

    // Pump network
    //Serial.println("Pumping");
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
        // Serial.println("SENDING data to you!");
        sendToServer(0,answer.teamID,answer.answer);

      }
      else{
        // Ignore
      }

    }
    break;


  case TRANSMIT_Q:
    network.update();

    /* 1) Read serial data from server
     2) parse data into char arrays, then to struct
     3) send to every client that has joined the game!
     */
     
    
    if(save ==0){
      while(Serial.available()){
        // Serial.println("now we are here");
        
        incomming = Serial.read();
        Serial.println(incomming);
       
        if(incomming == 'q'){
          // if q, the next is a question! Until \0
          Serial.println("OK we got q");
          save =1;
          int bufPos = 0;
          break;
         }
        }
      
      }
     
     // Got save!
     
     if(save==1){
     
       while(Serial.available()){
       
       incomming = Serial.read();
        buffer[bufPos] = incomming;
        if(incomming == '\r' || incomming == '\n' || incomming == '\0'){
        // Done, reset
        bufPos =0;
        save =2;
        Serial.print("(END by rn0) WE GOT:");
       Serial.println(buffer);
        break;
        }
        else if(bufPos < BUFFERLEN){
          bufPos++;
        }else{
        // Done, reset
         bufPos =0;
        save =2;
        Serial.print("(END by bufflen) WE GOT:");
       Serial.println(buffer);
        break;
        }
      
       }
       
     
     }
       
       if(save ==2){
       //Got something to send!!!!
       
       // Create payload
       char * ptr;
       question.questionID = buffer[0]-48; // Char to byte
       ptr = &buffer[1];
       strncpy(question.optionA,ptr,ANSLEN);
        ptr = &buffer[1+6];
        strncpy(question.optionB,ptr,ANSLEN);
        ptr = &buffer[1+12];
        strncpy(question.optionC,ptr,ANSLEN);
        ptr = &buffer[1+18];
        strncpy(question.optionD,ptr,ANSLEN);
      
         for(int i =0;i<MAXCLIENTS;i++){
           if(clients[i] != 0){
           // Lets send to this guy!
            RF24NetworkHeader header(/*to node*/ clients[i]);
            bool ok = network.write(header,&question,sizeof(question));
            network.update();
             if(ok){
            Serial.print("OK SEND for:");
            Serial.print(clients[i]);
            Serial.println(".");
             }else{
             // Retry code
             
             
             }
           }
         }
         
         // All sent! 
         save = 0;
         state = RECV_A;
       
       }
       
       
     
          

          // Buffer = id,6,6,6,6\0.
          // 6*4 = 24
          // + 4*, = 28
          // + id + \0 = 30

    break;

  case RECV_A:
    network.update();

    /* 1) Read the network
     2) Check if the client has answered the current quesion
     3) if not, parse the data 
     4) transmit to gameserver.
     */

    // ToDo: add array to keep track of the clients who have answered the current question


    break;





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

