# Homework 3: Web Security

**Course:** Seguridad Informática
**Professor:** Alejandro Proaño
**University:** Universidad San Francisco de Quito (USFQ)

**Students:**
- Jesus Alarcon (00324826)
- Gabriela Coloma (00325312)

**Date:** November 27, 2025

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


