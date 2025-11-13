# Deber 2 – Seguridad Informática

**Gabriela Coloma – Francisco Alarcón**  
**13 de noviembre del 2025**

---

## General Instructions

- If you need to write a numerical analysis or a mathematical proof, take advantage of the LaTeX support that markdown (md) offers.  
- Do not include photos or scans of your work done with pen and paper.  
- Submit your assignment as a pull request to the class repository, in the `/homework/hw2` directory. Please create a folder that includes your last name to identify your submission.

---

## 1. Standard Digital Signature Protocol Review

First, let's analyze some aspects of the right method. The first thing to be noted is that the example does not assure confidentiality, which is important to take into consideration. This is said because, in the example, the message is sent with no encryption process. Then we can understand that a hash is made from the message; let's say it's "hello." So, the hash is computed, and we get H(M). Then it uses asymmetric cryptography, so the sender encrypts using his private key so that when the receiver gets the whole package, he can only decrypt it using the sender's public key. This way, the authentication part is proven because only the public key of the one who actually sends the package can decrypt the whole thing. Then the integrity is proven when the receiver calculates the hash of the message and compares the one he got vs. the one the sender sent; if they are the same, the message was not altered, and the integrity is proven.

### Critique of Flawed Alternatives

#### Mechanism 1

Now let's talk about the first mechanism. This one proposes to use symmetric cryptography, which means both the sender and the receiver need to share a common key. The process is the same as before: the sender computes a hash from our "hello" message. Then the sender encrypts the message and the hash using the shared key. When he sends the package, the receiver has no way of decrypting the package because he doesn't have the private key of the sender, so he would have to send the package back to ask if the signature is actually his and if the message was not altered. First of all, authenticity is not achieved because the receiver cannot check for himself if the message actually came from the sender and not from an attacker. He can't check for integrity either because he can't decrypt the message.

#### Mechanism 2

For mechanism number two, the sender encrypts the whole message and doesn't use hashing. In this mechanism, the authenticity part is partially covered because it does use asymmetric cryptography, which means the sender encrypts using his private key, and the receiver can only decrypt the message using the sender's public key. This can prove that he is the sender, but it confuses signature with encryption. The correct process uses encryption only on the hash message, which is meant to prove authenticity, but this one doesn't "sign" for authentication; instead, it encrypts the whole message. In concept, the receiver could verify the sender with this, but the concepts are confused. As we said in the beginning, confidentiality isn't really measured here, but this method would fail because anyone could read the message using the sender's public key. Now, for integrity, it doesn't work due to the lack of hashing. This way, even though the receiver gets the message, he has no way of comparing the result to see if the message arrived without any changes. Meaning this method actually could pass as correct for authenticity but fails at the integrity part.

---

## 2. Vulnerability to Attack Vectors

### Scenario 1

When we are talking about signatures, the process is like this: a hash is calculated from the text, and the hash is encrypted using the sender's private key, letting the receiver decrypt the hash with the sender's public key, and only that key will decrypt the message, proving authentication. In this case, if the signature process was done correctly and using the whole message, including the "to Mark" part, if the receiver, in this case Bob, takes the message and decrypts it using Alice's public key, Bob will find the hash and the message. Then he can calculate the hash of the message and compare the one he received with the one he calculated, and in this case, they will be different, meaning the message was altered. In this case, Bob would detect the alteration. If the hash was made of a fraction of the message, then the alteration would go without any notice.

The vulnerabilities that Oscar is exploiting are, first, the possible partial integrity protection, which, as was already explained, means that if the hash was made of only a part of the message, the message could be partially altered. For example, if the hash was only made of the first part of the text "Transfer $1000" and the "to Mark" part was not covered, Oscar could modify that part without being noticeable for Bob. Also, the message needs to be sent using a safe transportation channel so that it can't be intercepted on the way to the receiver.

