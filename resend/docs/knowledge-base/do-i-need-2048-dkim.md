> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Do I need 2048-bit DKIM?

> Learn why 1024-bit DKIM is enough for transactional and marketing mail, and how it compares to 2048-bit keys.

**For almost every sender, you do not need 2048-bit DKIM.** Resend signs outbound mail with 1024-bit DKIM keys, which is RFC-compliant, accepted by every major mailbox provider, and satisfies the bulk sender requirements that inbox service providers enforce.

## 1024-bit is RFC-compliant

[RFC 8301 §3.2](https://datatracker.ietf.org/doc/html/rfc8301#section-3.2) establishes 1024 bits as the minimum length verifiers must support and recommends signers use keys of at least 1024 bits. Mailbox providers including Gmail, Outlook, Yahoo, and Apple all accept 1024-bit DKIM signatures, and 1024-bit keys remain widely used across the industry for transactional and marketing mail.

## 1024-bit meets bulk sender requirements

The 2024 bulk sender requirements from Google, Yahoo, and Microsoft (which apply to anyone sending more than 5,000 messages per day to their users) require DKIM authentication alongside SPF and DMARC. **None of them mandate a specific DKIM key length**. 1024-bit DKIM signing fully satisfies these requirements, and Resend's domain setup gives you DKIM out of the box.

## 1024-bit vs 2048-bit keys

|                       | 1024-bit                                                  | 2048-bit                                                                                   |
| --------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Security**          | Meets current RFC recommendations for email signing       | Stronger cryptographic margin, better future-proofing                                      |
| **Performance**       | Faster signing and verification                           | More system resources required, can add latency                                            |
| **DNS compatibility** | Fits comfortably in a single TXT record                   | Longer public key; some DNS providers require splitting the record or hit character limits |
| **Setup**             | Straightforward, works with every DNS provider we've seen | Requires careful setup; misconfigured records can fail verification                        |

## Trade-offs of 2048-bit

* **Delivery latency.** Larger keys take longer to sign and verify on every message, which can add delay at scale.
* **DNS friction.** Most DNS providers now support the longer TXT record length needed for 2048-bit public keys, but some still impose character limits or require the value to be split into multiple strings. That's a common source of broken DKIM records and failed verifications.
* **No deliverability upside.** Inbox providers do not reward 2048-bit signatures with better placement.

## Our stance

For transactional and marketing mail, **1024-bit DKIM is the right choice.** It meets the RFC, satisfies bulk sender requirements from every major inbox provider, and keeps DNS setup simple and reliable. Resend does not currently support 2048-bit keys.

We are keeping a close eye on customer interest and evolving industry best practices. If expectations shift, we will update this article and add support accordingly.

<Note>
  If your security or compliance team has a specific requirement for 2048-bit
  DKIM, [let us know](https://resend.com/help).
</Note>
