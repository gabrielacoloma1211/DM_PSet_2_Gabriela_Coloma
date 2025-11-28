# Homework 3: Web Security

**Course:** Seguridad Informática
**Professor:** Alejandro Proaño
**University:** Universidad San Francisco de Quito (USFQ)

**Students:**
- Jesus Alarcon (00324826)
- Gabriela Coloma (00325312)

**Date:** November 27, 2025

---
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

---

# Part 2: DVWA Deployment and Common Attacks

## Task A: DVWA Installation via Docker

### Docker Command

```bash
docker run --rm -d --name dvwa -p 8080:80 vulnerables/web-dvwa
```

Note: Port 8080 was used on the host to avoid conflicts with other services.

### Access Information
- URL: http://localhost:8080/
- Username: admin
- Password: password

### Screenshot
See file: `screenshots/DVWA_login.png`

---

## Task B: Attack Execution and Documentation

Security level configured: **Medium**

### Attack 1: SQL Injection

**Vulnerability Name:** SQL Injection

**Payload Used:**
```
1 OR 1=1#
```

**Method:** POST (Medium security uses POST instead of GET for this vulnerability)

**Explanation:**

The Medium security level implements `mysql_real_escape_string()` which escapes single and double quotes. The payload bypasses this protection by avoiding quotes entirely. Instead, it uses a numeric context where quotes are not required. The `OR 1=1` condition makes the WHERE clause always evaluate to true, and the `#` symbol comments out the rest of the SQL query, preventing syntax errors.

**Result:** Successfully extracted all user records from the database (5 users: admin, Gordon Brown, Hack Me, Pablo Picasso, Bob Smith).

**Evidence:** See files `evidence/sqli_result.html` and `screenshots/SQL_INjection.png`

---

### Attack 2: Cross-Site Scripting (XSS)

**Vulnerability Name:** Reflected XSS

**Payload Used:**
```html
<ScRiPt>alert('XSS')</ScRiPt>
```

**Explanation:**

The Medium security level filters the `<script>` tag in lowercase. The payload bypasses this filter using mixed-case letters (ScRiPt). Since HTML parsing is case-insensitive, the browser still interprets and executes the script tag despite the capitalization. Alternative bypasses include using event handlers like `<img src=x onerror=alert('XSS')>` or HTML5 tags such as `<svg/onload=alert('XSS')>`.

**Result:** JavaScript code executed successfully in the browser context.

**Evidence:** See files `evidence/xss_result.html` and `screenshots/xss_attack.png`

---

### Attack 3: Command Injection

**Vulnerability Name:** OS Command Injection

**Payload Used:**
```
127.0.0.1 & whoami
```

**Explanation:**

The Medium security level blocks certain command separators including `&&` and `;`. However, the single ampersand `&` is not filtered. This separator executes the second command in the background, allowing arbitrary command execution. The payload successfully runs the `whoami` command after the ping command, revealing the web server user as `www-data`.

**Result:** Command executed successfully, system information disclosed.

**Evidence:** See files `evidence/command_injection_result.html` and `screenshots/Command_Injection.png`

---

# Part 3: Web Application Firewall Deployment

## Task A: WAF Deployment

### WAF Solution

**Name:** ModSecurity 3.0.14 with Nginx reverse proxy

**Ruleset:** OWASP Core Rule Set (CRS) version 4.20.0

**Total Rules Loaded:** 836 security rules

### Installation Method

Using Docker Compose with the official OWASP ModSecurity CRS image:

```yaml
version: '3.8'

services:
  dvwa:
    image: vulnerables/web-dvwa
    container_name: dvwa_backend
    networks:
      - waf_network

  waf:
    image: owasp/modsecurity-crs:nginx-alpine
    container_name: waf_proxy
    ports:
      - "9090:8080"
    depends_on:
      - dvwa
    networks:
      - waf_network
    environment:
      - BACKEND=http://dvwa:80
      - PROXY=1
      - MODSEC_RULE_ENGINE=On
      - PARANOIA=1
      - ANOMALY_INBOUND=5
      - ANOMALY_OUTBOUND=4
      - PORT=8080
      - SSL_PORT=8443

networks:
  waf_network:
    driver: bridge
```

### Network Architecture

