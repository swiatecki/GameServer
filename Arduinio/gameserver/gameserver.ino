#include <RF24Network.h>
#include <RF24.h>
#include <SPI.h>

#define ANSLEN 6
#define MAXCLIENTS 18
#define BUFFERLEN 30

byte debug = 0; // Set this to 1, and compile for verbose info.

int numC = 0;



const unsigned long interval = 2000; //ms

// When did we last send?
unsigned long last_sent;

// How many have we sent already
unsigned long packets_sent;


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


int allAns =0;
int beforeAns =0;

byte state;

char buffer[BUFFERLEN];

const byte PREGAME = 0;
const byte TRANSMIT_Q = 1;
const byte RECV_A = 2;

uint16_t clients[MAXCLIENTS] = {0};

  
//int rcvFrom[MAXCLIENTS+1] = {0};
int rcvFrom[100] = {0};
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


int numClients =0;

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
        
        if(clients[i] == header_in.from_node){
         // in list already, ignore and exit for!
         break;
        }else{
         // New client, add it! 
          Serial.print("GOT new client for pos");
          Serial.println(numClients);
          numC ++;
          clients[numClients] = header_in.from_node;
          numClients++;
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
      //Serial.println("here");
      while(Serial.available()){
         
        
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
       Serial.print(buffer);
       Serial.println("X");
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
           
          //Serial.print("i: ");
          //Serial.println(i);
           if(clients[i] != 0){
           // Lets send to this guy!
            RF24NetworkHeader header(/*to node*/ clients[i]);
             Serial.print("transmitting to ");
             Serial.println(clients[i]);
          
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
              bool sendOK = false;
              
              do{
               sendOK = network.write(header,&question,sizeof(question));
               network.update();
              
              }while(sendOK == false);
              
              
             //sendTo[i] = 2; // 2 is fail
             }
           }
         }
         // Implement som ok retry!
         
       /*  int allOK =1;
         for(int i =0;i<MAXCLIENTS;i++){
         
           
           if(clients[i] == 2){
           allOK = 
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
    
    while ( network.available() )
      {
        
        RF24NetworkHeader header_ans;
        
        network.read(header_ans,&answer,sizeof(answer));
      
          
          if(debug){
        Serial.print("Got ans from");
          Serial.println(answer.teamID);
          Serial.print("With QID");
          Serial.println(answer.questionID);
          }
       
       if(answer.questionID != currentQuestion){
      // Serial.println("ignore1");
       //IGNORE!
       }else{
         
        if(rcvFrom[answer.teamID] == 0){
          // New answer, send to server
          
          Serial.println("Got new, uniqe ans:");
          
        
          sendToServer(answer.questionID,answer.teamID, answer.answer);
            
          rcvFrom[answer.teamID] = 1;
          Serial.print("Writing to space ");
          Serial.println(answer.teamID);
       
         
        }else{
       // Serial.println("ignore2");
        }
      }
      }

       allAns =0;
       
       //check number of answers
       for(int i=0;i<100;i++){
       
       if(rcvFrom[i]){
       allAns++;
      
       
       }
       
       }
       
       if(allAns > 0){
       
       beforeAns += allAns;
       }
       
          for(int x=0;x<100;x++){
 
      rcvFrom[x] = 0;

       }
       
       
     unsigned long now = millis();
            if ( now - last_sent >= interval  )
            {
              last_sent = now;

        Serial.print("BF is:");
       Serial.println(beforeAns);
  
  }
    
       
   
       
       int tmp2 =0;
       
       // Check number of clients
       
       for(int i=0;i<MAXCLIENTS;i++){
       
       if(clients[i] != 0){
       
       tmp2++;
       }
       
       }
       
       /*Serial.print("Tmp2 is:");
       Serial.print(tmp2);
       Serial.print("allAns is:");
       Serial.println(allAns);*/
       
       if(numC == beforeAns){
       
       // all recv - gogo
      
       Serial.println("All recieved, GOING to transmit");
       Serial.println(beforeAns);
        Serial.println(tmp2);
       beforeAns =0;
        // Reset stuff for next time! 
        allAns = 0;
        
         state = TRANSMIT_Q;
        
      for(int x=0;x<100;x++){
 
      rcvFrom[x] = 0;

       }
       
       }
       
       
       
     /*  Serial.print("AllAns:");
       Serial.print(allAns);
       Serial.print("tmp2:");
       Serial.println(tmp2); */
       //
       
      

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