Some cryptographic solutions could be to make sure that the whole message, or all relevant parts of it, are included in the hashing process, thus ensuring that the signature covers the whole thing and that any alteration in any part of the message would be detected. Also, using safe transportation such as TLS to protect the message on the way to the recipient. TLS is a cryptographic protocol that assures integrity, authentication, and also confidentiality. It uses a handshake between Alice and Bob and ensures that the message cannot be modified on the way to the recipient.


### Scenario 2

This second scenario is an example of a replay attack; this attack takes parts or the whole transmitted message and replays them in a different context (Aura, 1997). The problem in this scenario is not that the message is altered or modified, but that Oscar intercepts the message and sends it over and over again. In this case, if the system doesn't have a way to check that the message is repeated, the recipient would process this request multiple times, and in this example not one transfer of 1000 is going to be made but a hundred, making Alice lose a lot of money.

Oscar is taking advantage of both the lack of id of the message and the stateless protocol. The first one means that the message doesn't have an id, timestamp, or any method to know that the message was already sent and that it was already processed by the receiver. The stateless protocol means that the system we assume is being used doesn't record past transactions, so it has again no way of knowing that this message is repeated. So this basically means that the mechanism could be covering authentication and also integrity but not the replay of this message.

Some ways of getting rid of this problem could be to use an identification for the message, meaning we could put an ID to the message and include it into the hash and signature; this way the receiver Bob could be able to identify that it is the same message being sent over and over again and not a new one. Another way could be to use a timestamp that is basically to let messages be valid just for a short period of time; this works by putting a short message with the time period in which the receiver Bob would accept this message, making all the other replays not accepted by Bob. This must be placed inside the signature to not let the attacker change it like the previous case, and if the replay is made inside the timestamp it is not useful but can be helpful. The receiver should also keep track of the messages received, making the receiver verify that the id has not been processed before and if it has don't accept it and don't process it.

Additionally, using a secure communication protocol like TLS can help protect the messages while they are being sent, making it more difficult for attackers to capture or replay them later. However, TLS alone does not fully prevent replay attacks, unique transaction IDs and timestamps are still required at the application level to detect and reject duplicated messages.

> Aura, T. (1997, June). Strategies against replay attacks. In Proceedings 10th Computer Security Foundations Workshop (pp. 59-68). IEEE.

---

## 3. Research: Transport Layer Security (TLS 1.3)

### Architecture and Evolution

When TLS 1.3 was finalized in 2018, it was a massive leap forward from version 1.2, with the clear goals of making it faster and safer. The biggest speed boost came from overhauling the initial "handshake," cutting it down from two round-trips to just one. This can save hundreds of crucial milliseconds for web performance.
On the security side, the philosophy was "less is more." The designers removed a ton of old, clunky, and insecure features, like the static RSA key exchange (which lacked Perfect Forward Secrecy), old Diffie-Hellman methods, compression (which was vulnerable), and any cipher that wasn't an AEAD. This simplification is a huge win, as a simpler protocol is harder to implement incorrectly. Furthermore, Perfect Forward Secrecy (PFS) is now mandatory, meaning unique, temporary keys protect every session. Finally, more of the handshake is encrypted, hiding metadata like the server's certificate from eavesdroppers.

### Cryptographic Primitives

TLS 1.3 is very strict about the "crypto building blocks" it allows. The most important rule is the exclusive use of AEAD ciphers (Authenticated Encryption with Associated Data), which combine encryption (confidentiality) and integrity verification (authentication) into a single, less error-prone step. The main ones used are TLS_AES_128_GCM_SHA256 and TLS_CHACHA20_POLY1305_SHA256.
For key exchange, everything centers on ephemeral (temporary) methods, using modern Elliptic Curve Diffie-Hellman (ECDHE) or standard Diffie-Hellman with very large, secure prime numbers. For digital signatures, it supports modern algorithms like RSA-PSS, ECDSA, and EdDSA.
Just as important is what was removed: all the old, broken algorithms are officially banned, including MD5, SHA-1, RC4, DES, and 3DES.


### How Security Goals Are Met