```
Client → WAF (ModSecurity + Nginx) → DVWA Backend
  ↓         Port 9090:8080              Port 80
HTTP      [OWASP CRS Rules]         [Vulnerable App]
Request   [Anomaly Scoring]         [No Protection]
```

The WAF acts as a reverse proxy, inspecting all HTTP traffic before forwarding legitimate requests to the DVWA backend. Malicious requests are blocked and never reach the vulnerable application.

---

## Task B: Defense Testing and Analysis

### Test 1: SQL Injection Attack

**Payload:** `1 OR 1=1#`

**Result:** Request blocked

**HTTP Status Code:** 403 Forbidden

**WAF Response:**
```
403 Forbidden
ModSecurity: Access denied with code 403
```

**Triggered Rules:**
- Rule ID: 942100 - "SQL Injection Attack Detected via libinjection"
- Anomaly Score: 5
- Action: DENY

**ModSecurity Log Entry:**
```json
{
  "message": "SQL Injection Attack Detected via libinjection",
  "ruleId": "942100",
  "file": "/etc/modsecurity.d/owasp-crs/rules/REQUEST-942-APPLICATION-ATTACK-SQLI.conf",
  "data": "Matched Data: 1&1c found within ARGS:id: 1 OR 1=1#",
  "severity": "2"
}
```

---

### Test 2: XSS Attack

**Payload:** `<ScRiPt>alert('XSS')</ScRiPt>`

**Result:** Request blocked

**HTTP Status Code:** 403 Forbidden

**Triggered Rules:**
- Rule ID: 941100 - "XSS Attack Detected via libinjection"
- Rule ID: 941110 - "XSS Filter - Category 1: Script Tag Vector"
- Rule ID: 941160 - "NoScript XSS InjectionChecker: HTML Injection"
- Rule ID: 941390 - "Javascript method detected"
- Anomaly Score: 20
- Action: DENY

---

### Test 3: Command Injection Attack

**Payload:** `127.0.0.1 & whoami`

**Result:** Request blocked

**HTTP Status Code:** 403 Forbidden

**Triggered Rules:**
- Rule ID: 932235 - "Remote Command Execution: Unix Command Injection"
- Rule ID: 932260 - "Remote Command Execution: Direct Unix Command Execution"
- Rule ID: 932380 - "Remote Command Execution: Windows Command Injection"
- Anomaly Score: 15
- Action: DENY

---

### Screenshot Evidence

See file: `screenshots/WAF.png`

---

## Comparative Analysis: SQL Injection vs HTTP Flood DDoS

Both SQL Injection and HTTP Flood attacks target the application layer (Layer 7) using HTTP/HTTPS protocols, making them appear similar to legitimate traffic. However, they differ fundamentally in their objectives and execution methods.

SQL Injection aims to exploit vulnerabilities in application logic to extract, modify, or delete data from databases. It requires technical knowledge of SQL syntax and application behavior. A single, carefully crafted request can compromise an entire database. Detection relies on content analysis through Web Application Firewalls that use pattern matching and anomaly detection to identify malicious SQL syntax.

In contrast, HTTP Flood DDoS attacks seek to exhaust server resources through sheer volume of requests. These attacks require minimal technical skill but substantial resources, typically leveraging botnets to generate thousands or millions of requests. Detection depends on behavioral analysis, rate limiting, and traffic pattern recognition rather than content inspection.

While WAFs effectively mitigate SQL Injection by analyzing request content, defending against HTTP Flood requires additional layers including CDNs, rate limiting, CAPTCHA challenges, and traffic shaping. SQL Injection compromises data confidentiality and integrity, whereas HTTP Flood impacts service availability. The key distinction is quality versus quantity: SQL Injection needs one precise attack; HTTP Flood needs overwhelming volume.

---

## Conclusion

The implementation of ModSecurity with OWASP CRS successfully blocked all tested attacks with a 100% detection rate. The WAF demonstrated effective protection against common OWASP Top 10 vulnerabilities that bypassed DVWA's Medium security filters. This validates the importance of defense-in-depth strategies combining secure coding practices with network-level security controls.

---

## References

- OWASP ModSecurity Core Rule Set: https://coreruleset.org/
- DVWA Project: https://github.com/digininja/DVWA
- OWASP Top 10: https://owasp.org/www-project-top-ten/


