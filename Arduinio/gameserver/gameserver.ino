#include <RF24Network.h>
#include <RF24.h>
#include <SPI.h>

#define MSGLEN 50


RF24 radio(8,7);

// Network uses that radio
RF24Network network(radio);

// Address of our node
const uint16_t this_node = 0;

// Address of the other node
const uint16_t other_node = 1;

const unsigned long interval = 2000; //ms

// When did we last send?
unsigned long last_sent;

// How many have we sent already
unsigned long packets_sent;

// Structure of our payload
struct payload_t
{
  char msg[MSGLEN];
  
};



payload_t out,in;
uint16_t to=0;
int to_send=0;

void setup(void)
{
  Serial.begin(57600);
  Serial.println("RF24Network/examples/helloworld_rx/");
 
  SPI.begin();
  radio.begin();
  network.begin(/*channel*/ 100, /*node address*/ this_node);
}

void loop(void)
{
  // Pump the network regularly
  network.update();

  // Is there anything ready for us?
  while ( network.available() )
  {
    // If so, grab it and print it out
    RF24NetworkHeader header;
    
    network.read(header,&in,sizeof(in));
    
    to = header.from_node;
   Serial.print("got something");
   Serial.print(" - From:");
   Serial.println(to);
   
   
   strncpy(out.msg,in.msg,MSGLEN);
   Serial.write(out.msg);
     Serial.println("");
   to_send++;
   
   
   
  }
  
  
  // Send part 
  
  // If it's time to send a message, send it!
if(to_send > 0){


    Serial.print("Sending...");
  Serial.println("");


    RF24NetworkHeader header(/*to node*/ to);
    bool ok = network.write(header,&out,sizeof(out));
    if (ok)
      Serial.println("ok.");
    else
      Serial.println("failed.");
      
      to_send--;
}
  
  
  
}
// vim:ai:cin:sts=2 sw=2 ft=cpp