This new design comprehensively delivers on its security promises. Confidentiality is handled by the AEAD ciphers, and since encryption starts much earlier, it also protects metadata. Integrity comes from the "Authenticated" part of the AEAD ciphers, where every message includes a tag making it impossible to modify without detection. Authentication still relies on X.509 certificates but is now more robust: the server proves it owns its private key by signing a hash of the entire handshake transcript, binding its identity to that specific connection.

### Modern Applications

Because it's both faster and more secure, TLS 1.3 has been adopted everywhere. It's the standard in all major web browsers (Chrome, Firefox, Safari) and servers/CDNs (like Cloudflare). It's crucial for API communications in microservices, especially on mobile or IoT. It's also used to secure email (SMTP/IMAP), VPNs, and new privacy protocols like DNS-over-HTTPS (DoH) and DNS-over-TLS (DoT) . It's even baked directly into QUIC (HTTP/3), the new protocol that's making the web even faster.

---

## 4. Design Problem: Secure E-Contract Signing System (SECS)

For this problem, we need to design a system (SECS) where Alice and Bob can sign a digital contract. The key is that we must be able to prove they both signed it (non-repudiation of origin) and prove they both received the final copy (non-repudiation of receipt), with enough strength to hold up in court.

### System Architecture

To build trust, we can't just email a file back and forth. We need neutral, trusted third parties. I see four main components: a Certificate Authority (CA), which acts as the "digital passport office" to verify identities and issue certificates; a Time Stamping Authority (TSA), which functions as a "digital notary" to prove what existed at what time; a Contract Repository Server (CRS), which will be our "secure vault" and storage witness; and the Client Applications that Alice and Bob use to handle the crypto.

### Contract Signing Protocol

I've broken the process into four phases to ensure every step is verifiable.
#### Phase 1: Contract Creation (Alice)
Alice creates the contract $C$, calculates its hash $H(C)$ (with SHA-384), and then signs that hash. Importantly, her signature also includes a unique Contract_ID, a timestamp $T1$, and the word "INTENT", to prevent claims of accidental signing. She then sends the contract, her signature, and her certificate to Bob over a secure TLS 1.3 channel.
#### Phase 2: Counter-Signature (Bob)
Bob receives the package, verifies Alice's certificate with the CA, and validates her signature. He independently computes the contract's hash to ensure it wasn't altered. If everything checks out, he creates his own signature (Sig_B), which includes the hash $H(C)$, Alice's signature (Sig_A), his own "ACCEPT" string, the Contract_ID, and a new timestamp $T2$. He then sends his signature and certificate back to Alice.
#### Phase 3: Repository Commitment (Both)
Now, both parties have the complete evidence package $E$. To prove when this was finalized, they both send a hash of this package to the TSA to get a secure timestamp ($TS_A$ and $TS_B$). They then both submit the full, timestamped evidence package to the Contract Repository Server (CRS). The CRS accepts it, logs it, and gives each of them a signed digital "receipt" ($R$) that proves it was stored.
#### Phase 4: Acknowledgment (Both)
This is the final step to prove receipt. Both Alice and Bob sign the receipt $R$ they got from the CRS and send that acknowledgment back to the CRS. The CRS stores these final acknowledgments ($Ack_A$, $Ack_B$) in its immutable log, closing the loop.


### Non-Repudiation Mechanisms

This design specifically addresses both types of non-repudiation. Non-Repudiation of Origin (proving they signed) is handled by the digital signatures that link their unique private keys to the content, intent, and timestamps. Non-Repudiation of Receipt (proving they received it) is the CRS's job. By submitting the signed acknowledgment (Phase 4), both parties are cryptographically confirming: "I have received the final, signed contract."

### Legal Enforceability

This system is designed to be "bulletproof" in a legal challenge. Private keys must be stored in Hardware Security Modules (HSMs) to prevent theft, and all communication uses TLS 1.3. Replay attacks are prevented by the unique Contract_ID and timestamps. The final evidence package contains everything a court would need: the contract, the certificate chains, the signatures, the third-party timestamps, and the complete, immutable audit log from the CRS, aligning with standards like eIDAS and the ESIGN Act.

---

