# Part 1: Research and Analysis of DDoS Attack Techniques (Unchanged)

**Objective:** Students will conduct in-depth research on the common methods used to execute Distributed Denial of Service (DDoS) attacks, focusing on the layers of the OSI model they target and how they operate.

---

## Task A: Categorization and Description

Research and define the three primary categories of DDoS attacks (Volumetric, Protocol, Application Layer). For each category, describe its goal and provide at least two specific attack examples. Present your findings in a comparison table.

| DDos Category     | Primary goal of attack                                                                                                                                                                                                                                  | Examples              | Description                                                                                                                                                                                                                                                                                                                                                    |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Volumetric        | Its primary goal is to consume all the available bandwidth. This means the attack sends a massive amount of traffic until it saturates the network. The attacker sends large volumes of garbage data that overwhelm the victim’s bandwidth.             | Reflection Amplification | The attacker sends a small request to a server but uses the victim’s IP address, so the server actually responds to the victim. The responses from the server are much larger than the requests, and because the victim receives so many of them, its bandwidth becomes fully consumed.                                                                      |
|                   |                                                                                                                                                                                                                                                         | ICMP Flood             | The attacker sends a very large number of echo-requests, which are normally used for diagnostics or to check device connectivity. The victim must respond to the same amount of requests, which causes its bandwidth to be consumed and unavailable for legitimate traffic.                                                                                |
| Protocol          | Its primary goal is to consume protocol resources. This means the attacker wants to exhaust the server’s connection-state tables or protocol handling capacity. For example, in the TCP protocol, the attacker sends many requests without completing the connection, filling up the server’s table of half-open or invalid connections. | TCP Reset Flood        | The attacker sends a large number of TCP packets with the RST flag, forcing the server to immediately drop active connections, even real ones, and exhausting protocol processing resources.                                                                                                                          |
|                   |                                                                                                                                                                                                                                                         | ICMP Fragmentation     | The attacker sends large ICMP packets that are fragmented into many small pieces. When these fragments arrive, the server has to reassemble them to reconstruct the complete packet and then process the ICMP request. Handling the reassembly of so many packets causes the CPU, memory, and reassembly buffer to become overwhelmed.                         |
| Application layer | The main goal is to attack the application itself meaning this works on the OSI Layer 7. These attacks exhaust resources such as CPU, memory, threads, or database connections by overwhelming the server with requests that seem legitimete.          | Slow Read              | The attacker sends an HTTP request, for example, a normal GET request. The server begins delivering the response, but the attacker reads it as slowly as possible, sometimes as slow as 1 byte per second. This forces the server to keep the connection open for a long time, eventually exhausting its available connections.                               |
|                   |                                                                                                                                                                                                                                                         | API Resource Exhaustion | The attacker sends many heavy resource API requests that require calculations or database operations. This forces the server to consume large amounts of CPU and memory, eventually causing the application to fail or to lower its performance.                                                                       |

---

## Task B: In-Depth Attack Profile

Choose one specific attack from your table (e.g., DNS Amplification) and write a detailed profile (250-350 words) that explains its Mechanism, the Resource Exhaustion it causes, and how Botnets/Amplification are used.

### Volumetric:

The ICMP Flood consists of sending ICMP echo requests from the attacker to the victim. ICMP echo requests are usually used for health diagnosis and for checking the connection between two devices. In normal use, the echo request can be sent with tools like ping or traceroute: ping checks the connection, and traceroute checks the route used to connect two devices.

This attack wants to send a massive amount of echo requests to the victim. The victim tries to follow the correct or usual protocol and tries to send replies to all of these echo requests, which are called echo replies. This causes the saturation of the victim’s incoming and outgoing bandwidth. This attack seeks to overwhelm the victim’s capacity to respond to so much traffic and max out its bandwidth. The big amount of traffic already on the network causes messages that are legitimate to not be able to arrive to the victim.

One thing to take into consideration is that because it is using the ICMP echo request, this does not require a handshake, meaning it is easier for the attacker to generate these requests.

This type of attack is actually symmetrical, which means that the bandwidth that is being occupied is proportional to the amount of traffic and direct echo requests that are being sent and the echo replies they generate. This explains why normally this type of attack can rely on botnets to saturate the victim’s bandwidth.

---

### Protocol: 

A Transmission Control Protocol Reset or also known as a TCP Reset is a type of protocol type DDoS attack in which the victim or the system is overwhelmed by receiving a high volume of forged TCP RST packets. A TCP reset is a flag in a TCP packet that is normally used to terminate an active TCP connection when one endpoint wants to close the session immediately. These packets want to disrupt normal communication and to exhaust the system’s resources.

When the system receives a massive number of RST packets, it attempts to verify whether each corresponds to a real problem. 

Attackers often rely on botnets to generate a really high volume, globally distributed RST floods. Each bot sends forged packets, and the combined traffic overwhelms the victim. 

The attack overwhelms the system’s connection tracking subsystem, like the TCP control block. Processing millions of RST packets consumes CPU cycles, the memory used for storing information, and the kernel resources. Apart from that, the frequent invalid resets can damage genuine connections, forcing servers or clients to repeatedly re-establish sessions, further increasing workload. At high enough rates, the system cannot keep up with this, and the final result is a slow service or for the system to fail. Other devices such as load balancers, firewalls, and intrusion prevention systems can be also targeted, as they maintain session states and can be overwhelmed by the volume of packets.

---

### Transport layer: 

An API (Application Programming Interface) resource exhaustion attack is an application-layer DDoS attack in which the system is overwhelmed by repeatedly sending requests to API endpoints that need an long time of computations, operations or resources. 

The attacker sends a large number of requests, usually ment to take a really long time, but realistic enough so that the requests are confused as real ones and may appear as normal or common user behavior, making them difficult to block or to get noticed. The attack works because the application must  process each request before responding to each one, the server automatically slows down by ‘real-looking’ traffic that overwhelms its compute capacity.

These attacks, that once again require extensive calculations or database operations, force the server to consume resources like the CPU, the memory, and database connections. 

Another thing to take into consideration, since these API requests can be anything from database queries to authentication routines, or complex calculations, they offer a great opportunity for attackers to saturate server resources with a low traffic volume meaning they don’t necessarrily need to send thousands and thousands of these requests.

Attackers could use botnets to distribute these API calls. Each bot could issues an exhaustive API request, so the overall effect overwhelms the server even if each device contributes a small load. Botnets could also be used to vary request patterns and evade detection by traditional security measures.

