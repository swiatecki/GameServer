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

const uint16_t to = 01;

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

uint16_t clients[MAXCLIENTS] = {0};

  
int rcvFrom[MAXCLIENTS+1] = {0};
byte sendTo[MAXCLIENTS+1] = {0};

byte save =0;

int to_send=0;

 char incomming;
     int bufPos;


byte currentQuestion =0;

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
 
  
  if(state == PREGAME || state == RECV_A ){
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
      RF24NetworkHeader header_in;

      // Check if its a new client.
      // Lets see what he has
      network.read(header_in,&answer,sizeof(answer));
      
      
      for(int i =0;i<MAXCLIENTS;i++){
        //Serial.print(tmp,BIN);
       // Serial.print("vs");
        //Serial.print(header_in.from_node,BIN);
        Serial.println("");
        if(clients[i] == header_in.from_node){
         // in list already, ignore
         break;
        }else{
         // New client, add it! 
          Serial.print("GOT new client at pos");
          Serial.print(i);
          clients[i] = header_in.from_node;
          i=MAXCLIENTS;
          break;
        
        }

      }

      
       // Serial.print(header_in.from_node,BIN);
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
       
        Serial.print("CREATING PAYLOAD, with ID:");
        Serial.println( question.questionID);
       currentQuestion =  question.questionID;
       ptr = &buffer[1];
       strncpy(question.optionA,ptr,ANSLEN);
        ptr = &buffer[1+6];
        strncpy(question.optionB,ptr,ANSLEN);
        ptr = &buffer[1+12];
        strncpy(question.optionC,ptr,ANSLEN);
        ptr = &buffer[1+18];
        strncpy(question.optionD,ptr,ANSLEN);
      
         for(int i =0;i<MAXCLIENTS;i++){
          //Serial.println("here ");
           if(clients[i] != 0){
           // Lets send to this guy!
            RF24NetworkHeader header(/*to node*/ clients[i]);
             Serial.println("transmitting for");
          
             bool ok = network.write(header,&question,sizeof(question));
           network.update();
             if(ok){
            Serial.print("OK SEND for:");
            Serial.print(clients[i]);
            Serial.println(".");
            sendTo[i] = 1; 
             }else{
             // Retry code
             Serial.print("send failed for:");
              Serial.println(clients[i]);
             sendTo[i] = 2; // 2 is fail
             }
           }
         }
         // Implement som ok retry!
         /*for(int i =0;i<MAXCLIENTS;i++){
         if(sendTo[i] == 2){
         // at least one failed!!
         
         }
         
         }*/
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
  {
    
    
    network.update();

    /* 1) Read the network
     2) Check if the client has answered the current quesion
     3) if not, parse the data 
     4) transmit to gameserver.
     */

    // ToDo: add array to keep track of the clients who have answered the current question

    while ( network.available() )
      {
        
        RF24NetworkHeader header;
        
        network.read(header,&answer,sizeof(answer));
        
       /* Serial.print("Got ans from");
          Serial.println(answer.teamID);
          Serial.print("With QID");
          Serial.println(answer.questionID);*/
       
       if(answer.questionID != currentQuestion){
      // Serial.println("ignore1");
       //IGNORE!
       }else{
         
        if(rcvFrom[answer.teamID] == 0){
          // New answer, send to server
          
          Serial.print("Got new, uniqe ans:");
          
        
          sendToServer(answer.questionID,answer.teamID, answer.answer);
            
          rcvFrom[answer.teamID] = 1;
          
        }else{
       // Serial.println("ignore2");
        }
      }
      }

     // Fix for more than one client!!!!
      if(rcvFrom[1] == 1){
       state = TRANSMIT_Q;
       
       
       
       
       // Reset stuff for next time! 
       
       for(int i=0;i<MAXCLIENTS;i++){
       
       rcvFrom[i]=0;
       
       }
       
      }

      }
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

